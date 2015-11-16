CC=gcc
CFLAGS=-Wall -O2 -m32
ASFLAGS=-m32
LDFLAGS=-pthread -lm -m32 -Wl,-no_pie
X86_OBJS=asm_x86lib.o asm_x86.o
X86_TARGET = native

RM=rm -f
asm_x86.S: asm_x86.cpuexasm
	python ./asm_x86.py asm_x86.cpuexasm
$(X86_TARGET): $(X86_OBJS)
	$(CC) $(LDFLAGS) -o $@ $^
-include $(DEPS)
clean:
	$(RM) asm_x86.S $(X86_OBJS) $(X86_TARGET)

