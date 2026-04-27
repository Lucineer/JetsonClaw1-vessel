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

int main(){
    printf("=== Suite 64b: V9 Verification ===\n\n");
    int R=4096;
    cudaStream_t s; cudaStreamCreate(&s);

    half*dw,*di; float*do7; half*do9;
    cudaMalloc(&dw,(size_t)R*DIM*2); cudaMalloc(&di,DIM*2);
    cudaMalloc(&do7,R*4); cudaMalloc(&do9,R*2);
    std::vector<half> hw(R*DIM), hi(DIM);
    for(size_t i=0;i<(size_t)R*DIM;i++)
        hw[i]=__float2half(0.01f*(2.0f*(float)rand()/RAND_MAX-1.0f));
    for(int i=0;i<DIM;i++) hi[i]=__float2half(0.5f*cosf((float)i/DIM*6.2832f));
    cudaMemcpy(dw,hw.data(),R*DIM*2,cudaMemcpyHostToDevice);
    cudaMemcpy(di,hi.data(),DIM*2,cudaMemcpyHostToDevice);

    // Correctness
    dim3 g8((R+7)/8), g16((R+15)/16);
    infer_v7<<<g8,256,0,s>>>(dw,di,do7,R,DIM);
    infer_v9<<<g16,256,0,s>>>(dw,di,do9,R,DIM);
    cudaStreamSynchronize(s);

    std::vector<float> r7(R); std::vector<half> r9(R);
    cudaMemcpy(r7.data(),do7,R*4,cudaMemcpyDeviceToHost);
    cudaMemcpy(r9.data(),do9,R*2,cudaMemcpyDeviceToHost);

    float max_err=0, avg_err=0;
    for(int i=0;i<R;i++){
        float diff=fabsf(r7[i]-__half2float(r9[i]));
        float rel=r7[i]!=0?diff/fabsf(r7[i]):diff;
        if(rel>max_err) max_err=rel;
        avg_err+=rel;
    }
    avg_err/=R;
    printf("  V7 vs V9: max_err=%.4f%% avg_err=%.4f%% (FP16 accum)\n", max_err*100, avg_err*100);

    // V9 vs V7 scaling
    printf("\n--- V9 (16 rooms/block) vs V7 (8 rooms/block) ---\n");
    printf("%-10s | %8s | %8s | %6s\n","Rooms","V7 us","V9 us","V9/V7");
    printf("----------|----------|----------|--------\n");
    int rs[]={2048,4096,8192};
    for(int t=0;t<3;t++){
        int rooms=rs[t];
        dim3 gv((rooms+7)/8), gn((rooms+15)/16);
        cudaEvent_t sa,ea,sb,eb;
        cudaEventCreate(&sa); cudaEventCreate(&ea);
        cudaEventCreate(&sb); cudaEventCreate(&eb);
        for(int i=0;i<WARMUP;i++) infer_v7<<<gv,256,0,s>>>(dw,di,do7,rooms,DIM);
        cudaStreamSynchronize(s); cudaEventRecord(sa,s);
        for(int i=0;i<ITERS;i++) infer_v7<<<gv,256,0,s>>>(dw,di,do7,rooms,DIM);
        cudaEventRecord(ea,s); cudaStreamSynchronize(s);
        float m1; cudaEventElapsedTime(&m1,sa,ea);
        for(int i=0;i<WARMUP;i++) infer_v9<<<gn,256,0,s>>>(dw,di,do9,rooms,DIM);
        cudaStreamSynchronize(s); cudaEventRecord(sb,s);
        for(int i=0;i<ITERS;i++) infer_v9<<<gn,256,0,s>>>(dw,di,do9,rooms,DIM);
        cudaEventRecord(eb,s); cudaStreamSynchronize(s);
        float m2; cudaEventElapsedTime(&m2,sb,eb);
        cudaEventDestroy(sa); cudaEventDestroy(ea);
        cudaEventDestroy(sb); cudaEventDestroy(eb);
        printf("%-10d | %6.2f   | %6.2f   | %.2f\n",rooms,
            m1/ITERS*1000, m2/ITERS*1000, (m2/ITERS)/(m1/ITERS));
    }

    // V9 sustained
    printf("\n--- V9 Sustained (1M inferences, 4096 rooms) ---\n");
    for(int i=0;i<1000;i++) infer_v9<<<g16,256,0,s>>>(dw,di,do9,R,DIM);
    cudaStreamSynchronize(s);
    cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
    cudaEventRecord(s1,s);
    for(int i=0;i<1000000;i++) infer_v9<<<g16,256,0,s>>>(dw,di,do9,R,DIM);
    cudaEventRecord(e1,s); cudaStreamSynchronize(s);
    float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
    printf("  V9 1M sustained: %.2f us, %.1f M qps\n", ms/1000000*1000, R/(ms/1000000*1000));

    cudaStreamDestroy(s); cudaFree(dw); cudaFree(di); cudaFree(do7); cudaFree(do9);
    printf("\n=== Suite 64b Complete ===\n");
}
