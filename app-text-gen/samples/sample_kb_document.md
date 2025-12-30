# Introduction to the 6502 Microprocessor

## Overview

The 6502 is an 8-bit microprocessor that was widely used in the 1970s and 1980s. It powered computers like the Apple II, Atari 2600, and the Commodore 64.

## Key Characteristics

The 6502 has a simple yet powerful instruction set with just 56 basic instructions. It uses a single accumulator for arithmetic operations and has two index registers (X and Y) for memory addressing.

### Registers

- **Accumulator (A)**: Main register for arithmetic and logic operations
- **Index Register X**: Used for indexed addressing modes
- **Index Register Y**: Used for indexed addressing modes
- **Program Counter (PC)**: 16-bit register pointing to the next instruction
- **Stack Pointer (SP)**: Points to the top of the stack in page 1 memory
- **Status Register (P)**: Contains processor flags

### Memory Organization

The 6502 uses 16-bit addresses, allowing access to 64KB of memory. The memory is typically organized as follows:

- $0000-$00FF: Zero Page (256 bytes, fast access)
- $0100-$01FF: Stack (256 bytes)
- $0200-$FFFF: Main program memory

## Addressing Modes

The 6502 supports several addressing modes:

1. **Implied**: No operand required
2. **Accumulator**: Operation on the accumulator
3. **Immediate**: 8-bit constant value
4. **Zero Page**: 8-bit address in zero page
5. **Zero Page, X**: Zero page address + X index
6. **Zero Page, Y**: Zero page address + Y index
7. **Absolute**: 16-bit address
8. **Absolute, X**: Absolute address + X index
9. **Absolute, Y**: Absolute address + Y index
10. **Indirect**: Pointer-based addressing
11. **Indexed Indirect**: Combines indexing and indirect addressing
12. **Indirect Indexed**: Indirect addressing with Y indexing
13. **Relative**: For branch instructions

## Common Instructions

### Load/Store Instructions
- **LDA**: Load Accumulator
- **LDX**: Load X Register
- **LDY**: Load Y Register
- **STA**: Store Accumulator
- **STX**: Store X Register
- **STY**: Store Y Register

### Arithmetic Operations
- **ADC**: Add with Carry
- **SBC**: Subtract with Carry
- **INC**: Increment Memory
- **DEC**: Decrement Memory
- **INX**: Increment X
- **DEX**: Decrement X
- **INY**: Increment Y
- **DEY**: Decrement Y

### Logical Operations
- **AND**: Logical AND
- **ORA**: Logical OR
- **EOR**: Logical XOR
- **BIT**: Bit Test

### Control Flow
- **JMP**: Jump to address
- **JSR**: Jump to Subroutine
- **RTS**: Return from Subroutine
- **BEQ**: Branch if Equal to Zero
- **BNE**: Branch if Not Equal
- **BCS**: Branch if Carry Set
- **BCC**: Branch if Carry Clear

## Instruction Timing

Each instruction takes a specific number of clock cycles to execute:
- Fastest instructions: 2 cycles (e.g., NOP, DEX)
- Slowest instructions: 6+ cycles (e.g., absolute indirect addressing)

## Status Register Flags

The Status Register contains 8 flags that affect program flow:

- **C** (Carry): Set if arithmetic operation produces a carry
- **Z** (Zero): Set if result is zero
- **I** (Interrupt Disable): Prevents interrupts when set
- **D** (Decimal): Enables decimal mode
- **B** (Break): Set when a break instruction is executed
- **V** (Overflow): Set if arithmetic operation overflows
- **N** (Negative): Set if result is negative (bit 7 = 1)

## Conclusion

The 6502 remains a classic microprocessor due to its simplicity and power. Its clean instruction set and efficient addressing modes made it popular for embedded systems and game consoles. Understanding the 6502 provides valuable insights into microprocessor design and low-level programming.

