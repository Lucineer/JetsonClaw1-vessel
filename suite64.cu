/**
 * Suite #64: Combined Optimizations — The Ultimate Kernel
 * Combine everything that worked:
 * 1. L2 persist (partial, 1K rooms pinned)
 * 2. FP16 accumulation
 * 3. Unroll 4x
 * 4. Warp shuffle reduction
 * 5. 8 rooms per block
 * 
 * Also test: what's the actual maximum qps achievable?
 */
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cuda_fp16.h>
#define DIM 256
#define WARMUP 500
#define ITERS 10000

__global__ void infer_v7(const half* w, const half* inp, float* out, int n, int d) {
    int rb=blockIdx.x*8; int ri=threadIdx.x/32; int lane=threadIdx.x%32;
    if(rb+ri>=n) return;
    float sum=0.0f;
    for(int i=lane;i<d;i+=32) sum+=__half2float(w[(rb+ri)*d+i])*__half2float(inp[i]);
    for(int o=16;o>0;o>>=1) sum+=__shfl_down_sync(0xffffffff,sum,o);
    if(lane==0) out[rb+ri]=sum;
}

// V8: FP16 accum + unroll4 + direct L2 reads
__global__ void infer_v8(const half* w, const half* inp, half* out, int n, int d) {
    int rb=blockIdx.x*8; int ri=threadIdx.x/32; int lane=threadIdx.x%32;
    if(rb+ri>=n) return;
    const half* wp=w+(rb+ri)*d;
    half sum=__float2half(0.0f);
    #pragma unroll 4
    for(int i=lane;i<d;i+=32) sum=__hadd(sum,__hmul(wp[i],inp[i]));
    for(int o=16;o>0;o>>=1) sum=__hadd(sum,__shfl_sync(0xffffffff,sum,o));
    if(lane==0) out[rb+ri]=sum;
}

// V9: V8 + 16 rooms per block (more warps, better occupancy)
__global__ void infer_v9(const half* w, const half* inp, half* out, int n, int d) {
    int rb=blockIdx.x*16; int ri=threadIdx.x/32; int lane=threadIdx.x%32;
    if(rb+ri>=n) return;
    const half* wp=w+(rb+ri)*d;
    half sum=__float2half(0.0f);
    #pragma unroll 4
    for(int i=lane;i<d;i+=32) sum=__hadd(sum,__hmul(wp[i],inp[i]));
    for(int o=16;o>0;o>>=1) sum=__hadd(sum,__shfl_sync(0xffffffff,sum,o));
    if(lane==0) out[rb+ri]=sum;
}

// V10: 4 rooms per block (more shared resources per warp)
__global__ void infer_v10(const half* w, const half* inp, half* out, int n, int d) {
    int rb=blockIdx.x*4; int ri=threadIdx.x/32; int lane=threadIdx.x%32;
    if(rb+ri>=n) return;
    const half* wp=w+(rb+ri)*d;
    half sum=__float2half(0.0f);
    #pragma unroll 8
    for(int i=lane;i<d;i+=32) sum=__hadd(sum,__hmul(wp[i],inp[i]));
    for(int o=16;o>0;o>>=1) sum=__hadd(sum,__shfl_sync(0xffffffff,sum,o));
    if(lane==0) out[rb+ri]=sum;
}

// V11: 2 rooms per block (128 threads = 4 warps)
__global__ void infer_v11(const half* w, const half* inp, half* out, int n, int d) {
    int rb=blockIdx.x*2; int ri=threadIdx.x/64; int lane=threadIdx.x%64;
    if(rb+ri>=n) return;
    const half* wp=w+(rb+ri)*d;
    half sum=__float2half(0.0f);
    // 64 threads per room, each reads 4 elements
    #pragma unroll 4
    for(int i=lane*4;i<(lane+1)*4 && i<d;i++) sum=__hadd(sum,__hmul(wp[i],inp[i]));
    // Reduce within 64-thread group
    for(int o=32;o>0;o>>=1) sum=__hadd(sum,__shfl_sync(0xffffffff,sum,o));
    if(threadIdx.x%64==0) out[rb+ri]=sum;
}

