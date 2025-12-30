#!/usr/bin/env python3
"""
Debug script to check embedding index integrity
"""
import json
import os

def check_embeddings():
    embedding_file = "embeddings/conversation_embeddings.json"
    
    if not os.path.exists(embedding_file):
        print("❌ Embedding file not found!")
        return
    
    print("📖 Checking embeddings file...\n")
    
    with open(embedding_file, 'r') as f:
        data = json.load(f)
    
    entries = data.get('entries', [])
    print(f"Total entries: {len(entries)}")
    print(f"Last updated: {data.get('last_updated')}\n")
    
    if not entries:
        print("⚠️  No entries found in index!")
        return
    
    print("=" * 60)
    print("First Entry Details:")
    print("=" * 60)
    
    first = entries[0]
    print(f"Pair ID: {first.get('pair_id')}")
    print(f"Conversation ID: {first.get('conversation_id')}")
    print(f"Model: {first.get('model')}")
    print(f"Timestamp: {first.get('timestamp')}")
    
    embedding = first.get('embedding', [])
    print(f"\nEmbedding exists: {len(embedding) > 0}")
    print(f"Embedding length: {len(embedding)}")
    print(f"Expected length: 1536 (for text-embedding-3-small)")
    
    if embedding:
        print(f"First 10 values: {embedding[:10]}")
        print(f"Min value: {min(embedding):.6f}")
        print(f"Max value: {max(embedding):.6f}")
        print(f"Average value: {sum(embedding)/len(embedding):.6f}")
    
    print(f"\nUser message preview: {first.get('user_message', '')[:100]}...")
    print(f"Assistant message preview: {first.get('assistant_message', '')[:100]}...\n")
    
    print("=" * 60)
    print("All Entries Summary:")
    print("=" * 60)
    
    valid_embeddings = 0
    missing_embeddings = 0
    
    for i, entry in enumerate(entries):
        embedding = entry.get('embedding', [])
        if len(embedding) == 1536:
            valid_embeddings += 1
        else:
            missing_embeddings += 1
            if i < 3:  # Show first few problematic entries
                print(f"Entry {i} ({entry.get('pair_id')}): embedding length = {len(embedding)}")
    
    print(f"\nValid embeddings (length=1536): {valid_embeddings}")
    print(f"Invalid/missing embeddings: {missing_embeddings}")
    print(f"Validity rate: {(valid_embeddings/len(entries)*100):.1f}%")
    
    if valid_embeddings == len(entries):
        print("\n✅ All embeddings are valid!")
    else:
        print(f"\n⚠️  {missing_embeddings} entries have invalid embeddings")
    
    print("\n" + "=" * 60)
    print("Recommendation:")
    print("=" * 60)
    
    if valid_embeddings < len(entries):
        print("⚠️  Some embeddings are corrupted or missing.")
        print("Try clearing the embeddings file and re-indexing:")
        print("  1. Delete: app-text-gen/embeddings/conversation_embeddings.json")
        print("  2. Restart the app and re-index your conversation: 'index'")
    else:
        print("✅ Embeddings look good!")
        print("\nIf semantic search still returns no results:")
        print("  1. Lower RAG_SIMILARITY_THRESHOLD in .env to 0.15-0.20")
        print("  2. The low similarity scores (0.09-0.19) are normal for")
        print("     text-embedding-3-small - it has lower avg similarity")

if __name__ == "__main__":
    check_embeddings()

