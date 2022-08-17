#This document contains the Python code implementing the Jack compiler specified in Chapters 10 and 11. 

#Import sys, regex, and XML parser modules for use by compiler
import sys, re
import xml.etree.ElementTree as ET


#Tokenizer module. Collection of functions used to tokenize a Jack program file.

class JackTokenizer:

	symbols = ["{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~"]

	keywords = ["class","method","function","constructor","int","boolean","char","void","var","static","field","let","do","if","else","while","return","true","false","null","this"]

	#Determines whether end of Jack file has been reached
	@staticmethod
	def hasMoreTokens(next_char):
		if next_char != "":
			return True
		else:
			return False

	#Returns type of current token. Argument is a string starting from current file pointer that is long enough to determine token type.
	@staticmethod
	def tokenType(token_classifier_string):
		if token_classifier_string[0] in JackTokenizer.symbols:
			return "symbol"
		elif token_classifier_string[0] == "\"":
			return "stringConstant"
		elif token_classifier_string[0].isdigit() == True:
			return "integerConstant"
		elif any(token_classifier_string.find(x) == 0 for x in JackTokenizer.keywords):
			keyword = ""
			for i in JackTokenizer.keywords:
				if token_classifier_string.find(i) == 0:
					keyword = i
			keyword_length = len(keyword)
			if (token_classifier_string[keyword_length] in JackTokenizer.symbols) or (token_classifier_string[keyword_length] == " "):
				return "keyword"
			else:
				return "identifier"
		elif token_classifier_string[0] != " ":
			return "identifier"

	#Returns the keyword which is the current token
	@staticmethod
	def keyWord(token_classifier_string):
		for i in JackTokenizer.keywords:
			if token_classifier_string.find(i) == 0:
				return i 

	#Returns the symbol which is the current token
	@staticmethod
	def symbol(token_classifier_string): 
		if token_classifier_string[0] == "<":
			return "&lt;"
		elif token_classifier_string[0] == ">":
			return "&gt;"
		elif token_classifier_string[0] == "\"":
			return "&quot;"
		elif token_classifier_string[0] == "&":
			return "&amp;"
		else:
			return token_classifier_string[0]

	#Returns the integer value which is the current token
	@staticmethod
	def intVal(file):
		integer = True
		int_val = ""
		while integer == True:
			int_val = int_val + file.read(1)
			integer = file.read(1).isdigit()
			file.seek(-1,1)
		return int_val

	#Returns the string value which is the current token
	@staticmethod
	def stringVal(file):
		still_string = -1
		file.seek(1,1)
		string_val = ""
		while still_string == -1:
			string_val = string_val + file.read(1)
			still_string = file.read(1).find("\"")
			file.seek(-1,1)
		return string_val

	#Returns identifier value which is the current token
	@staticmethod
	def identifier(file): 
		still_identifier = True
		identifier_val = ""
		while still_identifier == True:
			identifier_val = identifier_val + file.read(1)
			current_loc = file.tell()
			identifier_test_string = file.read(1)
			if JackTokenizer.tokenType(identifier_test_string) == "symbol" or identifier_test_string == " ": 
				still_identifier = False
			else: 
				still_identifier = True 
			file.seek(current_loc,0) 
		return identifier_val



#Symbol table module. Collection of functions used to build and query symbol table during compilation.

