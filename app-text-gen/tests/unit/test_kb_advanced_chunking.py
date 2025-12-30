#!/usr/bin/env python3
"""
Interactive test of KB document addition with advanced chunking strategies
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kb_manager import KnowledgeBase

def main():
    """Interactive test of KB with advanced chunking"""
    print("\n" + "="*70)
    print("INTERACTIVE KB TEST - ADVANCED CHUNKING STRATEGIES")
    print("="*70)
    
    # Initialize KB
    try:
        kb = KnowledgeBase()
        print("[OK] Knowledge Base initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize KB: {e}")
        return 1
    
    # Create a collection
    print("\n" + "="*70)
    print("Step 1: Create Collection")
    print("="*70)
    
    collection_name = "test-microprocessor-docs"
    description = "Test collection for microprocessor documentation"
    kb.create_collection(collection_name, description)
    print(f"[OK] Created collection: {collection_name}")
    
    # Add document with different strategies
    sample_file = Path(__file__).parent / "test_sample.txt"
    
    if not sample_file.exists():
        print(f"[FAIL] Sample file not found: {sample_file}")
        return 1
    
    print("\n" + "="*70)
    print("Step 2: Add Document with Different Chunking Strategies")
    print("="*70)
    
    strategies = ["paragraphs", "sentences", "sliding_window", "semantic"]
    
    for i, strategy in enumerate(strategies, 1):
        doc_title = f"Microprocessors - {strategy.replace('_', ' ').title()}"
        print(f"\n--- Adding document with {strategy} strategy ({i}/{len(strategies)}) ---")
        
        success = kb.add_document(
            str(sample_file),
            collection_name,
            doc_title,
            strategy
        )
        
        if success:
            print(f"[OK] Document added successfully with {strategy} strategy")
        else:
            print(f"[FAIL] Failed to add document with {strategy} strategy")
    
    # List documents and show stats
    print("\n" + "="*70)
    print("Step 3: View Collection Statistics")
    print("="*70)
    
    stats = kb.get_collection_stats(collection_name)
    print(f"\nCollection: {stats['name']}")
    print(f"  Documents: {stats['document_count']}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total words: {stats['total_words']}")
    print(f"  Indexed: {stats['indexed_documents']}/{stats['document_count']}")
    
    # List documents with strategy info
    print("\n" + "="*70)
    print("Step 4: List Documents with Strategy Info")
    print("="*70)
    
    docs = kb.list_documents(collection_name)
    for doc in docs:
        print(f"\nDocument: {doc['title']}")
        print(f"  ID: {doc['id']}")
        print(f"  Chunks: {doc['chunk_count']}")
        print(f"  Words: {doc['total_words']}")
        print(f"  Avg chunk: {doc['total_words'] // doc['chunk_count']} words")
        
        # Show strategy from first chunk if available
        if doc.get('chunks') and doc['chunks']:
            first_chunk = doc['chunks'][0]
            strategy = first_chunk.get('strategy', 'unknown')
            print(f"  Strategy: {strategy}")
    
    # Show comparison
    print("\n" + "="*70)
    print("Step 5: Strategy Comparison")
    print("="*70)
    
    print("\nChunk Count by Strategy:")
    for doc in docs:
        title = doc['title']
        chunk_count = doc['chunk_count']
        avg_chunk = doc['total_words'] // chunk_count if chunk_count > 0 else 0
        print(f"  {title:45} | Chunks: {chunk_count:2d} | Avg: {avg_chunk:3d} words")
    
    print("\n[OK] All tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

