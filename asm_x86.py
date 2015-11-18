#!/Usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import chain
import math

ignore={".text",".globl",".align",".data",".literal8"}
nowrite=ignore
onereg={"limm","j","in","out","hlt","show"}

# 2引数まで対応
def call(func):
    return "subl $24, %esp; movl %ebx, 4(%esp); movl %eax, (%esp); call {0}; addl $24, %esp".format(func)

def incq(var):
    return "movl ${0}, %eax; movl (%eax), %ecx; addl $1, %ecx; adcl $0, 4(%eax); movl %ecx, (%eax)".format(var)

def convert_op1(inst,instno,reg,imm):
    if inst=="limm":
        if isinstance(imm,int):
            return "\t\t{2};movl ${0:d}, ({1:d}*4+_regs);".format(imm, reg, incq("_limm_count"))
        else:
            return "\t\t{2};movl ${0}, %eax; movl %eax, ({1:d}*4+_regs);".format(imm, reg, incq("_limm_count"))
    elif inst=="j":
        return "movl $inst_{0:03X}, %eax; movl %eax, ({1:d}*4+_regs); jmp inst_{2:03X};".format(instno+1, reg, instno+int(imm,0))
    elif inst=="in":
        return "{0}; movl %eax, ({1:d}*4+_regs);".format(call("_in"),reg)
    elif inst=="out":
        return "movl ({0:d}*4+_regs), %eax; {1};".format(reg,call("_out"))
    elif inst=="hlt":
        return "popl %ebp; ret;"
    elif inst=="show":
        return "movl ({0:d}*4+_regs), %eax; {1};".format(reg,call("_show"))
    else:
        return ""

def convert_op3(inst,instno,reg1,reg2,reg3):
    if inst=="cmp":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ebx; {2}; movl %eax, ({3:d}*4+_regs);".format(reg2, reg3, call("_cmp"), reg1)
    elif inst=="jr":
        return "movl ({0:d}*4+_regs), %eax; movl $inst_{1:03X}, %ebx; movl %ebx, ({2:d}*4+_regs); jmp *%eax;".format(reg2, instno+1, reg1)
    elif inst=="stw":
        return "STW({0:d},{1:d})".format(reg1, reg2)
    elif inst=="ldw":
        return "LDW({0:d},{1:d})".format(reg1, reg2)
    elif inst in {"add","sub","and","or","xor"}:
        return "movl ({0:d}*4+_regs), %eax; {1}l ({2:d}*4+_regs), %eax; movl %eax, ({3:d}*4+_regs)".format(reg2, inst, reg3, reg1)
    elif inst=="not":
        return "movl ({0:d}*4+_regs), %eax; not %eax; movl %eax, ({1:d}*4+_regs)".format(reg2, reg1)
    elif inst=="sll":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ecx; cmpl $32, %ecx; jl tmp_label_{2:d}; movl $0, %eax; tmp_label_{2:d}: shll %cl, %eax; movl %eax, ({3:d}*4+_regs)".format(reg2, reg3, instno, reg1)
    elif inst=="srl":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ecx; cmpl $32, %ecx; jl tmp_label_{2:d}; movl $0, %eax; tmp_label_{2:d}: shrl %cl, %eax; movl %eax, ({3:d}*4+_regs)".format(reg2, reg3, instno, reg1)
    elif inst=="jreq":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; movl $inst_{3:03X}, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(1, reg2, reg3, instno+1, reg1, "je", instno)
    elif inst=="jrneq":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; movl $inst_{3:03X}, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(1, reg2, reg3, instno+1, reg1, "jne", instno)
    elif inst=="jrgt":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; movl $inst_{3:03X}, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(2, reg2, reg3, instno+1, reg1, "je", instno)
    elif inst=="jrgte":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; movl $inst_{3:03X}, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(0, reg2, reg3, instno+1, reg1, "jne", instno)
    elif inst=="jrlt":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; movl $inst_{3:03X}, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(0, reg2, reg3, instno+1, reg1, "je", instno)
    elif inst=="jrlte":
        return "movl ({1:d}*4+_regs), %ecx; movl ({2:d}*4+_regs), %eax; movl $inst_{3:03X}, %ebx; movl %ebx, ({4:d}*4+_regs); cmpl ${0:d}, %ecx; {5} tmp_label_{6:d}; jmp inst_{3:03X}; .align 4; tmp_label_{6:d}: jmp *%eax;".format(2, reg2, reg3, instno+1, reg1, "jne", instno)
    elif inst in {"fadd","fmul","finv"}:
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ebx; {2}; movl %eax, ({3:d}*4+_regs);".format(reg2, reg3, call("_"+inst), reg1)
    elif inst=="fsqrt":
        return "movl ({0:d}*4+_regs), %eax; {1}; movl %eax, ({2:d}*4+_regs);".format(reg2, call("_"+inst), reg1)
    elif inst in "fcmpl":
        return "movl ({0:d}*4+_regs), %eax; movl ({1:d}*4+_regs), %ebx; {2}; movl %eax, ({3:d}*4+_regs);".format(reg2, reg3, call("_"+inst), reg1)
    return ""