class SymbolTable:
	
	def __init__(self,class_scope_table={},subroutine_scope_table={}):
		self.class_scope_table = class_scope_table
		self.subroutine_scope_table = subroutine_scope_table
	
	#Adds a new symbol to symbol table
	def Define(self,name,var_type,kind):
		
		#If variable has a class scope, append variable to class symbol table 
		if kind=="static" or kind =="field":
			self.class_scope_table[name] = {"type": var_type, "kind": kind, "index": self.VarCount(kind,"class")}

		#If variable has a subroutine scope, append variable to subroutine symbol table 
		elif kind == "argument" or kind == "local":
			self.subroutine_scope_table[name] = {"type": var_type, "kind": kind, "index": self.VarCount(kind,"subroutine")}

	#Adds one to suboroutine argument indices in a symbol needed (needed because for methods object pointer is first argument at VM level)
	def IncrementArgumentIndices(self):
		for key in self.subroutine_scope_table:
			if self.subroutine_scope_table[key]["kind"] == "argument":
				self.subroutine_scope_table[key]["index"] = self.subroutine_scope_table[key]["index"] + 1
	
	#Returns number of variables of a particular kind in current scope (class or subroutine)
	def VarCount(self,kind,scope):

		#Count number of variables of with kind kind in class_scope table and return value
		if scope == "class":
			class_scope_count = 0
			for i in self.class_scope_table:
				if self.class_scope_table[i]["kind"] == kind:
					class_scope_count = class_scope_count + 1
			return class_scope_count 

		#Count number of variables of with kind kind in subroutine_scope table and return value
		elif scope == "subroutine":
			subroutine_scope_count = 0
			for i in self.subroutine_scope_table:
				if self.subroutine_scope_table[i]["kind"] == kind:
					subroutine_scope_count = subroutine_scope_count + 1
			return subroutine_scope_count

	
	#Returns kind of the named identifier in the current scope (class or subroutine)
	def KindOf(self,name,scope):

		#Return kind of the named identifier if current scope is class
		if scope ==  "class":
			if self.class_scope_table.get(name,"not_in_table") != "not_in_table":
				return self.class_scope_table[name]["kind"]
			else:
				return "NONE"

		#Return kind of the named identifier if current scope is subroutine
		if scope == "subroutine":
			if self.subroutine_scope_table.get(name,"not_in_table") != "not_in_table":
				return self.subroutine_scope_table[name]["kind"]
			else:
				return "NONE"


	#Returns type of the named identifier in current scope (class or subroutine)
	def TypeOf(self,name,scope):

		#Return type of the named identifier if current scope is class
		if scope ==  "class":
			if self.class_scope_table.get(name,"not_in_table") != "not_in_table":
				return self.class_scope_table[name]["type"]
			else:
				return "NONE"

		#Return type of the named identifier if current scope is subroutine
		if scope == "subroutine":
			if self.subroutine_scope_table.get(name,"not_in_table") != "not_in_table":
				return self.subroutine_scope_table[name]["type"]
			else:
				return "NONE"


	#Returns Index of named identifier in current scope (class or subroutine)
	def IndexOf(self,name,scope):

		#Return index of the named identifier if current scope is class
		if scope ==  "class":
			if self.class_scope_table.get(name,"not_in_table") != "not_in_table":
				return self.class_scope_table[name]["index"]
			else:
				return "NONE"

		#Return index of the named identifier if current scope is subroutine
		if scope == "subroutine":
			if self.subroutine_scope_table.get(name,"not_in_table") != "not_in_table":
				return self.subroutine_scope_table[name]["index"]
			else:
				return "NONE"


#VM writer module. Collection of functions that can be used to write VM code to output VM files.
class VMWriter:

	#Function for writing push VM commands
	@staticmethod
	def writePush(segment,index):
		return "push " + segment + " " + str(index) + "\n"

	#Function for writing pop VM commands
	@staticmethod
	def writePop(segment,index):
		return "pop " + segment + " " + str(index) + "\n"

	#Function for writing arithmetic VM commands
	@staticmethod
	def writeArithmetic(command):
		return command + "\n"

	#Function for writing VM labels
	@staticmethod
	def writeLabel(label):
		return "label " + label + "\n"

	#Function for writing goto VM commands
	@staticmethod
	def writeGoto(label):
		return "goto " + label + "\n"

	#Function for writing if-goto VM commands
	@staticmethod
	def writeIf(label):
		return "if-goto " + label + "\n"

	#Function for writing function-calling VM commands
	@staticmethod
	def writeCall(name,nArgs):
		return "call " + name + " " + str(nArgs) + "\n"

	#Function for writing function definition VM commands
	@staticmethod
	def writeFunction(name,nLocals):
		return "function " + name + " " + str(nLocals) + "\n"

	#Function for writing return VM commands
	@staticmethod
	def writeReturn():
		return "return" + "\n"



