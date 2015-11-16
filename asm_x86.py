#!/Usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import chain
import math

ignore={".text",".globl",".align",".data",".literal8"}
nowrite=ignore
onereg={"limm","j","in","out","hlt"}

# 2引数まで対応
def call(func):
    return "subl $24, %esp; movl %ebx, 4(%esp); movl %eax, (%esp); call {0}; addl $24, %esp".format(func)

def convert_op1(inst,instno,reg,imm):
    if inst=="limm":
        if isinstance(imm,int):
            return "\t\t{2};movl ${0:d}, ({1:d}*4+_regs);".format(imm, reg, call("_count_limm"))
        else:
            return "\t\t{2};movl (_limm_count), %eax;incl %eax;movl %eax, (_limm_count);\nmovl ${0}, %eax; shrl $2, %eax; movl %eax, ({1:d}*4+_regs);".format(imm, reg, call("_count_limm"))
    elif inst=="j":
        return "movl $inst_{0:03X}, %eax; shrl $2, %eax; movl %eax, ({1:d}*4+_regs); jmp inst_{2:03X};".format(instno+1, reg, instno+int(imm,0))
    elif inst=="in":
        return "{0}; movl %eax, ({1:d}*4+_regs);".format(call("_in"),reg)
    elif inst=="out":
        return "movl ({0:d}*4+_regs), %eax; {1};".format(reg,call("_out"))
    elif inst=="hlt":
        return "popl %ebp; ret;"
    else:
        return ""

