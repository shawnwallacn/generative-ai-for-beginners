# Next Steps: Getting Phase 1 Running

## Quick Start Checklist

### ✅ Code is Ready
- `semantic_search.py` module created
- App integration complete
- All dependencies in `requirements.txt`
- No linting errors

### 📋 To Get Phase 1 Working:

#### Step 1: Azure Setup (5-10 minutes)
```bash
# Open your terminal and run:
az login

# Then copy/paste these commands (or see SEMANTIC_SEARCH_SETUP.md):
az group create --name genai-search --location eastus

az cognitiveservices account create \
  --name genai-openai \
  --resource-group genai-search \
  --location eastus \
  --kind OpenAI \
  --sku s0

az cognitiveservices account deployment create \
  --name genai-openai \
  --resource-group genai-search \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small \
  --model-version "1" \
  --model-format OpenAI \
  --sku-capacity 100 --sku-name "Standard"

# Get credentials
az cognitiveservices account show \
  --name genai-openai \
  --resource-group genai-search | jq -r .properties.endpoint

az cognitiveservices account keys list \
  --name genai-openai \
  --resource-group genai-search | jq -r .key1
```

#### Step 2: Configure `.env` (2 minutes)
In `app-text-gen/.env`:
```env
GITHUB_TOKEN=your_github_token

AZURE_OPENAI_API_KEY=<paste_key_from_step1>
AZURE_OPENAI_ENDPOINT=<paste_endpoint_from_step1>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-15-preview

RAG_ENABLED=true
RAG_CONTEXT_CHUNKS=3
RAG_SIMILARITY_THRESHOLD=0.75
EMBEDDING_BATCH_SIZE=100
```

#### Step 3: Install Dependencies (2-5 minutes)
```bash
cd app-text-gen

# Activate venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install
pip install -r requirements.txt
```

#### Step 4: Test! (2 minutes)
```bash
python src/app.py
```

In the app:
```
1. Have a conversation:
   Enter your prompt: What is Python?
   [Let model respond]

2. Index it:
   Enter your prompt: index
   [Follow prompts]

3. Search semantically:
   Enter your prompt: semantic-search
   Enter query: programming language
   [Should find your conversation!]

4. View stats:
   Enter your prompt: embedding-stats
   [Shows your index stats]

5. Exit:
   Enter your prompt: exit
```

---

## What Gets Created Automatically

Once you start the app with proper Azure credentials:

```
app-text-gen/
├── embeddings/
│   └── conversation_embeddings.json  [AUTO-CREATED on first index]
```

The app will:
- ✅ Auto-create embeddings directory
- ✅ Initialize Azure embeddings client
- ✅ Save embeddings on `index` command
- ✅ Load embeddings on startup

---

## Files to Read

1. **SEMANTIC_SEARCH_SETUP.md** - Full detailed setup guide
2. **PHASE_1_SUMMARY.md** - Technical implementation details
3. **README.md** - Updated with new commands

---

## Estimated Time: 15-20 minutes

| Task | Time |
|------|------|
| Azure setup | 5-10 min |
| Configure .env | 2 min |
| Install dependencies | 2-5 min |
| Test the app | 2 min |
| **Total** | **15-20 min** |

---

## Questions?

If anything fails:
1. Check `.env` configuration first (most common issue)
2. Verify Azure resources created: `az cognitiveservices account list`
3. Test Azure credentials: Make sure endpoint ends with `/`
4. Check Python version: `python --version` (should be 3.9+)

---

## After Phase 1 Works

Once semantic search is working:
- 🎉 Celebrate! You've implemented lesson 08 concepts
- 📝 Try creating conversations and searching them
- 🚀 Ready for Phase 2: RAG Integration
  - Auto-inject context into responses
  - Smarter, context-aware answers
  - Coming next!

---

**Let's get Phase 1 live!** 🚀