#Compilation engine module. Collection of functions used to recursively parse syntactic structure of Jack program files and output compiled Jack virtual machine code. 
class CompilationEngine:

	def __init__(self,tokenized_file,vm_file):
		self.tokenized_file = tokenized_file
		self.vm_file = vm_file

	symbol_table = SymbolTable() #Initialize a symbol table class variable for use by all functions in class

	class_name = "" #Initialize class variable used to hold class name for each Jack file being compiled

	label_count = 0 #Initialize variable used to create unique labels for use for branching/control flow VM commands

	#Parses and compiles a tokenized Jack program file (each class is a separate file according to rules of Jack language)
	def CompileClass(self):
		
		#Clear class and subroutine scope symbol tables when beginning compilation of a new class
		CompilationEngine.symbol_table.class_scope_table = {} 
		CompilationEngine.symbol_table.subroutine_scope_table = {}  

		#measure length of xml file (i.e. number of lines in XML file) to determine when "while" loop below should stop
		self.tokenized_file.seek(0)
		tree = ET.parse(self.tokenized_file)
		root = tree.getroot()
		max_root_index = len(root) 
		
		#create index variable to use to move through tokenized Jack program file and initiaze it to zero
		root_index = 0

		#go through tokens in tokenized Jack program file and parse syntactic structure, outputting XML file with parsed syntactic structure
		while root_index<max_root_index:
			current_token = root[root_index]
			#if at beginning of document, assign class name to a variable for use in naming VM functions
			if current_token.tag == "keyword" and current_token.text == "class":
				CompilationEngine.class_name = root[root_index+1].text
				root_index = root_index + 3 #Advance beyond "class", name of class, and "{" tokens
			#if current_token indicates class variable declaration, call CompileClassVarDec, which parses and compiles variable declaration and returns updated root_index
			elif current_token.tag == "keyword" and (current_token.text == "static" or current_token.text == "field"):
				root_index = self.CompileClassVarDec(root,root_index) 
			#if current_token indicates subroutine, call CompileSubroutine, which parses and compiles subroutine and returns updated root_index
			elif current_token.tag == "keyword" and (current_token.text == "constructor" or current_token.text == "function" or current_token.text == "method"):
				root_index = self.CompileSubroutine(root,root_index) 
			#if reach end of tokenized Jack program file, compilation of file is complete
			elif current_token.tag == "symbol" and current_token.text == "}":
				break 
		

	def CompileClassVarDec(self,root,root_index):

		var_kind = root[root_index].text #assign "static" or "field" (as the case may be) to a variable
		root_index = root_index + 1
		var_type = root[root_index].text #assign variable type to a variable
		root_index = root_index + 1

		#write variable types and names to parsed_file
		more_vars = True
		while more_vars == True:
			var_name = root[root_index].text
			CompilationEngine.symbol_table.Define(var_name,var_type,var_kind) #Add variable to class scope symbol table
			root_index = root_index+1
			if root[root_index].text == ",":
				root_index = root_index+1 #Skip over comma and continue adding variables to symbol table if there are additional variables 
			else:
				more_vars = False #End loop if there aren't any other variables

		#increment root_index to skip over semicolon at end of class variable declaration and return value to calling CompileClass function
		root_index = root_index + 1 
		return root_index

	
	def CompileSubroutine(self,root,root_index):

		#Clear subroutine symbol table at beginning of new subroutine 
		CompilationEngine.symbol_table.subroutine_scope_table = {}  
		
		#Record type of subroutine, return value type, and subroutine name for later use
		subroutine_type = root[root_index].text
		root_index = root_index + 1
		return_value_type = root[root_index].text 
		root_index = root_index + 1
		subroutine_name = root[root_index].text
		root_index = root_index + 2 #skip over parenthesis before parameter list		

		#If there are any parameters, call CompileParameterList, which compiles the parameter list (essentially just adding each argument to subroutine symbol table), and returns root_index value that CompileSubroutine should continue compiling from
		root_index = self.CompileParameterList(root,root_index,subroutine_type)
		if subroutine_type == "method": #If subroutine is a method, add 1 to all argument indices, since at VM level first argument will be object method is called on
			CompilationEngine.symbol_table.IncrementArgumentIndices()

		#If there are any variable declarations, call CompileVarDec, which compiles the variable declarations (essentially just adding each declared local variable to subroutine symbolt table) and returns root_index value that CompileSubroutine should continue compiling from
		while root[root_index].text == "var":
			root_index = self.CompileVarDec(root,root_index)

		#Write function name and number of local variables to vm_file
		num_local_vars = CompilationEngine.symbol_table.VarCount("local","subroutine")
		self.vm_file.write(VMWriter.writeFunction(CompilationEngine.class_name + "." + subroutine_name, num_local_vars))

		#If subroutine is a method or a constructor, emit code that points "this" to base address of object
		if subroutine_type == "method":
			self.vm_file.write(VMWriter.writePush("argument",0)) #Push pointer to object base address to top of stack
			self.vm_file.write(VMWriter.writePop("pointer",0)) #Store pointer to object base address in pointer 0 so that "this" refers to base address of object
		elif subroutine_type == "constructor":
			self.vm_file.write(VMWriter.writePush("constant",CompilationEngine.symbol_table.VarCount("field","class"))) #Push number of fields in object being constructed to top of stack
			self.vm_file.write(VMWriter.writeCall("Memory.alloc",1)) #Call Memory.alloc, which should push base address of memory segment of sufficient size to store object to top of stack
			self.vm_file.write(VMWriter.writePop("pointer",0)) #Store pointer to base address of object being created in pointer 0 so that "this" refers to base address of object

		#If there are any statements, call CompileStatements, which compiles the statements and returns root_index value that CompileSubroutine should continue compiling from
		statement_initial_tokens = ["let","if","while","do","return"]
		if root[root_index].text in statement_initial_tokens:
			root_index = self.CompileStatements(root,root_index)

		#Increment root_index (need to skip over subroutine closing brace) and return value to calling CompileClass function
		root_index = root_index + 1 
		return root_index


	def CompileParameterList(self,root,root_index,subroutine_type):

			#Add arguments in parameter list to subroutine symbol table 
			continue_param_compilation = False
			if root[root_index].text != ")": #Determine whether there are any parameters/arguments to compile
				continue_param_compilation = True
			else: #If there aren't any parameters/arguments to compile, skip over parameter list closing parenthesis and subroutine body opening brace
				root_index = root_index + 2
			
			while continue_param_compilation == True:
				var_type = root[root_index].text #Assign variable type to a variable
				root_index = root_index + 1
				var_name = root[root_index].text #Assign variable name to a variable
				root_index = root_index + 1
				CompilationEngine.symbol_table.Define(var_name,var_type,"argument") #Add argument to subroutine symbol table

				if root[root_index].text != ",": #Determine if end of parameter list has been reached
					continue_param_compilation = False
					root_index = root_index + 2 #Skip over parenthesis at end of parameter list and brace at beginning of subroutine body
				else:
					root_index = root_index + 1 #Skip over comma separating arguments

			#Return root_index value to calling function
			return root_index


	def CompileVarDec(self,root,root_index):

		#Assign variable type to a local variable:
		root_index = root_index + 1 #Skip over "var"
		var_type = root[root_index].text
		root_index = root_index + 1

		#Add variables to subroutine symbol table:
		more_vars = True
		while more_vars == True:
			var_name = root[root_index].text
			CompilationEngine.symbol_table.Define(var_name,var_type,"local")
			root_index = root_index + 1
			if root[root_index].text != ",": #Determine whether there are any other variables in variable declaration
				more_vars = False
				root_index = root_index + 1 #Skip over semicolon at end of variable declaration
			else:
				root_index = root_index + 1 #Skip over comma separating variables in variable declaration

		#Return root_index to calling function
		return root_index 


	def CompileStatements(self,root,root_index):

		#Loop to parse and compile each statement in statement sequence
		continue_statement_compilation = True
		while continue_statement_compilation == True:
			
			#Call relevant function to parse and compile type of statement under consideration
			if root[root_index].text == "let":
				root_index = self.CompileLet(root,root_index)
			elif root[root_index].text == "if":
				root_index = self.CompileIf(root,root_index)
			elif root[root_index].text == "while":
				root_index = self.CompileWhile(root,root_index)
			elif root[root_index].text == "do":
				root_index = self.CompileDo(root,root_index)
			elif root[root_index].text == "return":
				root_index = self.CompileReturn(root,root_index)

			#Check if next token indicates another statement that needs to be compiled
			if root[root_index].text in ["let","if","while","do","return"]:
				continue_statement_compilation = True
			else:
				continue_statement_compilation = False

		#Return updated root_index value to calling function
		return root_index


	#Parses and compiles a "let" statement

	def CompileLet(self,root,root_index):

		root_index = root_index + 1 #Skip over "let"
		
		#Store variable name on left-hand side of equality in a local variable
		var_name = root[root_index].text

		#Store variable scope, kind, and index in local variables
		if CompilationEngine.symbol_table.KindOf(var_name,"subroutine") != "NONE":
			var_scope = "subroutine"
			var_kind = CompilationEngine.symbol_table.KindOf(var_name,"subroutine")
			var_index = CompilationEngine.symbol_table.IndexOf(var_name,"subroutine")
			var_type = CompilationEngine.symbol_table.TypeOf(var_name,"subroutine")
	
		else:
			var_scope = "class"
			var_kind = CompilationEngine.symbol_table.KindOf(var_name,"class")
			var_index = CompilationEngine.symbol_table.IndexOf(var_name,"class")
			var_type = CompilationEngine.symbol_table.TypeOf(var_name,"class")

		root_index = root_index + 1
		
		#Execute parsing and compilation of let statement
		if root[root_index].text == "[": #Code to execute to parse and compile an assignment to an array element
			root_index = root_index + 1 #Skip over opening bracket 
			root_index = self.CompileExpression(root,root_index) #Parse and compile expression in brackets. The output VM code should result in value of expression being pushed to top of stack.
			root_index = root_index + 2 #Skip over closing bracket and "=" symbol
			if var_kind == "field": #Code to push array pointer to top of stack if variable is a field of "this" object (i.e. object current subroutine was called on)
				self.vm_file.write(VMWriter.writePush("this",var_index))
			if var_kind != "field": #Code to push array pointer to top of stack if variable isn't a field of "this" object
				self.vm_file.write(VMWriter.writePush(var_kind,var_index)) 
			self.vm_file.write(VMWriter.writeArithmetic("add")) #Add array element index to array pointer and leave value on top of stack
			self.vm_file.write(VMWriter.writePop("temp",1)) #Store address of array element in the temp segment of VM memory (need to keep pointer 1 available in case there are arrays on right hand side of "=")
			root_index = self.CompileExpression(root,root_index) #Parse and compile expression on right-hand side of equal sign. This should result in value of expression being pushed to top of stack.
			self.vm_file.write(VMWriter.writePush("temp",1)) #Push address of array element to top of stack
			self.vm_file.write(VMWriter.writePop("pointer",1)) #Pop address of array element and store in pointer segment of VM memory
			self.vm_file.write(VMWriter.writePop("that",0)) #Store value of expression on right-hand-side of "=" in array element
			

		else: #code that parses and compiles let statement if variable being assigned isn't an array element 
			root_index = root_index + 1	#Skip over "=" symbol	
			root_index = self.CompileExpression(root,root_index) #Parse and compile expression on right-hand side of equal sign. This should result in value of expression being pushed to top of stack.
			if var_kind == "field": #Code to pop value of expression on right hand side of "=" to the appropriate register if variable is a field of current object
				self.vm_file.write(VMWriter.writePop("this",var_index))
			else: #Code to pop value of expression on right hand side of "=" to the appropriate register if variable isn't a field of current object
				self.vm_file.write(VMWriter.writePop(var_kind,var_index)) #Store value in appropriate VM register 


		#Skip over semicolon at end of let statement
		root_index = root_index + 1

		#Return value of root_index to calling function
		return root_index


	#Parses and compiles an if statement
	def CompileIf(self,root,root_index):

		root_index = root_index + 2 #Skip over "if" and opening parenthesis before if condition
		root_index = self.CompileExpression(root,root_index) #Parse and compile if condition expression. VM code emitted should result in "true" (-1) or "false" (0) being pushed to top of the stack.
		
		local_label_count = CompilationEngine.label_count #Create local_label_count variable 
		CompilationEngine.label_count = CompilationEngine.label_count + 1 #Increment class label_count variable (if there are "if" or "while" statements within this "if" statement, want them to have a different label_count value to ensure unique label naming)

		self.vm_file.write(VMWriter.writeIf("condition-true" + str(local_label_count))) #Write VM code indicating where to continue execution from when "if" condition is true
		self.vm_file.write(VMWriter.writeGoto("condition-false" + str(local_label_count))) #Write VM code indicating where to continue execution from when "if" condition is false
		
		#Write VM code to execute when "if" condition is true
		self.vm_file.write(VMWriter.writeLabel("condition-true" + str(local_label_count))) #Write VM label to jump to when "if" condition is true
		root_index = root_index + 2 #Skip over parenthesis after end of if condition and brace at beginning of statements to execute if condition true
		root_index = self.CompileStatements(root,root_index) #Parse and compile statements to execute if condition satisfied
		root_index = root_index + 1 #Skip over closing brace at end of statements
		self.vm_file.write(VMWriter.writeGoto("if-statement-end" + str(local_label_count))) #Write VM code indicating where to continue execution from after executing statements
		
		self.vm_file.write(VMWriter.writeLabel("condition-false" + str(local_label_count))) #Write label to jump to when "if" condition isn't true
		
		#Write VM code to execute when "if" condition is false and there is an "else" component to "if" statement
		if root[root_index].text == "else": 
			root_index = root_index + 2 #Skip over "else" and opening brace before statements
			root_index = self.CompileStatements(root,root_index) #Parse and compile statements to execute if condition not satisfied
			root_index = root_index + 1 #Skip over closing brace at end of statements
		
		self.vm_file.write(VMWriter.writeLabel("if-statement-end" + str(local_label_count))) #Write label to jump to after executing statements when "if" condition is true
		
		#Return value of root_index to calling function
		return root_index


	#Parse and compile a while statement
	def CompileWhile(self,root,root_index):

		local_label_count = CompilationEngine.label_count #Create local_label_count variable 
		CompilationEngine.label_count = CompilationEngine.label_count + 1 #Increment class label_count variable (if there are "if" or "while" statements within this "if" statement, want them to have a different label_count value to ensure unique label naming)

		root_index = root_index + 2 #Skip over "while" and opening parenthesis enclosing "while" condition
		self.vm_file.write(VMWriter.writeLabel("start-of-while" + str(local_label_count))) #Write VM label to loop back to each time "while" loop statements are executed
		root_index = self.CompileExpression(root,root_index) #Parse and compile condition expression
		self.vm_file.write(VMWriter.writeIf("condition-true" + str(local_label_count))) #Write VM code indicating where to continue execution from when "while" condition is true
		self.vm_file.write(VMWriter.writeGoto("condition-false" + str(local_label_count))) #Write VM code indicating where to continue execution from when "while" condition is false
		root_index = root_index + 1 #Skip over parenthesis at end of "while" condition

		#Write VM code to execute when "while" condition is true
		self.vm_file.write(VMWriter.writeLabel("condition-true" + str(local_label_count))) #Write VM label indicating where to continue executing from when "while" condition is true
		root_index = root_index + 1 #Skip over brace at beginning of statements to execute when "while" condition true
		root_index = self.CompileStatements(root,root_index) #Parse and compile statements to execute while condition satisfied
		self.vm_file.write(VMWriter.writeGoto("start-of-while" + str(local_label_count))) #Write VM code to loop back to check "while" condition
		root_index = root_index + 1 #Skip over brace at end of statements

		#Write label to jump to when "while" statement is false 
		self.vm_file.write(VMWriter.writeLabel("condition-false" + str(local_label_count)))
		
		#Return value of root_index to calling function
		return root_index
	
	
	#Parse and compile a "do" statement

	def CompileDo(self,root,root_index):

		root_index = root_index + 1 #Skip over "do"
		root_index = self.CompileTerm(root,root_index) #Compile subroutine call, which should result in returned value being pushed top of stack
		self.vm_file.write(VMWriter.writePop("temp",0)) #Pop returned default value from subroutine call off of stack to get rid of it
		root_index = root_index + 1 #Skip over semicolon at end of "do" statement
		return root_index

	#Parse and compile a return statement
	def CompileReturn(self,root,root_index):

		root_index = root_index + 1 #Skip over "return"
		
		#If return statement includes an expression, parse and compile it, which should emit VM code that results in return value being left on top of stack
		if root[root_index].text != ";":
			root_index = self.CompileExpression(root,root_index) 
		
		#If return statement doesn't include an expression, push default return value (which will be ignored by calling function) 0 to top of stack
		elif root[root_index].text == ";":
			self.vm_file.write(VMWriter.writePush("constant",0))

		#Return 
		self.vm_file.write(VMWriter.writeReturn())
		root_index = root_index + 1 #Skip over semicolon at end of return statement

		#Return value of root_index to calling function
		return root_index


	#Parses and compiles an expression
	def CompileExpression(self,root,root_index):
			
		still_expression = True
		while still_expression == True:
			root_index = self.CompileTerm(root,root_index) #Parse and compile term, which should push value of term to top of stack
			if root[root_index].text in ["+","-","*","/","&","|","<",">","="]: #Code to execute if expression includes any operators
				operator = root[root_index].text
				
				#First parse and compile term to right of operator, which should result in value of this term being pushed to top of stack, then call operator
				if operator == "+": 
					root_index = self.CompileTerm(root,root_index+1) 
					self.vm_file.write(VMWriter.writeArithmetic("add"))
				elif operator == "-": 
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeArithmetic("sub"))
				elif operator == "=": 
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeArithmetic("eq"))
				elif operator == ">": 
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeArithmetic("gt"))
				elif operator == "<": 
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeArithmetic("lt"))
				elif operator == "&": 
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeArithmetic("and"))
				elif operator == "|": 
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeArithmetic("or"))
				elif operator == "*":
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeCall("Math.multiply",2))
				elif operator == "/":
					root_index = self.CompileTerm(root,root_index+1)
					self.vm_file.write(VMWriter.writeCall("Math.divide",2))

			else:
				still_expression = False

		#Return value of root_index to calling function
		return root_index


	#Parse and compile a term
	def CompileTerm(self,root,root_index):
		
		if root[root_index].tag == "integerConstant": #Compile an integer
			self.vm_file.write(VMWriter.writePush("constant",int(root[root_index].text))) #Push integer constant to top of stack
			root_index = root_index + 1
		
		elif root[root_index].tag == "stringConstant": #Compile a string constant, which should leave a pointer to base address of Unicode representation of string constant at top of stack
			string_length = len(root[root_index].text) #Assign length of string constant to a local variable
			self.vm_file.write(VMWriter.writePush("constant",string_length)) #Push length of string constant to stack, 
			self.vm_file.write(VMWriter.writeCall("String.new",1)) #Call String.new OS function to create new string of designated length, which should return base address for new string			
			for i in root[root_index].text: #Append each of the characters in the string constant to the string in memory
				self.vm_file.write(VMWriter.writePush("constant",ord(i))) #Push Unicode representation of character to top of stack
				self.vm_file.write(VMWriter.writeCall("String.appendChar",2)) #Call String.append OS function to append Unicode character to array in memory representing string constant
			root_index = root_index + 1		

		elif root[root_index].tag == "keyword": #Compile a keyword constant
			
			if root[root_index].text == "true": #Compile "true"
				self.vm_file.write(VMWriter.writePush("constant",0)) #Push 0 (i.e. "false") to top of stack
				self.vm_file.write(VMWriter.writeArithmetic("not")) #"Not" the "false" on top of stack to get "true" on top of stack
			
			elif root[root_index].text == "false": #Compile "false"
				self.vm_file.write(VMWriter.writePush("constant",0)) #Push zero (which represents "false" or "null") to top of stack
			
			elif root[root_index].text == "this": #Compile "this"
				self.vm_file.write(VMWriter.writePush("pointer",0)) #Push pointer to "this" object to top of stack
			
			elif root[root_index].text == "null": #Compile "null"
				self.vm_file.write(VMWriter.writePush("constant",0)) #Push zero (which stands for "false" or "null") to top of stack
			
			root_index = root_index + 1
		
		elif root[root_index].tag == "identifier":
			if root[root_index + 1].text in [".","("]: #Parse and compile a subroutine call	

				#Assign subroutine name and potentially also object or class identifier to a local variable
				identifier = root[root_index].text #Assign subroutine name (if calling a method within another method on some object) or class name (if calling a function or constructor) or object variable name (if calling a method from another class or a method within class but not on "this" object of calling function) to a local variable
				root_index = root_index + 1
				if root[root_index].text == ".": #If subroutine call involves a class or variable name, add "." and subroutine name to local variable
					identifier = identifier + root[root_index].text #Add "." to identifier
					root_index = root_index + 1
					identifier = identifier + root[root_index].text #Add subroutine name to identifier
					root_index = root_index + 1
				
				#Emit VM code that pushes arguments of called function to top of stack
				root_index = root_index + 1 #Skip over opening parenthesis in expression list
				nArgs = 0 #Initialize variable to count number of arguments
				period_index = identifier.find(".")
				
				if period_index == -1: #If subroutine called is a method called from within a method and is called on same object as calling method, then push pointer 0 (a pointer to the base address of the address of the object calling method was called on) to top of stack (i.e. it will be first argument of called function)
					nArgs = 1 #Increment nArgs to add object method is called on to total number of arguments
					self.vm_file.write(VMWriter.writePush("pointer",0))
					identifier = CompilationEngine.class_name + "." + identifier #Rename identifier so that it is in form class.function for VM code writing

				if period_index != -1: #If subroutine called is a method called on an object other than object calling method was called on, then locate object in symbol_table and push pointer to object to top of stack so it is first argument of called method
					string_before_period = identifier[0:period_index]
					string_after_period = identifier[period_index + 1:]
					if CompilationEngine.symbol_table.KindOf(string_before_period,"subroutine") != "NONE": #Code to execute if object is in subroutine scope
						nArgs = 1 #Increment nArgs to add object method is called on to total number of arguments
						object_kind = CompilationEngine.symbol_table.KindOf(string_before_period,"subroutine")
						object_index = CompilationEngine.symbol_table.IndexOf(string_before_period,"subroutine")
						self.vm_file.write(VMWriter.writePush(object_kind,object_index))
						identifier = CompilationEngine.symbol_table.TypeOf(string_before_period,"subroutine") + "." + string_after_period #Rename identifier so that it is in form class.function for VM code writing
					elif CompilationEngine.symbol_table.KindOf(string_before_period,"class") != "NONE": #Code to execute if object not in subroutine scope
						nArgs = 1 #Increment nArgs to add object method is called on to total number of arguments
						object_kind = CompilationEngine.symbol_table.KindOf(string_before_period,"class")
						object_index = CompilationEngine.symbol_table.IndexOf(string_before_period,"class")
						if object_kind == "field": #Code to execute if method called on a field of "this" object
							self.vm_file.write(VMWriter.writePush("this",object_index)) #Pushes value of field to top of stack
						else: #Code to execute if method called on something other than field of "this" object
							self.vm_file.write(VMWriter.writePush(object_kind,object_index))
						identifier = CompilationEngine.symbol_table.TypeOf(string_before_period,"class") + "." + string_after_period #Rename identifier so that it is in form class.function for VM code writing

				nArgs_and_root_index = self.CompileExpressionList(root,root_index) #Parse and compile expression list within subroutine call, which should push subroutine arguments to top of stack
				
				#Call function 
				nArgs = nArgs + nArgs_and_root_index["nArgs"]
				self.vm_file.write(VMWriter.writeCall(identifier,nArgs))
				root_index = nArgs_and_root_index["root_index"] + 1 #Skip over closing parenthesis at end of expression list 

			
			else: #Parse and compile a variable name (including an array entry)
				
				#Assign variable kind, type, and index to local variables
				var_kind = CompilationEngine.symbol_table.KindOf(root[root_index].text,"subroutine")
				
				if var_kind != "NONE":
					var_type = CompilationEngine.symbol_table.TypeOf(root[root_index].text,"subroutine")
					var_index = CompilationEngine.symbol_table.IndexOf(root[root_index].text,"subroutine")
				
				elif var_kind == "NONE":
					var_kind = CompilationEngine.symbol_table.KindOf(root[root_index].text,"class")
					var_type = CompilationEngine.symbol_table.TypeOf(root[root_index].text,"class")
					var_index = CompilationEngine.symbol_table.IndexOf(root[root_index].text,"class")
				
				if root[root_index+1].text == "[": #Code to execute to parse and compile an array entry
				
					#Skip over opening bracket
					root_index = root_index + 2 

					#Compile expression in brackets indicating which array element is being referenced, which should push value of expression to top of stack
					root_index = self.CompileExpression(root,root_index)

					#Push base address of array to top of stack
					if var_kind != "field": #Code for pushing array base address to top of stack if variable isn't an object field
						self.vm_file.write(VMWriter.writePush(var_kind,var_index))
					if var_kind == "field": #Code for pushing array base address to top of stack if variable is an object field
						self.vm_file.write(VMWriter.writePush("this",var_index))

					#Add base address and index, which will leave address of array entry at top of stack
					self.vm_file.write(VMWriter.writeArithmetic("add"))

					#Leave value of array entry at top of stack
					self.vm_file.write(VMWriter.writePop("pointer",1))
					self.vm_file.write(VMWriter.writePush("that",0))

					#Skip over closing bracket
					root_index = root_index + 1

			
				else: #Parse and compile a non-array entry variable name
					
					#Push value of variable to top of stack
					if var_kind == "field": #Code to execute if variable is a field of the current object
						self.vm_file.write(VMWriter.writePush("this",var_index)) #Push pointer to base address of object current method was called on to top of stack

					if var_kind != "field": #Code to execute if variable isn't a field of the current object
						self.vm_file.write(VMWriter.writePush(var_kind,var_index))

					root_index = root_index + 1

		
		elif root[root_index].text == "(": #Parse and compile an expression term
			root_index = root_index + 1 #Skip over opening parenthesis
			root_index = self.CompileExpression(root,root_index) #Parse and compile expression 
			root_index = root_index + 1 #Skip over closing parenthesis
		
		elif root[root_index].text in ["-","~"]: #Compile a unary operator and following term
			if root[root_index].text == "-": #Compile arithmetic negation and following term
				root_index = self.CompileTerm(root,root_index+1) #Parse and compile term immediately to right of "-", which should leave value of this term at top of stack
				self.vm_file.write(VMWriter.writeArithmetic("neg")) #Take arithmetic negation of value on top of stack and leave result on top of stack
			elif root[root_index].text == "~": #Compile logical negation and following term
				root_index = self.CompileTerm(root,root_index+1) #Parse and compile term immediately to right of "~", which should leave value of this term at top of stack
				self.vm_file.write(VMWriter.writeArithmetic("not")) #Take logical negation of value on top of stack and leave result on top of stack

		#Return value of root_index to calling function
		return root_index



	def CompileExpressionList(self,root,root_index):
		
		nArgs = 0 #Initialize variable to count number of arguments/expressions in expression list
		
		#Loop over expressions in expression list, compiling each one
		while root[root_index].text != ")":
			if root[root_index].text != ",":
				root_index = self.CompileExpression(root,root_index)
				nArgs = nArgs + 1
			else:
				root_index = root_index + 1 #Skip comma separating expressions

		#Assign number of arguments in expression list and root_index to continue compilation from to a dictionary
		nArgs_and_root_index = {"nArgs": nArgs, "root_index":root_index}

		return nArgs_and_root_index 


