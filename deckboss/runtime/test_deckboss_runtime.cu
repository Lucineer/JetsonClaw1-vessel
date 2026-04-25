/**
 * test_deckboss_runtime.c — Integration test for deckboss runtime
 * 
 * Compile: /usr/local/cuda-12.6/bin/nvcc -arch=sm_87 -O3 \
 *          deckboss_runtime.cu test_deckboss_runtime.cu -o test_deckboss_runtime
 */

#include "deckboss_runtime.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>

int main() {
    printf("============================================================\n");
    printf("deckboss Runtime — Integration Test\n");
    printf("============================================================\n\n");
    
    const int DIM = 256;
    const int MAX_ROOMS = 2048;
    const int ITERS = 100000;
    
    // 1. Initialize
    printf("[1] Initializing deckboss (dim=%d, max_rooms=%d)...\n", DIM, MAX_ROOMS);
    deckboss_ctx* ctx = deckboss_init(DIM, MAX_ROOMS);
    if (!ctx) {
        printf("    FAILED: deckboss_init returned NULL\n");
        return 1;
    }
    printf("    OK\n");
    
    // 2. Check memory
    float used_mb, total_mb;
    deckboss_memory_usage(ctx, &used_mb, &total_mb);
    printf("[2] GPU memory: %.1f MB allocated\n", total_mb);
    
    // 3. Load rooms
    printf("[3] Loading 512 rooms...\n");
    half* weights = (half*)malloc(DIM * sizeof(half));
    half* input = (half*)malloc(DIM * sizeof(half));
    
    srand(42);
    for (int i = 0; i < DIM; i++)
        input[i] = __float2half((float)rand() / RAND_MAX - 0.5f);
    
    for (int r = 0; r < 512; r++) {
        for (int i = 0; i < DIM; i++)
            weights[i] = __float2half((float)rand() / RAND_MAX - 0.5f);
        int ret = deckboss_load_room(ctx, r, weights, DIM);
        if (ret != 0) {
            printf("    FAILED to load room %d: %s\n", r, deckboss_last_error(ctx));
            return 1;
        }
    }
    deckboss_wait(ctx);
    printf("    OK (512 rooms loaded)\n");
    
    // 4. Set input
    printf("[4] Setting input vector...\n");
    int ret = deckboss_set_input(ctx, input, DIM);
    if (ret != 0) {
        printf("    FAILED: %s\n", deckboss_last_error(ctx));
        return 1;
    }
    printf("    OK\n");
    
    // 5. Single inference
    printf("[5] Single room inference...\n");
    float result;
    int room_id = 42;
    float latency = deckboss_infer(ctx, &room_id, 1, &result);
    printf("    Room %d output: %.4f (latency: %.1f us)\n", room_id, result, latency);
    
    // 6. Batch inference — production (6 rooms)
    printf("\n[6] Production benchmark (6 rooms, %d iterations)...\n", ITERS);
    int prod_ids[] = {0, 1, 2, 3, 4, 5};
    float prod_results[6];
    
    // Warmup
    for (int i = 0; i < 2000; i++)
        deckboss_infer(ctx, prod_ids, 6, prod_results);
    
    float total_us = 0;
    for (int i = 0; i < ITERS; i++)
        total_us += deckboss_infer(ctx, prod_ids, 6, prod_results);
    
    float avg_us = total_us / ITERS;
    printf("    Avg latency: %.1f us/batch | %.2f us/room | %.0f room-qps\n",
           avg_us, avg_us / 6.0, 6.0 / (avg_us / 1000000.0));
    printf("    Sample outputs: %.4f, %.4f, %.4f\n", 
           prod_results[0], prod_results[1], prod_results[2]);
    
    // 7. Fleet benchmark (64 rooms)
    printf("\n[7] Fleet benchmark (64 rooms, %d iterations)...\n", ITERS);
    int fleet_ids[64];
    float fleet_results[64];
    for (int i = 0; i < 64; i++) fleet_ids[i] = i;
    
    for (int i = 0; i < 2000; i++)
        deckboss_infer(ctx, fleet_ids, 64, fleet_results);
    
    total_us = 0;
    for (int i = 0; i < ITERS; i++)
        total_us += deckboss_infer(ctx, fleet_ids, 64, fleet_results);
    
    avg_us = total_us / ITERS;
    printf("    Avg latency: %.1f us/batch | %.3f us/room | %.0f room-qps\n",
           avg_us, avg_us / 64.0, 64.0 / (avg_us / 1000000.0));
    
    // 8. Large batch (256 rooms)
    printf("\n[8] Large batch (256 rooms, %d iterations)...\n", ITERS);
    int large_ids[256];
    float large_results[256];
    for (int i = 0; i < 256; i++) large_ids[i] = i;
    
    for (int i = 0; i < 1000; i++)
        deckboss_infer(ctx, large_ids, 256, large_results);
    
    total_us = 0;
    for (int i = 0; i < ITERS; i++)
        total_us += deckboss_infer(ctx, large_ids, 256, large_results);
    
    avg_us = total_us / ITERS;
    printf("    Avg latency: %.1f us/batch | %.3f us/room | %.0f room-qps\n",
           avg_us, avg_us / 256.0, 256.0 / (avg_us / 1000000.0));
    
    // 9. Weight swap benchmark
    printf("\n[9] Weight swap benchmark (10000 swaps)...\n");
    for (int i = 0; i < DIM; i++)
        weights[i] = __float2half(0.42f);
    
    cudaEvent_t sw_start, sw_stop;
    cudaEventCreate(&sw_start);
    cudaEventCreate(&sw_stop);
    
    cudaEventRecord(sw_start);
    for (int i = 0; i < 10000; i++)
        deckboss_swap_weights(ctx, 42, weights, DIM);
    deckboss_wait(ctx);
    cudaEventRecord(sw_stop);
    cudaEventSynchronize(sw_stop);
    
    float swap_ms;
    cudaEventElapsedTime(&swap_ms, sw_start, sw_stop);
    printf("    10000 swaps in %.1f ms (%.2f us/swap, %.0f swaps/sec)\n",
           swap_ms, swap_ms / 10000.0 * 1000.0, 10000.0 / (swap_ms / 1000.0));
    
    cudaEventDestroy(sw_start);
    cudaEventDestroy(sw_stop);
    
    // 10. Stats
    printf("\n[10] Runtime statistics:\n");
    int64_t total_infers;
    float avg_latency;
    deckboss_stats(ctx, &total_infers, &avg_latency);
    printf("    Total infers: %ld\n", (long)total_infers);
    printf("    Avg latency: %.1f us\n", avg_latency);
    
    // 11. Cleanup
    printf("\n[11] Destroying runtime...\n");
    deckboss_destroy(ctx);
    free(weights);
    free(input);
    printf("    OK\n\n");
    
    printf("============================================================\n");
    printf("ALL TESTS PASSED\n");
    printf("============================================================\n");
    
    return 0;
}
