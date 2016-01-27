#!/Usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from itertools import chain
import math

ignore={".text",".globl",".align",".data",".literal8"}
nowrite=ignore
onereg={"limm","in","out","hlt","show"}
twoireg={"stwi","ldwi","jif","ci","addi","subi"}
twoicreg={"cmpic","cmpaic","jic","fjic"}
threecreg={"cmpc","fcmpc","cmpac","fcmpac","jrc","fjrc"}

def convert_op1(inst,instno,reg,imm):
    if inst=="limm":
        if isinstance(imm,int):
            return "INCQ({2});movl ${0:d}, ({1:d}*4+cdecl(regs));".format(imm, reg, "cdecl(limm_count)")
        else:
            return "INCQ({2});movl ${0}, %eax; movl %eax, ({1:d}*4+cdecl(regs));".format(imm, reg, "cdecl(limm_count)")
    elif inst=="in":
        return "CALL({0}); movl %eax, ({1:d}*4+cdecl(regs));".format("cdecl(in)",reg)
    elif inst=="out":
        return "movl ({0:d}*4+cdecl(regs)), %eax; CALL({1});".format(reg,"cdecl(out)")
    elif inst=="hlt":
        return "popl %ebp; ret;"
    elif inst=="show":
        return "movl ({0:d}*4+cdecl(regs)), %eax; CALL({1});".format(reg,"cdecl(show)")
    else:
        return ""

def convert_op2i(inst,instno,reg1,reg2,imm):
    if inst=="stwi":
        return "STWI({0:d},{1:d},{2:d})".format(reg1, reg2, imm)
    elif inst=="ldwi":
        return "LDWI({0:d},{1:d},{2:d})".format(reg1, reg2, imm)
    elif inst=="addi":
        return "ADDI({0:d},{1:d},{2:d})".format(reg1, reg2, imm)
    elif inst=="subi":
        return "SUBI({0:d},{1:d},{2:d})".format(reg1, reg2, imm)
    elif inst=="jif":
        return "JIF({0:d},{1:d},{2},{3:03X},{4:03X})".format(reg1, reg2, imm, instno+1, instno)
    elif inst=="ci":
        if imm=="min_caml_count":
            return "INCQ({0});".format("cdecl(generic_count)")
        elif imm=="min_caml_showexec":
            return "CALL({0});".format("cdecl(showexec)")
        elif imm=="min_caml_setcurexec" or imm=="min_caml_sce":
            return "CALL({0});".format("cdecl(setcurexec)")
        elif imm=="min_caml_getexecdiff" or imm=="min_caml_ged":
            return "CALL({0});".format("cdecl(getexecdiff)")
        elif imm=="min_caml_generic":
            return "movl (7*4+cdecl(regs)), %eax; movl (8*4+cdecl(regs)), %ebx; movl (9*4+cdecl(regs)), %ecx; movl (10*4+cdecl(regs)), %edx; CALL({0}); movl %eax, (7*4+cdecl(regs));".format("cdecl(generic)")
        else:
            return "CI({0:d},{1:d},{2},{3:03X},{4:03X})".format(reg1, reg2, imm, instno+1, instno)
    else:
        return ""

def convert_op2ic(inst,instno,reg1,reg2,imm,condition):
    if inst=="cmpic":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ${1:d}, %ebx; movl ${2:d}, %ecx; CALL({3}); movl %eax, ({4:d}*4+cdecl(regs));".format(reg2, imm, condition, "cdecl(cmpc)", reg1)
    elif inst=="cmpaic":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ${1:d}, %ebx; movl ${2:d}, %ecx; CALL({3}); andl %eax, ({4:d}*4+cdecl(regs));".format(reg2, imm, condition, "cdecl(cmpc)", reg1)
    elif inst=="jic":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); JIC({4},{5:03X},{6:03X})".format(reg1, reg2, condition, "cdecl(cmpc)", imm, instno + 1, instno)
    elif inst=="fjic":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); JIC({4},{5:03X},{6:03X})".format(reg1, reg2, condition, "cdecl(fcmpc)", imm, instno + 1, instno)
    else:
        return ""

