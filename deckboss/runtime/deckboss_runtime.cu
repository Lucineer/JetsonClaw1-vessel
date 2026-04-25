/**
 * deckboss_runtime.cu — Production Inference Runtime Implementation
 * 
 * Compile: /usr/local/cuda-12.6/bin/nvcc -arch=sm_87 -O3 -c deckboss_runtime.cu -o deckboss_runtime.o
 * 
 * Based on 14 benchmark suites:
 * - Direct-mapped weights (no indirection)
 * - 4 CUDA streams (optimal for Orin)
 * - Batched inference (single kernel launch)
 * - No CUDA Graphs, no quantization, no gather
 * - Zero-copy output (unified memory, no D2H copy)
 * - Async pinned input (H2D overlap)
 */

#include "deckboss_runtime.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>

#define DB_CHECK(call) do { \
    cudaError_t _err = call; \
    if (_err != cudaSuccess) { \
        snprintf(ctx->last_error_msg, sizeof(ctx->last_error_msg), \
                 "CUDA error %s:%d: %s", __FILE__, __LINE__, cudaGetErrorString(_err)); \
        ctx->last_error = (int)_err; \
        return -1; \
    } \
} while(0)

__global__ void db_batch_infer(const half* __restrict__ weights,
                                const half* __restrict__ input,
                                float* __restrict__ output,
                                int dim, int num_rooms) {
    int room = blockIdx.x;
    if (room >= num_rooms) return;
    int lane = threadIdx.x;
    
    float sum = 0.0f;
    for (int i = lane; i < dim; i += 32)
        sum += __half2float(weights[(size_t)room * dim + i]) * __half2float(input[i]);
    
    #pragma unroll
    for (int offset = 16; offset > 0; offset /= 2)
        sum += __shfl_down_sync(0xffffffff, sum, offset);
    
    if (lane == 0) {
        float x = sum;
        output[room] = x * 0.5f * (1.0f + tanhf(0.7978845608f * (x + 0.044715f * x * x * x)));
    }
}

deckboss_ctx* deckboss_init(int dim, int max_rooms) {
    deckboss_ctx* ctx = (deckboss_ctx*)calloc(1, sizeof(deckboss_ctx));
    if (!ctx) return NULL;
    
    ctx->config.dim = dim;
    ctx->config.max_rooms = max_rooms;
    ctx->config.num_streams = 4;
    
    // Allocate GPU memory
    cudaError_t err;
    err = cudaMalloc(&ctx->d_weights, (size_t)max_rooms * dim * sizeof(half));
    if (err != cudaSuccess) { free(ctx); return NULL; }
    
    err = cudaMalloc(&ctx->d_input, dim * sizeof(half));
    if (err != cudaSuccess) { cudaFree(ctx->d_weights); free(ctx); return NULL; }
    
    err = cudaMalloc(&ctx->d_output, max_rooms * sizeof(float));
    if (err != cudaSuccess) { 
        cudaFree(ctx->d_weights); cudaFree(ctx->d_input); free(ctx); return NULL; 
    }
    
    // Zero weights
    err = cudaMemset(ctx->d_weights, 0, (size_t)max_rooms * dim * sizeof(half));
    if (err != cudaSuccess) { 
        cudaFree(ctx->d_weights); cudaFree(ctx->d_input); cudaFree(ctx->d_output); free(ctx); return NULL; 
    }
    
    // Create streams
    ctx->streams = (cudaStream_t*)calloc(4, sizeof(cudaStream_t));
    for (int i = 0; i < 4; i++) {
        err = cudaStreamCreate(&ctx->streams[i]);
        if (err != cudaSuccess) {
            for (int j = 0; j < i; j++) cudaStreamDestroy(ctx->streams[j]);
            cudaFree(ctx->d_weights); cudaFree(ctx->d_input); cudaFree(ctx->d_output);
            free(ctx->streams); free(ctx); return NULL;
        }
    }
    
    ctx->stream_idx = 0;
    ctx->rooms_loaded = 0;
    ctx->total_infers = 0;
    ctx->total_latency_ms = 0;
    ctx->last_error = 0;
    
    return ctx;
}

