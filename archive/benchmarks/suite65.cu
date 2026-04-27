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

__global__ void infer_i8_sym(const char* w, const char* inp, float* out,
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
    printf("=== Suite #65: INT8 Quantized Inference ===\n\n");
    int R=4096;
    cudaStream_t s; cudaStreamCreate(&s);
    dim3 grid((R+7)/8);

    half*dw16,*di16; float*do16;
    cudaMalloc(&dw16,(size_t)R*DIM*2); cudaMalloc(&di16,DIM*2); cudaMalloc(&do16,R*4);
    std::vector<half> hw(R*DIM), hi(DIM);
    for(size_t i=0;i<(size_t)R*DIM;i++)
        hw[i]=__float2half(0.01f*(2.0f*(float)rand()/RAND_MAX-1.0f));
    for(int i=0;i<DIM;i++) hi[i]=__float2half(0.5f*cosf((float)i/DIM*6.2832f));
    cudaMemcpy(dw16,hw.data(),R*DIM*2,cudaMemcpyHostToDevice);
    cudaMemcpy(di16,hi.data(),DIM*2,cudaMemcpyHostToDevice);

    // Quantize to INT8 symmetric
    std::vector<char> wq(R*DIM), iq(DIM);
    std::vector<float> ws(R); float iscale;
    float imax=0;
    for(int i=0;i<DIM;i++){float v=fabsf(__half2float(hi[i]));if(v>imax)imax=v;}
    iscale=imax/127.0f;
    for(int i=0;i<DIM;i++) iq[i]=(char)(__half2float(hi[i])/iscale);
    for(int r=0;r<R;r++){
        float wmax=0;
        for(int d=0;d<DIM;d++){float v=fabsf(__half2float(hw[r*DIM+d]));if(v>wmax)wmax=v;}
        ws[r]=wmax/127.0f;
        float inv=ws[r]>0?127.0f/wmax:0;
        for(int d=0;d<DIM;d++) wq[r*DIM+d]=(char)(__half2float(hw[r*DIM+d])*inv);
    }

    char*dwq,*diq; float*dws;
    cudaMalloc(&dwq,(size_t)R*DIM); cudaMalloc(&diq,DIM); cudaMalloc(&dws,R*4);
    cudaMemcpy(dwq,wq.data(),R*DIM,cudaMemcpyHostToDevice);
    cudaMemcpy(diq,iq.data(),DIM,cudaMemcpyHostToDevice);
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
     printf("  V7 FP16: %.2f us, %.1f M qps\n", v7_us, R/v7_us);
    }

    // INT8 symmetric
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_i8_sym<<<grid,256,0,s>>>(dwq,diq,doi8,dws,iscale,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_i8_sym<<<grid,256,0,s>>>(dwq,diq,doi8,dws,iscale,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     float us=ms/ITERS*1000;
     printf("  INT8 sym:  %.2f us, %.1f M qps (%.2fx FP16)\n", us, R/us, v7_us/us);
    }

    // Accuracy
    printf("\n  Accuracy:\n");
    infer_v7<<<grid,256,0,s>>>(dw16,di16,do16,R,DIM);
    infer_i8_sym<<<grid,256,0,s>>>(dwq,diq,doi8,dws,iscale,R,DIM);
    cudaStreamSynchronize(s);
    std::vector<float> rf(R), ri8(R);
    cudaMemcpy(rf.data(),do16,R*4,cudaMemcpyDeviceToHost);
    cudaMemcpy(ri8.data(),doi8,R*4,cudaMemcpyDeviceToHost);
    float me=0,ae=0;
    for(int r=0;r<R;r++){float d=fabsf(rf[r]-ri8[r]);float rel=rf[r]!=0?d/fabsf(rf[r]):d;if(rel>me)me=rel;ae+=rel;}
    ae/=R;
    printf("    Max rel err: %.4f%%  Avg: %.4f%%\n", me*100, ae*100);
    for(int r=0;r<4;r++) printf("    R%d: FP16=%.6f INT8=%.6f\n",r,rf[r],ri8[r]);

    // Memory
    printf("\n  Memory: FP16=%dKB INT8=%dKB+scales=%dKB (%.1fx smaller)\n",
        R*DIM*2/1024, R*DIM/1024, R*4/1024, (float)(R*DIM*2)/(R*DIM+R*4));

    // Scaling
    printf("\n  Scaling:\n");
    printf("  %-8s | %8s | %8s | %6s\n","Rooms","FP16","INT8","FP16/I8");
    printf("  ---------|----------|----------|--------\n");
    int ts[]={64,256,1024,4096,8192};
    for(int t=0;t<5;t++){
        int rooms=ts[t]; dim3 g((rooms+7)/8);
        cudaEvent_t sa,ea,sb,eb;
        cudaEventCreate(&sa); cudaEventCreate(&ea); cudaEventCreate(&sb); cudaEventCreate(&eb);
        for(int i=0;i<WARMUP;i++) infer_v7<<<g,256,0,s>>>(dw16,di16,do16,rooms,DIM);
        cudaStreamSynchronize(s); cudaEventRecord(sa,s);
        for(int i=0;i<ITERS;i++) infer_v7<<<g,256,0,s>>>(dw16,di16,do16,rooms,DIM);
        cudaEventRecord(ea,s); cudaStreamSynchronize(s);
        float m1; cudaEventElapsedTime(&m1,sa,ea);
        for(int i=0;i<WARMUP;i++) infer_i8_sym<<<g,256,0,s>>>(dwq,diq,doi8,dws,iscale,rooms,DIM);
        cudaStreamSynchronize(s); cudaEventRecord(sb,s);
        for(int i=0;i<ITERS;i++) infer_i8_sym<<<g,256,0,s>>>(dwq,diq,doi8,dws,iscale,rooms,DIM);
        cudaEventRecord(eb,s); cudaStreamSynchronize(s);
        float m2; cudaEventElapsedTime(&m2,sb,eb);
        cudaEventDestroy(sa); cudaEventDestroy(ea); cudaEventDestroy(sb); cudaEventDestroy(eb);
        printf("  %-8d | %6.2f   | %6.2f   | %.2f\n",rooms,m1/ITERS*1000,m2/ITERS*1000,(m1/ITERS)/(m2/ITERS));
    }

    cudaStreamDestroy(s);
    cudaFree(dw16); cudaFree(di16); cudaFree(do16);
    cudaFree(dwq); cudaFree(diq); cudaFree(dws); cudaFree(doi8);
    printf("\n=== Suite #65 Complete ===\n");
}