def convert_op3c(inst,instno,reg1,reg2,reg3,condition):
    if inst=="cmpc":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); movl %eax, ({4:d}*4+cdecl(regs));".format(reg2, reg3, condition, "cdecl(cmpc)", reg1)
    elif inst=="fcmpc":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); movl %eax, ({4:d}*4+cdecl(regs));".format(reg2, reg3, condition, "cdecl(fcmpc)", reg1)
    elif inst=="cmpac":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); andl %eax, ({4:d}*4+cdecl(regs));".format(reg2, reg3, condition, "cdecl(cmpc)", reg1)
    elif inst=="fcmpac":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); andl %eax, ({4:d}*4+cdecl(regs));".format(reg2, reg3, condition, "cdecl(fcmpc)", reg1)
    elif inst=="jrc":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); JRC({4:d},{5:03X},{6:03X})".format(reg1, reg2, condition, "cdecl(cmpc)", reg3, instno + 1, instno)
    elif inst=="fjrc":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; movl ${2:d}, %ecx; CALL({3}); JRC({4:d},{5:03X},{6:03X})".format(reg1, reg2, condition, "cdecl(fcmpc)", reg3, instno + 1, instno)
    else:
        return ""
    
def convert_op3(inst,instno,reg1,reg2,reg3):
    if inst=="jrf":
        return "JRF({0:d},{1:d},{2:d},{3:03X},{4:03X})".format(reg1, reg2, reg3, instno+1, instno)
    elif inst=="cr":
        return "CR({0:d},{1:d},{2:d},{3:03X},{4:03X})".format(reg1, reg2, reg3, instno+1, instno)
    elif inst=="stw":
        return "STW({0:d},{1:d},{2:d})".format(reg1, reg2, reg3)
    elif inst=="ldw":
        return "LDW({0:d},{1:d},{2:d})".format(reg1, reg2, reg3)
    elif inst in {"add","sub","and","or","xor"}:
        return "movl ({0:d}*4+cdecl(regs)), %eax; {1}l ({2:d}*4+cdecl(regs)), %eax; movl %eax, ({3:d}*4+cdecl(regs))".format(reg2, inst, reg3, reg1)
    elif inst=="sll":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ecx; cmpl $32, %ecx; jl tmp_label_{2:03X}; movl $0, %eax; tmp_label_{2:03X}: shll %cl, %eax; movl %eax, ({3:d}*4+cdecl(regs))".format(reg2, reg3, instno, reg1)
    elif inst=="srl":
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ecx; cmpl $32, %ecx; jl tmp_label_{2:03X}; movl $0, %eax; tmp_label_{2:03X}: shrl %cl, %eax; movl %eax, ({3:d}*4+cdecl(regs))".format(reg2, reg3, instno, reg1)
    # 0.015
    elif inst in {"fadd","fsub","fmul","finv","faba"}:
        return "movl ({0:d}*4+cdecl(regs)), %eax; movl ({1:d}*4+cdecl(regs)), %ebx; CALL({2}); movl %eax, ({3:d}*4+cdecl(regs));".format(reg2, reg3, "cdecl("+inst+")", reg1)
    elif inst=="fsqrt":
        return "movl ({0:d}*4+cdecl(regs)), %eax; CALL({1}); movl %eax, ({2:d}*4+cdecl(regs));".format(reg2, "cdecl("+inst+")", reg1)
    else:
        return ""

def get_labels(program):
    instnum=0
    datanum = 0
    labels={
        "min_caml_count:":0,
        "min_caml_showexec:":0,
        "min_caml_setcurexec:":0,
        "min_caml_sce:":0,
        "min_caml_getexecdiff:":0,
        "min_caml_ged:":0,
        "min_caml_generic:":0
    }
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

