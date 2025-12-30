# Quick Start: RAG & Search Features Workflow

## Overview

Your app has **TWO powerful search systems**:

1. **Local KB Search** - Fast, conversation-based
2. **Enterprise Cosmos Search** - Cloud-scale, dual-source

Both use embeddings and AI to find relevant content.

---

## Complete Workflow Diagram

```
START
  |
  v
[1] ADD DOCUMENTS TO KB
  |
  +---> Type: kb
  |     Option 2: Add document
  |     Choose collection
  |     Select chunking strategy
  |     (stored locally in JSONL)
  |
  v
[2a] INDEX FOR LOCAL SEARCH         [2b] INDEX FOR COSMOS DB
  |                                   |
  +---> Type: index-kb                +---> Type: kb
  |     (Indexes to local             |     Option 7: Bulk index
  |     embedding index)              |     (Indexes to Cosmos DB
  |                                   |     with embeddings)
  v                                   v
[3a] USE kb-search                  [3b] USE cosmos-search
  |                                   |
  +---> Search conversations          +---> Enterprise search
  |     & local KB                    |     & cloud vectors
  |     (Fast, local)                 |     (Comprehensive, cloud)
  v                                   v
RESULTS WITH RELEVANCE SCORES
  |
  v
DONE
```

---

## Step-by-Step Workflow

### Phase 1: Add Documents (One Time)

```
STEP 1: Enter KB Menu
  Command: kb
  Display: Knowledge Base Management menu

STEP 2: Create Collection (if needed)
  Option: 1
  Input: Collection name (e.g., "6502-docs")
  Input: Description (optional)
  Result: Collection created

STEP 3: Add Document
  Option: 2
  Select: Collection from list
  Input: File path to document
  Input: Document title (optional)
  Select: Chunking strategy (1-5)
           1. Paragraphs (default)
           2. Sentences
           3. Size-based
           4. Sliding Window
           5. Semantic
  Result: Document added & split into chunks
```

### Phase 2a: Local Search Setup

```
STEP 1: Index for Local Search
  Command: index-kb
  Process: Reads all KB documents
           Generates embeddings for chunks
           Stores in local index (embeddings/)
  Result: Ready for kb-search
  Time: ~1-2 minutes for all docs

STEP 2: Use Local Search
  Command: kb-search
  Input: Search query
  Output: Top 5 results from KB
          With relevance scores
          Fast & local
```

### Phase 2b: Enterprise Cosmos Search Setup

```
STEP 1: Index for Cosmos DB
  Command: kb
  Option: 7 (Bulk index KB to Cosmos DB)
  Confirm: yes
  Process: Reads all KB documents
           Generates embeddings for ALL chunks
           Stores in Azure Cosmos DB
           Shows progress (1/25, 2/25, ...)
  Result: Ready for cosmos-search
  Time: ~2-3 minutes for all docs

STEP 2: Use Cosmos Search
  Command: cosmos-search
  Input: Search query
  Process: Generates query embedding
           Searches local KB
           Searches Cosmos DB
           Merges results by relevance
  Output: Top 5 results from BOTH sources
          With source labels [Local KB] or [Cosmos DB]
          With relevance scores
          With cache statistics
```

---

## Command Reference

### Adding Content

| Command | Purpose | Time |
|---------|---------|------|
| `kb` then Option 1 | Create collection | <1s |
| `kb` then Option 2 | Add document | 5-10s |
| `kb` then Option 3 | List collections | <1s |
| `kb` then Option 4 | List documents | <1s |

### Indexing (Different Systems!)

| Command | Indexes To | Purpose | Time |
|---------|-----------|---------|------|
| `index-kb` | Local index | For `kb-search` | 1-2 min |
| `kb` Option 7 | Cosmos DB | For `cosmos-search` | 2-3 min |

### Searching

| Command | Searches | Results From | Speed |
|---------|----------|--------------|-------|
| `kb-search` | Local index | KB only | Very fast |
| `cosmos-search` | Cosmos DB | KB + Cloud | Fast |
| `semantic-search` | All | Conversations | Fast |

---

## Quick Decision Tree

```
I want to search KB documents:
  |
  +-- LOCAL & FAST?
  |    YES -> kb-search
  |    (after: index-kb)
  |
  +-- ENTERPRISE & COMPREHENSIVE?
       YES -> cosmos-search
       (after: kb menu Option 7)
```

---

## Recommended Workflow

### First Time Setup (15 minutes total)

```
1. Add your documents:
   kb → Option 2 → add documents

2. Index for local search:
   index-kb
   (Wait 1-2 minutes)

3. Test local search:
   kb-search
   (Verify it works)

4. Index for Cosmos DB:
   kb → Option 7 → confirm
   (Wait 2-3 minutes)

5. Test enterprise search:
   cosmos-search
   (Verify it works)

DONE! Both systems ready.
```

### Daily Usage

```
Just use commands:
  kb-search       (fast local search)
  cosmos-search   (comprehensive cloud search)

Add new docs:
  kb → Option 2 → add document
  (automatically indexed locally)
  
For Cosmos DB indexing:
  kb → Option 7 (only if adding many new docs)
```

---

## Key Points to Remember

### Two Index Systems

