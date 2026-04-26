#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cuda_fp16.h>
#include <mma.h>
#define DIM 256
#define WARMUP 200
#define ITERS 2000

__global__ void infer_v7(const half* w, const half* inp, float* out, int n, int d) {
    int rb=blockIdx.x*8; int ri=threadIdx.x/32; int lane=threadIdx.x%32;
    if(rb+ri>=n) return;
    float sum=0.0f;
    for(int i=lane;i<d;i+=32) sum+=__half2float(w[(rb+ri)*d+i])*__half2float(inp[i]);
    for(int o=16;o>0;o>>=1) sum+=__shfl_down_sync(0xffffffff,sum,o);
    if(lane==0) out[rb+ri]=sum;
}

// WMMA: 16x16x16 FP16 matmul per warp
// Each block processes one 16x16 tile of weights x input vector
// For dim=256: need 16 tiles of 16 columns each
__global__ void infer_wmma(const half* w, const half* inp, float* out,
                            int n, int d) {
    // Block processes 8 rooms x 1 input vector
    // Weight matrix: 8x256, Input: 256x1, Output: 8x1
    // Use WMMA 16x16x16 fragments
    int rb=blockIdx.x*8; // block processes rooms [rb, rb+8)
    int warp_id=threadIdx.x/32;
    int lane=threadIdx.x%32;
    int room=rb+warp_id; // each warp handles one room

    if(room>=n) return;

    // Load input vector fragment (16 elements)
    wmma::fragment<wmma::matrix_a, 16, 16, 16, half, wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, half, wmma::col_major> b_frag;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> c_frag;

    wmma::fill_fragment(c_frag, 0.0f);

    // Process dim=256 as 16 tiles of 16 elements
    for(int tile=0; tile<d/16; tile++){
        // Load 16x16 tile: row = room, cols = tile*16 to tile*16+15
        // Matrix A is 1x16 (one row of weights)
        // But WMMA needs 16x16... each warp uses same input tile
        // A: weights[room][tile*16..tile*16+15] - shape 1x16, but WMMA needs 16x16
        // Solution: treat room weight as a 16x16 matrix (pad with zeros)
        // Actually: load 16 rows x 16 cols from weight matrix
        // But each warp only has 1 room (1 row)...
        // WMMA requires ALL 16 rows of the fragment to be loaded

        // Alternative: each block handles 16 rooms (not 8)
        // 8 warps * 16 rows = 128 rooms? No...
        // Each warp processes 1 WMMA op = 16 output elements
        // For 1 room output: we need 1x1 output from 1x256 x 256x1
        // WMMA gives 16x16 output from 16x16 x 16x16

        // Correct approach: pack 16 rooms as the matrix rows
        // Weight tile: 16 rooms x 16 dims (16x16)
        // Input tile: 16 dims x 1 (16x1, need 16x16 -> replicate)
        // Output: 16 rooms x 1 (16x1, need 16x16 -> first column)

        // Load weight fragment (16 rows from rooms rb+warp_id*16 to rb+warp_id*16+15)
        wmma::load_matrix_sync(a_frag, w+(rb+warp_id*16+lane/4)*d+tile*16, d);
        // Load input fragment (16 elements, broadcast to 16x16)
        // Input is 256x1, take 16 elements at tile*16
        wmma::load_matrix_sync(b_frag, inp+tile*16, 1);
        // But b_frag is 16x16 and input is 16x1... need col_major with stride=1
        // Actually input[0..15] as 16x1 col-major = each element is a column
        // WMMA col_major B: 16x16 matrix, stride=16 -> loads 16 elements from each column
        // For a 16x1 vector: load with stride=1 -> fills first column of 16x16

        wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
    }

    // Store result: first column of c_frag
    // c_frag is 16x16 float, we need element [0..15][0]
    float results[16];
    wmma::store_matrix_sync(results, c_frag, 16, wmma::mem_row_major);

    if(lane==0){
        for(int r=0;r<16;r++){
            int room_idx=rb+warp_id*16+r;
            if(room_idx<n) out[room_idx]=results[r*16]; // first column
        }
    }
}

