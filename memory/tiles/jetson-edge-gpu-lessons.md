---
id: jetson-edge-gpu-lessons
created: 2026-04-28
updated: 2026-04-28
tags: [jetson, cuda, gpu, edge]
---

# Jetson-Edge-GPU-Lessons

Key lessons learned running AI workloads on Jetson Orin Nano 8GB:

1. 8GB unified RAM means models over ~6.5GB OOM (Python overhead)
2. nvcc at /usr/local/cuda-12.6, 1024 CUDA cores
3. ARM64: most things compile, Rust needs a real machine
4. Thermal: 48-49°C sustained, passive cooling fine
5. LiteRT-LM for edge inference (deepseek-r1-1.5b, qwen-0.5b, smolLM-135m)
6. Model routing: classify task → pick best local model by size/capability
7. No sudo: systemctl --user for services, user-level installs only
8. DNS hiccups: intermittent, need retry logic
9. ESM/CJS: NEVER import same package both ways
10. 68MB .git_backup dirs block git push — delete immediately
