@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@0
D=D+A
@R13
M=D
@SP
A=M-1
D=M
@R13
A=M
M=D
@SP
D=M-1
@SP
M=D
($LOOP_START)
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
@0
A=D+A
D=M
@SP
A=M
M=D
D=A+1
@SP
M=D
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
@0
D=D+A
@R13
M=D
@SP
A=M-1
D=M
@R13
A=M
M=D
@SP
D=M-1
@SP
M=D
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
@ARG
D=M
@0
D=D+A
@R13
M=D
@SP
A=M-1
D=M
@R13
A=M
M=D
@SP
D=M-1
@SP
M=D
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
@SP
A=M-1
D=M
@SP
M=M-1
@$LOOP_START
D;JNE
@LCL
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