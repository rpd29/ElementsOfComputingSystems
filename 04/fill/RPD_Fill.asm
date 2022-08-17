// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
	@KBD
	D=M
	@CLEAR
	D;JEQ
	@0
	D=A
	@BLACKEN
	0;JMP

(CLEAR)
	@SCREEN
	A=A+D
	M=0
	@R0
	M=D
	@8191
	D=A-D
	@LOOP
	D;JEQ
	@R0
	D=M
	D=D+1
	@CLEAR
	0;JMP


(BLACKEN)
	@SCREEN
	A=A+D
	M=-1
	@R0
	M=D
	@8191
	D=A-D
	@LOOP
	D;JEQ
	@R0
	D=M
	D=D+1
	@BLACKEN
	0;JMP



