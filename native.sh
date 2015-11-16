#!/bin/sh
cp $1 asm_x86.cpuexasm
echo "generating native binary:"
make native
./native
ppmtobmp stdout > stdout.bmp
rm asm_x86.cpuexasm
