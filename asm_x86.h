#ifndef __LIGHTNING_ASM_X86_H__
#define __LIGHTNING_ASM_X86_H__

#if defined(__APPLE__)
# define cdecl(s) _##s
#else
# define cdecl(s) s
#endif


// 3引数まで対応
#define CALL(func) subl $24, %esp; movl %ecx, 8(%esp); movl %ebx, 4(%esp); movl %eax, (%esp); call func; addl $24, %esp

#define INCQ(var) movl $var, %eax; movl (%eax), %ecx; addl $1, %ecx; adcl $0, 4(%eax); movl %ecx, (%eax)

#define LDW(dest, src, offset) movl (src*4+cdecl(regs)), %eax; movl (offset*4+cdecl(regs)), %ebx; addl %ebx, %eax; shll $2, %eax; addl (cdecl(mem_offset)), %eax; movl (%eax), %eax; movl %eax, (dest*4+cdecl(regs));
#define STW(dest, src, offset) movl (dest*4+cdecl(regs)), %eax; movl (offset*4+cdecl(regs)), %ebx; addl %ebx, %eax; shll $2, %eax; addl (cdecl(mem_offset)), %eax; movl (src*4+cdecl(regs)), %ebx; movl %ebx, (%eax);

#define ADDI(dest, src, imm) movl (src*4+cdecl(regs)), %eax; addl $imm, %eax; movl %eax, (dest*4+cdecl(regs))
#define SUBI(dest, src, imm) movl (src*4+cdecl(regs)), %eax; subl $imm, %eax; movl %eax, (dest*4+cdecl(regs))

#define LDWI(dest, src, imm) movl (src*4+cdecl(regs)), %eax; addl $imm, %eax; shll $2, %eax; addl (cdecl(mem_offset)), %eax; movl (%eax), %eax; movl %eax, (dest*4+cdecl(regs));
#define STWI(dest, src, imm) movl (dest*4+cdecl(regs)), %eax; addl $imm, %eax; shll $2, %eax; addl (cdecl(mem_offset)), %eax; movl (src*4+cdecl(regs)), %ebx; movl %ebx, (%eax);

#define JIC(imm, next, cur) movl %eax, %ecx; movl $imm, %eax; cmpl $1, %ecx; je tmp_label_##cur; jmp inst_##next; tmp_label_##cur: jmp *%eax;
#define JRC(target, next, cur) movl %eax, %ecx; movl (target*4+cdecl(regs)), %eax; cmpl $1, %ecx; je tmp_label_##cur; jmp inst_##next; tmp_label_##cur: jmp *%eax;

#define JIF(dest, cond, imm, next, cur) movl (cond*4+cdecl(regs)), %ecx; movl $imm, %eax; cmpl $0, %ecx; je tmp_label_##cur; jmp inst_##next; tmp_label_##cur: movl $0, (dest*4+cdecl(regs)); jmp *%eax;
#define JRF(dest, cond, target, next, cur) movl (cond*4+cdecl(regs)), %ecx; movl (target*4+cdecl(regs)), %eax; cmpl $0, %ecx; je tmp_label_##cur; jmp inst_##next; tmp_label_##cur: movl $0, (dest*4+cdecl(regs)); jmp *%eax;

#define CI(dest, cond, imm, next, cur) movl (cond*4+cdecl(regs)), %ecx; movl $imm, %eax; movl $inst_##next, %ebx; movl %ebx, (dest*4+cdecl(regs)); cmpl $0, %ecx; je tmp_label_##cur; jmp inst_##next; tmp_label_##cur: jmp *%eax;
#define CR(dest, cond, target, next, cur) movl (cond*4+cdecl(regs)), %ecx; movl (target*4+cdecl(regs)), %eax; movl $inst_##next, %ebx; movl %ebx, (dest*4+cdecl(regs)); cmpl $0, %ecx; je tmp_label_##cur; jmp inst_##next; tmp_label_##cur: jmp *%eax;

#endif /* __LIGHTNING_ASM_X86_H__ */
