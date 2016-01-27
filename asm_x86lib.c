#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <stdlib.h>
#include <inttypes.h> 

FILE *rfp, *wfp;
extern uint64_t limm_count[1];
extern uint64_t exec_count[1];
extern uint64_t generic_count[1];
extern uint32_t regs[256];
extern uint32_t *mem_offset[1];

typedef union {
  uint32_t i;
  float f;
} Float;

uint32_t generic(uint32_t comm, uint32_t a1, uint32_t a2, uint32_t a3) {
  switch(comm) {
  case 0:
    printf("generic cmd test (a1:%d, a2:%d, a3:%d)\n", a1, a2, a3);
    return 123;
    break;
  case 901:
    // int_of_float
    {
      Float f1;
      f1.i = a2;
      assert((int)f1.f == a1);
    }
    break;
  case 902:
    // float_of_int
    {
      Float f1;
      f1.f = (float)a2;
      assert(f1.i == a1);
    }
    break;
  default:
    printf("undefined generic cmd called.\n");
  }
  return 0;
}

uint32_t in() {
  return getc(rfp);
}

void out(uint32_t a) {
  putc(a&0xff,wfp);
  fflush(wfp);
}

uint32_t cmpc(int32_t a, int32_t b, uint32_t c) {
  if (a > b) {
    return c & 4 ? 1 : 0;
  } else if (a == b) {
    return c & 2 ? 1 : 0;
  }
  return c & 1 ? 1 : 0;
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

void showexec() {
  static int i = 0;
  printf("%d cur exec: %"PRIu64"\n",i, exec_count[0]);
  fflush(stdout);
  i++;
}

void trace(int a) {
  printf("eip: 0x%x\n", a);
  fflush(stdout);
}

#define FIFOMAX 1000000 

typedef struct {
  int i;
  uint64_t buf[FIFOMAX];
} Fifo;
Fifo exec_fifo;
uint64_t section_exec = 0;

void setcurexec() {
  if (exec_fifo.i >= FIFOMAX) {
    printf("exec fifo overflowed\n");
    exit(-1);
  }
  exec_fifo.buf[exec_fifo.i] = exec_count[0];
  exec_fifo.i++;
}

void getexecdiff() {
  static int i = 0;
  exec_fifo.i--;
  if (exec_fifo.i < 0) {
    printf("exec fifo underflowed\n");
    exit(-1);
  }
  uint64_t cnt = exec_count[0] - exec_fifo.buf[exec_fifo.i];
  section_exec += cnt;
  printf("%d exec cnts: %"PRIu64"\n",i, cnt);
  i++;
}

uint32_t fadd(uint32_t a, uint32_t b) {
  Float ra, rb, rt;
  ra.i = a;
  rb.i = b;
  rt.f = ra.f + rb.f;
  return rt.i;
}

uint32_t fsub(uint32_t a, uint32_t b) {
  Float ra, rb, rt;
  ra.i = a;
  rb.i = b;
  rt.f = ra.f - rb.f;
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

uint32_t faba(uint32_t a, uint32_t b) {
  Float ra, rb, rt;
  ra.i = a;
  rb.i = b;
  rt.f = fabsf(ra.f + rb.f);
  return rt.i;
}

uint32_t fam(uint32_t a, uint32_t b, uint32_t c) {
  Float ra, rb, rc, rt;
  ra.i = a;
  rb.i = b;
  rc.i = c;
  rt.f = ra.f * rb.f + rc.f;
  return rt.i;
}

uint32_t fsqrt(uint32_t a) {
  Float ra, rt;
  ra.i = a;
  rt.f = sqrtf(ra.f);
  return rt.i;
}

int fcmpc(uint32_t a, uint32_t b, uint32_t c) {
  Float ra, rb;
  ra.i = a;
  rb.i = b;
  if (ra.f > rb.f) {
    return c & 4 ? 1 : 0;
  } else if (ra.f == rb.f) {
    return c & 2 ? 1 : 0;
  }
  return c & 1 ? 1 : 0;
}

void min_caml_entry();

int main() {
  int i;
  if ((rfp = fopen("stdin", "r")) == NULL) {
    fprintf(stderr, "%sのオープンに失敗しました。\n", "stdin");
    return EXIT_FAILURE;
  }
  if ((wfp = fopen("stdout", "w")) == NULL) {
    fprintf(stderr, "%sのオープンに失敗しました。\n", "stdout");
    return EXIT_FAILURE;
  }
  exec_fifo.i = 0;
  // メモリ空間(SRAM)は4MB
  mem_offset[0] = malloc(4*1024*1024);
  printf("registers    : 0x%x\n", (uint32_t)regs);
  printf("memory space : 0x%x\n", (uint32_t)(mem_offset[0]));
  fflush(stdout);
  for (i = 0; i < 255; i++) {
    regs[i] = 0;
  }
  min_caml_entry();
  printf("limm_count:%f\n",limm_count[0]/100000000.0);
  printf("generic_count:%"PRIu64"\n",generic_count[0]);
  printf("section_exec_count:%f\n",section_exec/100000000.0);
  printf("exec_count:%f\n",exec_count[0]/100000000.0);
  return 0;
}
