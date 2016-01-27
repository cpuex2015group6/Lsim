CFLAGS=-Wall -O2 -m32 -g0 -mfpmath=sse -msse2
ASFLAGS=-m32 -g0
OS := $(shell uname)
ifeq ($(OS),Linux)
LDFLAGS= -m32 -mfpmath=sse -msse2 -g0
LD=g++
endif
ifeq ($(OS),Darwin)
LDFLAGS=-pthread -lm -m32 -mfpmath=sse -msse2 -Wl,-no_pie -g0
LD=gcc
endif
X86_OBJS=asm_x86lib.o asm_x86.o
X86_TARGET = native

RM=rm -f
asm_x86.S: asm_x86.cpuexasm
	python ./asm_x86.py asm_x86.cpuexasm
$(X86_TARGET): $(X86_OBJS)
	$(LD) $(LDFLAGS) -o $@ $^
-include $(DEPS)
clean:
	$(RM) asm_x86.S $(X86_OBJS) $(X86_TARGET)

