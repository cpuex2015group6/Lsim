#ifndef __LIGHTNING_ASM_X86_H__
#define __LIGHTNING_ASM_X86_H__

// 2引数まで対応
#define CALL(func) subl $24, %esp; movl %ebx, 4(%esp); movl %eax, (%esp); call func; addl $24, %esp
#define INCQ(var) movl $var, %eax; movl (%eax), %ecx; addl $1, %ecx; adcl $0, 4(%eax); movl %ecx, (%eax)
#define LDW(dest, src) movl (src*4+_regs), %eax; shll $2, %eax; addl (_mem_offset), %eax; movl (%eax), %eax; movl %eax, (dest*4+_regs);
#define STW(dest, src) movl (dest*4+_regs), %eax; shll $2, %eax; addl (_mem_offset), %eax; movl (src*4+_regs), %ebx; movl %ebx, (%eax);

#endif /* __LIGHTNING_ASM_X86_H__ */
