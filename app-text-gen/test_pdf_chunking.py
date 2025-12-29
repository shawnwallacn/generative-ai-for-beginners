#!/usr/bin/env python3
"""
Test KB document addition with working PDF and advanced chunking strategies
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kb_manager import KnowledgeBase

def main():
    """Test KB with python-cheatsheet.pdf"""
    print("\n" + "="*70)
    print("KB PDF TEST - PYTHON CHEATSHEET (Text-based PDF)")
    print("="*70)
    
    # Initialize KB
    try:
        kb = KnowledgeBase()
        print("[OK] Knowledge Base initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize KB: {e}")
        return 1
    
    # Create a collection for PDF test
    collection_name = "python-reference"
    kb.create_collection(collection_name, "Python reference materials")
    print(f"[OK] Created collection: {collection_name}")
    
    # Test with python-cheatsheet.pdf
    pdf_file = Path(__file__).parent / "python-cheatsheet.pdf"
    
    if not pdf_file.exists():
        print(f"[FAIL] PDF not found: {pdf_file}")
        return 1
    
    print(f"\n[OK] Found: {pdf_file.name} ({pdf_file.stat().st_size / 1024:.1f} KB)")
    
    # Add with different strategies
    strategies = ["paragraphs", "sentences", "semantic"]
    
    print(f"\n{'='*70}")
    print("Testing PDF with different chunking strategies")
    print(f"{'='*70}")
    
    for i, strategy in enumerate(strategies, 1):
        doc_title = f"Python Cheatsheet - {strategy.replace('_', ' ').title()}"
        print(f"\n[{i}/{len(strategies)}] Adding with {strategy} strategy...")
        
        success = kb.add_document(
            str(pdf_file),
            collection_name,
            doc_title,
            strategy
        )
        
        if success:
            print(f"    [OK] Success!")
        else:
            print(f"    [FAIL] Failed")
    
    # Show results
    print(f"\n{'='*70}")
    print("Results")
    print(f"{'='*70}")
    
    stats = kb.get_collection_stats(collection_name)
    print(f"\nCollection: {stats['name']}")
    print(f"  Documents: {stats['document_count']}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total words: {stats['total_words']}")
    
    docs = kb.list_documents(collection_name)
    print(f"\nDocuments by strategy:")
    for doc in docs:
        chunks = doc['chunk_count']
        words = doc['total_words']
        avg = words // chunks if chunks > 0 else 0
        strategy = doc['title'].split(' - ')[-1]
        print(f"  - {strategy:15} | Chunks: {chunks:2} | Words: {words:4} | Avg: {avg:3}/chunk")
    
    print(f"\n[OK] PDF test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

