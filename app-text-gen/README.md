# Text Generation Application with Enterprise RAG

A comprehensive AI application combining GitHub Models, Azure OpenAI, and enterprise-scale Retrieval-Augmented Generation (RAG) capabilities. Features advanced document processing, semantic search, function calling, image generation, and production-grade security.

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- GitHub account with GitHub Models access
- GitHub Personal Access Token (optional: Azure account for semantic search)

### Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd app-text-gen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure .env file
touch .env  # Windows: echo . > .env

# Add your tokens to .env:
GITHUB_TOKEN=your_github_token
AZURE_OPENAI_API_KEY=your_azure_key        # Optional - for embeddings
AZURE_OPENAI_ENDPOINT=https://...          # Optional
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=...     # Optional
COSMOS_DB_ENDPOINT=https://...              # Optional - for enterprise RAG
COSMOS_DB_KEY=your_cosmos_key               # Optional
COSMOS_DB_DATABASE_NAME=genai-kb            # Optional
COSMOS_DB_CONTAINER_NAME=documents          # Optional

# 3. Run the app
python src/app.py
```

## Project Structure

```
app-text-gen/
├── src/                          # Core application code
│   ├── app.py                    # Main entry point
│   ├── kb_manager.py             # Knowledge Base management
│   ├── embedding_generator.py    # Azure OpenAI embeddings
│   ├── cosmos_storage.py         # Cosmos DB integration
│   ├── rag.py                    # RAG engine
│   ├── semantic_search.py        # Vector search
│   ├── function_calling.py       # Function calling
│   ├── image_generator.py        # DALL-E 3
│   └── [other modules]           # Additional features
├── knowledge_base/               # KB documents and indexes
├── conversations/                # Saved conversations
├── embeddings/                   # Search indexes
├── profiles/                     # User configurations
├── generated_images/             # DALL-E outputs
├── statistics/                   # Usage stats
├── audit_logs/                   # Security audit trails
└── requirements.txt              # Dependencies
```

## Core Features

### 🔍 Enterprise RAG System
- **5 Chunking Strategies**: Paragraphs, sentences, size-based, sliding window, semantic
- **Dual-Source Search**: Local KB + Azure Cosmos DB
- **Semantic Embeddings**: Azure OpenAI 1536-dimensional vectors
- **Intelligent Caching**: Up to 1000 cached embeddings
- **Agent-Based KB Search**: LLM intelligently chooses between `search_local_kb` (fast) and `search_enterprise_kb` (comprehensive)
- **Production-Ready**: Error handling, logging, monitoring

### 💬 AI Capabilities
- Multiple model support (GPT-4, GPT-4o, Claude, etc.)
- Streaming responses
- Function calling with automatic tool invocation
- Batch processing for bulk operations
- Conversation history and management

### 🎨 Content Generation
- DALL-E 3 image generation
- Code extraction and summarization
- Template-based prompt engineering
- Conversation analysis and insights

### 🔐 Security & Privacy
- Prompt injection detection
- Sensitive data detection (emails, API keys, etc.)
- Privacy-preserving data collection
- Comprehensive audit logging
- User data controls

### 📊 Analytics & Management
- Usage statistics and cost tracking
- Feedback rating system
- Conversation search and export
- Model parameter management
- Batch job management

## Commands Reference

### Main Operations
```
kb              - Manage Knowledge Base documents
kb-search       - Search local KB (instant, manual command)
cosmos-search   - Enterprise search (dual-source, manual command)
index-kb        - Index KB for local search
semantic-search - Search conversations with embeddings

Chat with Agent Functions (Automatic):
  - search_local_kb         - Fast local KB search (agent chooses when appropriate)
  - search_enterprise_kb    - Comprehensive dual-source search (agent chooses when appropriate)

model           - Switch AI model
system          - Set system prompt
prompt          - View current prompt

history         - View conversation history
save            - Save current conversation
load            - Load saved conversation
clear           - Clear conversation

rate            - Rate last response
feedback-stats  - View feedback statistics

export          - Export conversation
analyze         - Analyze conversation
batch           - Manage batch jobs

image           - Generate image (DALL-E 3)
fc-snippets     - View extracted code snippets
fc-summaries    - View extracted summaries

privacy         - Data privacy settings
security        - Security status
audit           - View audit trail
stats           - Usage statistics