#Collection of functions used to drive overall compilation process

class JackAnalyzer: 

	@staticmethod
	def CreateFilePaths(): #Create array of file paths for Jack files to be compiled
		jack_file_paths = [sys.argv[1]]
		if jack_file_paths[0].find(".jack") == -1:
			if jack_file_paths[0].endswith("/") == False:
				jack_file_paths[0] = jack_file_paths[0] + "/"
			jack_file_directory = jack_file_paths[0] 
			forward_slash_loc = jack_file_directory[:-1].rfind("/") + 1
			jack_file_paths = []
			import glob, os
			os.chdir(jack_file_directory)
			for file in glob.glob("*.jack"):
				if file.find("_cleaned") == -1:
					jack_file_paths.append(jack_file_directory + file)
		return jack_file_paths

	
	@staticmethod
	def TokenizeAndCompile(jack_file_path): #Tokenize and compile file at jack_file_path
		
		tokenized_file_path = jack_file_path[0:-5] + "T_mine.xml"
		vm_file_path = jack_file_path[0:-5] + ".vm"

		#Remove comments and replace tabs and newlines with spaces from Jack file
		jack_file_cleaned = jack_file_path[0:-5] + "_cleaned" + ".jack"
		with open(jack_file_path,'r') as initial_jack_file, open(jack_file_cleaned,'w') as clean_jack_file:
			initial_file = initial_jack_file.read()
			initial_file = re.sub(r"/\*(.|\n)*?\*/","",initial_file)
			initial_file = re.sub(r"//.*","",initial_file)
			initial_file = re.sub(r"\n"," ",initial_file)
			initial_file = re.sub(r"\r"," ",initial_file)
			initial_file = re.sub(r"\t"," ",initial_file)		
			clean_jack_file.write(initial_file)

		
		with open(jack_file_cleaned,'r') as jack_file, open(tokenized_file_path,'w+') as tokenized_file, open(vm_file_path,'w+') as vm_file:

			#Execute tokenization of Jack program files
			tokenized_file.write("<tokens>" + "\n") 
			previous_token = ""
			while JackTokenizer.hasMoreTokens(jack_file.read(1)) == True:
				jack_file.seek(-1,1)
				#Skip spaces
				current_char = jack_file.read(1)
				while current_char == " ":
					current_char = jack_file.read(1)
				if current_char != "":
					jack_file.seek(-1,1)
				elif current_char == "": 
					break
				current_loc = jack_file.tell()
				token_type = JackTokenizer.tokenType(jack_file.read(13))
				jack_file.seek(current_loc,0)
				if token_type == "symbol":
					token = JackTokenizer.symbol(jack_file.read(1))
				elif token_type == "stringConstant":
					token = JackTokenizer.stringVal(jack_file)
				elif token_type == "integerConstant":
					token = JackTokenizer.intVal(jack_file)
				elif token_type == "keyword":
					token = JackTokenizer.keyWord(jack_file.read(13))
				elif token_type == "identifier":
					token = JackTokenizer.identifier(jack_file)
				tokenized_file.write("\t" + "<" + token_type + ">" + token + "</" + token_type + ">" + "\n")
				jack_file.seek(current_loc,0)
				if token_type == "stringConstant":
					#Accounting for quotations around string constant when advancing to next token
					jack_file.seek(len(token)+2,1)
				elif token == "&lt;" or token == "&gt;" or token == "&quot;" or token == "&amp;":
					jack_file.seek(1,1)
				else: 
					#If current token isn't a string_constant, advance by length of current token
					jack_file.seek(len(token),1)
			tokenized_file.write("</tokens>")

	
			#Compile tokenized file
			class_to_compile = CompilationEngine(tokenized_file,vm_file)
			class_to_compile.CompileClass()



#Execute compilation
jack_file_paths = JackAnalyzer.CreateFilePaths()
for i in jack_file_paths:
	JackAnalyzer.TokenizeAndCompile(i)
	






