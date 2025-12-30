# Phase 2 Setup: Status & Next Steps

## Current Status: 🔄 Cosmos DB Provisioning in Progress

### Timeline
- ✅ Provider registration (Microsoft.DocumentDB)
- ✅ Initial eastus creation attempt (failed due to capacity)
- ✅ Cleanup of failed account
- 🔄 westus provisioning (in progress - 5-10 minutes expected)
- ⏳ Database and container creation
- ⏳ Credential retrieval
- ⏳ Integration and testing

---

## What's Being Created

### Azure Cosmos DB Account
```
Account Name: genai-cosmosdb
Region: westus
Consistency: Strong
API: NoSQL (SQL)
Type: GlobalDocumentDB
Status: Creating...
```

### Database & Container
```
Database Name: genai-kb
Container Name: documents
Partition Key: /collection_id
Throughput: 400 RU/s (minimum)
```

---

## Files Created & Ready

### Setup Scripts
✅ `setup_cosmos_db.py` - Initial setup orchestration
✅ `complete_cosmos_setup.py` - Complete setup with DB/container creation
✅ `retrieve_cosmos_credentials.py` - Get connection strings
✅ `test_cosmos_connection.py` - Verify connection

### Code Implementation
✅ `src/cosmos_storage.py` - Storage layer with all methods
  - `CosmosDBStorage` class
  - `DualSourceSearch` class
  - Vector search capabilities
  - Keyword search
  - Collection management

### Configuration & Documentation
✅ `requirements.txt` - Updated with azure-cosmos>=4.5.0
✅ `AZURE_COSMOS_SETUP.md` - Infrastructure guide
✅ `COSMOS_REGION_SETUP.md` - Region selection & troubleshooting
✅ `PHASE2_IMPLEMENTATION_GUIDE.md` - Complete implementation guide

---

## How to Check Provisioning Status

### Option 1: Check Terminal
Status updates will appear in the background terminal when complete

### Option 2: Manual Check via CLI
```bash
az cosmosdb show --resource-group genai-search --name genai-cosmosdb \
  --query "provisioningState" -o tsv

# Expected outputs:
# Creating   <- Still provisioning
# Succeeded  <- Ready!
# Failed     <- Try fallback region
```

### Option 3: Azure Portal
https://portal.azure.com → Search "genai-cosmosdb" in resource group

---

## What to Do When Provisioning Completes

### Step 1: Run Complete Setup (5 minutes)
```bash
cd app-text-gen
python complete_cosmos_setup.py
```
This will:
- ✅ Verify account is provisioned
- ✅ Create database
- ✅ Create container
- ✅ Retrieve credentials
- ✅ Generate .env configuration

### Step 2: Update .env File (2 minutes)
Copy the output from Step 1 to your `.env` file:
```env
COSMOS_DB_ENDPOINT=...
COSMOS_DB_KEY=...
COSMOS_DB_CONNECTION_STRING=...
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
COSMOS_DB_REGION=westus
```

### Step 3: Install SDK (1 minute)
```bash
pip install azure-cosmos
# Or update all:
pip install -r requirements.txt
```

### Step 4: Test Connection (1 minute)
```bash
python test_cosmos_connection.py
```
Should show: `[OK] COSMOS DB READY!`

### Step 5: Continue Implementation (30+ minutes)
Ready to:
- Integrate CosmosDBStorage with KB manager
- Implement document indexing
- Test dual-source search
- Verify end-to-end

---

## Estimated Timeline

| Task | Duration | Status |
|------|----------|--------|
| Cosmos DB provisioning | 5-10 min | 🔄 In progress |
| Complete setup script | 5 min | ⏳ After provision |
| .env configuration | 2 min | ⏳ After setup |
| SDK installation | 1 min | ⏳ Ready now |
| Connection test | 1 min | ⏳ After provision |
| KB integration | 30 min | ⏳ After connection |
| **Total** | **~45 min** | |

---

## What If Provisioning Fails Again?

