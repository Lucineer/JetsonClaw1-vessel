---
id: gguf-format-v3
created: 2026-04-30
updated: 2026-04-30
tags: [format, machine-learning, ggml]
---

# GGUF v3 File Format — Field Notes

GGUF (GGML Universal Format) is the file format used by llama.cpp for quantized large language models.

## Header (24 bytes)
| Offset | Size | Field | Example |
|--------|------|-------|---------|
| 0 | 4 | magic | 0x46554747 ("GGUF") |
| 4 | 4 | version | 3 |
| 8 | 8 | tensor_count | 339 |
| 16 | 8 | metadata_kv_count | 26 |

## Metadata Entry Format (CRITICAL — got this wrong initially)
Each KV pair uses this format:
```
key: string (8-byte little-endian length + UTF-8 data)
value_type: uint32
value: variable (depends on type)
```

**I originally reversed this** — I read `value_type` first, then tried to read the key at the wrong offset. This caused "key_len = 7308890738324930560" and type=0x14 (20, invalid).

## Value Types
| ID | Type | Size |
|----|------|------|
| 0 | uint8 | 1 |
| 4 | uint32 | 4 |
| 5 | int32 | 4 |
| 6 | float32 | 4 |
| 7 | bool | 1 |
| 8 | string | 8+len |
| 9 | array | 4(type)+8(len)+data |
| 10 | uint64 | 8 |

## Tensor Info (after metadata)
```
name: string (8-byte length + data)
n_dims: uint32
dims[]: uint64[n_dims]
type: uint32
offset: uint64
```
