# This document contains the Python source code for the virtual machine translator specified in Chapters 6 and 7. 

#Import sys, re, glob, and os modules and assign vm file file path to variable or (if supplied path ends in a directory) vm file file paths to list

import sys, re
vm_file_paths = [sys.argv[1]]
hack_file_path = vm_file_paths[0][:-3] + ".asm"
if vm_file_paths[0].find(".vm") == -1:
	if vm_file_paths[0].endswith("/") == False:
		vm_file_paths[0] = vm_file_paths[0] + "/"
	vm_file_directory = vm_file_paths[0] 
	forward_slash_loc = vm_file_directory[:-1].rfind("/") + 1
	hack_file_path = vm_file_directory + vm_file_directory[forward_slash_loc:-1] + ".asm"
	vm_file_paths = []
	import glob, os
	os.chdir(vm_file_directory)
	for file in glob.glob("*.vm"):
		vm_file_paths.append(vm_file_directory + file)
print vm_file_paths


#PARSER MODULE CLASS

class vm_cmd:
	def __init__(self,vm_command):
		self.vm_command = vm_command

	def remove_comments_trailing_leading_whitespace(self):
		comm_loc = self.vm_command.find("//")
		if comm_loc == 0:
			self.vm_command = ""
		elif comm_loc != -1:
			self.vm_command = self.vm_command[:comm_loc]
		return (self.vm_command.rstrip()).lstrip()

	def command_type(self):
		arithmetic_commands = ["add","sub","neg","eq","gt","lt","and","or","not"]
		first_space_loc = self.vm_command.find(" ")
		if first_space_loc == -1:
			for i in arithmetic_commands:
				if i in self.vm_command:
					return "C_ARITHMETIC"
			if "return" in self.vm_command:
				return "C_RETURN"
		if "push" in self.vm_command[:first_space_loc]:
			return "C_PUSH"
		elif "pop" in self.vm_command[:first_space_loc]:
			return "C_POP"
		elif "if-goto" in self.vm_command[:first_space_loc]:
			return "C_IF"
		elif "goto" in self.vm_command[:first_space_loc]:
			return "C_GOTO"
		elif "function" in self.vm_command[:first_space_loc]:
			return "C_FUNCTION"
		elif "call" in self.vm_command[:first_space_loc]:
			return "C_CALL"
		elif "label" in self.vm_command[:first_space_loc]:
			return "C_LABEL"

	def arg1(self):
		if self.command_type() == "C_ARITHMETIC":
			return self.vm_command
		if self.command_type() == "C_PUSH":
			push_loc = self.vm_command.find("push") + 5
			second_space_loc = self.vm_command.rfind(" ")
			return self.vm_command[push_loc:second_space_loc]
		if self.command_type() == "C_POP":
			pop_loc = self.vm_command.find("pop") + 4
			second_space_loc = self.vm_command.rfind(" ")
			return self.vm_command[pop_loc:second_space_loc]
		if self.command_type() == "C_LABEL":
			label_loc = self.vm_command.find("label") + 6 
			return self.vm_command[label_loc:]
		if self.command_type() == "C_GOTO":
			goto_loc = self.vm_command.find("goto") + 5 
			return self.vm_command[goto_loc:]
		if self.command_type() == "C_IF":
			if_loc = self.vm_command.find("if-goto") + 8 
			return self.vm_command[if_loc:]
		if self.command_type() == "C_FUNCTION":
			function_loc = self.vm_command.find("function") + 9
			second_space_loc = self.vm_command.rfind(" ")
			return self.vm_command[function_loc:second_space_loc]
		if self.command_type() == "C_CALL":
			call_loc = self.vm_command.find("call") + 5
			second_space_loc = self.vm_command.rfind(" ") 
			return self.vm_command[call_loc:second_space_loc]

	def arg2(self):
		if self.command_type() in ["C_PUSH","C_POP","C_FUNCTION","C_CALL"]:
			second_space_loc = self.vm_command.rfind(" ") + 1
			return int(self.vm_command[second_space_loc:])


#CODE WRITER MODULE CLASS

EQ_COUNT = 0 # Initialize increment variable to use to ensure unique label naming for inline "eq" assembly branching
GT_COUNT = 0 # Initialize increment variable to use to ensure unique label naming for inline "gt" assembly branching
LT_COUNT = 0 # Initialize increment variable to use to ensure unique label naming for inline "lt" assembly branching

