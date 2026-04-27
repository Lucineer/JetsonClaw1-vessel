# DeckBoss Runtime Makefile
# Jetson Orin Nano (sm_87), CUDA 12.6

NVCC := /usr/local/cuda-12.6/bin/nvcc
ARCH := sm_87
CFLAGS := -O3 -use_fast_math
INCLUDES := -I.

.PHONY: all test clean

all: libdeckboss.so

# Shared library
libdeckboss.so: deckboss_runtime.cu deckboss.h
	$(NVCC) -arch=$(ARCH) $(CFLAGS) -shared -fPIC $(INCLUDES) $< -o $@

# Static library
libdeckboss.a: deckboss_runtime.cu deckboss.h
	$(NVCC) -arch=$(ARCH) $(CFLAGS) -c $(INCLUDES) $< -o deckboss_runtime.o
	ar rcs $@ deckboss_runtime.o

# Tests
test: test_deckboss_runtime zerocopy_test
	./test_deckboss_runtime
	./zerocopy_test

test_deckboss_runtime: deckboss_runtime.cu test_deckboss_runtime.cu deckboss.h
	$(NVCC) -arch=$(ARCH) $(CFLAGS) $(INCLUDES) $^ -o $@

zerocopy_test: deckboss_runtime.cu test_zerocopy.cu deckboss.h
	$(NVCC) -arch=$(ARCH) $(CFLAGS) $(INCLUDES) $^ -o $@

# Example
example: example_infer.c deckboss_runtime.cu deckboss.h
	$(NVCC) -arch=$(ARCH) $(CFLAGS) $(INCLUDES) example_infer.c deckboss_runtime.cu -o example_infer

clean:
	rm -f *.o *.so *.a test_deckboss_runtime zerocopy_test example_infer