int main(){
    printf("=== Suite #64: Combined Optimizations ===\n\n");
    int R=4096;
    cudaStream_t s; cudaStreamCreate(&s);

    half*dw,*di; float*do_; half*do16;
    cudaMalloc(&dw,(size_t)R*DIM*2); cudaMalloc(&di,DIM*2);
    cudaMalloc(&do_,R*4); cudaMalloc(&do16,R*2);
    std::vector<half> hw(R*DIM), hi(DIM);
    for(size_t i=0;i<(size_t)R*DIM;i++)
        hw[i]=__float2half(0.01f*(2.0f*(float)rand()/RAND_MAX-1.0f));
    for(int i=0;i<DIM;i++) hi[i]=__float2half(0.5f*cosf((float)i/DIM*6.2832f));
    cudaMemcpy(dw,hw.data(),R*DIM*2,cudaMemcpyHostToDevice);
    cudaMemcpy(di,hi.data(),DIM*2,cudaMemcpyHostToDevice);

    // Setup L2 persist for first 1024 rooms
    int l2_max=0;
    cudaDeviceGetAttribute(&l2_max, cudaDevAttrMaxPersistingL2CacheSize, 0);
    printf("  L2 persist max: %d KB\n", l2_max/1024);

    // Baseline: V7 no persist
    dim3 g8((R+7)/8);
    float v7_us;
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v7<<<g8,256,0,s>>>(dw,di,do_,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v7<<<g8,256,0,s>>>(dw,di,do_,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     v7_us=ms/ITERS*1000;
     printf("  V7 baseline: %.2f us, %.1f M qps\n", v7_us, R/v7_us);
    }

    // V8: FP16 accum + unroll4 (no persist)
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v8<<<g8,256,0,s>>>(dw,di,do16,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v8<<<g8,256,0,s>>>(dw,di,do16,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  V8 (fp16+u4): %.2f us, %.1f M qps (%.2fx)\n",
         ms/ITERS*1000, R/(ms/ITERS*1000), v7_us/(ms/ITERS*1000));
    }

    // V8 + L2 persist
    cudaStreamAttrValue attr;
    attr.accessPolicyWindow.base_ptr=dw;
    attr.accessPolicyWindow.num_bytes=(size_t)1024*DIM*sizeof(half);
    attr.accessPolicyWindow.hitRatio=1.0f;
    attr.accessPolicyWindow.hitProp=cudaAccessPropertyPersisting;
    attr.accessPolicyWindow.missProp=cudaAccessPropertyStreaming;
    cudaStreamSetAttribute(s, cudaStreamAttributeAccessPolicyWindow, &attr);

    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v8<<<g8,256,0,s>>>(dw,di,do16,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v8<<<g8,256,0,s>>>(dw,di,do16,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  V8+persist:    %.2f us, %.1f M qps (%.2fx)\n",
         ms/ITERS*1000, R/(ms/ITERS*1000), v7_us/(ms/ITERS*1000));
    }

    // Reset persist for clean comparison
    attr.accessPolicyWindow.base_ptr=0;
    attr.accessPolicyWindow.num_bytes=0;
    attr.accessPolicyWindow.hitRatio=0.0f;
    attr.accessPolicyWindow.hitProp=cudaAccessPropertyNormal;
    attr.accessPolicyWindow.missProp=cudaAccessPropertyNormal;
    cudaStreamSetAttribute(s, cudaStreamAttributeAccessPolicyWindow, &attr);

    // V9: 16 rooms per block
    dim3 g16((R+15)/16);
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v9<<<g16,256,0,s>>>(dw,di,do16,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v9<<<g16,256,0,s>>>(dw,di,do16,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  V9 (16r/block): %.2f us, %.1f M qps (%.2fx)\n",
         ms/ITERS*1000, R/(ms/ITERS*1000), v7_us/(ms/ITERS*1000));
    }

    // V10: 4 rooms per block + unroll8
    dim3 g4((R+3)/4);
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v10<<<g4,256,0,s>>>(dw,di,do16,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v10<<<g4,256,0,s>>>(dw,di,do16,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  V10 (4r+u8):   %.2f us, %.1f M qps (%.2fx)\n",
         ms/ITERS*1000, R/(ms/ITERS*1000), v7_us/(ms/ITERS*1000));
    }

    // V11: 2 rooms per block (128 threads)
    dim3 g2((R+1)/2);
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v11<<<g2,128,0,s>>>(dw,di,do16,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v11<<<g2,128,0,s>>>(dw,di,do16,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  V11 (2r/128t): %.2f us, %.1f M qps (%.2fx)\n",
         ms/ITERS*1000, R/(ms/ITERS*1000), v7_us/(ms/ITERS*1000));
    }

    // Find best kernel, do sustained run
    printf("\n--- Best Kernel Sustained (1M inferences) ---\n");
    // V8+persist was likely best, re-enable
    attr.accessPolicyWindow.base_ptr=dw;
    attr.accessPolicyWindow.num_bytes=(size_t)1024*DIM*sizeof(half);
    attr.accessPolicyWindow.hitRatio=1.0f;
    attr.accessPolicyWindow.hitProp=cudaAccessPropertyPersisting;
    attr.accessPolicyWindow.missProp=cudaAccessPropertyStreaming;
    cudaStreamSetAttribute(s, cudaStreamAttributeAccessPolicyWindow, &attr);

    // Warm up thoroughly
    for(int i=0;i<1000;i++) infer_v8<<<g8,256,0,s>>>(dw,di,do16,R,DIM);
    cudaStreamSynchronize(s);

    cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
    cudaEventRecord(s1,s);
    for(int i=0;i<1000000;i++) infer_v8<<<g8,256,0,s>>>(dw,di,do16,R,DIM);
    cudaEventRecord(e1,s); cudaStreamSynchronize(s);
    float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
    float sus_us=ms/1000000*1000;
    printf("  V8+persist 1M: %.2f us avg, %.1f M qps sustained\n", sus_us, R/sus_us);
    printf("  Total time: %.2f seconds\n", ms/1000);

    // Also test at optimal batch size (8192)
    printf("\n--- Best Kernel at 8192 Rooms ---\n");
    int R2=8192;
    dim3 g8b((R2+7)/8);
    // Allocate enough output
    half*do16b; cudaMalloc(&do16b, R2*2);

    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v8<<<g8b,256,0,s>>>(dw,di,do16b,R2,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v8<<<g8b,256,0,s>>>(dw,di,do16b,R2,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms2; cudaEventElapsedTime(&ms2,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  V8 8192 rooms: %.2f us, %.1f M qps\n",
         ms2/ITERS*1000, R2/(ms2/ITERS*1000));
    }

    // Reset
    attr.accessPolicyWindow.base_ptr=0;
    attr.accessPolicyWindow.num_bytes=0;
    attr.accessPolicyWindow.hitProp=cudaAccessPropertyNormal;
    attr.accessPolicyWindow.missProp=cudaAccessPropertyNormal;
    cudaStreamSetAttribute(s, cudaStreamAttributeAccessPolicyWindow, &attr);

    cudaStreamDestroy(s); cudaFree(dw); cudaFree(di); cudaFree(do_); cudaFree(do16); cudaFree(do16b);
    printf("\n=== Suite #64 Complete ===\n");
}
