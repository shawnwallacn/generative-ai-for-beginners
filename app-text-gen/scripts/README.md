# Scripts Directory

Utility and setup scripts for app-text-gen.

## Structure

```
scripts/
├── setup/             # Azure Cosmos DB setup scripts
│   ├── setup_cosmos_db.py              # Create Cosmos DB account
│   ├── complete_cosmos_setup.py        # Create database and container
│   ├── setup_and_test_cosmos.py        # Setup and test
│   └── retrieve_cosmos_credentials.py  # Retrieve existing credentials
│
└── diagnostics/       # Verification and diagnostic scripts
    ├── check_dalle3.py       # Verify DALL-E 3 setup
    └── check_embeddings.py   # Verify embeddings work
```

## Setup Scripts

### setup_cosmos_db.py
Creates an Azure Cosmos DB account.

```bash
python scripts/setup/setup_cosmos_db.py
```

**Requirements:**
- Azure CLI installed
- Azure subscription
- Logged in with `az login`

**Output:**
- Cosmos DB account created
- Endpoint and key provided

### complete_cosmos_setup.py
Creates database and container after account setup.

```bash
python scripts/setup/complete_cosmos_setup.py
```

**Requirements:**
- Cosmos DB account already created
- Azure credentials in `.env`

**Creates:**
- Database: `genai-kb`
- Container: `documents`

### setup_and_test_cosmos.py
Combined setup and verification script.

```bash
python scripts/setup/setup_and_test_cosmos.py
```

### retrieve_cosmos_credentials.py
Retrieves credentials from existing Cosmos DB account.

```bash
python scripts/setup/retrieve_cosmos_credentials.py
```

## Diagnostic Scripts

### check_dalle3.py
Verifies DALL-E 3 is properly configured and working.

```bash
python scripts/diagnostics/check_dalle3.py
```

**Checks:**
- Azure OpenAI API key
- DALL-E 3 model availability
- Test image generation

### check_embeddings.py
Verifies embedding generation is working.

```bash
python scripts/diagnostics/check_embeddings.py
```

**Checks:**
- Azure OpenAI API key
- Embedding model availability
- Sample embedding generation
- Embedding dimension

## Environment Configuration

All scripts use environment variables from `.env`:

```env
# Azure Cosmos DB
COSMOS_DB_ENDPOINT=https://...
COSMOS_DB_KEY=...
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small
```

## Quick Start

### First-time Cosmos DB setup:
```bash
# 1. Create account
python scripts/setup/setup_cosmos_db.py

# 2. Update .env with credentials

# 3. Create database and container
python scripts/setup/complete_cosmos_setup.py

# 4. Verify setup
python scripts/setup/setup_and_test_cosmos.py
```

### Verify services:
```bash
# Check DALL-E 3
python scripts/diagnostics/check_dalle3.py

# Check embeddings
python scripts/diagnostics/check_embeddings.py
```

## Troubleshooting

### Script fails to find Azure CLI
- Install Azure CLI: `choco install azure-cli` (Windows) or `brew install azure-cli` (Mac)
- Or download from: https://docs.microsoft.com/cli/azure/install-azure-cli

### Azure authentication fails
- Run: `az login`
- Select subscription: `az account set -s <subscription-id>`

### Cosmos DB creation fails
- Check Azure subscription has capacity
- Try different region if current one is unavailable
- Check Azure quotas

### Environment variables not found
- Create `.env` file in project root
- Add required variables (see Environment Configuration)
- Scripts use `python-dotenv` to load them

