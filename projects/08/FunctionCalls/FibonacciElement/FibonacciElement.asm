@256
D=A
@SP
M=D
@0
D=A
@SP
A=M
M=D
A=A+1
D=A
@SP
M=D
@0
D=A
@SP
A=M
M=D
A=A+1
D=A
@SP
M=D
@0
D=A
@SP
A=M
M=D
A=A+1
D=A
@SP
M=D
@0
D=A
@SP
A=M
M=D
A=A+1
D=A
@SP
M=D
@0
D=A
@SP
A=M
M=D
A=A+1
D=A
@SP
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(Main.fibonacci)
@0
D=A
@R13
M=D
@function_call2_0
D;JEQ
(function_call_0)
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@R13
MD=M-1
@function_call_0
D;JGT
(function_call2_0)
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M
A=A-1
D=M
A=A-1
D=M-D
@LT0
D;JLT
@SP
A=M
A=A-1
A=A-1
M=0
@NLT0
0;JMP
(LT0)
@SP
A=M
A=A-1
A=A-1
M=-1
(NLT0)
@SP
M=M-1
@SP
A=M-1
D=M
@SP
M=M-1
@Main.fibonacci$IF_TRUE
D;JNE
@Main.fibonacci$IF_FALSE
0;JMP
(Main.fibonacci$IF_TRUE)
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@SP
A=M-1
D=M
@ARG
A=M
M=D
D=A+1
@SP
M=D
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D
@R13
D=M
A=D-1
D=M
@THAT
M=D
@R14
A=M
0;JMP
(Main.fibonacci$IF_FALSE)
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
A=M
A=A-1
D=M
A=A-1
D=M-D
M=D
D=A+1
@0
M=D
@return0
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
@LCL
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@ARG
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@THIS
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@THAT
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(return0)
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@0
A=M
A=A-1
D=M
A=A-1
D=M-D
M=D
D=A+1
@0
M=D
@return1
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
@LCL
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@ARG
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@THIS
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@THAT
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(return1)
@0
A=M
A=A-1
D=M
A=A-1
A=M
D=A+D
@0
A=M
A=A-1
A=A-1
M=D
D=A+1
@0
M=D
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@SP
A=M-1
D=M
@ARG
A=M
M=D
D=A+1
@SP
M=D
@R13
D=M
@4
A=D-A
D=M
@LCL
M=D
@R13
D=M
@3
A=D-A
D=M
@ARG
M=D
@R13
D=M
@2
A=D-A
D=M
@THIS
M=D
@R13
D=M
A=D-1
D=M
@THAT
M=D
@R14
A=M
0;JMP
(Sys.init)
@0
D=A
@R13
M=D
@function_call2_1
D;JEQ
(function_call_1)
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@R13
MD=M-1
@function_call_1
D;JGT
(function_call2_1)
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
@return2
D=A
@SP
A=M
M=D
D=A+1
@SP
M=D
@LCL
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@ARG
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@THIS
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@THAT
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
@SP
D=M
@1
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(return2)
(Sys.init$WHILE)
@Sys.init$WHILE
0;JMP