def convert_op3(inst,instno,reg1,reg2,reg3):
    if inst=="cmp":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ebx; {2}; movl %eax, ({3:d}*4+_regs);".format(reg2, reg3, call("_cmp"), reg1)
    elif inst=="jr":
        return "movl ({0:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{1:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({2:d}*4+_regs); jmp *%eax;".format(reg2, instno+1, reg1)
    elif inst=="stw":
        return "movl ({0:d}*4+_regs), %eax; shll $2, %eax; movl ({1:d}*4+_regs), %ebx; movl %ebx, (%eax);".format(reg1, reg2)
    elif inst=="ldw":
        return "movl ({0:d}*4+_regs), %eax; shll $2, %eax; movl (%eax), %eax; movl %eax, ({1:d}*4+_regs);".format(reg2, reg1)
    elif inst in {"add","sub","and","or","xor"}:
        return "movl ({0:d}*4+_regs), %eax; {1}l ({2:d}*4+_regs), %eax; movl %eax, ({3:d}*4+_regs)".format(reg2, inst, reg3, reg1)
    elif inst=="not":
        return "movl ({0:d}*4+_regs), %eax; not %eax; movl %eax, ({1:d}*4+_regs)".format(reg2, reg1)
    elif inst=="sll":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ecx; shll %cl, %eax; movl %eax, ({2:d}*4+_regs)".format(reg2, reg3, reg1)
    elif inst=="srl":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ecx; shrl %cl, %eax; movl %eax, ({2:d}*4+_regs)".format(reg2, reg3, reg1)
    elif inst=="jreq":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{3:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(1, reg2, reg3, instno+1, reg1, "je", instno)
    elif inst=="jrneq":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{3:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(1, reg2, reg3, instno+1, reg1, "jne", instno)
    elif inst=="jrgt":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{3:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(2, reg2, reg3, instno+1, reg1, "je", instno)
    elif inst=="jrgte":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{3:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(0, reg2, reg3, instno+1, reg1, "jne", instno)
    elif inst=="jrlt":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{3:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(0, reg2, reg3, instno+1, reg1, "je", instno)
    elif inst=="jrlte":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; shll $2, %eax; movl $inst_{3:03X}, %ebx; shrl $2, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(2, reg2, reg3, instno+1, reg1, "jne", instno)
    elif inst in {"fadd","fmul","fdiv"}:
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ebx; {2}; movl %eax, ({3:d}*4+_regs);".format(reg2, reg3, call("_"+inst), reg1)
    elif inst=="fsqrt":
        return "movl ({0:d}*4+_regs), %eax; {1}; movl %eax, ({2:d}*4+_regs);".format(reg2, call("_"+inst), reg1)
    elif inst in "fcmpl":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ebx; {2}; movl %eax, ({3:d}*4+_regs);".format(reg2, reg3, call("_"+inst), reg1)
    return ""

def get_labels(program):
    instnum=0
    labels={}
    for inst in program:
        if len(inst)==0 or (inst[0] in nowrite):#nowrite or empty
            continue
        elif ":" in inst[0]:#label
            labels[inst[0]]=instnum
        else:#inst & ".long"
            instnum+=1
    return labels,instnum

def reg(s):
    if not s.startswith("r"):
        print "'{}' is not a register".format(s)
    return int("0x"+s[1:],0)

def imm(s,label):
    if s+":" in label:
        return s
    else:
        return int(s,0)

def float_to_cfloat(a):
    if a>=0:
        sign=0
    else:
        sign=1
    
    a=abs(a)

    if a!=0:
        m,e=math.frexp(a)
        expo=int(e+126)
        man=int((m-0.5)*pow(2,24))
    else:
        expo=0
        man=0

    ret=(sign<<31)+(expo<<23)+man
    
    return "{0:d}".format(ret)
    
def fimm(s):
    if s.endswith("d"):
        return float(s[:-1])#todo
    else:
        print("{} is not a float".format(s))
        exit(1)

def write_binary(fp,fp_comment,program,program_org,labels,count_flag):
    instno=0
    if count_flag:
        count_asm="\t\t{0};\n".format(call("_count_exec"))
    else:
        count_asm=""
    for line,inst in enumerate(program):
        wrote_flag=False
        #print line
        #print inst
        if len(inst)==0:#nothing
            pass
        elif inst[0] in ignore:
            pass
        elif inst[0] in labels:
            fp.write(".align 4;\t{0}\n".format(inst[0]))
        elif inst[0]==".long":#long
            fp.write("\t\t.long {0}\n".format(float_to_cfloat(fimm(inst[1]))))
        elif inst[0] in onereg:#one reg operation
            if not(len(inst)==3):
                print "wrong number of args in line {}.".format(line)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op1(inst[0],instno,reg(inst[1]),imm(inst[2],labels))
                if inst_str=="":
                    print "undefined opcode in line {}".format(line)
                    print " ".join(inst)
                    exit(1)
                fp.write((".align 4; inst_{0:03X}:\n{1}\t\t{2}\n".format(instno,count_asm,inst_str)))
                wrote_flag=True
        else:#three reg operation
            if not(len(inst)==4 or len(inst)==3):#delete!
                print "wrong number of args in line {}.".format(line)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op3(inst[0],instno,reg(inst[1]),reg(inst[2]),reg(inst[3]))
                if inst_str=="":
                    print "undefined opcode in line {}".format(line)
                    print " ".join(inst)
                    exit(1)
                fp.write(".align 4; inst_{0:03X}:\n{1}\t\t{2}\n".format(instno,count_asm,inst_str))
                wrote_flag=True
        if wrote_flag==True:
            fp_comment.write(program_org[line].ljust(35)+"\t#{0:03X}\n".format(instno))
            instno+=1
        else:
            fp_comment.write(program_org[line]+"\n")

#================main=================
def main():
    argv=sys.argv
    file_in_name=sys.argv[1]
    file_out_name=sys.argv[1].split(".")[0]+".S"
    file_comment_name=sys.argv[1].split(".")[0]+".com"
    file_in=open(file_in_name,"r")
    file_out=open(file_out_name,"wb")
    file_comment=open(file_comment_name,"w")

    #load program and parse
    program_org= file_in.read().split("\n")
    program=[list(chain.from_iterable([ss.split() for ss in s.split("#")[0].split(",")])) for s in program_org]

    #get instnum & labels
    labels,instnum=get_labels(program)


    file_out.write(".global _min_caml_entry\n")
    file_out.write("_min_caml_entry:")
    file_out.write("\t\tpushl %ebp; movl %esp, %ebp; ")
    file_out.write("\t\tjmp _min_caml_start;\n")
    write_binary(file_out,file_comment,program,program_org,labels,True)
    file_out.write("\t\tpopl %ebp;\n")
    file_out.write("\t\tret;\n")
    
    print("Assembling succeeded.")
    print("Dumped '{}' ({} instructions).".format(file_out_name,instnum))
    print("Dumped '{}'.".format(file_comment_name))


if __name__ =="__main__":
    main()
