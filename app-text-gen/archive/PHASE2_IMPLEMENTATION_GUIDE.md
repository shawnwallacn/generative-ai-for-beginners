# Phase 2: Enterprise RAG with Azure Cosmos DB Integration

## Overview

**Goal:** Integrate Azure Cosmos DB as a cloud-native vector database for KB documents while maintaining the existing local JSONL-based RAG for conversations.

**Architecture:** Dual-source search combining:
- Local JSONL storage (Conversations, temporary data)
- Azure Cosmos DB (KB documents with embeddings)

**Benefits:**
- Learn enterprise-scale application patterns
- Scalable vector database for large document libraries
- Professional semantic search capabilities
- Maintain conversation privacy in local storage

---

## Current Status

### Phase 1: ✅ COMPLETE
- ✅ 5 advanced chunking strategies implemented
- ✅ NLTK integration for sentence tokenization
- ✅ Tested with text-based PDFs
- ✅ Updated UI to select chunking strategy

### Phase 2: 🚀 IN PROGRESS

#### Step 1: Infrastructure Setup (Provisioning)
- 🔄 Azure Cosmos DB account creation
- ⏳ Database and container setup
- ⏳ Connection credentials retrieval

#### Step 2: Code Implementation (Ready)
- ✅ `CosmosDBStorage` class implemented
- ✅ Vector search methods available
- ✅ Metadata indexing prepared
- ⏳ Integration with KB manager

#### Step 3: Application Integration (Pending)
- ⏳ Update KB manager to use Cosmos DB
- ⏳ Implement dual-source search
- ⏳ Add result merging/ranking
- ⏳ Update audit logging

#### Step 4: Testing & Documentation (Pending)
- ⏳ End-to-end testing
- ⏳ Performance validation
- ⏳ Update README documentation

---

## Cosmos DB Infrastructure

### Account Details
```
Subscription: Visual Studio Professional
Resource Group: genai-search
Account Name: genai-cosmosdb
Region: eastus
Database: genai-kb
Container: documents
Partition Key: /collection_id
```

### Connection Configuration
```env
COSMOS_DB_ENDPOINT=https://genai-cosmosdb.documents.azure.com:443/
COSMOS_DB_KEY=<primary-key>
COSMOS_DB_CONNECTION_STRING=<connection-string>
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
```

---

## Code Structure

### New Files Created

#### `cosmos_storage.py`
**Purpose:** Azure Cosmos DB storage layer

**Classes:**
- `CosmosDBStorage`: Main storage interface
  - `store_document()`: Store KB document with embeddings
  - `search_by_embedding()`: Vector similarity search
  - `search_by_keyword()`: Keyword-based search
  - `get_document()`: Retrieve document by ID
  - `list_documents()`: List collection documents
  - `delete_document()`: Delete document
  - `get_collection_stats()`: Collection statistics
  
- `DualSourceSearch`: Hybrid search orchestration
  - `search()`: Search across both sources
  - `_rank_results()`: Merge and rank results

### Existing Files to Modify

#### `kb_manager.py`
**Changes needed:**
```python
# Import new storage
from cosmos_storage import CosmosDBStorage, DualSourceSearch

# Add to KnowledgeBase class:
- cosmos_storage instance
- dual_search instance
- Methods to toggle storage backend
- Update add_document() to index to Cosmos DB
- Update search() to use dual-source search
```

#### `app.py`
**Changes needed:**
```python
# Import Cosmos DB configuration
from cosmos_storage import CosmosDBStorage

# Initialize Cosmos DB storage on startup
# Add configuration loading from .env

# Update search logic to use DualSourceSearch
```

#### `requirements.txt`
**Additions needed:**
```
azure-cosmos>=4.5.0
```

---

## Implementation Roadmap

### Phase 2a: Setup & Configuration (In Progress)
1. ✅ Create Cosmos DB account
2. ⏳ Create database and container
3. ⏳ Retrieve credentials
4. ⏳ Update .env configuration
5. ⏳ Install azure-cosmos package

### Phase 2b: Core Implementation (Next)
1. Create KB integration class
2. Modify KB manager for Cosmos DB indexing
3. Implement embedding generation for documents
4. Add to Cosmos DB with embeddings
5. Implement search wrapper

### Phase 2c: Advanced Features (Following)
1. Intelligent result merging
2. Source-aware ranking
3. Audit trail integration
4. Performance monitoring
5. Vector search optimization

### Phase 2d: Testing & Polish (Final)
1. End-to-end testing
2. Performance benchmarking
3. Error handling and recovery
4. Documentation updates
5. Production readiness

---

## Cosmos DB Document Schema

### KB Document Structure
```json
{
  "id": "doc_collection_1234567890",
  "collection_id": "6502-docs",
  "title": "6502 Microprocessor Guide",
  "content": "... full content ...",
  "created_at": "2025-12-30T12:00:00Z",
  "indexed_at": "2025-12-30T12:05:00Z",
  "metadata": {
    "source": "pdf",
    "file_path": "path/to/file.pdf",
    "file_size": 1234567,
    "chunking_strategy": "semantic"
  },
  "chunks": [
    {
      "chunk_id": "doc_..._chunk_0",
      "text": "... chunk text ...",
      "word_count": 245,
      "embedding": [0.123, 0.456, ...],
      "index": 0,
      "strategy": "semantic"
    },
    // ... more chunks ...
  ]
}
```

