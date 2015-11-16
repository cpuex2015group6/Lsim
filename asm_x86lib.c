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
  printf("%d eax: %d\n",i, a);
  fflush(stdout);
  i++;
  if (i ==2000) {
    while(1){}
  }
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


extern int min_caml_entry();
uint32_t regs[256];
uint64_t limm_count = 0;
uint64_t exec_count = 0;

void count_limm() {
  limm_count++;
}

void count_exec() {
  exec_count++;
}

int main() {
  limm_count++;
  if ((rfp = fopen("stdin", "r")) == NULL) {
    fprintf(stderr, "%sのオープンに失敗しました。\n", "stdin");
    return EXIT_FAILURE;
  }
  if ((wfp = fopen("stdout", "w")) == NULL) {
    fprintf(stderr, "%sのオープンに失敗しました。\n", "stdout");
    return EXIT_FAILURE;
  }
  regs[3] = ((uint32_t)malloc(1*1024*1024))/4;
  regs[4] = ((uint32_t)malloc(2*1024*1024))/4;
  regs[255] = 0;
  min_caml_entry();
  printf("limm_count:%f\n",limm_count/100000000.0);
  printf("exec_count:%f\n",exec_count/100000000.0);
  return 0;
}
