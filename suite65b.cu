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

__global__ void infer_i8(const char* w, const char* inp, float* out,
                          const float* ws, float iscale, int n, int d) {
    int rb=blockIdx.x*8; int ri=threadIdx.x/32; int lane=threadIdx.x%32;
    if(rb+ri>=n) return;
    int room=rb+ri;
    int sum=0;
    #pragma unroll 4
    for(int i=lane;i<d;i+=32) sum+=(int)w[room*d+i]*(int)inp[i];
    for(int o=16;o>0;o>>=1) sum+=__shfl_down_sync(0xffffffff,sum,o);
    if(lane==0) out[room]=(float)sum*ws[room]*iscale;
}

int main(){
    printf("=== Suite #65b: INT8 with Global Scale ===\n\n");
    int R=4096;
    cudaStream_t s; cudaStreamCreate(&s);
    dim3 grid((R+7)/8);

    half*dw16,*di16; float*do16;
    cudaMalloc(&dw16,(size_t)R*DIM*2); cudaMalloc(&di16,DIM*2); cudaMalloc(&do16,R*4);
    std::vector<half> hw(R*DIM), hi(DIM);
    // Use larger weights so quantization doesn't lose everything
    for(size_t i=0;i<(size_t)R*DIM;i++)
        hw[i]=__float2half(0.5f*(2.0f*(float)rand()/RAND_MAX-1.0f));
    for(int i=0;i<DIM;i++) hi[i]=__float2half(cosf((float)i/DIM*6.2832f));
    cudaMemcpy(dw16,hw.data(),R*DIM*2,cudaMemcpyHostToDevice);
    cudaMemcpy(di16,hi.data(),DIM*2,cudaMemcpyHostToDevice);

    // Global quantization: find global max across ALL weights
    float gmax=0;
    for(size_t i=0;i<(size_t)R*DIM;i++){
        float v=fabsf(__half2float(hw[i]));
        if(v>gmax) gmax=v;
    }
    float gscale=gmax/127.0f;
    printf("  Global max weight: %.4f, scale: %.6f\n", gmax, gscale);

    std::vector<char> wq(R*DIM), iq(DIM);
    for(size_t i=0;i<(size_t)R*DIM;i++)
        wq[i]=(char)(__half2float(hw[i])/gscale);
    for(int i=0;i<DIM;i++)
        iq[i]=(char)(__half2float(hi[i])/gscale);

    char*dwq,*diq; cudaMalloc(&dwq,(size_t)R*DIM); cudaMalloc(&diq,DIM);
    cudaMemcpy(dwq,wq.data(),R*DIM,cudaMemcpyHostToDevice);
    cudaMemcpy(diq,iq.data(),DIM,cudaMemcpyHostToDevice);

    // Per-room scale (more accurate)
    std::vector<float> ws(R);
    for(int r=0;r<R;r++){
        float rm=0;
        for(int d=0;d<DIM;d++){float v=fabsf(__half2float(hw[r*DIM+d]));if(v>rm)rm=v;}
        ws[r]=rm>0?rm/127.0f:gscale;
    }
    float*dws; cudaMalloc(&dws,R*4);
    cudaMemcpy(dws,ws.data(),R*4,cudaMemcpyHostToDevice);
    float*doi8; cudaMalloc(&doi8,R*4);

    // V7 baseline
    float v7_us;
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v7<<<grid,256,0,s>>>(dw16,di16,do16,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v7<<<grid,256,0,s>>>(dw16,di16,do16,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     v7_us=ms/ITERS*1000;
    }

    // INT8 per-room scale
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_i8<<<grid,256,0,s>>>(dwq,diq,doi8,dws,gscale,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_i8<<<grid,256,0,s>>>(dwq,diq,doi8,dws,gscale,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     float us=ms/ITERS*1000;
     printf("  V7 FP16: %.2f us, %.1f M qps\n", v7_us, R/v7_us);
     printf("  INT8:    %.2f us, %.1f M qps (%.2fx)\n", us, R/us, v7_us/us);
    }

    // Accuracy
    infer_v7<<<grid,256,0,s>>>(dw16,di16,do16,R,DIM);
    infer_i8<<<grid,256,0,s>>>(dwq,diq,doi8,dws,gscale,R,DIM);
    cudaStreamSynchronize(s);
    std::vector<float> rf(R), ri8(R);
    cudaMemcpy(rf.data(),do16,R*4,cudaMemcpyDeviceToHost);
    cudaMemcpy(ri8.data(),doi8,R*4,cudaMemcpyDeviceToHost);
    float me=0,ae=0;
    for(int r=0;r<R;r++){float d=fabsf(rf[r]-ri8[r]);float rel=rf[r]!=0?d/fabsf(rf[r]):d;if(rel>me)me=rel;ae+=rel;}
    ae/=R;
    printf("  Max rel err: %.4f%%  Avg: %.4f%%\n", me*100, ae*100);
    for(int r=0;r<8;r++) printf("    R%d: FP16=%.6f INT8=%.6f diff=%.2e\n",r,rf[r],ri8[r],fabsf(rf[r]-ri8[r]));

    // Dim scaling: how does accuracy vary with dim?
    printf("\n  Dim sweep (INT8 accuracy at dim=N):\n");
    printf("  %-8s | %10s | %10s | %10s\n","dim","max err%","avg err%","speedup");
    printf("  ---------|------------|------------|------------\n");
    int dims[]={32,64,128,256,512};
    for(int dd=0;dd<5;dd++){
        int D=dims[dd];
        // Regenerate data for this dim
        std::vector<half> hw2(R*D), hi2(D);
        for(size_t i=0;i<(size_t)R*D;i++)
            hw2[i]=__float2half(0.5f*(2.0f*(float)rand()/RAND_MAX-1.0f));
        for(int i=0;i<D;i++) hi2[i]=__float2half(cosf((float)i/D*6.2832f));

        float gm=0;
        for(size_t i=0;i<(size_t)R*D;i++){float v=fabsf(__half2float(hw2[i]));if(v>gm)gm=v;}
        float gs=gm/127.0f;
        std::vector<char> wq2(R*D), iq2(D);
        for(size_t i=0;i<(size_t)R*D;i++) wq2[i]=(char)(__half2float(hw2[i])/gs);
        for(int i=0;i<D;i++) iq2[i]=(char)(__half2float(hi2[i])/gs);

        half*dw2,*di2; float*do2,*do8;
        char*cw2,*ci2;
        cudaMalloc(&dw2,(size_t)R*D*2); cudaMalloc(&di2,D*2);
        cudaMalloc(&do2,R*4); cudaMalloc(&do8,R*4);
        cudaMalloc(&cw2,(size_t)R*D); cudaMalloc(&ci2,D);
        cudaMemcpy(dw2,hw2.data(),R*D*2,cudaMemcpyHostToDevice);
        cudaMemcpy(di2,hi2.data(),D*2,cudaMemcpyHostToDevice);
        cudaMemcpy(cw2,wq2.data(),R*D,cudaMemcpyHostToDevice);
        cudaMemcpy(ci2,iq2.data(),D,cudaMemcpyHostToDevice);

        std::vector<float> ws2(R);
        for(int r=0;r<R;r++){float rm=0;for(int d=0;d<D;d++){float v=fabsf(__half2float(hw2[r*D+d]));if(v>rm)rm=v;}ws2[r]=rm>0?rm/127.0f:gs;}
        float*dws2; cudaMalloc(&dws2,R*4);
        cudaMemcpy(dws2,ws2.data(),R*4,cudaMemcpyHostToDevice);

        dim3 g((R+7)/8);
        infer_v7<<<g,256,0,s>>>(dw2,di2,do2,R,D);
        infer_i8<<<g,256,0,s>>>(cw2,ci2,do8,dws2,gs,R,D);
        cudaStreamSynchronize(s);

        std::vector<float> r2(R), r8(R);
        cudaMemcpy(r2.data(),do2,R*4,cudaMemcpyDeviceToHost);
        cudaMemcpy(r8.data(),do8,R*4,cudaMemcpyDeviceToHost);
        float me2=0,ae2=0;
        for(int r=0;r<R;r++){float d=fabsf(r2[r]-r8[r]);float rel=r2[r]!=0?d/fabsf(r2[r]):d;if(rel>me2)me2=rel;ae2+=rel;}
        ae2/=R;

        // Speedup benchmark
        cudaEvent_t sa,ea,sb,eb;
        cudaEventCreate(&sa); cudaEventCreate(&ea); cudaEventCreate(&sb); cudaEventCreate(&eb);
        for(int i=0;i<200;i++) infer_v7<<<g,256,0,s>>>(dw2,di2,do2,R,D);
        cudaStreamSynchronize(s); cudaEventRecord(sa,s);
        for(int i=0;i<2000;i++) infer_v7<<<g,256,0,s>>>(dw2,di2,do2,R,D);
        cudaEventRecord(ea,s); cudaStreamSynchronize(s);
        float m1; cudaEventElapsedTime(&m1,sa,ea);
        for(int i=0;i<200;i++) infer_i8<<<g,256,0,s>>>(cw2,ci2,do8,dws2,gs,R,D);
        cudaStreamSynchronize(s); cudaEventRecord(sb,s);
        for(int i=0;i<2000;i++) infer_i8<<<g,256,0,s>>>(cw2,ci2,do8,dws2,gs,R,D);
        cudaEventRecord(eb,s); cudaStreamSynchronize(s);
        float m2; cudaEventElapsedTime(&m2,sb,eb);
        cudaEventDestroy(sa); cudaEventDestroy(ea); cudaEventDestroy(sb); cudaEventDestroy(eb);

        printf("  %-8d | %8.4f   | %8.4f   | %8.2f\n",D,me2*100,ae2*100,(m1/2000)/(m2/2000));
        cudaFree(dw2); cudaFree(di2); cudaFree(do2); cudaFree(do8);
        cudaFree(cw2); cudaFree(ci2); cudaFree(dws2);
    }

    cudaStreamDestroy(s);
    cudaFree(dw16); cudaFree(di16); cudaFree(do16);
    cudaFree(dwq); cudaFree(diq); cudaFree(dws); cudaFree(doi8);
    printf("\n=== Suite #65b Complete ===\n");
}
