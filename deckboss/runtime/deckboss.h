/**
 * deckboss.h — DeckBoss Production Runtime API
 * 
 * C API for running Tensor Core room inference on Jetson Orin.
 * Designed for embedding: PLATO hermits, CLI tools, other agents.
 * 
 * Version: 0.1.0-alpha
 * Target: Jetson Orin (sm_87), CUDA 12.6
 */

#ifndef DECKBOSS_H
#define DECKBOSS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ===== Types ===== */

/** Opaque handle to a DeckBoss instance */
typedef struct deckboss_s* deckboss_t;

/** Opaque handle to a loaded room */
typedef struct db_room_s* db_room_t;

/** Result codes */
typedef enum {
    DB_OK           = 0,    /* Success */
    DB_ERR_INIT     = -1,   /* CUDA/init failure */
    DB_ERR_NOMEM    = -2,   /* Out of GPU memory */
    DB_ERR_ROOM     = -3,   /* Room not found or invalid */
    DB_ERR_INFER    = -4,   /* Inference failed */
    DB_ERR_PARAM    = -5,   /* Invalid parameter */
    DB_ERR_CONFIG   = -6,   /* Bad configuration */
    DB_ERR_GPU      = -7,   /* GPU not available */
} db_result_t;

/** Room configuration */
typedef struct {
    const char* name;           /* Room identifier */
    const char* engine_path;    /* Path to .trt engine file */
    uint32_t   max_batch;       /* Max batch size (default: 1) */
    uint32_t   priority;        /* Stream priority (default: 0) */
    float      gpu_mem_limit_mb;/* Max GPU memory for this room */
} db_room_config_t;

/** Inference request */
typedef struct {
    const void* input;          /* Input tensor data (FP16) */
    size_t      input_bytes;    /* Size of input in bytes */
    void*       output;         /* Output buffer (pre-allocated) */
    size_t      output_bytes;   /* Expected output size */
} db_infer_request_t;

/** Inference result */
typedef struct {
    db_result_t status;         /* Result code */
    float       latency_ms;     /* Inference time in milliseconds */
    uint32_t    gpu_mem_used_mb;/* GPU memory after inference */
} db_infer_result_t;

/** Device info */
typedef struct {
    const char* gpu_name;       /* e.g. "Orin (nvgpu)" */
    uint32_t    sm_version;     /* e.g. 87 */
    uint64_t    total_mem_mb;   /* Total GPU memory in MB */
    uint64_t    free_mem_mb;    /* Available GPU memory in MB */
    float       temperature_c;  /* GPU temperature */
    uint32_t    clock_sm_mhz;   /* SM clock frequency */
} db_device_info_t;

/** Callback for async inference completion */
typedef void (*db_infer_callback_t)(db_infer_result_t* result, void* user_data);

/* ===== Lifecycle ===== */

/**
 * Initialize DeckBoss runtime.
 * Call once at process start. Loads CUDA, queries GPU, allocates shared resources.
 * 
 * @param config_path  Path to deckboss.conf (NULL for defaults)
 * @param out_handle   Receives the deckboss instance handle
 * @return DB_OK on success
 */
db_result_t deckboss_init(const char* config_path, deckboss_t* out_handle);

/**
 * Shut down DeckBoss and free all resources.
 * Unloads all rooms, frees CUDA memory.
 */
db_result_t deckboss_shutdown(deckboss_t db);

/**
 * Query device information.
 */
db_result_t deckboss_device_info(deckboss_t db, db_device_info_t* info);

/* ===== Room Management ===== */

/**
 * Load a room (TensorRT engine) for inference.
 * 
 * @param db       DeckBoss instance
 * @param config   Room configuration
 * @param out_room Receives room handle
 * @return DB_OK on success
 */
db_result_t deckboss_load_room(deckboss_t db, const db_room_config_t* config, db_room_t* out_room);

/**
 * Unload a room and free its GPU memory.
 */
db_result_t deckboss_unload_room(db_room_t room);

/**
 * Switch to a different room for subsequent inference calls.
 * Equivalent to deckboss_set_active_room() — the active room is used by
 * deckboss_infer() when no room is specified.
 */
db_result_t deckboss_switch_room(deckboss_t db, db_room_t room);

/**
 * Get currently active room handle.
 */
db_result_t deckboss_active_room(deckboss_t db, db_room_t* out_room);

/**
 * List all loaded rooms.
 * @param names  Output buffer for room names
 * @param count  Max names to write; receives actual count
 */
db_result_t deckboss_list_rooms(deckboss_t db, const char** names, uint32_t* count);

/* ===== Inference ===== */

/**
 * Run synchronous inference on the active room.
 * 
 * @param db       DeckBoss instance
 * @param request  Input/output buffers
 * @param result   Receives timing and status info
 */
db_result_t deckboss_infer(deckboss_t db, const db_infer_request_t* request, db_infer_result_t* result);

/**
 * Run inference on a specific room (no need to switch).
 */
db_result_t deckboss_infer_room(db_room_t room, const db_infer_request_t* request, db_infer_result_t* result);

/**
 * Run asynchronous inference. Callback fires when complete.
 * Non-blocking — safe to call from PLATO event loop.
 */
db_result_t deckboss_infer_async(deckboss_t db, const db_infer_request_t* request, 
                                  db_infer_callback_t callback, void* user_data);

/* ===== Utility ===== */

/**
 * Get last error message (thread-local).
 */
const char* deckboss_last_error(void);

/**
 * Get DeckBoss version string.
 */
const char* deckboss_version(void);

/**
 * Get GPU memory stats for monitoring.
 */
db_result_t deckboss_memory_stats(deckboss_t db, uint64_t* used_mb, uint64_t* free_mb);

#ifdef __cplusplus
}
#endif

#endif /* DECKBOSS_H */
