# Azure Cosmos DB Setup - Region Selection & Troubleshooting

## Issue: Zonal Redundancy Capacity Constraint

### What Happened
When trying to create Cosmos DB in `eastus` region, Azure returned:
```
ServiceUnavailable: High demand in East US region for zonal redundant accounts
```

### Solution
Azure Cosmos DB accounts support **Availability Zones** (zonal redundancy) by default, which has capacity constraints in some regions. We're switching to `westus` which has better availability.

---

## Region Options

### Current Attempt: `westus`
- **Status:** Provisioning
- **Latency from Virginia:** ~40ms
- **Typical availability:** Good
- **Use case:** General purpose, learning/development

### Alternatives if westus fails:

| Region | Availability | Notes |
|--------|-------------|-------|
| westus2 | High | Secondary US West region |
| centralus | High | Central United States |
| canadaeast | High | Canada (if data residency needed) |
| northeurope | High | Ireland (lowest latency if in EU) |

---

## Updated Configuration

### New Setup for `westus`

```env
# Azure Cosmos DB Configuration (westus)
COSMOS_DB_ENDPOINT=https://genai-cosmosdb.documents.azure.com:443/
COSMOS_DB_KEY=<primary-key>
COSMOS_DB_CONNECTION_STRING=<connection-string>
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
COSMOS_DB_REGION=westus
```

---

## Fallback Procedure

If westus also fails, try these commands in order:

### Fallback 1: westus2
```bash
az cosmosdb create \
  --resource-group genai-search \
  --name genai-cosmosdb \
  --kind GlobalDocumentDB \
  --default-consistency-level Strong \
  --locations regionName=westus2 failoverPriority=0
```

### Fallback 2: centralus
```bash
az cosmosdb create \
  --resource-group genai-search \
  --name genai-cosmosdb \
  --kind GlobalDocumentDB \
  --default-consistency-level Strong \
  --locations regionName=centralus failoverPriority=0
```

### Fallback 3: Disable Zone Redundancy (if needed)
```bash
# This removes availability zone redundancy - reduces resilience but works everywhere
az cosmosdb create \
  --resource-group genai-search \
  --name genai-cosmosdb \
  --kind GlobalDocumentDB \
  --default-consistency-level Strong \
  --locations regionName=eastus failoverPriority=0 \
  --enable-automatic-failover false
```

---

## Why This Happens

### Zonal Redundancy (Default)
- **What it is:** Data replicated across 3 availability zones
- **Benefit:** High availability, disaster recovery
- **Cost:** Slightly higher (automatic failover)
- **Issue:** Limited capacity in some regions due to high demand

### Non-Zonal (Alternative)
- **What it is:** Single zone deployment
- **Benefit:** Works everywhere, cheaper
- **Issue:** Lower availability (only one zone)
- **Use:** Development, learning environments

---

## Monitoring Progress

### Check Provisioning Status
```bash
# While creating:
az cosmosdb show \
  --resource-group genai-search \
  --name genai-cosmosdb \
  --query "{Name: name, Status: provisioningState}" -o table

# Expected outputs while creating:
# Status: Creating
# Status: Succeeded  ← Creation complete
# Status: Failed     ← Try fallback region
```

### When Creation Completes
Run credential retrieval:
```bash
python retrieve_cosmos_credentials.py
```

This will output all connection strings automatically.

---

## Next Steps

1. **Wait for westus provisioning** (5-10 minutes)
2. **Verify success:**
   ```bash
   az cosmosdb show --resource-group genai-search --name genai-cosmosdb
   ```
3. **Retrieve credentials:**
   ```bash
   python retrieve_cosmos_credentials.py
   ```
4. **Update .env with credentials**
5. **Continue Phase 2 implementation**

---

## Performance Impact

### Latency Comparison
- **eastus:** ~20ms from Azure OpenAI (same region)
- **westus:** ~40ms from Azure OpenAI (slight latency)
- **Impact:** Negligible for learning/development
- **Production:** May want multi-region for resilience

---

## Cost Impact

### Regional Pricing (Approximate)
- **Zonal Redundant:** $60-80/month (400 RU/s)
- **Non-Zonal:** $50-60/month (400 RU/s)
- **Free tier:** Still applies (12 months on VS subscription)

### Free Tier Details
- First 1 GB/month: Free
- First 400 RU/s: Free
- 12 months on Visual Studio Professional subscription
- Perfect for development!

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| ServiceUnavailable | Try different region (westus, westus2, centralus) |
| Subscription not registered | Run: `az provider register --namespace Microsoft.DocumentDB` |
| Access Denied | Check: `az account show` - verify correct subscription |
| Container not found | Database/container may not exist yet - run setup |
| Connection timeout | Verify endpoint URL and network connectivity |

---

## Status Tracking

- [ ] westus provisioning initiated
- [ ] Provisioning complete (check status)
- [ ] Database and containers created
- [ ] Credentials retrieved
- [ ] .env configuration updated
- [ ] azure-cosmos installed
- [ ] Integration tests passing

---

**Current Status:** Provisioning Cosmos DB in westus region...

Check back in 5-10 minutes to see provisioning status!