void deckboss_destroy(deckboss_ctx* ctx) {
    if (!ctx) return;
    
    for (int i = 0; i < 4; i++)
        if (ctx->streams[i]) cudaStreamDestroy(ctx->streams[i]);
    
    if (ctx->d_weights) cudaFree(ctx->d_weights);
    if (ctx->d_input) cudaFree(ctx->d_input);
    if (ctx->d_output) cudaFree(ctx->d_output);
    
    // Zero-copy buffers
    if (ctx->h_zerocopy_output) cudaFreeHost(ctx->h_zerocopy_output);
    if (ctx->h_zerocopy_input) cudaFreeHost(ctx->h_zerocopy_input);
    
    free(ctx->streams);
    free(ctx);
}

int deckboss_load_room(deckboss_ctx* ctx, int room_id, const half* weights, int dim) {
    if (!ctx || room_id < 0 || room_id >= ctx->config.max_rooms) return -1;
    if (dim != ctx->config.dim) return -1;
    
    cudaError_t err = cudaMemcpyAsync(
        ctx->d_weights + (size_t)room_id * dim,
        weights, dim * sizeof(half),
        cudaMemcpyHostToDevice,
        ctx->streams[0]
    );
    
    if (err != cudaSuccess) {
        snprintf(ctx->last_error_msg, sizeof(ctx->last_error_msg), 
                 "cudaMemcpyAsync failed: %s", cudaGetErrorString(err));
        ctx->last_error = (int)err;
        return -1;
    }
    
    ctx->rooms_loaded++;
    return 0;
}

int deckboss_swap_weights(deckboss_ctx* ctx, int room_id, const half* weights, int dim) {
    return deckboss_load_room(ctx, room_id, weights, dim);
}

int deckboss_set_input(deckboss_ctx* ctx, const half* input, int dim) {
    if (!ctx || dim != ctx->config.dim) return -1;
    
    DB_CHECK(cudaMemcpyAsync(ctx->d_input, input, dim * sizeof(half),
                              cudaMemcpyHostToDevice, ctx->streams[0]));
    return 0;
}

int deckboss_infer_async(deckboss_ctx* ctx, const int* room_ids, int num_rooms, float* d_output) {
    if (!ctx || !room_ids || num_rooms <= 0) return -1;
    
    cudaStream_t s = ctx->streams[ctx->stream_idx++ % 4];
    
    dim3 block(32);
    dim3 grid(num_rooms);
    
    db_batch_infer<<<grid, block, 0, s>>>(
        ctx->d_weights, ctx->d_input, 
        d_output ? d_output : ctx->d_output,
        ctx->config.dim, num_rooms
    );
    
    return 0;
}

int deckboss_wait(deckboss_ctx* ctx) {
    if (!ctx) return -1;
    
    for (int i = 0; i < 4; i++)
        cudaStreamSynchronize(ctx->streams[i]);
    
    return 0;
}

float deckboss_infer(deckboss_ctx* ctx, const int* room_ids, int num_rooms, float* output) {
    if (!ctx || !room_ids || num_rooms <= 0 || !output) return -1.0f;
    
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    cudaEventRecord(start);
    
    // Launch inference
    deckboss_infer_async(ctx, room_ids, num_rooms, ctx->d_output);
    
    // Wait for completion
    deckboss_wait(ctx);
    
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float ms;
    cudaEventElapsedTime(&ms, start, stop);
    
    // Copy output back to host
    cudaMemcpy(output, ctx->d_output, num_rooms * sizeof(float), cudaMemcpyDeviceToHost);
    
    // Stats
    ctx->total_infers++;
    ctx->total_latency_ms += ms;
    
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    
    return ms * 1000.0f; // return microseconds
}

void deckboss_memory_usage(deckboss_ctx* ctx, float* used_mb, float* total_mb) {
    if (!ctx) return;
    
    size_t weights_bytes = (size_t)ctx->config.max_rooms * ctx->config.dim * sizeof(half);
    size_t input_bytes = ctx->config.dim * sizeof(half);
    size_t output_bytes = ctx->config.max_rooms * sizeof(float);
    size_t total = weights_bytes + input_bytes + output_bytes;
    
    if (total_mb) *total_mb = (float)total / (1024 * 1024);
    
    // Actual rooms loaded
    size_t used = (size_t)ctx->rooms_loaded * ctx->config.dim * sizeof(half);
    if (used_mb) *used_mb = (float)used / (1024 * 1024);
}