def get_labels(program):
    instnum=0
    datanum = 0
    labels={}
    for inst in program:
        if len(inst)==0 or (inst[0] in nowrite):#nowrite or empty
            continue
        elif ":" in inst[0]:#label
            if inst[0].startswith("l."):
                labels[inst[0]]=datanum
            else:
                labels[inst[0]]=instnum
        elif inst[0]==".long":#long
            datanum+=1
        else:#inst
            instnum+=1
    return labels,instnum

def reg(s):
    if not s.startswith("r"):
        print "'{}' is not a register".format(s)
    return int("0x"+s[1:],0)

def imm(s,label):
    if s+":" in label:
        if s.startswith("l."):
            return label[s+":"]
        else:
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

def write_data(fp,fp_comment,program,program_org,labels,count_flag):
    datano=0
    for line,inst in enumerate(program):
        #print line
        #print inst
        if len(inst)==0:#nothing
            pass
        elif inst[0] in ignore:
            pass
        elif inst[0]==".long":#long
            fp.write("\t\tmovl $0x{0:X}, %eax; addl (_mem_offset), %eax; movl $0x{1:08X}, (%eax);\n".format(datano*4, imm(inst[1],labels)))
            datano+=1
        else:
            pass

def write_binary(fp,fp_comment,program,program_org,labels,count_flag):
    instno=0
    if count_flag:
        count_asm="\t\t{0};\n".format(incq("_exec_count"))
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
            pass
        elif inst[0] in onereg:#one reg operation
            if not(len(inst)==3):
                print "wrong number of args in line {}.".format(line + 1)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op1(inst[0],instno,reg(inst[1]),imm(inst[2],labels))
                if inst_str=="":
                    print "undefined opcode in line {}".format(line + 1)
                    print " ".join(inst)
                    exit(1)
                fp.write("// line:{0:d}\t{1}\n".format(line + 1,program_org[line]))
                fp.write(".align 4; inst_{0:03X}:\n{1}\t\t{2}\n".format(instno,count_asm,inst_str))
                wrote_flag=True
        else:#three reg operation
            if not(len(inst)==4 or len(inst)==3):#delete!
                print "wrong number of args in line {}.".format(line + 1)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op3(inst[0],instno,reg(inst[1]),reg(inst[2]),reg(inst[3]))
                if inst_str=="":
                    print "undefined opcode in line {}".format(line + 1)
                    print " ".join(inst)
                    exit(1)
                fp.write("// line:{0:d}\t{1}\n".format(line + 1,program_org[line]))
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


    file_out.write("#include \"asm_x86.h\"\n")
    file_out.write(".globl _regs\n")
    file_out.write("\t\t.comm _regs, 1024\n")
    file_out.write(".globl _limm_count\n")
    file_out.write("\t\t.comm _limm_count,8\n")
    file_out.write(".globl _exec_count\n")
    file_out.write("\t\t.comm _exec_count,8\n")
    file_out.write(".globl _generic_count\n")
    file_out.write("\t\t.comm _generic_count,4\n")
    file_out.write(".globl _mem_offset\n")
    file_out.write("\t\t.comm _mem_offset,4\n")
    file_out.write(".text\n")
    file_out.write(".align 4\n")
    file_out.write(".global _min_caml_entry\n")
    file_out.write("_min_caml_entry:\n")
    file_out.write("\t\tpushl %ebp; movl %esp, %ebp;\n")
    write_data(file_out,file_comment,program,program_org,labels,True)
    file_out.write("\t\tjmp _min_caml_init;\n")
    write_binary(file_out,file_comment,program,program_org,labels,True)
    file_out.write("\t\tpopl %ebp;\n")
    file_out.write("\t\tret;\n")
    
    print("Assembling succeeded.")
    print("Dumped '{}' ({} instructions).".format(file_out_name,instnum))
    print("Dumped '{}'.".format(file_comment_name))


if __name__ =="__main__":
    main()
