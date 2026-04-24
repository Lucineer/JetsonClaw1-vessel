/**
 * example_infer.c — DeckBoss usage example
 * 
 * Demonstrates: init, load room, run inference, cleanup.
 * Compile: gcc -o example_infer example_infer.c -L/opt/deckboss/lib -ldeckboss -I/opt/deckboss/include
 * Run:     ./example_infer
 */

#include <stdio.h>
#include <stdlib.h>
#include "deckboss.h"

int main(int argc, char** argv) {
    deckboss_t db = NULL;
    db_result_t rc;
    
    /* 1. Initialize */
    rc = deckboss_init(NULL, &db);
    if (rc != DB_OK) {
        fprintf(stderr, "Init failed: %s\n", deckboss_last_error());
        return 1;
    }
    printf("DeckBoss %s initialized\n", deckboss_version());
    
    /* 2. Device info */
    db_device_info_t info;
    rc = deckboss_device_info(db, &info);
    if (rc == DB_OK) {
        printf("GPU: %s (sm_%u), %.0fMB free, %.1f°C\n",
               info.gpu_name, info.sm_version, 
               (double)info.free_mem_mb, info.temperature_c);
    }
    
    /* 3. Load a room */
    db_room_config_t room_cfg = {
        .name = "chess-room",
        .engine_path = "/opt/deckboss/rooms/chess-room.trt",
        .max_batch = 1,
        .priority = 0,
        .gpu_mem_limit_mb = 512.0f
    };
    db_room_t room = NULL;
    rc = deckboss_load_room(db, &room_cfg, &room);
    if (rc != DB_OK) {
        fprintf(stderr, "Load room failed: %s\n", deckboss_last_error());
        deckboss_shutdown(db);
        return 1;
    }
    printf("Room '%s' loaded\n", room_cfg.name);
    
    /* 4. Run inference */
    /* In production: populate input from PLATO bridge / network */
    float input[256] = {0};  /* dummy FP16-compatible data */
    float output[256] = {0};
    
    db_infer_request_t req = {
        .input = input,
        .input_bytes = sizeof(input),
        .output = output,
        .output_bytes = sizeof(output)
    };
    
    db_infer_result_t result;
    rc = deckboss_infer_room(room, &req, &result);
    if (rc == DB_OK) {
        printf("Inference: %.2fms, GPU mem: %uMB\n", 
               result.latency_ms, result.gpu_mem_used_mb);
    } else {
        fprintf(stderr, "Inference failed: %s\n", deckboss_last_error());
    }
    
    /* 5. Memory check */
    uint64_t used, free;
    deckboss_memory_stats(db, &used, &free);
    printf("GPU memory: %luMB used, %luMB free\n", used, free);
    
    /* 6. Cleanup */
    deckboss_unload_room(room);
    deckboss_shutdown(db);
    printf("Shutdown complete\n");
    
    return 0;
}