// Simpler WMMA: use tensor cores via cublas
__global__ void infer_wmma_simple(const half* w, const half* inp, float* out,
                                   int n, int d) {
    // This kernel uses the HMMA instruction directly via PTX
    // Not available through CUDA C++ easily, so we use a manual approach
    // Just verify WMMA compiles and runs
    int rb=blockIdx.x*16; int warp=threadIdx.x/32; int lane=threadIdx.x%32;

    wmma::fragment<wmma::matrix_a, 16, 16, 16, half, wmma::row_major> a;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, half, wmma::col_major> b;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> c;
    wmma::fill_fragment(c, 0.0f);

    // Process 16 rooms per warp
    int base_room=rb+warp*16;
    if(base_room>=n) return;

    for(int t=0; t<d/16; t++){
        // Load 16 rows x 16 cols from weight matrix
        // Rows: base_room + (lane % 16), Cols: t*16 + (lane / 16)
        // But load_matrix_sync needs contiguous memory per row
        wmma::load_matrix_sync(a, w+(base_room)*d+t*16, d);
        // Load 16 elements from input as col-major 16x1
        wmma::load_matrix_sync(b, inp+t*16, 1);
        wmma::mma_sync(c, a, b, c);
    }

    float res[16*16];
    wmma::store_matrix_sync(res, c, 16, wmma::mem_row_major);

    if(lane<16){
        int room=base_room+lane;
        if(room<n) out[room]=res[lane*16]; // first column element
    }
}

int main(){
    printf("=== Suite #67: Tensor Core WMMA ===\n\n");
    int R=4096;
    cudaStream_t s; cudaStreamCreate(&s);
    dim3 grid8((R+7)/8);

    half*dw,*di; float*do_;
    cudaMalloc(&dw,(size_t)R*DIM*2); cudaMalloc(&di,DIM*2); cudaMalloc(&do_,R*4);
    std::vector<half> hw(R*DIM), hi(DIM);
    for(size_t i=0;i<(size_t)R*DIM;i++)
        hw[i]=__float2half(0.01f*(2.0f*(float)rand()/RAND_MAX-1.0f));
    for(int i=0;i<DIM;i++) hi[i]=__float2half(0.5f*cosf((float)i/DIM*6.2832f));
    cudaMemcpy(dw,hw.data(),R*DIM*2,cudaMemcpyHostToDevice);
    cudaMemcpy(di,hi.data(),DIM*2,cudaMemcpyHostToDevice);

    // V7 baseline
    float v7_us;
    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<WARMUP;i++) infer_v7<<<grid8,256,0,s>>>(dw,di,do_,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_v7<<<grid,256,0,s>>>(dw,di,do_,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     v7_us=ms/ITERS*1000;
     printf("  V7: %.2f us, %.1f M qps\n", v7_us, R/v7_us);
    }

    // WMMA
    printf("\n  WMMA (16 rooms/warp, 8 warps/block = 128 rooms/block)...\n");
    dim3 grid16((R+127)/128);
    float*do_wmma; cudaMalloc(&do_wmma,R*4);

    {cudaEvent_t s1,e1; cudaEventCreate(&s1); cudaEventCreate(&e1);
     for(int i=0;i<50;i++) infer_wmma<<<grid16,256,0,s>>>(dw,di,do_wmma,R,DIM);
     cudaStreamSynchronize(s); cudaEventRecord(s1,s);
     for(int i=0;i<ITERS;i++) infer_wmma<<<grid16,256,0,s>>>(dw,di,do_wmma,R,DIM);
     cudaEventRecord(e1,s); cudaStreamSynchronize(s);
     float ms; cudaEventElapsedTime(&ms,s1,e1); cudaEventDestroy(s1); cudaEventDestroy(e1);
     printf("  WMMA: %.2f us, %.1f M qps (%.2fx V7)\n", ms/ITERS*1000, R/(ms/ITERS*1000), v7_us/(ms/ITERS*1000));
    }

    // Correctness
    infer_v7<<<grid8,256,0,s>>>(dw,di,do_,R,DIM);
    infer_wmma<<<grid16,256,0,s>>>(dw,di,do_wmma,R,DIM);
    cudaStreamSynchronize(s);
    std::vector<float> rv(R), rw(R);
    cudaMemcpy(rv.data(),do_,R*4,cudaMemcpyDeviceToHost);
    cudaMemcpy(rw.data(),do_wmma,R*4,cudaMemcpyDeviceToHost);
    int ok=0;
    for(int i=0;i<R;i++) if(fabsf(rv[i]-rw[i])<0.01) ok++;
    printf("  Correct: %d/%d (%.1f%%)\n", ok, R, ok*100.0f/R);
    for(int i=0;i<4;i++) printf("    R%d: V7=%.6f WMMA=%.6f\n",i,rv[i],rw[i]);

    cudaStreamDestroy(s);
    cudaFree(dw); cudaFree(di); cudaFree(do_); cudaFree(do_wmma);
    printf("\n=== Suite #67 Complete ===\n");
}
