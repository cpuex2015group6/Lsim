#ifndef __LIGHTNING_ASM_X86_H__
#define __LIGHTNING_ASM_X86_H__

#define LDW(dest, src) movl (src*4+_regs), %eax; shll $2, %eax; addl (_mem_offset), %eax; movl (%eax), %eax; movl %eax, (dest*4+_regs);
#define STW(dest, src) movl (dest*4+_regs), %eax; shll $2, %eax; addl (_mem_offset), %eax; movl (src*4+_regs), %ebx; movl %ebx, (%eax);

#endif /* __LIGHTNING_ASM_X86_H__ */
