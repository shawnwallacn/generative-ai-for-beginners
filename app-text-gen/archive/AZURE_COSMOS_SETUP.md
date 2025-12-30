# Azure Setup for Phase 2: Cosmos DB Integration

## Current Azure Configuration

### Account Information
- **Account**: shawn.wall@accenture.com
- **Subscription**: Visual Studio Professional Subscription (24c27a46-a775-4754-a207-2893b5903065)
- **Region**: eastus

### Existing Resources
- **Resource Group**: genai-search
- **OpenAI Resource**: genai-openai (S0 SKU)
  - Endpoint: https://eastus.api.cognitive.microsoft.com/
  - Location: eastus

### Cosmos DB Status
- **Status**: Not yet created
- **Plan**: Create new Cosmos DB account in genai-search resource group

---

## Phase 2 Implementation Plan

### Step 1: Create Azure Cosmos DB Account
```bash
# Create Cosmos DB with NoSQL API (for vector database)
az cosmosdb create \
  --resource-group genai-search \
  --name genai-cosmosdb \
  --kind GlobalDocumentDB \
  --default-consistency-level Strong \
  --locations regionName=eastus failoverPriority=0 \
  --enable-multiple-write-locations false
```

### Step 2: Create Database and Container
```bash
# Create database
az cosmosdb sql database create \
  --resource-group genai-search \
  --account-name genai-cosmosdb \
  --name genai-kb

# Create container for KB documents with vector indexing
az cosmosdb sql container create \
  --resource-group genai-search \
  --account-name genai-cosmosdb \
  --database-name genai-kb \
  --name documents \
  --partition-key-path /collection_id
```

### Step 3: Get Connection Credentials
```bash
# Get primary connection string
az cosmosdb keys list \
  --resource-group genai-search \
  --name genai-cosmosdb \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv
```

### Step 4: Update .env File
```
# Add to your .env file:
COSMOS_DB_CONNECTION_STRING=<from step 3>
COSMOS_DB_ENDPOINT=<endpoint from portal>
COSMOS_DB_KEY=<primary key>
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
```

---

## Architecture Overview

### Data Flow
```
KB Document
    ↓
PDF Parser / Text Extraction
    ↓
Advanced Chunking Strategy (5 options)
    ↓
Embedding Generation (Azure OpenAI)
    ↓
Dual Storage:
├─ Local JSONL (Conversations - existing)
└─ Azure Cosmos DB (KB Documents - new)
    ↓
Search & Retrieval (Dual-source)
    ↓
Result Ranking & Merging
    ↓
LLM Context
```

### Dual-Source Architecture
- **Local Storage (JSONL)**: Conversation history, temporary data
- **Cloud Storage (Cosmos DB)**: KB documents, vectors, metadata
- **Benefits**: 
  - Learn enterprise patterns
  - Scalable for large document libraries
  - Professional vector search
  - Maintain local privacy for conversations

---

## Implementation Tasks

### Phase 2a: Setup (Infrastructure)
- [ ] Create Cosmos DB account via Azure CLI
- [ ] Create database and containers
- [ ] Retrieve connection credentials
- [ ] Update .env configuration

### Phase 2b: Implementation (Code)
- [ ] Create `CosmosDBStorage` class
- [ ] Implement document indexing to Cosmos DB
- [ ] Add vector storage for embeddings
- [ ] Implement dual-source search

### Phase 2c: Integration (App)
- [ ] Update KB manager to use Cosmos DB
- [ ] Implement intelligent result merging
- [ ] Add Cosmos DB query logging
- [ ] Update audit trail

### Phase 2d: Testing & Documentation
- [ ] Test Cosmos DB operations
- [ ] Test dual-source search
- [ ] Verify performance
- [ ] Update README

---

## Estimated Costs

### Cosmos DB Pricing (eastus)
- **Provisioned Throughput**: 400 RU/s (minimum)
  - Hourly cost: ~$0.08/hour
  - Monthly: ~$60-80 (estimates, autopilot pricing lower)
  
- **Storage**: Per GB/month
  - First 1GB documents: included
  - Beyond 1GB: ~$0.25/GB/month

### Total Monthly Estimate
- **Free tier option**: 400 RU/s + 1GB storage (free for 12 months with Visual Studio subscription)
- **Pay-as-you-go**: $60-80/month for basic use

---

## Next Steps

1. **Run Azure CLI commands** to create infrastructure
2. **Get connection credentials** from Azure
3. **Update .env** with Cosmos DB settings
4. **Start Phase 2b** implementation with `CosmosDBStorage` class
5. **Integrate** with existing KB manager

---

## Resources

- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [Vector Search in Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/vector-search)
- [Azure CLI Cosmos DB Commands](https://docs.microsoft.com/en-us/cli/azure/cosmosdb)
- [Python SDK for Cosmos DB](https://docs.microsoft.com/en-us/python/api/overview/azure/cosmos-db)

---

## Questions Before We Proceed?

- Use the free tier on Visual Studio subscription? (Recommended)
- Different region for Cosmos DB? (eastus is current)
- Container naming conventions? (documents, chunks, vectors)
- Throughput settings? (400 RU/s is minimum, suitable for learning)

Let me know if you're ready to proceed with creating the infrastructure!