help            - Show all commands
exit/quit       - Exit program
```

## Documentation

### Getting Started
- **[RAG_QUICK_START_GUIDE.md](RAG_QUICK_START_GUIDE.md)** - Complete workflows and reference

### Feature Guides
- **[ADVANCED_CHUNKING_SUMMARY.md](ADVANCED_CHUNKING_SUMMARY.md)** - Document chunking strategies
- **[CHUNKING_QUICK_REFERENCE.md](CHUNKING_QUICK_REFERENCE.md)** - Quick reference card
- **[FUNCTION_CALLING_GUIDE.md](FUNCTION_CALLING_GUIDE.md)** - Function calling and code extraction
- **[IMAGE_GENERATION_SUMMARY.md](IMAGE_GENERATION_SUMMARY.md)** - DALL-E 3 integration
- **[PRIVACY_SETTINGS_GUIDE.md](PRIVACY_SETTINGS_GUIDE.md)** - Data privacy controls
- **[AUDIT_LOGGING_GUIDE.md](AUDIT_LOGGING_GUIDE.md)** - Security audit trail system
- **[SECURITY_FEATURES.md](SECURITY_FEATURES.md)** - Prompt injection and sensitive data detection
- **[UX_IMPROVEMENTS_SUMMARY.md](UX_IMPROVEMENTS_SUMMARY.md)** - User experience features
- **[SEMANTIC_SEARCH_SETUP.md](SEMANTIC_SEARCH_SETUP.md)** - Vector embeddings and search

### Sample Documents
See [samples/](samples/) folder for example KB documents

### Archive
Historical development documentation in [archive/](archive/) folder

## Examples

### Example 1: Add and Search KB Documents

```bash
$ python src/app.py

Enter your prompt (or command): kb

Knowledge Base Management
Documents: 5 | Collections: 2
Options:
1. Create collection
2. Add document
...

Select option (0-6): 2
Available collections:
1. tech-docs
Select collection: 1
File path: /path/to/document.pdf
Document title: My Document
Chunking strategy: 1 (Paragraphs)

[+] Document added successfully
```

### Example 2: Search with Cosmos DB

```bash
Enter your prompt (or command): cosmos-search

Enter your search query: Tell me about microprocessors

[+] Found 5 results from dual sources:

1. [cosmos_kb] Relevance: 85.3%
   Document: Introduction to Microprocessors
   Text: A microprocessor is the computational...

2. [cosmos_kb] Relevance: 82.1%
   Document: CPU Architecture
   Text: Modern processors use multi-core designs...
```

### Example 3: Generate Images

```bash
Enter your prompt (or command): image

DALL-E 3 Image Generation
Enter prompt: A futuristic city at sunset

[+] Image generated and saved to: generated_images/image_20251230_143052.png
```

## System Requirements

- **Python**: 3.9+
- **Memory**: 2GB minimum, 4GB+ recommended
- **Storage**: 5GB+ for KB and embeddings
- **Network**: Internet connection for API calls

## Environment Variables

```env
# GitHub Models (Required)
GITHUB_TOKEN=your_token

