#!/usr/bin/env python3
"""
Test script for advanced chunking strategies
Tests all 5 chunking methods with sample documents
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kb_manager import DocumentChunker

# Sample documents for testing
SAMPLE_DOCS = {
    "technical": """
Introduction to the 6502 CPU

The 6502 is an 8-bit microprocessor widely used in the 1970s and 1980s. 
It powered computers like the Apple II, Atari 2600, and Commodore 64.

Architecture Overview

The 6502 has three 8-bit registers: Accumulator (A), X, and Y. 
It supports addressing modes like immediate, zero page, absolute, and indexed addressing. 
The processor can access up to 64KB of memory using a 16-bit address bus.

Instruction Set

The 6502 instruction set includes 56 official instructions. Common instructions include:
- LDA (Load Accumulator): Loads a value into the A register
- STA (Store Accumulator): Stores A register value to memory
- ADC (Add with Carry): Adds value to accumulator with carry
- SBC (Subtract with Carry): Subtracts value from accumulator with borrow
- INC (Increment): Increments memory or register value
- DEC (Decrement): Decrements memory or register value
- CMP (Compare): Compares accumulator with memory or register
- JMP (Jump): Unconditional jump to new address
- JSR (Jump to Subroutine): Jump to subroutine with return address on stack

Memory Layout

The 6502 memory space is organized as follows:
- $0000-$00FF: Zero Page (256 bytes, fast access)
- $0100-$01FF: Stack (256 bytes, for push/pop operations)
- $0200-$FFFF: Main memory (65024 bytes, general purpose)

Status Register

The status register (P) contains 8 flags:
- C (Carry): Set after arithmetic operations that overflow
- Z (Zero): Set when result is zero
- I (Interrupt Disable): Disables interrupts when set
- D (Decimal Mode): Enables BCD arithmetic when set
- B (Break): Set on software break instruction
- V (Overflow): Set on signed arithmetic overflow
- N (Negative): Set when bit 7 of result is set

Programming Techniques

Common 6502 programming techniques include:
- Loop unrolling for performance optimization
- Self-modifying code for dynamic behavior
- Using zero page for frequently accessed variables
- Stack manipulation for function calls and local variables
    """,
    
    "essay": """
The Rise of Microcomputing

The 1970s and 1980s saw a revolution in computing. Personal computers became affordable and accessible to individuals and small businesses. 
This era gave birth to computing legends like the Apple II, Commodore 64, and Atari systems.

Early Personal Computers

Before the 1970s, computers were massive machines that filled entire rooms. They were expensive and required specialized knowledge to operate. 
The advent of microprocessors changed everything. Companies like MOS Technology, Intel, and Motorola began producing affordable chips that could power personal computers.

The Apple II

Released in 1977, the Apple II was one of the first successful personal computers. Steve Wozniak designed it around the 6502 microprocessor. 
It featured color graphics, a keyboard, and easy-to-use software like VisiCalc. The Apple II became the foundation for Apple's business empire.

The Commodore 64

Released in 1982, the Commodore 64 became the best-selling computer of all time. Its combination of power, affordability, and gaming capabilities made it incredibly popular. 
Musicians and producers used it for music production. Programmers used it to learn game development. Artists used it to create pixel art and animations.

The Atari 2600

The Atari 2600 brought gaming into homes worldwide. Released in 1977, it pioneered the cartridge-based gaming console concept. 
Games like Pac-Man and Space Invaders brought arcade experiences home. The Atari 2600 established many conventions still used in gaming today.

Impact on Technology

These early personal computers established many principles still relevant today. User-friendly interfaces, affordable hardware, and accessible software were revolutionary concepts. 
They proved that computing could be for everyone, not just specialists. This democratization of technology led directly to the personal computer boom of the 1990s and the internet age.

Legacy

