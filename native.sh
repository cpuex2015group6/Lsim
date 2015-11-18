#!/bin/sh
cp $1 asm_x86.cpuexasm && echo "generating native binary:" && make native && rm asm_x86.cpuexasm && ./native && ppmtobmp stdout > stdout.bmp
