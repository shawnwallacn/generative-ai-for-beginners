# Semantic Search Setup Guide

This guide walks you through setting up Azure OpenAI embeddings for semantic search in the text generation app.

## Overview

The app now supports **semantic search** using Azure OpenAI embeddings (text-embedding-3-small). This enables you to:
- 🔍 Search conversations using natural language (not just keywords)
- 🎯 Find semantically similar messages
- 📊 View embedding statistics
- 🚀 Prepare for Phase 2: RAG (Retrieval-Augmented Generation)

## Prerequisites

- ✅ Azure MSDN subscription (with $70/month credit)
- ✅ Azure CLI installed ([Download](https://learn.microsoft.com/cli/azure/install-azure-cli))
- ✅ GitHub Models API key (already configured)

## Step 1: Azure OpenAI Setup

### 1.1 Login to Azure CLI

```bash
az login
```

This will open your browser to authenticate. After authentication, you'll see your subscriptions listed.

### 1.2 Create Resource Group

```bash
az group create --name genai-search --location eastus
```

**Note:** If you prefer a different region, check [model availability](https://aka.ms/oai/models) first.

### 1.3 Create Azure OpenAI Resource

```bash
az cognitiveservices account create \
  --name genai-openai \
  --resource-group genai-search \
  --location eastus \
  --kind OpenAI \
  --sku s0
```

**Wait for this to complete** (takes 1-2 minutes).

### 1.4 Deploy Text Embedding Model

```bash
az cognitiveservices account deployment create \
  --name genai-openai \
  --resource-group genai-search \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small \
  --model-version "1" \
  --model-format OpenAI \
  --sku-capacity 100 --sku-name "Standard"
```

### 1.5 Get Your Credentials

Copy the commands below and run them to get your credentials:

```bash
# Get your endpoint
# Get endpoint
az cognitiveservices account show --name genai-openai --resource-group genai-search | ConvertFrom-Json | Select-Object -ExpandProperty properties | Select-Object -ExpandProperty endpoint

# Get API key
az cognitiveservices account keys list --name genai-openai --resource-group genai-search | ConvertFrom-Json | Select-Object -ExpandProperty key1
```

**Save these values!** You'll need them for the `.env` file.

## Step 2: Update Environment Variables

Open or create `.env` file in the `app-text-gen/` directory and add:

```env
# Existing - GitHub Models (Chat)
GITHUB_TOKEN=your_github_token_here

# New - Azure OpenAI (Embeddings)
AZURE_OPENAI_API_KEY=<your_key_from_step_1.5>
AZURE_OPENAI_ENDPOINT=<your_endpoint_from_step_1.5>
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Semantic Search Settings
RAG_ENABLED=true
RAG_CONTEXT_CHUNKS=3
RAG_SIMILARITY_THRESHOLD=0.75
EMBEDDING_BATCH_SIZE=100
```

**⚠️ IMPORTANT:** Never commit `.env` to git - it's already in `.gitignore`

## Step 3: Install Dependencies

```bash
# Navigate to app directory
cd app-text-gen

# Activate virtual environment (if not already active)
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

New packages installed:
- `azure-ai-inference` - Azure OpenAI embeddings
- `numpy` - Numerical operations
- `scikit-learn` - Cosine similarity calculations

## Step 4: Test the Setup

Run the app and test semantic search:

```bash
python src/app.py
```

In the app, run these test commands:

```
# Test 1: Have a conversation
Enter your prompt: What is Python?
[Model responds...]

# Test 2: Index the conversation
Enter your prompt: index
[Follow the prompts to index your conversation]

# Test 3: Search semantically
Enter your prompt: semantic-search
Enter search query: What is the programming language?
[Should find the conversation from Test 1]

# Test 4: View statistics
Enter your prompt: embedding-stats
[Shows your embedding index statistics]
```

## How It Works

### Message Pair Indexing

Conversations are indexed as **message pairs** (user + assistant exchange):

```
Message Pair 1:
  User: "How do I learn Python?"
  Assistant: "Here are the best resources..."
  Embedding: [0.123, -0.456, ..., 0.789]

Message Pair 2:
  User: "What's the difference between lists and tuples?"
  Assistant: "Lists are mutable, tuples are immutable..."
  Embedding: [0.234, -0.567, ..., 0.890]
```

### Semantic Search Process

1. **Convert Query to Embedding**
   - Your search query: "How do I start learning programming?"
   - Converted to 1536-dimensional vector

2. **Calculate Similarity**
   - Compare your query embedding against all indexed message pairs
   - Uses cosine similarity (0.0 to 1.0)

3. **Return Top Results**
   - Returns most similar message pairs
   - Sorted by relevance score
   - Shows both user question and assistant answer

### Storage

Embeddings are stored locally in:
```
app-text-gen/
├── embeddings/
│   └── conversation_embeddings.json
```

This file contains:
- All indexed message pairs
- Their embeddings (vectors)
- Similarity scores
- Metadata (model, timestamp, etc.)

## Commands Reference

### Semantic Search Commands

```
# Interactive semantic search
semantic-search

# Index current conversation with embeddings
index

# View embedding index statistics
embedding-stats
```

### Regular Search (Still Available)

```
# Keyword-based search (no embeddings)
search
```

## Cost Estimation

**Monthly Cost with your $70 MSDN Credit:**

- text-embedding-3-small: **$0.02 per 1M tokens**
- Typical usage: 100 conversations per month
- Cost for 100 conversations (~500 tokens each): **$0.001**
- Monthly searches (1,000 searches): **$0.02**

**Total: < $1/month** ✨

Your $70/month credit covers many months of usage!

## Troubleshooting

### "Azure OpenAI credentials not found"

**Solution:** Check that `.env` file has:
- `AZURE_OPENAI_API_KEY` set correctly
- `AZURE_OPENAI_ENDPOINT` set correctly
- `.env` is in the `app-text-gen/` directory (not parent)

```bash
# Verify from app-text-gen directory
cat .env | grep AZURE
```

### "Error embedding text"

**Solution:** Possible causes:
1. **Wrong deployment name** - Verify it's `text-embedding-3-small`
2. **Invalid API key** - Regenerate from Azure portal
3. **Wrong endpoint** - Should end with `/` (e.g., `https://...openai.azure.com/`)
4. **API version** - Should be `2024-02-15-preview`

### "No results found" in semantic search

**Possible reasons:**
1. No conversations have been indexed yet - run `index` command
2. Similarity threshold too high - lower `RAG_SIMILARITY_THRESHOLD` in `.env`
3. Query too different from indexed conversations

**Solution:**
```
# Lower the threshold temporarily
RAG_SIMILARITY_THRESHOLD=0.50

# Or search with more general terms
semantic-search
Enter query: Python  # More general than "advanced decorators"
```

## Next Steps

### Phase 2: RAG Integration (Coming Soon)
- Automatically inject relevant conversation context
- Enable RAG mode with `rag-mode` command
- Get smarter responses with conversation context

### Phase 3: Knowledge Base
- Upload external documents
- Build searchable knowledge base
- Use for research and reference

## Testing with Sample Data

If you want to test without manually creating conversations:

```python
# Create a few test conversations
# In the app, type various questions and save them
# Then run semantic-search to find them

# Example test prompts:
"What is machine learning?"
"How do I use Python for data science?"
"Explain neural networks"
"What's the difference between supervised and unsupervised learning?"
```

Then search for: "Tell me about AI and machine learning"

It should find your previous responses!

## Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Text Embeddings Documentation](https://learn.microsoft.com/azure/ai-services/openai/how-to/embeddings)
- [Cosine Similarity Explained](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Lesson 08: Semantic Search](../08-building-search-applications/README.md)

## Support

If you encounter issues:

1. Check `.env` configuration (most common issue)
2. Verify Azure resources were created successfully
3. Ensure embeddings model is deployed
4. Check the embedding index file: `app-text-gen/embeddings/conversation_embeddings.json`

---

**Happy semantic searching!** 🚀

Next: Phase 2 RAG Integration will enable automatic context injection for even smarter responses!