The microcomputers of the 1970s and 1980s weren't just important historically. They remain beloved by enthusiasts and hobbyists. Modern emulators allow people to experience these machines. 
The games, music, and programs created on these platforms continue to inspire new generations. The era represents a unique moment when technology, creativity, and innovation converged.
    """
}

def test_chunking_strategy(name: str, text: str, chunker_func, *args, **kwargs):
    """Test a specific chunking strategy"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    
    try:
        chunks = chunker_func(text, *args, **kwargs)
        
        print(f"\n[OK] Chunked into {len(chunks)} chunks")
        print(f"\nStatistics:")
        print(f"  - Total chunks: {len(chunks)}")
        print(f"  - Avg chunk size: {sum(c['word_count'] for c in chunks) / len(chunks):.0f} words")
        print(f"  - Min chunk: {min(c['word_count'] for c in chunks)} words")
        print(f"  - Max chunk: {max(c['word_count'] for c in chunks)} words")
        
        print(f"\nFirst 3 chunks:")
        for i, chunk in enumerate(chunks[:3], 1):
            strategy = chunk.get('strategy', 'unknown')
            words = chunk['word_count']
            preview = chunk['text'][:80].replace('\n', ' ') + "..."
            print(f"\n  Chunk {i} (Strategy: {strategy}, Words: {words}):")
            print(f"  {preview}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    """Run all chunking strategy tests"""
    print("\n" + "="*70)
    print("ADVANCED CHUNKING STRATEGIES TEST")
    print("="*70)
    
    results = {}
    
    # Test with technical document
    doc_type = "Technical Document"
    text = SAMPLE_DOCS["technical"]
    
    print(f"\n{'='*70}")
    print(f"TESTING WITH: {doc_type}")
    print(f"Document size: {len(text)} characters, {len(text.split())} words")
    print(f"{'='*70}")
    
    # Test 1: Paragraphs (Original)
    results['paragraphs'] = test_chunking_strategy(
        "1. Paragraphs (Original)",
        text,
        DocumentChunker.chunk_by_paragraphs
    )
    
    # Test 2: Sentences (Original, improved with NLTK)
    results['sentences'] = test_chunking_strategy(
        "2. Sentences (5 sentences per chunk)",
        text,
        DocumentChunker.chunk_by_sentences,
        sentence_count=5
    )
    
    # Test 3: Size-based (Original)
    results['size'] = test_chunking_strategy(
        "3. Size-based (500 char chunks)",
        text,
        DocumentChunker.chunk_by_size,
        chunk_size=500
    )
    
    # Test 4: Sliding Window (NEW)
    results['sliding_window'] = test_chunking_strategy(
        "4. Sliding Window (400 char window, 200 char step)",
        text,
        DocumentChunker.chunk_by_sliding_window,
        window_size=400,
        step=200
    )
    
    # Test 5: Semantic (NEW)
    results['semantic'] = test_chunking_strategy(
        "5. Semantic (Topic-based grouping)",
        text,
        DocumentChunker.chunk_by_semantic,
        max_chunk_size=600
    )
    
    # Test with essay document
    print(f"\n\n{'='*70}")
    doc_type = "Essay Document"
    text = SAMPLE_DOCS["essay"]
    
    print(f"TESTING WITH: {doc_type}")
    print(f"Document size: {len(text)} characters, {len(text.split())} words")
    print(f"{'='*70}")
    
    essay_results = {}
    
    # Quick test of all strategies on essay
    essay_results['paragraphs'] = test_chunking_strategy(
        "1. Paragraphs",
        text,
        DocumentChunker.chunk_by_paragraphs
    )
    
    essay_results['sentences'] = test_chunking_strategy(
        "2. Sentences",
        text,
        DocumentChunker.chunk_by_sentences,
        sentence_count=5
    )
    
    essay_results['sliding_window'] = test_chunking_strategy(
        "4. Sliding Window",
        text,
        DocumentChunker.chunk_by_sliding_window,
        window_size=400,
        step=200
    )
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    all_passed = all(results.values()) and all(essay_results.values())
    
    print(f"\nTechnical Document Tests:")
    for strategy, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {strategy}")
    
    print(f"\nEssay Document Tests:")
    for strategy, passed in essay_results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {strategy}")
    
    if all_passed:
        print(f"\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[FAIL] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

