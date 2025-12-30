# Quick Reference: How to Index KB Documents to Cosmos DB

## The Issue

You have KB documents (25 total, 11 indexed locally), but they're not indexed to **Cosmos DB with embeddings**. The cosmos-search command searches:
1. Local embeddings (empty - returns nothing)
2. Cosmos DB embeddings (empty - documents not indexed there)

Result: No results found

## Solution: Index Documents to Cosmos DB

### Option 1: Manual Indexing (Per Document)

In the KB menu, after adding a document:
```
1. Create a small script to index existing documents
2. Or manually re-add documents with embeddings
```

### Option 2: Bulk Index Existing Documents (Recommended)

We need to add a method to index all KB documents at once to Cosmos DB.

### How It Should Work

```
1. Get all KB documents
2. For each document:
   a. Read document from local storage
   b. Generate embeddings for each chunk
   c. Store in Cosmos DB
3. Mark as indexed in Cosmos DB
```

### What We Need

Add this to `src/kb_manager.py`:

```python
def bulk_index_kb_to_cosmos(self) -> Dict:
    """
    Bulk index all KB documents to Cosmos DB with embeddings
    
    Returns:
        Statistics about indexing operation
    """
    from embedding_generator import EmbeddingGenerator
    
    if not self.cosmos_storage:
        print("[ERROR] Cosmos DB not available")
        return {}
    
    gen = EmbeddingGenerator()
    if not gen.is_available():
        print("[ERROR] Embedding generator not available")
        return {}
    
    stats = {
        "total_docs": 0,
        "indexed": 0,
        "failed": 0,
        "total_chunks": 0
    }
    
    # Get all documents
    all_docs = self.list_documents()
    
    for doc in all_docs:
        stats["total_docs"] += 1
        
        try:
            # Get chunk texts
            chunks = doc.get('chunks', [])
            if not chunks:
                continue
            
            chunk_texts = [c['text'] for c in chunks]
            stats["total_chunks"] += len(chunks)
            
            # Generate embeddings
            embeddings = gen.generate_batch_embeddings(chunk_texts)
            
            if embeddings and len(embeddings) == len(chunks):
                # Index to Cosmos DB
                self.index_document_to_cosmos(doc['id'], embeddings)
                stats["indexed"] += 1
            else:
                stats["failed"] += 1
        
        except Exception as e:
            print(f"  Error indexing {doc.get('id', 'unknown')}: {e}")
            stats["failed"] += 1
    
    return stats
```

### Then Add Menu Option

In `interactive_kb_menu()`, add:

```python
elif choice == "7":
    print("\n[*] Bulk indexing KB documents to Cosmos DB...")
    print("This will generate embeddings for all documents...")
    stats = kb.bulk_index_kb_to_cosmos()
    print(f"\n[+] Indexing complete!")
    print(f"    Documents: {stats['total_docs']}")
    print(f"    Indexed: {stats['indexed']}")
    print(f"    Failed: {stats['failed']}")
    print(f"    Total chunks: {stats['total_chunks']}")
```

## Current Workaround

You can test cosmos-search after manually adding a new document:

```
1. Type 'kb'
2. Option 2: Add document
3. Upload a document (it will be indexed)
4. Type 'cosmos-search'
5. Search for content from that document
```

New documents get indexed immediately when added (if using embeddings).

## Long-Term Solution

We should add "Bulk Index" option to KB menu that:
1. Takes all existing KB documents
2. Generates embeddings for their chunks
3. Stores in Cosmos DB
4. Shows progress/statistics

This is a quick fix that would complete the feature!