void deckboss_stats(deckboss_ctx* ctx, int64_t* total_infers, float* avg_latency) {
    if (!ctx) return;
    if (total_infers) *total_infers = ctx->total_infers;
    if (avg_latency) *avg_latency = ctx->total_infers > 0 
        ? (ctx->total_latency_ms / ctx->total_infers) * 1000.0f  // us
        : 0.0f;
}

const char* deckboss_last_error(deckboss_ctx* ctx) {
    if (!ctx) return "null context";
    return ctx->last_error_msg[0] ? ctx->last_error_msg : "no error";
}

deckboss_ctx* deckboss_init_zerocopy(int dim, int max_rooms) {
    deckboss_ctx* ctx = deckboss_init(dim, max_rooms);
    if (!ctx) return NULL;
    
    cudaError_t err;
    
    // Allocate zero-copy output buffer (host-visible, device-writable)
    err = cudaHostAlloc(&ctx->h_zerocopy_output, max_rooms * sizeof(float),
                        cudaHostAllocMapped);
    if (err != cudaSuccess) {
        snprintf(ctx->last_error_msg, sizeof(ctx->last_error_msg),
                 "cudaHostAlloc output failed: %s", cudaGetErrorString(err));
        deckboss_destroy(ctx);
        return NULL;
    }
    
    // Get device pointer for zero-copy output
    err = cudaHostGetDevicePointer(&ctx->d_zerocopy_output, ctx->h_zerocopy_output, 0);
    if (err != cudaSuccess) {
        snprintf(ctx->last_error_msg, sizeof(ctx->last_error_msg),
                 "cudaHostGetDevicePointer output failed: %s", cudaGetErrorString(err));
        cudaFreeHost(ctx->h_zerocopy_output);
        deckboss_destroy(ctx);
        return NULL;
    }
    
    // Allocate zero-copy input buffer (host-writable, device-readable)
    err = cudaHostAlloc(&ctx->h_zerocopy_input, dim * sizeof(half),
                        cudaHostAllocMapped);
    if (err != cudaSuccess) {
        snprintf(ctx->last_error_msg, sizeof(ctx->last_error_msg),
                 "cudaHostAlloc input failed: %s", cudaGetErrorString(err));
        cudaFreeHost(ctx->h_zerocopy_output);
        deckboss_destroy(ctx);
        return NULL;
    }
    
    err = cudaHostGetDevicePointer(&ctx->d_zerocopy_input, ctx->h_zerocopy_input, 0);
    if (err != cudaSuccess) {
        snprintf(ctx->last_error_msg, sizeof(ctx->last_error_msg),
                 "cudaHostGetDevicePointer input failed: %s", cudaGetErrorString(err));
        cudaFreeHost(ctx->h_zerocopy_input);
        cudaFreeHost(ctx->h_zerocopy_output);
        deckboss_destroy(ctx);
        return NULL;
    }
    
    ctx->zerocopy_enabled = 1;
    return ctx;
}

float* deckboss_zerocopy_infer(deckboss_ctx* ctx, const int* room_ids, int num_rooms) {
    if (!ctx || !ctx->zerocopy_enabled || !room_ids || num_rooms <= 0) return NULL;
    if (num_rooms > ctx->config.max_rooms) return NULL;
    
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    cudaEventRecord(start);
    
    // Use zero-copy device pointers directly
    cudaStream_t s = ctx->streams[ctx->stream_idx++ % 4];
    dim3 block(32);
    dim3 grid(num_rooms);
    
    db_batch_infer<<<grid, block, 0, s>>>(
        ctx->d_weights, ctx->d_zerocopy_input, ctx->d_zerocopy_output,
        ctx->config.dim, num_rooms
    );
    
    cudaStreamSynchronize(s);
    
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float ms;
    cudaEventElapsedTime(&ms, start, stop);
    
    ctx->total_infers++;
    ctx->total_latency_ms += ms;
    
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    
    // Return host-visible pointer — no D2H copy needed!
    return ctx->h_zerocopy_output;
}
