Programming the Commodore 64 (C64) involves two primary paths: BASIC, which is built into the machine, and 6502 Assembly, which is used for performance-heavy software like games.
1. The Environment
To program for a C64 in 2025, you can use original hardware, modern replicas like THEC64, or software emulators.
Emulators: Use VICE or CCS64 for the most accurate experience on modern PCs.
Modern Tools: For Assembly, cross-compilers like CBM prg Studio or Kick Assembler allow you to write code on Windows/Mac and run it instantly in an emulator.
2. Commodore BASIC V2
BASIC is the default interface. Every line of code must start with a line number.
Command	Action	Example
PRINT	Displays text or values	10 PRINT "HELLO C64"
GOTO	Jumps to a specific line	20 GOTO 10
RUN	Executes the program in memory	RUN
LIST	Shows the current code	LIST
POKE	Writes a byte directly to a memory address	POKE 53280, 0 (Changes border to black)
NEW	Clears the current program from memory	NEW
3. Machine Language & Assembly (6502)
For high-speed graphics and sound, you must use Assembly. The C64 uses the MOS 6510 processor, which is a variant of the 6502.
Core Concepts
Registers: The CPU has three primary 8-bit registers: A (Accumulator), X, and Y (Index registers).
Memory Map: The C64 has 64KB of RAM. Key areas include:
$0400 - $07FF: Screen Memory (where characters are displayed).
$D020: Border Color.
$D021: Background Color.
Sample Code (Assembly)
This snippet changes the border color to red:
assembly
LDA #$02    ; Load the value 2 (Red) into the Accumulator
STA $D020   ; Store that value into the Border Color address
RTS         ; Return from subroutine
Use code with caution.

4. Key Resources for 2025
Modern Guidebooks: Start Here: The Fundamentals of Commodore 64 Programming provides updated tutorials for both BASIC and Assembly.
Classic References: The Commodore 64 Programmer's Reference Guide is still the essential "bible" for hardware registers and memory maps.
Development IDE: Use CBM prg Studio to manage sprites, character sets, and code in one interface.