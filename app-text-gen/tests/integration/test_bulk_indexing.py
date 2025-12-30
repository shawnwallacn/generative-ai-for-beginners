#!/usr/bin/env python3
"""
Test script for Cosmos DB bulk indexing feature
Demonstrates indexing KB documents with embeddings
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
load_dotenv()

def test_bulk_indexing():
    """Test bulk indexing of KB documents to Cosmos DB"""
    
    print("\n" + "="*70)
    print("COSMOS DB BULK INDEXING TEST")
    print("="*70)
    
    try:
        from kb_manager import KnowledgeBase
        
        print("\n[TEST 1] Initialize KB with Cosmos DB")
        print("-" * 70)
        
        kb = KnowledgeBase(use_cosmos_db=True)
        
        if not kb.cosmos_storage:
            print("[WARNING] Cosmos DB not available")
            return False
        
        print("[OK] KB initialized with Cosmos DB support")
        
        print("\n[TEST 2] Check KB documents")
        print("-" * 70)
        
        stats = kb.get_stats()
        print(f"Total documents: {stats['document_count']}")
        print(f"Collections: {stats['collection_count']}")
        print(f"Indexed: {stats['indexed_documents']}")
        
        if stats['document_count'] == 0:
            print("[!] No documents to index")
            return False
        
        print("\n[TEST 3] Bulk index KB documents to Cosmos DB")
        print("-" * 70)
        print("\nThis will:")
        print("  1. Generate embeddings for all chunks")
        print("  2. Store in Cosmos DB")
        print("  3. Enable dual-source search")
        print()
        
        index_stats = kb.bulk_index_kb_to_cosmos()
        
        if not index_stats:
            print("[ERROR] Bulk indexing failed")
            return False
        
        print("\n[+] Bulk indexing completed successfully!")
        
        print("\n" + "="*70)
        print("TEST RESULT: SUCCESS")
        print("="*70)
        
        print("\nNext Steps:")
        print("1. Run: python src/app.py")
        print("2. Type: cosmos-search")
        print("3. Enter query: tell me about the 6502 microprocessor")
        print("4. View results from both local KB and Cosmos DB")
        
        return True
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_bulk_indexing()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(1)