# Azure OpenAI (Optional - for embeddings)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure Cosmos DB (Optional - for enterprise RAG)
COSMOS_DB_ENDPOINT=your_endpoint
COSMOS_DB_KEY=your_key
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
```

## Key Technologies

- **LLM APIs**: GitHub Models, Azure OpenAI, OpenAI
- **Vector DB**: Azure Cosmos DB
- **Embeddings**: Azure OpenAI (1536-dimensional)
- **Python Libraries**: openai, azure-cosmos, numpy, pandas, nltk
- **Data Storage**: JSON (local), Azure Cosmos DB (cloud)

## Architecture

### Complete System Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                              │
│                    Interactive CLI (app.py)                        │
│  Commands: kb, kb-search, cosmos-search, model, image, etc.      │
└─────────────────────────────────┬─────────────────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                v                 v                 v
    ┌──────────────────────┐  ┌──────────────┐  ┌──────────────┐
    │  CONVERSATION       │  │ KNOWLEDGE    │  │  IMAGE GEN   │
    │  MANAGEMENT         │  │  BASE (KB)   │  │  DALL-E 3    │
    │                      │  │              │  │              │
    │ • History           │  │ • Add docs   │  │ • Generate   │
    │ • Save/Load         │  │ • Collections│  │ • Metadata   │
    │ • Export            │  │ • Search     │  │ • Storage    │
    │ • Analysis          │  │ • Index      │  │              │
    └──────────────────────┘  └──────────────┘  └──────────────┘
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
                    v                            v
        ┌─────────────────────────┐   ┌──────────────────────────┐
        │   RAG ENGINE            │   │   AGENT FUNCTIONS        │
        │   (embedding_generator) │   │   (function_calling)     │
        │                         │   │                          │
        │ • Generate embeddings   │   │ • search_local_kb        │
        │ • Azure OpenAI API      │   │ • search_enterprise_kb   │
        │ • Cache (1000 items)    │   │ • Tool definitions       │
        │ • Batch processing      │   │ • Execute functions      │
        │                         │   │ • Extract snippets       │
        │                         │   │ • Create summaries       │
        └─────────────────────────┘   └──────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        v           v           v
    ┌──────────┐ ┌──────────┐ ┌──────────────┐
    │  LOCAL   │ │ COSMOS   │ │  SEMANTIC    │
    │   KB     │ │   DB     │ │   SEARCH     │
    │ SEARCH   │ │ SEARCH   │ │              │
    │          │ │          │ │ • Embeddings │
    │ JSONL    │ │ Vectors  │ │ • Indexing   │
    │ Files    │ │ Cloud    │ │ • Results    │
    └──────────┘ └──────────┘ └──────────────┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┴───────────────────────┐
        │                                   │
        v                                   v
    ┌────────────────────────────┐  ┌──────────────────────┐
    │    LOCAL STORAGE LAYER     │  │  EXTERNAL SERVICES  │
    │                            │  │                      │
    │ • conversations/           │  │ • GitHub Models API  │
    │   (conversation JSON)      │  │ • Azure OpenAI API   │
    │ • knowledge_base/          │  │ • Azure Cosmos DB    │
    │   (KB docs + indexes)      │  │ • DALL-E 3 API      │
    │ • embeddings/              │  │                      │
    │   (search indexes JSONL)   │  │ Auth via:            │
    │ • profiles/                │  │ • GITHUB_TOKEN       │
    │   (user configs)           │  │ • AZURE_OPENAI_*     │
    │ • statistics/              │  │ • COSMOS_DB_*        │
    │   (usage tracking CSV)     │  │                      │
    │ • audit_logs/              │  │                      │
    │   (security events)        │  │                      │
    │ • generated_images/        │  │                      │
    │   (DALL-E outputs)         │  │                      │
    └────────────────────────────┘  └──────────────────────┘
        │                                   │
        │        Data Flow:                │
        │ ← Retrieve              Store → │
        └──────────────────────────────────┘
```

### Key Components

**User Interface Layer**
- Interactive CLI with 35+ commands
- Command routing and parsing
- Response formatting and display

**Application Layer**
- Conversation management (history, save, export)
- Knowledge Base operations (CRUD, indexing)
- RAG/Embedding operations
- Function calling execution
- Image generation

**Processing Layer**
- Embedding generation (Azure OpenAI)
- Semantic search and indexing
- Function calling with tool invocation
- Dual-source search coordination

**Storage Layer**
- Local JSON/JSONL storage (conversations, KB, indexes)
- Azure Cosmos DB (vector database)
- Audit logs (security events)
- User profiles and configurations
- Usage statistics

**External APIs**
- GitHub Models (LLM inference)
- Azure OpenAI (embeddings, chat completion)
- Azure Cosmos DB (vector storage)
- DALL-E 3 (image generation)

## Testing

Run the included test scripts to verify functionality:

```bash
# Agent-Based KB Search
pytest tests/integration/test_phase_a_kb_tools.py  # Test new KB agent functions

# Additional tests
pytest tests/                                        # Run all tests
python scripts/setup/setup_and_test_cosmos.py      # Test Cosmos DB setup
```

## Performance

- **Embedding Generation**: ~500ms (new), <5ms (cached)
- **Dual-Source Search**: ~1.5s average
- **Cache Hit Rate**: 50%+ with reuse
- **Scalability**: 1000s of documents supported

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
python -m pip install --upgrade pip
```

### Azure OpenAI not working
- Verify `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` in `.env`
- Check Azure region availability
- Ensure embedding deployment name is correct

### Cosmos DB connection issues
- Verify `COSMOS_DB_ENDPOINT` and `COSMOS_DB_KEY` in `.env`
- Check internet connection
- Ensure Azure subscription is active

## License

See LICENSE file for details

## Support

For issues or questions:
1. Check the relevant feature guide in documentation/
2. Review test scripts for usage examples
3. Check audit logs for error details

---

**Last Updated**: December 2025
**Version**: 1.1.0
**Status**: Stable, Production-Ready