```
Local Index (embedding_index)
├─ Storage: embeddings/ (JSONL files)
├─ Commands: index-kb, kb-search
├─ Speed: Very fast
└─ Scope: KB only

Cosmos DB Index (cloud)
├─ Storage: Azure Cosmos DB
├─ Commands: kb Option 7, cosmos-search
├─ Speed: Fast
└─ Scope: KB + dual-source capability
```

### Chunking Strategies (Pick when adding document)

```
1. Paragraphs    → Best for essays, long content
2. Sentences     → Best for technical docs
3. Size-based    → Best for continuous text
4. Sliding Window → Best for preserving context
5. Semantic      → Best for mixed topics
```

### When to Use Each Search

```
kb-search
  ✓ Quick local searches
  ✓ Testing indexing
  ✓ When cloud not needed
  ✗ Enterprise scale
  ✗ Need cloud redundancy

cosmos-search
  ✓ Enterprise deployments
  ✓ Cloud-native apps
  ✓ Need redundancy
  ✓ Production scale
  ✗ Local-only constraints
  ✗ Need maximum speed
```

---

## Troubleshooting

### "No results found" in cosmos-search?

```
Check:
1. Did you run kb → Option 7 to index to Cosmos DB?
2. Do you have documents in KB? (kb → Option 4)
3. Try kb-search first to verify documents work locally
```

### What if indexing fails?

```
Local index (index-kb):
  → Check .env file set up
  → Verify KB has documents
  → Try adding 1 document first

Cosmos DB (kb Option 7):
  → Check Azure credentials
  → Verify internet connection
  → Try bulk indexing smaller subset
```

### Documents not showing up?

```
After adding document:
  1. Type: kb → Option 4 (list documents)
  2. Should see document listed
  3. If not, check file path was valid
```

---

## Performance Tips

### Optimize Indexing

```
Local Indexing:
  • Fewer, larger documents = faster
  • Sentence strategy = many chunks = slower
  • Semantic strategy = slower but better quality

Cosmos Indexing:
  • 25 documents with 245 chunks = ~2 min
  • Run once, reuse forever
  • Cache hits reduce API costs
```

### Optimize Search

```
kb-search:
  • Always instant (no API calls)
  • Good for testing
  • Use when speed critical

cosmos-search:
  • First query: ~1 second
  • Cached queries: <100ms
  • Better quality results
```

---

## Example Session

```
$ python src/app.py

Welcome to the GitHub Models Text Generation App!
...

Enter your prompt (or command): kb

Knowledge Base Management
Documents: 25 | Collections: 6
Indexed: 25/25

Options:
1. Create collection
2. Add document
3. List collections
4. List documents
5. View collection stats
6. View KB stats
7. Bulk index KB to Cosmos DB
0. Back to main menu

Select option (0-7): 4

Collections:
1. 6502-docs
2. Python-docs
...

Select collection: 1

Documents in 6502-docs:
- 6502 Microprocessor Guide: 4 chunks
- C64 Programming Primer: 2 chunks

Select option (0-7): 0

Enter your prompt (or command): cosmos-search

ENTERPRISE KB SEARCH - Cosmos DB + Embeddings

Enter your search query: tell me about the 6502

[+] Found 5 results from dual sources:

1. [cosmos_kb] Relevance: 73.8%
   Document: 6502 Microprocessor Guide
   Text: The 6502 is an 8-bit processor...

2. [cosmos_kb] Relevance: 71.1%
   Document: Microprocessors - Sentences
   Text: This 8-bit processor powered...

[Done!]
```

---

## Quick Reference Card

```
╔════════════════════════════════════════════════════════════╗
║           RAG SYSTEM QUICK REFERENCE                      ║
╠════════════════════════════════════════════════════════════╣
║ ADDING CONTENT                                             ║
║ ├─ kb → Option 1 = Create collection                      ║
║ ├─ kb → Option 2 = Add document                           ║
║ └─ Select chunking strategy (1-5)                         ║
║                                                            ║
║ INDEXING (CHOOSE ONE OR BOTH)                             ║
║ ├─ index-kb = Index for local search (1-2 min)           ║
║ └─ kb → Option 7 = Index for Cosmos DB (2-3 min)         ║
║                                                            ║
║ SEARCHING                                                  ║
║ ├─ kb-search = Search local KB (instant)                 ║
║ └─ cosmos-search = Search Cosmos DB (enterprise)          ║
║                                                            ║
║ VIEWING                                                    ║
║ ├─ kb → Option 3 = List collections                       ║
║ ├─ kb → Option 4 = List documents                         ║
║ ├─ kb → Option 5 = Collection stats                       ║
║ └─ kb → Option 6 = KB statistics                          ║
╚════════════════════════════════════════════════════════════╝
```

---

## Summary

Your RAG system has:

✅ **Two search engines** (local + cloud)
✅ **Five chunking strategies** (paragraphs, sentences, size, window, semantic)
✅ **Embeddings** (Azure OpenAI 1536-dimensional)
✅ **Intelligent caching** (reduces costs)
✅ **Production-ready** (error handling, logging)

**Start with:** Adding documents → Index locally → Try searches → Scale to Cosmos DB

**Enjoy your enterprise RAG system!** 🚀