### Search Result Structure
```json
{
  "doc_id": "doc_collection_1234567890",
  "title": "6502 Microprocessor Guide",
  "collection_id": "6502-docs",
  "chunk_id": "doc_..._chunk_5",
  "text": "... chunk text ...",
  "similarity": 0.87,
  "source": "cosmos",
  "strategy": "semantic"
}
```

---

## Implementation Examples

### Storing a Document
```python
from cosmos_storage import CosmosDBStorage

# Initialize
cosmos = CosmosDBStorage(
    endpoint=os.getenv("COSMOS_DB_ENDPOINT"),
    key=os.getenv("COSMOS_DB_KEY"),
    database_name="genai-kb",
    container_name="documents"
)

# Store document with embeddings
cosmos.store_document(
    doc_id="doc_6502-docs_0",
    collection_id="6502-docs",
    title="6502 Microprocessor Guide",
    content=full_content,
    chunks=chunks_list,
    embeddings=embeddings_list,
    metadata={"source": "pdf", "file": "guide.pdf"}
)
```

### Searching Documents
```python
# Vector search
results = cosmos.search_by_embedding(
    query_embedding=query_vector,
    collection_id="6502-docs",
    top_k=5,
    threshold=0.5
)

# Keyword search
results = cosmos.search_by_keyword(
    keyword="LDA instruction",
    collection_id="6502-docs",
    top_k=5
)
```

### Dual-Source Search
```python
from cosmos_storage import DualSourceSearch

dual_search = DualSourceSearch(local_storage, cosmos_storage)

# Search both sources
results = dual_search.search(
    query="explain LDA",
    embedding=query_vector,
    search_local=True,
    search_cosmos=True,
    top_k=5
)
```

---

## Configuration Steps

### 1. Azure CLI Setup (Automated)
```bash
# Provider registration
az provider register --namespace Microsoft.DocumentDB

# Create account (running...)
az cosmosdb create ...

# Create database
az cosmosdb sql database create ...

# Create container
az cosmosdb sql container create ...
```

### 2. Credentials Setup (Manual)
```bash
# Run after Cosmos DB is created:
python retrieve_cosmos_credentials.py

# Copy output to .env file
COSMOS_DB_ENDPOINT=...
COSMOS_DB_KEY=...
COSMOS_DB_CONNECTION_STRING=...
```

### 3. Python Environment
```bash
# Install Cosmos DB SDK
pip install azure-cosmos

# Or update requirements.txt
pip install -r requirements.txt
```

---

## Performance Considerations

### Partitioning Strategy
- **Partition Key:** `/collection_id`
- **Rationale:** Documents grouped by collection for efficient queries
- **Scalability:** Each collection scales independently

### Indexing Strategy
- **Vectors:** Indexed for similarity search
- **Metadata:** Indexed for keyword filtering
- **Partition Key:** Always indexed

### Throughput Settings
- **Development:** 400 RU/s (minimum, ~$60/month)
- **Production:** Auto-scale 4000-40000 RU/s
- **Estimate:** $0.08/hour or $60-80/month for basic use

### Query Optimization
- Use collection_id filter to limit partition range
- Batch operations when possible
- Cache frequently accessed documents

---

## Troubleshooting Guide

### Connection Issues
```python
# Test connection
cosmos = CosmosDBStorage(endpoint, key, db, container)
# Should print: "[OK] Connected to Cosmos DB"
```

### Missing Dependencies
```bash
# Install azure-cosmos
pip install azure-cosmos

# Or update all dependencies
pip install -r requirements.txt --upgrade
```

### Cosmos DB Not Found
```bash
# Check deployment status
az cosmosdb show --resource-group genai-search --name genai-cosmosdb

# Should show: "provisioningState": "Succeeded"
```

---

## Success Criteria

✅ **Phase 2 Complete When:**
1. Cosmos DB account provisioned and accessible
2. CosmosDBStorage class fully integrated
3. KB documents indexed to Cosmos DB with embeddings
4. Dual-source search working end-to-end
5. All tests passing
6. Documentation updated
7. No performance degradation vs Phase 1

---

## Next Steps

### Immediate (Today)
1. ✅ Set up Azure infrastructure
2. ✅ Create storage classes
3. ⏳ Retrieve connection credentials
4. ⏳ Update .env configuration

### This Week
1. Integrate Cosmos DB with KB manager
2. Implement embedding generation
3. Test document indexing
4. Verify dual-source search

### Following Week
1. Performance optimization
2. Advanced feature implementation
3. Production readiness review
4. Documentation polish

---

## Questions & Support

**Need help?**
- Check `AZURE_COSMOS_SETUP.md` for infrastructure details
- Review `cosmos_storage.py` for API reference
- Run diagnostic tests before deployment

**Expected wait time:**
- Cosmos DB creation: 5-10 minutes
- Database/container setup: 1-2 minutes
- Full provisioning: 10-15 minutes

Status: 🔄 **Currently provisioning Cosmos DB infrastructure**