### Plan B: Try Other Regions
```bash
# westus2
az cosmosdb delete --resource-group genai-search --name genai-cosmosdb --yes
az cosmosdb create --resource-group genai-search --name genai-cosmosdb \
  --kind GlobalDocumentDB --default-consistency-level Strong \
  --locations regionName=westus2 failoverPriority=0

# centralus
az cosmosdb create --resource-group genai-search --name genai-cosmosdb \
  --kind GlobalDocumentDB --default-consistency-level Strong \
  --locations regionName=centralus failoverPriority=0
```

### Plan C: Use Non-Zonal Deployment
If all regions fail due to zonal redundancy:
```bash
# This removes availability zone requirement
az cosmosdb create --resource-group genai-search --name genai-cosmosdb \
  --kind GlobalDocumentDB --default-consistency-level Strong \
  --locations regionName=eastus failoverPriority=0 \
  --enable-automatic-failover false
```

---

## Environment Variable Quick Reference

```env
# === Azure Cosmos DB ===
COSMOS_DB_ENDPOINT=https://genai-cosmosdb.documents.azure.com:443/
COSMOS_DB_KEY=<primary-key-from-azure>
COSMOS_DB_CONNECTION_STRING=AccountEndpoint=https://...
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
COSMOS_DB_REGION=westus

# === Existing Azure OpenAI (keep existing) ===
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT=...
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=...
AZURE_OPENAI_API_VERSION=2024-02-01

# === GitHub Models (keep existing) ===
GITHUB_TOKEN=...

# === Application Settings (keep existing) ===
DEFAULT_MODEL=gpt-4o-mini
SYSTEM_PROMPT=...
```

---

## Phase 2 Checklist

### Infrastructure
- [x] Provider registered (Microsoft.DocumentDB)
- [ ] Cosmos DB account created (westus)
- [ ] Database created (genai-kb)
- [ ] Container created (documents)
- [ ] Credentials retrieved
- [ ] .env updated
- [ ] azure-cosmos installed
- [ ] Connection tested

### Code Implementation
- [x] CosmosDBStorage class created
- [x] DualSourceSearch class created
- [ ] KB manager integration started
- [ ] Document indexing implemented
- [ ] Embedding generation added
- [ ] Dual-source search integrated
- [ ] Result merging implemented

### Testing & Validation
- [ ] Connection tests passing
- [ ] Document storage tests
- [ ] Search functionality tests
- [ ] Performance benchmarks
- [ ] End-to-end integration tests
- [ ] Audit logging integration

### Documentation
- [ ] README updated
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Configuration guide
- [ ] Troubleshooting guide

---

## Useful Commands

```bash
# Check provisioning status
az cosmosdb show --resource-group genai-search --name genai-cosmosdb \
  --query "{Name: name, Status: provisioningState}" -o table

# List all resources in group
az resource list --resource-group genai-search -o table

# Get account details
az cosmosdb show --resource-group genai-search --name genai-cosmosdb \
  --query "{Name: name, Endpoint: documentEndpoint, Region: locations[0].locationName}" -o json

# Delete if needed
az cosmosdb delete --resource-group genai-search --name genai-cosmosdb --yes
```

---

## Success Indicators

✅ **You'll know it's working when:**
1. `az cosmosdb show` returns `provisioningState: Succeeded`
2. `complete_cosmos_setup.py` generates credentials
3. `test_cosmos_connection.py` shows `[OK] COSMOS DB READY!`
4. Documents successfully indexed to Cosmos DB
5. Dual-source search returns results from both sources

---

## Support Resources

- **Azure Cosmos DB Docs:** https://docs.microsoft.com/azure/cosmos-db/
- **Python SDK:** https://docs.microsoft.com/python/api/overview/azure/cosmos-db
- **Vector Search:** https://learn.microsoft.com/azure/cosmos-db/vector-search
- **Pricing Calculator:** https://azure.microsoft.com/pricing/calculator/

---

**Last Updated:** 2025-12-30 14:30 UTC

**Provisioning Time:** Watch the background terminal for completion!

Come back and run `python complete_cosmos_setup.py` when provisioning finishes! 🚀


