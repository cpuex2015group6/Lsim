#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>

FILE *rfp, *wfp;

uint32_t in() {
  return getc(rfp);
}

void out(uint32_t a) {
  putc(a&0xff,wfp);
  fflush(wfp);
}
uint32_t cmp(int32_t a, int32_t b) {
  if (a > b) {
    return 2;
  } else if (a == b) {
    return 1;
  } else {
    return 0;
  }
}

void debug(int a) {
  static int i = 0;
  printf("%d eax: %d(0x%x)\n",i, a, a);
  fflush(stdout);
  i++;
}

void show(int a) {
  static int i = 0;
  printf("%d reg: %d(0x%x)\n",i, a, a);
  fflush(stdout);
  i++;
}

void trace(int a) {
  printf("eip: 0x%x\n", a);
  fflush(stdout);
}

typedef union {
  uint32_t i;
  float f;
} Float;

uint32_t fadd(uint32_t a, uint32_t b) {
  Float ra, rb, rt;
  ra.i = a;
  rb.i = b;
  rt.f = ra.f + rb.f;
  return rt.i;
}

uint32_t fmul(uint32_t a, uint32_t b) {
  Float ra, rb, rt;
  ra.i = a;
  rb.i = b;
  rt.f = ra.f * rb.f;
  return rt.i;
}

uint32_t finv(uint32_t a, uint32_t b) {
  Float ra, rt;
  ra.i = a;
  rt.f = 1.0 / ra.f;
  return rt.i;
}

uint32_t fsqrt(uint32_t a) {
  Float ra, rt;
  ra.i = a;
  rt.f = sqrtf(ra.f);
  return rt.i;
}

int fcmp(uint32_t a, uint32_t b) {
  Float ra, rb;
  ra.i = a;
  rb.i = b;
  if (ra.f > rb.f) {
    return 2;
  } else if (ra.f == rb.f) {
    return 1;
  } else {
    return 0;
  }
}

void min_caml_entry();

extern uint64_t limm_count[1];
extern uint64_t exec_count[1];
extern uint64_t generic_count[1];
extern uint32_t regs[256];
extern uint32_t *mem_offset[1];

int main() {
  if ((rfp = fopen("stdin", "r")) == NULL) {
    fprintf(stderr, "%sのオープンに失敗しました。\n", "stdin");
    return EXIT_FAILURE;
  }
  if ((wfp = fopen("stdout", "w")) == NULL) {
    fprintf(stderr, "%sのオープンに失敗しました。\n", "stdout");
    return EXIT_FAILURE;
  }
  // メモリ空間(SRAM)は4MB
  mem_offset[0] = malloc(4*1024*1024);
  printf("registers    : 0x%x\n", (uint32_t)regs);
  printf("memory space : 0x%x\n", (uint32_t)(mem_offset[0]));
  fflush(stdout);
  regs[255] = 0;
  min_caml_entry();
  printf("limm_count:%f\n",limm_count[0]/100000000.0);
  printf("generic_count:%f\n",generic_count[0]/100000000.0);
  printf("exec_count:%f\n",exec_count[0]/100000000.0);
  return 0;
}
