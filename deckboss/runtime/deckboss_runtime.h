/**
 * deckboss_runtime.h — Production Inference Runtime
 * 
 * Jetson-native room inference library.
 * Based on 14 benchmark suites of real hardware testing.
 * 
 * Usage:
 *   deckboss_ctx* ctx = deckboss_init(256, 2048);  // dim=256, max_rooms=2048
 *   deckboss_load_room(ctx, room_id, weights_ptr, dim);
 *   float results[64];
 *   deckboss_infer(ctx, room_ids, 64, input_ptr, results);
 *   deckboss_destroy(ctx);
 * 
 * Zero-copy mode (recommended on Jetson unified memory):
 *   deckboss_ctx* ctx = deckboss_init_zerocopy(256, 2048);
 *   deckboss_load_room(ctx, room_id, weights_ptr, dim);
 *   deckboss_set_input(ctx, input_ptr, dim);
 *   float* results = deckboss_zerocopy_infer(ctx, room_ids, 64);
 *   // results is host-visible, no D2H copy needed
 *   deckboss_destroy(ctx);
 * 
 * Build: nvcc -arch=sm_87 -O3 -c deckboss_runtime.cu -o deckboss_runtime.o
 * Link: nvcc -arch=sm_87 -shared deckboss_runtime.o -o libdeckboss.so
 */

#ifndef DECKBOSS_RUNTIME_H
#define DECKBOSS_RUNTIME_H

#include <cuda_fp16.h>
#include <cuda_runtime.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * deckboss configuration
 */
typedef struct {
    int dim;            // Room dimension (e.g., 256)
    int max_rooms;      // Max addressable rooms (e.g., 2048)
    int num_streams;    // CUDA streams (always 4 for Orin)
} deckboss_config;

/**
 * deckboss runtime context (opaque)
 */
typedef struct deckboss_ctx {
    deckboss_config config;
    
    // GPU memory — direct-mapped weight storage
    half* d_weights;        // [max_rooms * dim]
    half* d_input;          // [dim]
    float* d_output;        // [max_rooms]
    
    // Zero-copy memory (Jetson unified memory optimization)
    float* h_zerocopy_output;   // host-visible output buffer
    float* d_zerocopy_output;   // device pointer to same memory
    half* h_zerocopy_input;     // host-visible input buffer
    half* d_zerocopy_input;     // device pointer to same memory
    int zerocopy_enabled;
    
    // CUDA streams (4 for Orin, round-robin)
    cudaStream_t* streams;
    int stream_idx;
    
    // State tracking
    int rooms_loaded;
    int64_t total_infers;
    float total_latency_ms;
    
    // Error state
    int last_error;
    char last_error_msg[256];
} deckboss_ctx;

/**
 * Initialize deckboss runtime.
 * 
 * @param dim        Room dimension (weights per room)
 * @param max_rooms  Maximum number of rooms to cache
 * @return           Context pointer, or NULL on failure
 */
deckboss_ctx* deckboss_init(int dim, int max_rooms);

/**
 * Destroy deckboss runtime and free all GPU memory.
 */
void deckboss_destroy(deckboss_ctx* ctx);

/**
 * Load room weights into GPU memory (direct-mapped).
 * Thread-safe. Async (uses stream 0).
 * 
 * @param ctx       Runtime context
 * @param room_id   Room identifier (0 to max_rooms-1)
 * @param weights   FP16 weights array [dim]
 * @param dim       Dimension of weights
 * @return          0 on success, -1 on error
 */
int deckboss_load_room(deckboss_ctx* ctx, int room_id, const half* weights, int dim);

/**
 * Hot-swap room weights (same room, new weights).
 * Much faster than load (no allocation, just memcpy).
 * 
 * @param ctx       Runtime context
 * @param room_id   Room identifier
 * @param weights   New FP16 weights [dim]
 * @param dim       Dimension
 * @return          0 on success
 */
int deckboss_swap_weights(deckboss_ctx* ctx, int room_id, const half* weights, int dim);

/**
 * Set input vector for next inference batch.
 * 
 * @param ctx       Runtime context
 * @param input     FP16 input vector [dim]
 * @param dim       Dimension
 * @return          0 on success
 */
int deckboss_set_input(deckboss_ctx* ctx, const half* input, int dim);

/**
 * Run batched inference on multiple rooms.
 * Room weights must already be loaded (deckboss_load_room).
 * Uses 4-stream round-robin dispatch.
 * 
 * @param ctx       Runtime context
 * @param room_ids  Array of room IDs to infer [num_rooms]
 * @param num_rooms Number of rooms in batch
 * @param output    Output array [num_rooms] (host memory, copied back)
 * @return          Latency in microseconds, or -1 on error
 */
float deckboss_infer(deckboss_ctx* ctx, const int* room_ids, int num_rooms, float* output);

/**
 * Run batched inference, asynchronous.
 * Returns immediately. Call deckboss_wait() for results.
 * 
 * @param ctx       Runtime context
 * @param room_ids  Array of room IDs [num_rooms]
 * @param num_rooms Number of rooms
 * @param d_output  Pre-allocated GPU output buffer [num_rooms]
 * @return          0 on success
 */
int deckboss_infer_async(deckboss_ctx* ctx, const int* room_ids, int num_rooms, float* d_output);

/**
 * Wait for async inference to complete.
 * 
 * @param ctx   Runtime context
 * @return      0 on success
 */
int deckboss_wait(deckboss_ctx* ctx);

/**
 * Initialize deckboss with zero-copy output buffers.
 * On Jetson (unified memory), eliminates D2H copy entirely.
 * 3.7x faster than standard init for single-room inference.
 * 
 * @param dim        Room dimension
 * @param max_rooms  Maximum rooms to cache
 * @return           Context pointer, or NULL on failure
 */
deckboss_ctx* deckboss_init_zerocopy(int dim, int max_rooms);

/**
 * Run inference with zero-copy output.
 * Returns pointer to host-visible memory (no D2H copy).
 * Valid until next deckboss_zerocopy_infer or deckboss_destroy call.
 * 
 * @param ctx       Runtime context (must be init'd with zerocopy)
 * @param room_ids  Array of room IDs [num_rooms]
 * @param num_rooms Number of rooms
 * @return          Pointer to float[num_rooms] in host memory, NULL on error
 */
float* deckboss_zerocopy_infer(deckboss_ctx* ctx, const int* room_ids, int num_rooms);

/**
 * Get GPU memory usage.
 * 
 * @param ctx       Runtime context
 * @param used_mb   Output: used GPU memory in MB
 * @param total_mb  Output: total allocated in MB
 */
void deckboss_memory_usage(deckboss_ctx* ctx, float* used_mb, float* total_mb);

/**
 * Get runtime statistics.
 * 
 * @param ctx           Runtime context
 * @param total_infers  Output: total inference calls
 * @param avg_latency   Output: average latency in microseconds
 */
void deckboss_stats(deckboss_ctx* ctx, int64_t* total_infers, float* avg_latency);

/**
 * Get last error message.
 * 
 * @param ctx   Runtime context
 * @return      Error message string (valid until next call)
 */
const char* deckboss_last_error(deckboss_ctx* ctx);

#ifdef __cplusplus
}
#endif

#endif // DECKBOSS_RUNTIME_H
