#This document contains the Python source code for the the parser portion of the Jack compiler specified in Chapters 10 and 11. The completed compiler is in the folder for Chatper 11. 

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
			return "keyword"
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



#Compilation engine module. Collection of functions used to recursively parse syntactic structure of Jack program files and output compiled Jack virtual machine code. 

class CompilationEngine:

	def __init__(self,tokenized_file,parsed_file):
		self.tokenized_file = tokenized_file
		self.parsed_file = parsed_file

	#Parses and compiles a tokenized Jack program file (each class is a separate file according to rules of Jack language)
	def CompileClass(self):
		#measure length of xml file (i.e. number of lines in XML file) to determine when "while" loop below should stop
		self.tokenized_file.seek(0)
		tree = ET.parse(self.tokenized_file)
		root = tree.getroot()
		max_root_index = len(root) 
		
		#initialize variable to keep track of how much each line should be indented when written to parsed_file
		indent_level = 0

		#create index variable to use to move through tokenized Jack program file and initiaze it to zero
		root_index = 0

		#go through tokens in tokenized Jack program file and parse syntactic structure, outputting XML file with parsed syntactic structure
		while root_index<max_root_index:
			current_token = root[root_index]
			#if at beginning of document, write "class," class name, and opening brace ("{") to parsed_file
			if current_token.tag == "keyword" and current_token.text == "class":
				self.parsed_file.write("<class>" + "\n") 
				self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n")
				self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index+1].text + "</identifier>" + "\n")
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index+2].text + "</symbol>" + "\n")
				root_index = root_index + 3
			#if current_token indicates class variable declaration, call CompileClassVarDec, which parses variable declaration and returns updated root_index
			elif current_token.tag == "keyword" and (current_token.text == "static" or current_token.text == "field"):
				root_index = self.CompileClassVarDec(root,root_index,(indent_level+1)) 
			#if current_token indicates subroutine, call CompileSubroutine, which parses a subroutine and returns updated root_index
			elif current_token.tag == "keyword" and (current_token.text == "constructor" or current_token.text == "function" or current_token.text == "method"):
				root_index = self.CompileSubroutine(root,root_index,(indent_level+1)) 
			#if reach end of tokenized Jack program file, write closing brace and "</class>" tag
			elif current_token.tag == "symbol" and current_token.text == "}":
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + "}" + "</symbol>" + "\n")
				self.parsed_file.write("</class>")
				break 
		

	#Parses and compiles a class variable declaration
	def CompileClassVarDec(self,root,root_index,indent_level):

		#write class variable declaration tag to parsed_file
		self.parsed_file.write(indent_level*"\t" + "<classVarDec>" + "\n")

		current_token = root[root_index]
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + current_token.text + "</keyword>" + "\n") #write "static" or "field" to parsed_file
		root_index = root_index + 1
		current_token = root[root_index]
		self.parsed_file.write((indent_level+1)*"\t" + "<" + current_token.tag + ">" + current_token.text + "</" + current_token.tag + ">" + "\n") #Write variable type to parsed_file (could be either a keyword or identifier, so need to access tag attribute of current_token)
		root_index = root_index + 1

		#write variable types and names to parsed_file
		continue_var_writing = True
		while continue_var_writing == True:
			current_token = root[root_index]
			self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + current_token.text + "</identifier>" + "\n") #Write variable name to parsed_file
			root_index = root_index+1
			current_token = root[root_index]
			
			if current_token.text == ",":
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + current_token.text + "</symbol>" + "\n") #Write "," to parsed_file
				root_index = root_index+1
			else:
				continue_var_writing = False

		#write closing semicolon and class variable declaration tag to parsed_file
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + current_token.text + "</symbol>" + "\n") #write closing semicolon to parsed_file
		self.parsed_file.write(indent_level*"\t" + "</classVarDec>" + "\n") #write closing class variable declaration tag to parsed_file

		#increment root_index and return value to calling CompileClass function
		root_index = root_index +1
		return root_index

	#Parses and compiles a subroutine
	def CompileSubroutine(self,root,root_index,indent_level):

		#PROBABLY HAVE SOME CODE HERE CLEARING SUBROUTINE SYMBOL TABLE

		#Write subroutine declaration tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<subroutineDec>" + "\n") 
		
		#Write either "constructor," "function," or "method" to parsed_file, as the case may be
		current_token = root[root_index]
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + current_token.text + "</keyword>" + "\n")
		root_index = root_index + 1
		current_token = root[root_index]

		#Write either "void" or the specific type of return value to parsed_file. Need to delineate between case where tag is "keyword" and case where tag is "identifier."
		self.parsed_file.write((indent_level+1)*"\t" + "<" + current_token.tag + ">" + current_token.text + "</" + current_token.tag + ">" + "\n")
		root_index = root_index + 1
		current_token = root[root_index]

		#Write subroutine name (an identifier) to parsed_file
		self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + current_token.text + "</identifier>" + "\n")
		root_index = root_index + 1
		current_token = root[root_index]		

		#Write "(" to parsed_file
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + current_token.text + "</symbol>" + "\n")
		root_index = root_index + 1
		current_token = root[root_index]


		#If there are any parameters, call CompileParameterList, which compiles the parameter list and returns root_index value that CompileSubroutine should continue compiling from
		root_index = self.CompileParameterList(root,root_index,(indent_level+1))
		current_token = root[root_index]

		#Write ")" to parsed_file
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + current_token.text + "</symbol>" + "\n")
		root_index = root_index + 1
		current_token = root[root_index]

		#Write subroutine body tag to parsed_file
		self.parsed_file.write((indent_level+1)*"\t" + "<subroutineBody>" + "\n")

		#Write "{" to parsed_file
		self.parsed_file.write((indent_level+2)*"\t" + "<symbol>" + current_token.text + "</symbol>" + "\n")
		root_index = root_index + 1
		current_token = root[root_index]		

		#If there are any variable declarations, call CompileVarDec, which compiles the variable declarations and returns root_index value that CompileSubroutine should continue compiling from
		while current_token.text == "var":
			root_index = self.CompileVarDec(root,root_index,(indent_level+2))
			current_token = root[root_index]

		#If there are any statements, call CompileStatements, which compiles the statements and returns root_index value that CompileSubroutine should continue compiling from
		statement_initial_tokens = ["let","if","while","do","return"]
		if current_token.text in statement_initial_tokens:
			root_index = self.CompileStatements(root,root_index,(indent_level+2))
			current_token = root[root_index]

		#Write "}" to parsed_file
		self.parsed_file.write((indent_level+2)*"\t" + "<symbol>" + current_token.text + "</symbol>" + "\n")

		#Write "</subroutineBody>"
		self.parsed_file.write((indent_level+1)*"\t" + "</subroutineBody>" + "\n")

		#Write "</subroutineDec>" to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</subroutineDec>" + "\n")

		#Increment root_index and return value to calling CompileClass function
		root_index = root_index + 1
		return root_index

	#Parses and compiles a parameter list
	def CompileParameterList(self,root,root_index,indent_level):
		
			#Write parameter list opening tag to parsed_file
			self.parsed_file.write((indent_level)*"\t" + "<parameterList>" + "\n")

			#Write parameters to parsed_file 
			continue_param_compilation = False
			if root[root_index].text != ")":
				continue_param_compilation = True
			while continue_param_compilation == True:
				self.parsed_file.write((indent_level+1)*"\t" + "<" + root[root_index].tag + ">" + root[root_index].text + "</" + root[root_index].tag + ">" + "\n")
				self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index+1].text + "</identifier>" + "\n")
				if root[root_index+2].text != ",":
					continue_param_compilation = False
					root_index = root_index + 2
				else:
					self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index+2].text + "</symbol>" + "\n")
					root_index = root_index + 3

			#Write parameter list closing tag
			self.parsed_file.write((indent_level)*"\t" + "</parameterList>" + "\n")

			#Return root_index value to calling function
			return root_index


	def CompileVarDec(self,root,root_index,indent_level):

		#Write variable declaration opening tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<varDec>" + "\n")

		#Write "var" and variable type to parsed_file:
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n")
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<" + root[root_index].tag + ">" + root[root_index].text + "</" + root[root_index].tag + ">" + "\n")
		root_index = root_index + 1

		#Write variable names to parsed_file:
		continue_var_writing = True
		while continue_var_writing == True:
			self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n")
			root_index = root_index + 1
			if root[root_index].text != ",":
				continue_var_writing = False
			else:
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n")
				root_index = root_index + 1

		#Write ";" to parsed_file to mark end of variable declaration
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n")		
		root_index = root_index + 1
		
		#Write variable declaration closing tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</varDec>" + "\n")

		#Return root_index to calling function
		return root_index 


	def CompileStatements(self,root,root_index,indent_level):

		#Write opening statements tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<statements>" + "\n")

		#Loop to parse and compile each statement in statement sequence
		continue_statement_compilation = True
		while continue_statement_compilation == True:
			
			#Call relevant function to parse and compile type of statement under consideration
			if root[root_index].text == "let":
				root_index = self.CompileLet(root,root_index,(indent_level+1))
			elif root[root_index].text == "if":
				root_index = self.CompileIf(root,root_index,(indent_level+1))
			elif root[root_index].text == "while":
				root_index = self.CompileWhile(root,root_index,(indent_level+1))
			elif root[root_index].text == "do":
				root_index = self.CompileDo(root,root_index,(indent_level+1))
			elif root[root_index].text == "return":
				root_index = self.CompileReturn(root,root_index,(indent_level+1))

			#Check if next token indicates another statement that needs to be compiled
			if root[root_index].text in ["let","if","while","do","return"]:
				continue_statement_compilation = True
			else:
				continue_statement_compilation = False

		#Write closing statements tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</statements>" + "\n")

		#Return updated root_index value to calling function
		return root_index


	def CompileLet(self,root,root_index,indent_level):

		#Write opening let statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<letStatement>" + "\n")

		#Parse and compile let statement
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write "let" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n") #Write variable name to parsed_file
		root_index = root_index + 1
		if root[root_index].text == "[": #if variable name refers to an array, parse and compile expression in brackets to determine array element being referenced
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write opening bracket to parsed_file
			root_index = root_index + 1
			root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile expression in brackets 
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write closing bracket to parsed_file
			root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "=" to parsed_file
		root_index = root_index + 1
		root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile expression on right-hand side of let statement
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ";" to parsed_file
		root_index = root_index + 1

		#Write closing let statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</letStatement>" + "\n")

		#Return value of root_index to calling function
		return root_index


	def CompileIf(self,root,root_index,indent_level):

		#Write opening if statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<ifStatement>" + "\n")

		#Parse and compile if statement
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write "if" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "(" to parsed_file
		root_index = root_index + 1
		root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile condition expression
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ")" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "{" to parsed_file
		root_index = root_index + 1
		root_index = self.CompileStatements(root,root_index,(indent_level+1)) #Parse and compile statements to execute if condition satisfied
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "}" to parsed_file
		root_index = root_index + 1
		if root[root_index].text == "else":
			self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write "else" to parsed_file
			root_index = root_index + 1
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "{" to parsed_file
			root_index = root_index + 1
			root_index = self.CompileStatements(root,root_index,(indent_level+1)) #Parse and compile statements to execute if condition not satisfied
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "}" to parsed_file
			root_index = root_index + 1

		#Write closing if statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</ifStatement>" + "\n")

		#Return value of root_index to calling function
		return root_index


	def CompileWhile(self,root,root_index,indent_level):

		#Write opening while statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<whileStatement>" + "\n")

		#Parse and compile while statement
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write "while" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "(" to parsed_file
		root_index = root_index + 1
		root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile condition expression
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ")" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "{" to parsed_file
		root_index = root_index + 1
		root_index = self.CompileStatements(root,root_index,(indent_level+1)) #Parse and compile statements to execute while condition satisfied
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "}" to parsed_file
		root_index = root_index + 1

		#Write closing while statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</whileStatement>" + "\n")
		
		#Return value of root_index to calling function
		return root_index
	
	
	def CompileDo(self,root,root_index,indent_level):

		#Write opening do statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<doStatement>" + "\n")

		#Parse and compile do statement
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write "do" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n") #Write function, class, or variable name to parsed_file
		root_index = root_index + 1
		if root[root_index].text == ".": #Parse and compile rest of subroutine call if it involves a class or variable name
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "." to parsed_file
			root_index = root_index + 1
			self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n") #Write subroutine name to parsed_file
			root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "(" to parsed_file
		root_index = root_index + 1
		root_index = self.CompileExpressionList(root,root_index,(indent_level+1)) #Compile expression list within subroutine call
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ")" to parsed_file
		root_index = root_index + 1
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ";" to parsed_file
		root_index = root_index + 1

		#Write closing do statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</doStatement>" + "\n")

		#Return value of root_index to calling function
		return root_index

	
	def CompileReturn(self,root,root_index,indent_level):

		#Write opening return statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<returnStatement>" + "\n")

		#Parse and compile return statement
		self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write "return" to parsed_file
		root_index = root_index + 1
		if root[root_index].text != ";":
			root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile expression (if any)
		self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ";" to parsed_file
		root_index = root_index + 1

		#Write closing return statement tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</returnStatement>" + "\n")

		#Return value of root_index to calling function
		return root_index


	def CompileExpression(self,root,root_index,indent_level):

		#Write opening expression tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<expression>" + "\n")
			
		#Parse and compile expression
		still_expression = True
		while still_expression == True:
			root_index = self.CompileTerm(root,root_index,(indent_level+1)) #Parse and compile term
			if root[root_index].text in ["+","-","*","/","&","|","<",">","="]: #Compile operator, if any
				operator = root[root_index].text
				if operator == "<": # "<" is a reserved character in XML
					operator = "&lt;"
				elif operator == ">": # ">" is a reserved character in XML
					operator = "&gt;"
				elif operator == "&": # "&" is a reserved character in XML
					operator = "&amp;"
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + operator + "</symbol>" + "\n") #Write operator to parsed_file
				root_index = root_index + 1
			else:
				still_expression = False

		#Write closing expression tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</expression>" + "\n")

		#Return value of root_index to calling function
		return root_index


	def CompileTerm(self,root,root_index,indent_level):

		#Write opening term tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "<term>" + "\n")
		
		#Parse and compile term
		if root[root_index].tag == "integerConstant": #Parse and compile an integer
			self.parsed_file.write((indent_level+1)*"\t" + "<integerConstant>" + root[root_index].text + "</integerConstant>" + "\n") #Write integer to parsed_file
			root_index = root_index + 1
		
		elif root[root_index].tag == "stringConstant": #Parse and compile a string constant
			string = root[root_index].text
			string.replace('"','&quot;')
			self.parsed_file.write((indent_level+1)*"\t" + "<stringConstant>" + string + "</stringConstant>" + "\n") #Write string constant to parsed_file
			root_index = root_index + 1		

		elif root[root_index].tag == "keyword": #Parse and compile a keyword
			self.parsed_file.write((indent_level+1)*"\t" + "<keyword>" + root[root_index].text + "</keyword>" + "\n") #Write keyword to parsed_file
			root_index = root_index + 1
		
		elif root[root_index].tag == "identifier":
			if root[root_index + 1].text == "[": #Parse and compile a reference to an array entry
				self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n") #Write array variable name to parsed_file
				root_index = root_index + 1
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "[" to parsed_file
				root_index = root_index + 1
				root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile expression indicating array entry
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "]" to parsed_file
				root_index = root_index + 1
			elif root[root_index + 1].text in [".","("]: #Parse and compile a subroutine call
				self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n") #Write either variable name, class name, or function name to parsed_file
				root_index = root_index + 1
				if root[root_index].text == ".": #Parse and compile rest of subroutine call if it involves a class or variable name
					self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "." to parsed_file
					root_index = root_index + 1
					self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n") #Write subroutine name to parsed_file
					root_index = root_index + 1
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "(" to parsed_file
				root_index = root_index + 1
				root_index = self.CompileExpressionList(root,root_index,(indent_level+1)) #Compile expression list within subroutine call
				self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ")" to parsed_file
				root_index = root_index + 1
			else: #Parse and compile a variable name
				self.parsed_file.write((indent_level+1)*"\t" + "<identifier>" + root[root_index].text + "</identifier>" + "\n")
				root_index = root_index + 1

		
		elif root[root_index].text == "(": #Parse and compile an expression term
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "(" to parsed_file
			root_index = root_index + 1
			root_index = self.CompileExpression(root,root_index,(indent_level+1)) #Parse and compile expression 
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write ")" to parsed_file
			root_index = root_index + 1
		
		elif root[root_index].text in ["-","~"]: #Parse and compile a unary operator
			self.parsed_file.write((indent_level+1)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write unary operator to parsed_file
			root_index = root_index + 1
			root_index = self.CompileTerm(root,root_index,(indent_level+1))

		#Write closing term tag to parsed_file
		self.parsed_file.write((indent_level)*"\t" + "</term>" + "\n")

		#Return value of root_index to calling function
		return root_index



	def CompileExpressionList(self,root,root_index,indent_level):
		
		self.parsed_file.write((indent_level)*"\t" + "<expressionList>" + "\n")

		while root[root_index].text != ")":
			if root[root_index].text != ",":
				root_index = self.CompileExpression(root,root_index,indent_level)
			else:
				self.parsed_file.write((indent_level)*"\t" + "<symbol>" + root[root_index].text + "</symbol>" + "\n") #Write "," to parsed_file
				root_index = root_index + 1

		self.parsed_file.write((indent_level)*"\t" + "</expressionList>" + "\n")

		return root_index 


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
		parsed_file_path = jack_file_path[0:-5] + "_mine.xml"

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

		
		with open(jack_file_cleaned,'r') as jack_file, open(tokenized_file_path,'w+') as tokenized_file, open(parsed_file_path,'w+') as parsed_file:

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
				token_type = JackTokenizer.tokenType(jack_file.read(11))
				jack_file.seek(current_loc,0)
				if token_type == "symbol":
					token = JackTokenizer.symbol(jack_file.read(1))
				elif token_type == "stringConstant":
					token = JackTokenizer.stringVal(jack_file)
				elif token_type == "integerConstant":
					token = JackTokenizer.intVal(jack_file)
				elif token_type == "keyword":
					token = JackTokenizer.keyWord(jack_file.read(11))
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
			class_to_compile = CompilationEngine(tokenized_file,parsed_file)
			class_to_compile.CompileClass()



#Execute compilation
jack_file_paths = JackAnalyzer.CreateFilePaths()
for i in jack_file_paths:
	JackAnalyzer.TokenizeAndCompile(i)