class vm_cmd_to_write:
	def __init__(self,cmd_type,arg1,arg2):
		self.cmd_type = cmd_type
		self.arg1 = arg1
		self.arg2 = arg2

	def write_arithmetic(self,file):
		if self.arg1 == "add":
			file.write(
				"@0" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"A=M" + "\n" +
				"D=A+D" + "\n" +
				"@0" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=D" + "\n" +
				"D=A+1" + "\n" +
				"@0" + "\n" +
				"M=D" + "\n" 
				)

		if self.arg1 == "sub":
			file.write(
				"@0" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M-D" + "\n" +
				"M=D" + "\n" +
				"D=A+1" + "\n" +
				"@0" + "\n" +
				"M=D" + "\n"
				)

		if self.arg1 == "neg":
			file.write(
				"@0" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"M=-M" + "\n"
				)

		if self.arg1 == "eq":
			global EQ_COUNT
			file.write(
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M-D" + "\n" +
				"@EQ" + str(EQ_COUNT) + "\n" +
				"D;JEQ" + "\n" +
				"@SP" + "\n" + 
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=0" + "\n" +
				"@NEQ" + str(EQ_COUNT) + "\n" +
				"0;JMP" + "\n" +
				"(EQ" + str(EQ_COUNT) + ")" + "\n" +
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=-1" + "\n" +
				"(NEQ" + str(EQ_COUNT) + ")" + "\n" +
				"@SP" + "\n" +
				"M=M-1" + "\n" 
				)
			EQ_COUNT += 1


		if self.arg1 == "gt":
			global GT_COUNT
			file.write(
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M-D" + "\n" +
				"@GT" + str(GT_COUNT) + "\n" +
				"D;JGT" + "\n" +
				"@SP" + "\n" + 
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=0" + "\n" +
				"@NGT" + str(GT_COUNT) + "\n" +
				"0;JMP" + "\n" +
				"(GT" + str(GT_COUNT) + ")" + "\n" +
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=-1" + "\n" +
				"(NGT" + str(GT_COUNT) + ")" + "\n" +
				"@SP" + "\n" +
				"M=M-1" + "\n"
				)
			GT_COUNT += 1


		if self.arg1 == "lt":
			global LT_COUNT
			file.write(
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M-D" + "\n" +
				"@LT" + str(LT_COUNT) + "\n" +
				"D;JLT" + "\n" +
				"@SP" + "\n" + 
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=0" + "\n" +
				"@NLT" + str(LT_COUNT) + "\n" +
				"0;JMP" + "\n" +
				"(LT" + str(LT_COUNT) + ")" + "\n" +
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"A=A-1" + "\n" +
				"M=-1" + "\n" +
				"(NLT" + str(LT_COUNT) + ")" + "\n" +
				"@SP" + "\n" +
				"M=M-1" + "\n"
				)
			LT_COUNT += 1

		if self.arg1 == "and":
			file.write(
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"M=D&M" + "\n" +
				"@SP" + "\n" +
				"M=M-1" + "\n"
				)

		if self.arg1 == "or":
			file.write(
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"D=M" + "\n" +
				"A=A-1" + "\n" +
				"M=D|M" + "\n" +
				"@SP" + "\n" +
				"M=M-1" + "\n"
				)

		if self.arg1 == "not":
			file.write(
				"@SP" + "\n" +
				"A=M" + "\n" +
				"A=A-1" + "\n" +
				"M=!M" + "\n"
				)

	def write_push_pop(self,read_file,write_file):
		
		if self.cmd_type == "C_PUSH":
			if self.arg1 == "constant":
				write_file.write(
					"@" + str(self.arg2) + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"M=M+1" + "\n"
					)


			if self.arg1 == "local":
				write_file.write(
					"@LCL" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"A=D+A" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)
			

			if self.arg1 == "argument":
				write_file.write(
					"@ARG" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"A=D+A" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)
		
			if self.arg1 == "this":
				write_file.write(
					"@THIS" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"A=D+A" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "that":
				write_file.write(
					"@THAT" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"A=D+A" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "pointer":
				write_file.write(
					"@THIS" + "\n" +
					"D=A" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"A=D+A" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "temp":
				write_file.write(
					"@5" + "\n" +
					"D=A" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"A=D+A" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "static":
				write_file.write(
					"@" + read_file + "." + str(self.arg2) + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)



		if self.cmd_type == "C_POP":
			if self.arg1 == "local":
				write_file.write(
					"@LCL" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D+A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" + 
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "argument":
				write_file.write(
					"@ARG" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D+A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" + 
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "this":
				write_file.write(
					"@THIS" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D+A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" + 
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "that":
				write_file.write(
					"@THAT" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D+A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" + 
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "pointer":
				write_file.write(
					"@THIS" + "\n" +
					"D=A" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D+A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" + 
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "temp":
				write_file.write(
					"@5" + "\n" +
					"D=A" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D+A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" + 
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

			if self.arg1 == "static":
				write_file.write(
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@" + read_file + "." + str(self.arg2) + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"D=M-1" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" 
					)

	def write_label(self,write_file,label_function):
		write_file.write(
			"(" + label_function + "$" + self.arg1 + ")" + "\n" 
				)

	def write_goto(self,write_file,label_function):
			write_file.write(
				"@" + label_function + "$" + self.arg1 + "\n" +
				"0;JMP" + "\n"
					)

	def write_if(self,write_file,label_function):
			write_file.write(
					"@SP" + "\n" +
					"A=M-1" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"M=M-1" + "\n" +
					"@" + label_function + "$" + self.arg1 + "\n" +
					"D;JNE" + "\n"
					)

	def write_call(self,write_file):
			global return_inc
			write_file.write(
					#push ROM return address to stack
					"@return" + str(return_inc) + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" + 
					"M=D" + "\n" + 
					#push local segment pointer to stack
					"@LCL" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" + 
					"M=D" + "\n" + 
					#push argument segment pointer to stack
					"@ARG" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" + 
					"M=D" + "\n" +
					#push this segment pointer to stack
					"@THIS" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" + 
					"M=D" + "\n" +
					#push that segment pointer to stack
					"@THAT" + "\n" +
					"D=M" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"D=A+1" + "\n" +
					"@SP" + "\n" + 
					"M=D" + "\n" +
					#set argument segment pointer for called function
					"@SP" + "\n" +
					"D=M" + "\n" +
					"@" + str(self.arg2) + "\n" +
					"D=D-A" + "\n" +
					"@5" + "\n" + 
					"D=D-A" + "\n" +
					"@ARG" + "\n" + 
					"M=D" + "\n" +
					#set local segment pointer for called function
					"@SP" + "\n" +
					"D=M" + "\n" +
					"@LCL" + "\n" + 
					"M=D" + "\n" 
					#jump to called function
					"@" + self.arg1 + "\n" +
					"0;JMP" + "\n" + 
					#create label to mark point in ROM called function should return to
					"(" + "return" + str(return_inc) + ")" + "\n" 
					)

	def write_return(self,write_file):
			write_file.write(
					#create temporary pointer to called function local segment
					"@LCL" + "\n" +
					"D=M" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" +
					#create temporary variable for return address
					"@5" + "\n" +
					"A=D-A" + "\n" +
					"D=M" + "\n" +
					"@R14" + "\n" + 
					"M=D" + "\n" +
					#reposition return value for calling function
					"@SP" + "\n" + 
					"A=M-1" + "\n" + 
					"D=M" + "\n" + 
					"@ARG" + "\n" +
					"A=M" + "\n" + 
					"M=D" + "\n" +
					#restore SP of caller
					"D=A+1" + "\n" + 
					"@SP" + "\n" + 
					"M=D" + "\n" +
					#restore LCL pointer of caller
					"@R13" + "\n" + 
					"D=M" + "\n" +
					"@4" + "\n" +
					"A=D-A" + "\n" +
					"D=M" + "\n" + 
					"@LCL" + "\n" + 
					"M=D" + "\n" +
					#restore ARG pointer of caller
					"@R13" + "\n" + 
					"D=M" + "\n" +
					"@3" + "\n" +
					"A=D-A" + "\n" +
					"D=M" + "\n" + 
					"@ARG" + "\n" + 
					"M=D" + "\n" +
					#restore THIS pointer of caller
					"@R13" + "\n" + 
					"D=M" + "\n" +
					"@2" + "\n" +
					"A=D-A" + "\n" +
					"D=M" + "\n" + 
					"@THIS" + "\n" + 
					"M=D" + "\n" + 
					#restore THAT pointer of caller
					"@R13" + "\n" + 
					"D=M" + "\n" +
					"A=D-1" + "\n" +
					"D=M" + "\n" + 
					"@THAT" + "\n" + 
					"M=D" + "\n" + 
					#jump back to calling function 
					"@R14" + "\n" +
					"A=M" + "\n" +
					"0;JMP" + "\n" 
					)

	def write_function(self,write_file):
			global function_call_inc
			write_file.write(
					#create function label
					"(" + self.arg1 + ")" + "\n" +
					#initialize variable to count down zeros to push to stack
					"@" + str(self.arg2) + "\n" +
					"D=A" + "\n" +
					"@R13" + "\n" +
					"M=D" + "\n" + 
					"@" + "function_call2_" + str(function_call_inc2) + "\n" +
					"D;JEQ" + "\n" +
					"(" + "function_call_" + str(function_call_inc) + ")" + "\n" + 
					#push 0 onto stack to initialize local segment registers
					"@0" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"@SP" + "\n" +
					"M=M+1" + "\n" +
					#decrement variable indicating number of zeros that still need to be pushed
					"@R13" + "\n" +
					"MD=M-1" + "\n" +
					#if decrement variable >0, loop back and push another 0 to stack
					"@" + "function_call_" + str(function_call_inc) + "\n" + 
					"D;JGT" + "\n"
					"(" + "function_call2_" + str(function_call_inc2) + ")" + "\n" 
					)



#EXECUTE TRANSLATION FROM VM LANGUAGE TO HACK ASSEMBLY LANGUAGE

with open(hack_file_path,'w') as assembly_file:
	function_name = "" #initialize function_name to empty string
	return_inc = 0 #initialize return incrementer variable to create unique labels for return addresses
	function_call_inc = 0 #initialize function call incrementer variable to enable looping for local segment initialization
	function_call_inc2 = 0 #initial second function call incrementer variable to make sure no zeros get pushed to stack if function has no local variables
	#bootstrap code
	assembly_file.write(
					#initialize stack pointer to RAM[256]
					"@256" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" +
					#push zero to stack 
					"@0" + "\n" +
					"D=A" + "\n" + 
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"A=A+1" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" +
					#push another zero to stack 
					"@0" + "\n" +
					"D=A" + "\n" + 
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"A=A+1" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" +
					#push another zero to stack 
					"@0" + "\n" +
					"D=A" + "\n" + 
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"A=A+1" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" +
					#push another zero to stack
					"@0" + "\n" +
					"D=A" + "\n" + 
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"A=A+1" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" +
					#push another zero to stack
					"@0" + "\n" +
					"D=A" + "\n" + 
					"@SP" + "\n" +
					"A=M" + "\n" +
					"M=D" + "\n" +
					"A=A+1" + "\n" +
					"D=A" + "\n" +
					"@SP" + "\n" +
					"M=D" + "\n" +
					#set local segment pointer for Sys.init
					"@SP" + "\n" +
					"D=M" + "\n" +
					"@LCL" + "\n" + 
					"M=D" + "\n" +
					#jump to Sys.init
					"@Sys.init" + "\n" +
					"0;JMP" + "\n"   
				)
	
	
	for i in vm_file_paths:
		with open(i,'r') as vm_file:
			last_forward_slash_loc = i.rfind("/") + 1
			file_name = i[last_forward_slash_loc:]
			for line in vm_file:
				vm_line = vm_cmd(line)
				vm_line.vm_command = vm_line.remove_comments_trailing_leading_whitespace()
				if vm_line.vm_command != "":
					COMMAND_TYPE = vm_line.command_type()
					ARG1 = vm_line.arg1()
					ARG2 = vm_line.arg2()
					parsed_vm_command = vm_cmd_to_write(COMMAND_TYPE,ARG1,ARG2)
					if COMMAND_TYPE == "C_PUSH" or COMMAND_TYPE == "C_POP":
						parsed_vm_command.write_push_pop(file_name,assembly_file)
					if COMMAND_TYPE == "C_ARITHMETIC":
						parsed_vm_command.write_arithmetic(assembly_file)
					if COMMAND_TYPE == "C_LABEL":
						parsed_vm_command.write_label(assembly_file,function_name) 
					if COMMAND_TYPE == "C_GOTO":
						parsed_vm_command.write_goto(assembly_file,function_name)
					if COMMAND_TYPE == "C_IF":
						parsed_vm_command.write_if(assembly_file,function_name)
					if COMMAND_TYPE == "C_CALL":
						parsed_vm_command.write_call(assembly_file)
						return_inc += 1
					if COMMAND_TYPE == "C_RETURN":
						parsed_vm_command.write_return(assembly_file)
					if COMMAND_TYPE == "C_FUNCTION":
						function_name = parsed_vm_command.arg1
						parsed_vm_command.write_function(assembly_file)
						function_call_inc += 1
						function_call_inc2 += 1





					
					