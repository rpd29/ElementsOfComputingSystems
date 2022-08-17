# This document contains the Python source code for the assembler specified in Chapter 6. 

#Import sys module and assign assembly file file path to variable

import sys
assembly_file_path = sys.argv[1]


#PARSER MODULE CLASS

class assembly_cmd:
	def __init__(self,assembly_command):
		self.assembly_command = assembly_command

	def remove_spaces_comments_newline(self):
		self.assembly_command.replace(" ","")
		comm_loc = self.assembly_command.find("//")
		if comm_loc == 0:
			self.assembly_command = ""
		elif comm_loc != -1:
			self.assembly_command = self.assembly_command[:comm_loc]
		return (self.assembly_command.rstrip()).lstrip()

	def command_type(self):
		if "@" in self.assembly_command:
			return "A_COMMAND"
		elif "=" in self.assembly_command or ";" in self.assembly_command:
			return "C_COMMAND"
		elif "(" in self.assembly_command and ")" in self.assembly_command:
			return "L_COMMAND"

	def symbol(self):
		if self.command_type() == "A_COMMAND":
			at_loc = self.assembly_command.find("@") + 1
			return self.assembly_command[at_loc:]
		elif self.command_type() == "L_COMMAND":
			par_open = self.assembly_command.find("(") + 1
			par_close = self.assembly_command.find(")")
			return self.assembly_command[par_open:par_close]

	def dest(self):
		if self.command_type() == "C_COMMAND":
			eq_loc = self.assembly_command.find("=")
			if eq_loc != -1:
				return self.assembly_command[:eq_loc]
			else:
				return ""

	def comp(self):
		if self.command_type() == "C_COMMAND":
			eq_loc = self.assembly_command.find("=") + 1
			semicol_loc = self.assembly_command.find(";")
			if eq_loc != 0 and semicol_loc != -1: 
				return self.assembly_command[eq_loc:semicol_loc]
			elif eq_loc != 0 and semicol_loc == -1:
				return self.assembly_command[eq_loc:]
			elif eq_loc == 0 and semicol_loc != -1:
				return self.assembly_command[:semicol_loc]

	def jump(self):
		if self.command_type() == "C_COMMAND":
			semicol_loc = self.assembly_command.find(";") + 1
			if semicol_loc != 0:
				return self.assembly_command[semicol_loc:]


#CODE MODULE CLASS

class parsed_assembly_command:
	def __init__(self,dest,comp,jump):
		self.dest = dest
		self.comp = comp
		self.jump = jump

	def dest_bin(self):
		first_dig = "0"
		second_dig = "0"
		third_dig = "0"
		if self.dest.find("A") != -1:
			first_dig = "1"
		if self.dest.find("D") != -1:
			second_dig = "1"
		if self.dest.find("M") != -1:
			third_dig = "1"
		return first_dig + second_dig + third_dig

	def comp_bin(self):
		comp_dict = {
			"0": "0101010",
			"1": "0111111",
			"-1": "0111010",
			"D": "0001100",
			"A": "0110000",
			"M": "1110000",
			"!D": "0001101",
			"!A": "0110001",
			"!M": "1110001",
			"-D": "0001111",
			"-A": "0110011",
			"-M": "1110011",
			"D+1": "0011111",
			"A+1": "0110111",
			"M+1": "1110111",
			"D-1": "0001110",
			"A-1": "0110010",
			"M-1": "1110010",
			"D+A": "0000010",
			"D+M": "1000010",
			"D-A": "0010011",
			"D-M": "1010011",
			"A-D": "0000111",
			"M-D": "1000111",
			"D&A": "0000000",
			"D&M": "1000000",
			"D|A": "0010101",
			"D|M": "1010101"
		}

		return comp_dict.get(self.comp)

	def jump_bin(self):
		jump_dict = {
			None: "000",
			"JGT": "001",
			"JEQ": "010",
			"JGE": "011",
			"JLT": "100",
			"JNE": "101",
			"JLE": "110",
			"JMP": "111"
		}

		return jump_dict.get(self.jump)

#START BUILDING SYMBOL TABLE WITH PREDEFINED SYMBOLS AND LABELS

symbol_table = {
			"SP": 0,
			"LCL": 1,
			"ARG": 2,
			"THIS": 3,
			"THAT": 4,
			"R0": 0,
			"R1": 1,
			"R2": 2,
			"R3": 3,
			"R4": 4,
			"R5": 5,
			"R6": 6,
			"R7": 7,
			"R8": 8,
			"R9": 9,
			"R10": 10,
			"R11": 11,
			"R12": 12,
			"R13": 13,
			"R14": 14,
			"R15": 15,
			"SCREEN": 16384, 
			"KBD": 24576
		}



with open(assembly_file_path,'r') as assembly_file1:
	ROM_address = 0
	for line1 in assembly_file1:
		assembly_line1 = assembly_cmd(line1)
		assembly_line1.assembly_command = assembly_line1.remove_spaces_comments_newline()
		cmd_type1 = assembly_line1.command_type()
		if cmd_type1 == "L_COMMAND":
			symbol1 = assembly_line1.symbol()
			if symbol_table.get(symbol1) == None:
				symbol_table.update({symbol1: ROM_address})
		if cmd_type1 != None and cmd_type != "L_COMMAND":
			ROM_address += 1


# EXECUTE TRANSLATION FROM ASSEMBLY TO BINARY

with open(assembly_file_path,'r') as assembly_file, open(assembly_file_path[:-4] + '1.hack','w') as binary_file:
	RAM_address = 16
	for line in assembly_file:
		assembly_line = assembly_cmd(line)
		assembly_line.assembly_command = assembly_line.remove_spaces_comments_newline()
		if assembly_line.assembly_command != "":
			cmd_type = assembly_line.command_type()
			if cmd_type == "A_COMMAND":
				at_argument = assembly_line.symbol()
				if at_argument.isdigit() == False: 
					if symbol_table.get(at_argument) != None:
						binary_value = str(bin(symbol_table.get(at_argument)))[2:]
					else:
						symbol_table.update({at_argument: RAM_address})
						binary_value = str(bin(symbol_table.get(at_argument)))[2:]
						RAM_address += 1
				else:
					binary_value = str(bin(int(at_argument)))[2:]
				zeros_to_add = 15 - len(binary_value)
				binary_value_all_digits = "0"*zeros_to_add + binary_value
				binary_command = "0" + binary_value_all_digits
				binary_file.write(binary_command + '\n')
			if cmd_type == "C_COMMAND":
				destination = assembly_line.dest()
				computation = assembly_line.comp()
				print computation
				jump = assembly_line.jump()
				parsed_assembly = parsed_assembly_command(destination,computation,jump)
				destination_bin = str(parsed_assembly.dest_bin())
				computation_bin = str(parsed_assembly.comp_bin())
				jump_bin = str(parsed_assembly.jump_bin())
				binary_command = "111" + computation_bin + destination_bin + jump_bin
				binary_file.write(binary_command + '\n')






		






