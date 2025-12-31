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
║           RAG SYSTEM QUICK REFERENCE                       ║
╠════════════════════════════════════════════════════════════╣
║ ADDING CONTENT                                             ║
║ ├─ kb → Option 1 = Create collection                       ║
║ ├─ kb → Option 2 = Add document                            ║
║ └─ Select chunking strategy (1-5)                          ║
║                                                            ║
║ INDEXING (CHOOSE ONE OR BOTH)                              ║
║ ├─ index-kb = Index for local search (1-2 min)             ║
║ └─ kb → Option 7 = Index for Cosmos DB (2-3 min)           ║
║                                                            ║
║ SEARCHING                                                  ║
║ ├─ kb-search = Search local KB (instant)                   ║
║ └─ cosmos-search = Search Cosmos DB (enterprise)           ║
║                                                            ║
║ VIEWING                                                    ║
║ ├─ kb → Option 3 = List collections                        ║
║ ├─ kb → Option 4 = List documents                          ║
║ ├─ kb → Option 5 = Collection stats                        ║
║ └─ kb → Option 6 = KB statistics                           ║
╚════════════════════════════════════════════════════════════╝
```

---

## Auto KB Search in Chat

The main chat conversation now uses agent functions to search your Knowledge Base. The agent can intelligently choose between:
- **`search_local_kb`** - Fast local search (perfect for quick answers)
- **`search_enterprise_kb`** - Comprehensive dual-source search (local + Cosmos DB)

The system prompt guides the agent to make intelligent choices based on your query context:
- "Quick summary of..." → Uses `search_local_kb` (fast, instant)
- "Find ALL information about..." → Uses `search_enterprise_kb` (comprehensive)
- "Production" queries → Uses `search_enterprise_kb` (enterprise-scale)

### How It Works

When you chat, the agent now:
1. Sees your query
2. Analyzes the context (quick vs comprehensive need)
3. Chooses appropriate search function
4. Executes the search
5. Augments response with results

Example conversation flow:
```
You: "Tell me about the 6502"
  ↓
Agent: "This is a general query, quick answer is fine"
  ↓
Agent calls: search_local_kb
  ↓
Agent returns: Fast response with local KB results

You: "Find everything about 6502 including all variations"
  ↓
Agent: "User wants comprehensive results"
  ↓
Agent calls: search_enterprise_kb
  ↓
Agent returns: Complete response with local + Cosmos DB results
```


## Multi-Step Planning

**The agent can now execute complex multi-step workflows!**

### What's New

When you ask complex questions that require multiple steps, the agent can now:
1. Create a **plan** with multiple steps
2. Execute steps **sequentially**
3. Pass results between steps
4. Deliver comprehensive answers

### Example Multi-Step Scenarios

**Example 1: Search + Summarize**
```
You: "Find all 6502 information and create a comprehensive summary"
  ↓
Agent's Plan:
  Step 1: search_enterprise_kb for "6502 complete documentation"
  Step 2: create_summary from step 1 results
  ↓
Result: Comprehensive summary based on all findings
```

**Example 2: Search + Extract Code + Summarize**
```
You: "Find 6502 code examples, extract them, and summarize"
You: "Search local KB for 6502, then search enterprise KB for microprocessors, then create a summary comparing both results"
  ↓
Agent's Plan:
  Step 1: search_local_kb for "6502 assembly code"
  Step 2: extract_code_snippet from step 1 results
  Step 3: create_summary combining steps 1 and 2
  ↓
Result: Complete analysis with code examples
```

**Example 3: Multiple Searches + Analysis**
```
You: "Compare local KB and Cosmos DB results for microprocessors"
  ↓
Agent's Plan:
  Step 1: search_local_kb for "microprocessor architecture"
  Step 2: search_enterprise_kb for "microprocessor design"
  Step 3: create_summary comparing both results
  ↓
Result: Comparative analysis from both sources
```

### How Multi-Step Planning Works

**In Chat:**
1. You ask a complex question
2. Agent analyzes if multi-step is needed
3. Agent creates a PLAN with steps
4. System executes each step
5. Results flow from step to step
6. Agent provides final comprehensive response

**Key Features:**
- ✅ **Automatic**: No special syntax needed (agent decides)
- ✅ **Smart**: Avoids unnecessary multi-step when single-step suffices
- ✅ **Connected**: Step results flow to dependent steps
- ✅ **Robust**: Failures don't block other steps
- ✅ **Transparent**: You see the plan being executed

### When Multi-Step Plans Activate

The agent automatically uses multi-step plans when:
- Query requires analysis of search results + additional processing
- Multiple function outputs need combining
- Sequential reasoning is beneficial

Single-step execution remains for:
- Simple searches
- Direct questions
- Quick lookups
- Phase A agent functions

### Available Multi-Step Functions

- `search_local_kb` - Fast local knowledge base search
- `search_enterprise_kb` - Dual-source enterprise search
- `create_summary` - Create structured summaries
- `extract_code_snippet` - Extract and organize code
- `get_kb_document` - Retrieve full documents
- `get_kb_stats` - Get knowledge base statistics

### Example Chat Session

```bash
Enter your prompt (or command): Search for microprocessors and create a summary

Generating response using gpt-4...

[AGENT PLANNER] LLM proposed a multi-step plan.
[AGENT PLANNER] Executing valid plan with 2 steps...

[STEP 1] Executing: search_enterprise_kb
  Status: OK
  Result: Found 10 relevant documents

[STEP 2] Executing: create_summary
  Status: OK
  Result: Summary created with 5 key points

Multi-step plan executed:
- Step 1: search_enterprise_kb - OK
- Step 2: create_summary - OK

Final response from LLM:
"I searched the enterprise knowledge base and found comprehensive 
information about microprocessors. Here's a structured summary..."
```

### Important Notes

⚠️ **The agent is smart about planning:**
- Won't use multi-step if single-step works fine
- Automatically chooses best approach
- You don't need to request multi-step explicitly
- Regular chat works exactly as before
- Just use the app normally!

---

## Summary

Your RAG system now has:

✅ **Two search engines** (local + cloud)
✅ **Five chunking strategies** (paragraphs, sentences, size, window, semantic)
✅ **Embeddings** (Azure OpenAI 1536-dimensional)
✅ **Intelligent caching** (reduces costs)
✅ **Production-ready** (error handling, logging)
✅ **Agent-based KB search** (intelligent `search_local_kb` and `search_enterprise_kb` functions)
✅ **Multi-step planning** (complex workflows with result chaining)
✅ **Multiple search methods** (manual: kb-search, cosmos-search; automatic: chat agent)

**Current workflow:** Adding documents → Index locally → Try manual searches → Scale to Cosmos DB → Use in chat via agent functions

**Latest feature (Phase A):** Agent intelligently chooses between fast local and comprehensive enterprise searches in chat conversations!

**Enjoy your enterprise RAG system!** 🚀