def write_data(fp,fp_comment,program,program_org,labels):
    datano=0
    for line,inst in enumerate(program):
        #print line
        #print inst
        if len(inst)==0:#nothing
            pass
        elif inst[0] in ignore:
            pass
        elif inst[0]==".long":#long
            fp.write("\t\tmovl $0x{0:X}, %eax; addl (cdecl(mem_offset)), %eax; movl $0x{1:08X}, (%eax);\n".format(datano*4, imm(inst[1],labels)))
            datano+=1
        else:
            pass

def write_binary(fp,fp_comment,program,program_org,labels,count_flag):
    instno=0
    if count_flag:
        count_asm="\t\tINCQ({0});\n".format("cdecl(exec_count)")
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
            fp.write("\t{0}\n".format(inst[0]))
            #fp.write("\t\tcall get_eip; CALL({1});\n".format(reg,"_trace"))
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
        elif inst[0] in twoireg:#two reg & imm operation
            if not (len(inst)==4):
                print "wrong number of args in line {}.".format(line + 1)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op2i(inst[0],instno,reg(inst[1]),reg(inst[2]),imm(inst[3],labels))
                if inst_str=="":
                    print "undefined opcode in line {}".format(line + 1)
                    print " ".join(inst)
                    exit(1)
                fp.write("// line:{0:d}\t{1}\n".format(line + 1,program_org[line]))
                fp.write(".align 4; inst_{0:03X}:\n{1}\t\t{2}\n".format(instno,count_asm,inst_str))
                wrote_flag=True
        elif inst[0] in twoicreg:#two reg & imm & condition operation
            if not (len(inst)==5):
                print "wrong number of args in line {}.".format(line + 1)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op2ic(inst[0],instno,reg(inst[1]),reg(inst[2]),imm(inst[3],labels),int(inst[4],0))
                if inst_str=="":
                    print "undefined opcode in line {}".format(line + 1)
                    print " ".join(inst)
                    exit(1)
                fp.write("// line:{0:d}\t{1}\n".format(line + 1,program_org[line]))
                fp.write(".align 4; inst_{0:03X}:\n{1}\t\t{2}\n".format(instno,count_asm,inst_str))
                wrote_flag=True
        elif inst[0] in threecreg:#three reg & condition operation
            if not (len(inst)==5):
                print "wrong number of args in line {}.".format(line + 1)
                print " ".join(inst)
                exit(1)
            else:
                inst_str=convert_op3c(inst[0],instno,reg(inst[1]),reg(inst[2]),reg(inst[3]),int(inst[4],0))
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
    file_out.write(".globl cdecl(regs)\n")
    file_out.write("\t\t.comm cdecl(regs), 1024\n")
    file_out.write(".globl cdecl(limm_count)\n")
    file_out.write("\t\t.comm cdecl(limm_count),8\n")
    file_out.write(".globl cdecl(exec_count)\n")
    file_out.write("\t\t.comm cdecl(exec_count),8\n")
    file_out.write(".globl cdecl(generic_count)\n")
    file_out.write("\t\t.comm cdecl(generic_count),8\n")
    file_out.write(".globl cdecl(mem_offset)\n")
    file_out.write("\t\t.comm cdecl(mem_offset),4\n")
    file_out.write(".text\n")
    file_out.write(".align 4\n")
    file_out.write(".global cdecl(min_caml_entry)\n")
    file_out.write("cdecl(min_caml_entry):\n")
    file_out.write("\t\tpushl %ebp; movl %esp, %ebp;\n")
    write_data(file_out,file_comment,program,program_org,labels)
    file_out.write("\t\tjmp _min_caml_init;\n")
    write_binary(file_out,file_comment,program,program_org,labels,True)
    file_out.write("\t\tpopl %ebp;\n")
    file_out.write("\t\tret;\n")
    file_out.write("\t\tget_eip: movl (%esp), %eax; ret;\n")
    
    print("Assembling succeeded.")
    print("Dumped '{}' ({} instructions).".format(file_out_name,instnum))
    print("Dumped '{}'.".format(file_comment_name))


if __name__ =="__main__":
    main()
