# Text Generation Application

This project is a text generation application that utilizes **GitHub Models** to generate text based on user-defined prompts. It leverages the OpenAI Python SDK to interact with GitHub's inference API, making it simple and easy to use for both beginners and experienced developers.

## Project Structure

The project is organized as follows:

```
app-text-gen
├── src
│   ├── app.py                      # Main entry point of the application
│   ├── config.py                   # Configuration settings and model definitions
│   ├── github_models_api.py        # GitHub Models API utilities
│   ├── conversation_manager.py     # Save/load conversation functionality
│   ├── profile_manager.py          # User profile management
│   ├── prompt_templates.py         # Prompt templates for common tasks
│   ├── response_feedback.py        # Response rating and feedback system
│   ├── conversation_search.py      # Search and analyze conversations
│   ├── conversation_export.py      # Export conversations to multiple formats
│   ├── conversation_analysis.py    # Analyze conversation patterns and topics
│   ├── model_parameters.py         # Model parameter management
│   ├── batch_processing.py         # Batch job processing
│   ├── usage_stats.py              # Usage statistics and tracking
│   ├── semantic_search.py          # Semantic search with Azure OpenAI embeddings
│   ├── rag.py                      # RAG (Retrieval-Augmented Generation) engine
│   ├── kb_manager.py               # Knowledge Base document management
│   └── utils.py                    # Utility functions
├── conversations/                  # Saved conversation files (JSON format)
├── profiles/                       # User profile configurations (JSON format)
├── templates/                      # Custom prompt templates (JSON format)
├── feedback/                       # Response feedback and ratings (JSON format)
├── batch_jobs/                     # Batch processing jobs (JSON format)
├── batch_results/                  # Batch job results (CSV/JSON format)
├── exports/                        # Exported conversations (MD/CSV/HTML/TXT)
├── embeddings/                     # Embedding indexes (JSON format)
├── knowledge_base/                 # Knowledge Base documents and indexes
│   ├── collections/                # Document collections
│   ├── documents/                  # Stored documents
│   └── kb_index.json               # Knowledge Base index
├── statistics/                     # Usage statistics (CSV/JSON format)
├── .env                            # Environment variables (GITHUB_TOKEN, AZURE_OPENAI_*, etc.)
├── requirements.txt                # List of dependencies
├── check_embeddings.py             # Debug script to verify embedding index
└── README.md                       # Documentation for the project
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- A GitHub account with access to GitHub Models
- A GitHub personal access token with `repo` scope
- **(Optional) Azure subscription for semantic search** - Azure OpenAI embeddings provide semantic search capabilities (requires Azure account with OpenAI resource)

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd app-text-gen
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure GitHub Token

1. **Generate a GitHub Personal Access Token**:
   - Go to GitHub Settings → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
   - Click **Generate new token (classic)**
   - Give it a name (e.g., `ai-models-token`)
   - Select the `repo` scope
   - Click **Generate token** and copy it

2. **Create a `.env` file** in the project root:
   ```bash
   touch .env  # On Windows: echo . > .env
   ```

3. **Add your GitHub token** to the `.env` file:
   ```env
   GITHUB_TOKEN=your_github_token_here
   ```

   > ⚠️ **Important**: Never commit the `.env` file to version control. It's already in `.gitignore`.

### Step 5: Run the application

```bash
python src/app.py
```

You should see output like:
```
Prompt: Tell me a short story about a robot learning to cook.

Generated Text:
[Generated response from GitHub Models...]
```

## Virtual Environment Management

### Activating the Virtual Environment

**On Windows (PowerShell)**:
```bash
.\.venv\Scripts\Activate
```

**On Windows (Command Prompt)**:
```bash
.venv\Scripts\activate.bat
```

**On macOS/Linux**:
```bash
source venv/bin/activate
```

You should see `(.venv)` appear at the start of your prompt once activated.

### Deactivating the Virtual Environment

To exit the virtual environment, run:
```bash
deactivate
```

The `(.venv)` prefix will disappear from your prompt.

## Usage

### Running the Application

```bash
python src/app.py
```

### Interactive Features

Once the app starts, you'll see a list of available models:

```
============================================================
Available Models:
============================================================
1. claude-3.5-haiku
   Claude Haiku 4.5 - Small, fast model
2. gpt-4.1
   GPT-4.1 - Advanced model
3. gpt-4o
   GPT-4o - Full GPT-4 capability
4. gpt-4o-mini
   GPT-4o Mini - Smaller, efficient variant
5. gpt-5-mini
   GPT-5 Mini - Latest GPT-5 variant

Default model: gpt-4o-mini
============================================================
```

### Selecting a Model

1. **On startup**: Choose a model (1-5) or press Enter to use the default (`gpt-4o-mini`)
2. **During runtime**: Type `model` at any prompt to switch to a different model

### Commands

#### Chat & Text Generation
- **Generate text**: Type any prompt and press Enter to chat with the selected model
- **Switch model**: Type `model` to select a different AI model
- **Custom system prompt**: Type `system` to set custom instructions (e.g., "You are a Python expert")
- **View system prompt**: Type `prompt` to see the current system prompt

#### Prompt Templates
- **Use template**: Type `template` to select and use a pre-built prompt template
- **Create template**: Type `create-template` to create a custom reusable template
- **Available templates**: Coding Help, Creative Writing, Explain Concept, Code Review, Summarize, Brainstorm, Debug Error, Tutorial Writer

#### Response Feedback & Quality Control
- **Rate response**: Type `rate` to rate the last response (1-5 stars)
- **Flag issues**: Mark responses as having accuracy, bias, or harmful content issues
- **View feedback stats**: Type `feedback-stats` to see response rating statistics
- **View flagged responses**: Type `flagged` to see all flagged responses for review

#### Conversation Management
- **Conversation history**: Type `history` to view all messages in the current conversation
- **Save conversation**: Type `save` to save your conversation to a JSON file
- **Load conversation**: Type `load` to restore a previously saved conversation
- **Clear history**: Type `clear` to start a fresh conversation
- **Search conversations**: Type `search` to search through saved conversations by keywords
- **Export conversation**: Type `export` to export a conversation to Markdown, CSV, Plain Text, or HTML

#### Conversation Analysis
- **Analyze conversation**: Type `analyze` to see detailed analysis of a conversation
- **Analysis includes**: Message structure, word frequency, quality metrics, engagement ratio, and topic detection

#### Profile Management
- **Switch profile**: Type `profile` to load a different user profile
- **List profiles**: Type `profiles` to see all available profiles
- **View profile info**: Type `profile-info` to display current profile details
- **Create profile**: Type `new-profile` to create a new profile with custom settings
- **Save profile**: Type `save-profile` to save current model and system prompt to a profile

#### Model Parameters
- **Manage parameters**: Type `params` to adjust temperature, max tokens, and sampling parameters
- **Parameter presets**: Choose from 5 presets (Precise, Balanced, Creative, Concise, Verbose)
- **Fine-tuned control**: Adjust temperature, top_p, frequency penalty, and presence penalty

#### Batch Processing
- **Manage batches**: Type `batch` to create and manage batch jobs
- **Create from text**: Create a batch job by entering prompts directly
- **Create from file**: Import prompts from a file (TXT, CSV, or JSON)
- **Process batch**: Type `batch-run` to execute pending prompts in a batch job
- **Export results**: Export batch results to CSV or JSON format

#### Semantic Search & Embeddings
- **Semantic search**: Type `semantic-search` to find conversations by meaning
- **Index conversation**: Type `index` to generate embeddings for current conversation
- **Index KB**: Type `index-kb` to index all Knowledge Base documents with embeddings
- **KB search**: Type `kb-search` to search only Knowledge Base documents
- **View stats**: Type `embedding-stats` to see index statistics and details

#### RAG (Retrieval-Augmented Generation)
- **Configure RAG**: Type `rag` to enable/disable RAG and adjust settings
- **Auto context**: RAG automatically retrieves relevant context on every prompt (when enabled)
- **Adjust threshold**: Change similarity threshold to get more or fewer results
- **Control context**: Adjust how many context snippets are included

#### Knowledge Base Management
- **Manage KB**: Type `kb` to open knowledge base management menu
- **Create collections**: Organize documents into logical groups
- **Add documents**: Import TXT, Markdown, or PDF files
- **Index KB**: Type `index-kb` to index all KB documents with embeddings
- **Search KB**: Type `kb-search` to search only Knowledge Base documents
- **Automatic chunking**: Documents are split for optimal embedding and retrieval
- **Multiple formats**: Supports plain text, Markdown, and PDF documents

#### Usage Statistics
- **View stats**: Type `stats` to see your API usage, token counts, and cost estimates
- **Model comparison**: Compare usage and cost across different models
- **Usage trends**: Track usage by date and model
- **Export statistics**: Export usage data to CSV

#### Program Control
- **Exit**: Type `exit` or `quit` to end the program
- **Interrupt**: Press `Ctrl+C` to stop the app

### Example Session

```
Enter your prompt (or command): Tell me a joke about programming

Generating response using gpt-4o-mini...

Response:
Why do programmers prefer dark mode?

Because light attracts bugs! 🐛

------------------------------------------------------------

Enter your prompt (or command): model

============================================================
Available Models:
============================================================
1. claude-3.5-haiku
   Claude Haiku 4.5 - Small, fast model
... (model list)

Select a model (1-5) or press Enter for default: 2
Selected model: gpt-4.1

Enter your prompt (or command): exit

Thank you for using the Text Generation App. Goodbye!
```

## Advanced Features

### User Profiles

Profiles let you save and organize your preferred settings, including favorite models and system prompts. Perfect for switching between different roles or projects!

#### Creating and Managing Profiles

```
Enter your prompt (or command): new-profile
Enter a name for the new profile: python_expert
Profile 'python_expert' created and activated.

Enter your prompt (or command): system

============================================================
Set Custom System Prompt
============================================================
Current prompt: You are a helpful assistant.

Examples:
  - 'You are a Python programming expert'
  - 'You are a creative writing assistant'
  - 'You are a helpful teacher explaining concepts simply'

Enter your custom system prompt (or press Enter for default): You are an expert Python programmer with 20 years of experience
System prompt updated to: You are an expert Python programmer with 20 years of experience

Enter your prompt (or command): model

============================================================
Available Models:
============================================================
1. claude-3.5-haiku
   Claude Haiku 4.5 - Small, fast model
2. gpt-4.1
   GPT-4.1 - Advanced model
... (model list)

Select a model (1-5) or press Enter for default: 3
Selected model: gpt-4o

Enter your prompt (or command): save-profile

============================================================
Save Profile
============================================================
Current profile: python_expert

Options:
  1. Save to current profile (overwrite)
  2. Save as a new profile name

Enter your choice (1 or 2, or press Enter for option 1): 1
Profile 'python_expert' saved.
```

#### Switching Between Profiles

```
Enter your prompt (or command): profiles

============================================================
Available Profiles:
============================================================
1. default
   Model: gpt-4o-mini | Created: 2025-12-17T10:00:00
2. python_expert
   Model: gpt-4o | Created: 2025-12-17T15:30:00
3. creative_writer
   Model: claude-3.5-haiku | Created: 2025-12-17T14:15:00
============================================================

Enter your prompt (or command): profile

============================================================
Available Profiles:
============================================================
1. default
   Model: gpt-4o-mini | Created: 2025-12-17T10:00:00
2. python_expert
   Model: gpt-4o | Created: 2025-12-17T15:30:00
3. creative_writer
   Model: claude-3.5-haiku | Created: 2025-12-17T14:15:00
============================================================

Enter the number of the profile to load (or press Enter for default): 2
Loaded profile: python_expert
  Model: gpt-4o
  System Prompt: You are an expert Python programmer with 20 years of experience
```

#### Viewing Profile Details

```
Enter your prompt (or command): profile-info

============================================================
Profile: python_expert
============================================================
Model: gpt-4o
System Prompt: You are an expert Python programmer with 20 years of experience
Streaming: True
Created: 2025-12-17T15:30:00.123456
Last Used: 2025-12-17T16:45:30.654321
============================================================
```

#### Saving as New Profile

```
Enter your prompt (or command): save-profile

============================================================
Save Profile
============================================================
Current profile: python_expert

Options:
  1. Save to current profile (overwrite)
  2. Save as a new profile name

Enter your choice (1 or 2, or press Enter for option 1): 2
Enter the new profile name: advanced_python
Profile saved as 'advanced_python'.
```

**Profile Features:**
- **Automatic Loading**: Your default profile loads automatically on startup
- **Persistent Storage**: Profiles are saved as JSON files in the `profiles/` directory
- **Flexible Switching**: Switch between profiles at any time without restarting
- **Settings Persistence**: Each profile remembers your favorite model and custom system prompts
- **Flexible Saving**: Save changes to current profile or create new profiles from existing settings

### Conversation History

The app maintains a conversation history throughout your session:

```
Enter your prompt (or command): What is your name?
Generating response using gpt-4o-mini...

I'm Claude, an AI assistant made by Anthropic.

------------------------------------------------------------

Enter your prompt (or command): Do you remember what I just asked?
Generating response using gpt-4o-mini...

Yes! You just asked me what my name is, and I told you I'm Claude, an AI assistant made by Anthropic.

------------------------------------------------------------

Enter your prompt (or command): history
============================================================
Conversation History:
============================================================
1. [USER]: What is your name?
2. [ASSISTANT]: I'm Claude, an AI assistant made by Anthropic.
3. [USER]: Do you remember what I just asked?
4. [ASSISTANT]: Yes! You just asked me what my name is, and I...
============================================================
```

### Custom System Prompts

Personalize the AI's behavior by setting custom system prompts:

```
Enter your prompt (or command): system

============================================================
Set Custom System Prompt
============================================================
Current prompt: You are a helpful assistant.

Examples:
  - 'You are a Python programming expert'
  - 'You are a creative writing assistant'
  - 'You are a helpful teacher explaining concepts simply'

Enter your custom system prompt (or press Enter for default): You are an expert in 6502 assembly language

System prompt updated to: You are an expert in 6502 assembly language

Enter your prompt (or command): Explain the LDA instruction
Generating response using gpt-4o-mini...

The LDA (Load Accumulator) instruction is fundamental in 6502 assembly...
```

### Save and Load Conversations

Save your conversations to files and load them back later:

```
Enter your prompt (or command): save
Enter a name for this conversation (or press Enter for auto-generated): python_debugging_help

Conversation saved to: conversations/python_debugging_help.json

Enter your prompt (or command): load

============================================================
Saved Conversations:
============================================================
1. python_debugging_help.json
   Model: gpt-4o-mini | Messages: 8 | Time: 2025-12-17T15:30:45.123456
2. assembly_tutorial.json
   Model: gpt-4.1 | Messages: 12 | Time: 2025-12-17T14:15:22.654321
============================================================

Enter the number of the conversation to load (or press Enter to cancel): 1

Loaded conversation with 8 messages
System prompt: You are a Python programming expert
Model: gpt-4o-mini
```

Conversations are saved as JSON files in the `conversations/` directory and include:
- All messages (user and assistant)
- The system prompt used
- The model used
- Timestamp of when it was saved

### Prompt Templates

Pre-built templates speed up common tasks:

```
Enter your prompt (or command): template

============================================================
Available Prompt Templates:
============================================================
1. Coding Help
   Get help with programming problems
2. Creative Writing
   Assist with creative writing tasks
3. Explain Concept
   Explain complex concepts simply
... (8 templates total)
============================================================

Enter the number of the template to use: 1

============================================================
Using Template: Coding Help
============================================================
Description: Get help with programming problems

Template: I need help with {language} programming. {question}

Please fill in the following fields:
  language: Python
  question: How do I read a file?
```

**Built-in Templates:**
- **Coding Help**: Programming assistance with language-specific focus
- **Creative Writing**: Help with fiction, poetry, and creative content
- **Explain Concept**: Break down complex topics for any audience
- **Code Review**: Get feedback on code quality and improvements
- **Summarize Text**: Condense long text into key points
- **Brainstorm Ideas**: Generate creative ideas for projects
- **Debug Error**: Help diagnose and fix programming errors
- **Tutorial Writer**: Create step-by-step learning guides

### Response Feedback System

Rate and track response quality:

```
Enter your prompt (or command): rate

============================================================
Rate this Response
============================================================

How helpful was this response?
  1 - Not helpful at all
  2 - Somewhat unhelpful
  3 - Neutral
  4 - Helpful
  5 - Very helpful

Enter rating (1-5): 5

Does this response have any issues? (y/n): n

Any additional notes? (optional, press Enter to skip): 

Feedback saved! Thank you for your rating.
```

Then view statistics:

```
Enter your prompt (or command): feedback-stats

============================================================
Feedback Summary Statistics
============================================================

Total Responses Rated: 24
Average Rating: 4.25★ / 5★

Rating Distribution:
  ⭐⭐⭐⭐⭐ (5): 18 responses
  ⭐⭐⭐⭐  (4): 5 responses
  ⭐⭐⭐    (3): 1 responses
  ⭐⭐      (2): 0 responses
  ⭐        (1): 0 responses

Flagged Issues:
  - accuracy: 1
```

### Conversation Search & Export

Search and export your conversations:

```
Enter your prompt (or command): search

============================================================
Search Conversations
============================================================

Search by:
  1. Content (search in all messages)
  2. Prompt (search in system prompts)
  3. Model (search by model name)
  4. All (search everywhere)

Select search type: 1
Enter search query: Python

============================================================
Search Results (3 conversations found)
============================================================
...
```

Export to multiple formats:

```
Enter your prompt (or command): export

[Select conversation to export]

Export format:
  1. Markdown
  2. CSV
  3. Plain Text
  4. HTML
  5. All formats

Select format: 5
✓ Successfully exported 4 file(s):
  - exports/python_tutorial.md
  - exports/python_tutorial.csv
  - exports/python_tutorial.txt
  - exports/python_tutorial.html
```

### Conversation Analysis

Analyze patterns in your conversations:

```
Enter your prompt (or command): analyze

[Select conversation]

============================================================
Conversation Analysis: python_tutorial.json
============================================================

--- Structure ---
Total Messages:                50
User Messages:                 25
Assistant Messages:            25
Average User Message Length:   145 characters
Average Assistant Message:     320 characters

--- Quality Metrics ---
Depth:                         deep
Engagement:                    high
Length:                        long
Balance:                       well-balanced

--- Top Words (Content Frequency) ---
1. python              (15 times)
2. function            (12 times)
3. code                (11 times)
...
```

### Model Parameter Control

Fine-tune model behavior:

```
Enter your prompt (or command): params

============================================================
Model Parameters
============================================================

Options:
  1. View current parameters
  2. Set temperature
  3. Set max tokens
  4. Set top_p (nucleus sampling)
  5. Set frequency penalty
  6. Set presence penalty
  7. Configure all parameters
  8. Apply preset
  9. Reset to defaults
  0. Back to main menu
```

**Parameter Presets:**
1. **Precise/Analytical** - Factual, deterministic responses (Temperature: 0.2)
2. **Balanced** - General conversation (Temperature: 0.7) - Default
3. **Creative** - Creative writing & brainstorming (Temperature: 1.2)
4. **Concise** - Short, focused responses (Temperature: 0.5)
5. **Verbose** - Detailed, comprehensive responses (Temperature: 0.8)

### Batch Processing

Process multiple prompts efficiently:

```
Enter your prompt (or command): batch

============================================================
Batch Processing
============================================================

Options:
  1. Create batch from text input
  2. Create batch from file
  3. View batch jobs
  4. View job details
  5. Process batch job
  6. Export results
  0. Back to main menu

Select option: 1

Enter prompts (type 'DONE' on a new line to finish):
Prompt: What is Python?
Prompt: How do I use variables?
Prompt: What are functions?
Prompt: DONE

Enter model name (default: gpt-4o-mini): 

✓ Batch job created: batch_jobs/batch_20251217_114909.json
  Total prompts: 3
```

Then run the batch:

```
Enter your prompt (or command): batch-run

[Select batch job]

[1/3] Processing: "What is Python?"...
✓ Complete

[2/3] Processing: "How do I use variables?"...
✓ Complete

[3/3] Processing: "What are functions?"...
✓ Complete

============================================================
Batch Processing Complete!
✓ Processed: 3 prompts
============================================================
```

### Semantic Search with Embeddings (Phase 1: Complete ✅)

Search your conversations using AI-powered semantic search powered by Azure OpenAI embeddings:

```
Enter your prompt (or command): index

Index current conversation as 'conv_gpt-4.1_20251217_130409'? (y/n): y

Indexing conversation: conv_gpt-4.1_20251217_130409
  Generating embeddings for 2 message pairs...
  ✓ Indexed 2 message pairs
✓ Conversation indexed successfully!

Enter your prompt (or command): semantic-search

============================================================
Semantic Search
============================================================

Enter search query: register transfers

Searching embeddings for: 'register transfers'

============================================================
Semantic Search Results (2 matches)
============================================================

1. Similarity: 16.95% (Fair)
   Model: gpt-4.1 | Time: 2025-12-17T13:26:31.904354
   User:      what are the 6502 instruction set?
   Assistant: The **6502** microprocessor has a relatively small...

2. Similarity: 16.95% (Fair)
   Model: gpt-4.1 | Time: 2025-12-17T13:28:09.554621
   User:      what are the 6502 instruction set?
   Assistant: The **6502** microprocessor has a relatively small...
```

**Phase 1 Features:**
- **Conversation Indexing**: Convert conversations to semantic embeddings using Azure OpenAI
- **Semantic Search**: Find conversations by meaning, not just keywords
- **Similarity Scoring**: Results ranked by relevance (0-100%)
- **Persistent Index**: All indexed conversations stored in `embeddings/conversation_embeddings.json`
- **Batch Indexing**: Index multiple conversations efficiently
- **Cumulative Index**: New indexing adds to existing embeddings, no overwrites

**Commands:**
- `index` - Index current conversation with Azure OpenAI embeddings
- `semantic-search` - Search all indexed conversations using natural language
- `embedding-stats` - View embedding index statistics

**Setup:** See [SEMANTIC_SEARCH_SETUP.md](./SEMANTIC_SEARCH_SETUP.md) for Azure configuration.

**Configuration:**
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI resource endpoint
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` - Deployment name (default: `text-embedding-3-small`)
- `AZURE_OPENAI_API_VERSION` - API version (default: `2024-02-15-preview`)
- `RAG_SIMILARITY_THRESHOLD` - Minimum similarity score to return results (default: `0.15`)

### RAG (Retrieval-Augmented Generation) - Phase 2 (Complete ✅)

Automatically augment your chat responses with relevant context from your conversation history using AI-powered semantic search:

**How RAG Works:**
1. When you ask a question, RAG searches your indexed conversations for relevant context
2. The most relevant snippets are automatically added to the system prompt
3. The LLM uses this context to provide more accurate, informed responses
4. RAG is **enabled by default** when embeddings are available

**Example Without RAG:**
```
User: What is the LDA instruction?
LLM: The LDA instruction stands for Load Accumulator. It loads a value into the 
accumulator register from memory or an immediate value...
(Generic response from training data)
```

**Example With RAG:**
```
User: What is the LDA instruction?

[RAG] Found 3 relevant context(s):
  1. Relevance: 82.3% | Model: gpt-4.1
  2. Relevance: 78.9% | Model: gpt-4.1
  3. Relevance: 76.5% | Model: gpt-4.1

LLM: The LDA instruction, Load Accumulator, is one of the most important 6502 
instructions. Based on our previous discussions, the LDA instruction loads a value 
from memory into the accumulator register. It affects the Zero and Negative flags 
based on the loaded value... (More specific, contextual response)
```

**RAG Features:**
- **Automatic Context Retrieval**: Searches embeddings on every prompt when enabled
- **Smart Threshold**: Configurable similarity threshold (default: 0.15)
- **Adjustable Context Count**: Control how many context snippets to include (1-10, default: 3)
- **Token Awareness**: Respects max token limits for context
- **Easy Toggle**: Enable/disable RAG without restarting
- **Real-time Feedback**: See what context was retrieved and relevance scores

**Commands:**
- `rag` - Open RAG settings menu to configure or toggle RAG

**RAG Settings Menu:**
```
Enter your prompt (or command): rag

============================================================
RAG Settings
============================================================
Status: 🟢 ON | Threshold: 0.15 | Context: 3 snippets
Options:
1. Toggle RAG on/off
2. Set similarity threshold
3. Set context count (snippets)
4. Set max context tokens
0. Back to main menu

Select option (0-4): 1
✓ RAG disabled
```

**Configuration:**
- `RAG_SIMILARITY_THRESHOLD` - Minimum similarity score (0.0-1.0, default: 0.15)
- `RAG_CONTEXT_COUNT` - Number of context snippets to include (default: 3)
- `RAG_MAX_CONTEXT_TOKENS` - Maximum tokens for context (default: 2000)

**Tips for Best Results:**
- Lower the similarity threshold (try 0.10) if RAG finds no results
- Increase context count to get more diverse information
- Disable RAG for creative tasks where generic responses are better
- Use RAG for technical questions where context matters

### Knowledge Base Management (Phase 3: Complete ✅)

Add and manage external documents to create a personalized knowledge base. Documents are automatically chunked and indexed for semantic search, enhancing RAG capabilities.

**How Knowledge Base Works:**
1. Create collections (logical groups of documents)
2. Add documents (TXT, Markdown, PDF files)
3. Documents are automatically chunked for optimal embedding
4. KB documents are indexed alongside conversations
5. RAG retrieves from both conversations AND knowledge base
6. Get richer context for more informed responses

**Supported Document Formats:**
- **Plain Text (.txt)**: Simple text files, great for quick content
- **Markdown (.md)**: Formatted text with structure, preserves readability
- **PDF (.pdf)**: Complex documents, requires `pdfplumber` (optional: `pip install pdfplumber`)

**Chunking Strategies:**
- **Paragraphs** (default): Splits by paragraph breaks, best for most content
- **Sentences**: Groups sentences together, good for technical docs
- **Size-based**: Splits by character count, useful for uniform chunks

**Example Workflow:**
```
Enter your prompt (or command): kb

============================================================
Knowledge Base Management
============================================================
Documents: 0 | Collections: 0
Indexed: 0/0

Options:
1. Create collection
2. Add document to collection
3. List collections
4. List documents
5. View collection stats
6. View KB stats
0. Back to main menu

Select option (0-6): 1
Collection name: ai-research
Description: AI and ML research papers
✓ Collection 'ai-research' created

Select option (0-6): 2
Available collections:
  1. ai-research
Select collection (number): 1
File path: /path/to/document.md
Document title (optional): Neural Networks Basics

Chunking strategies:
1. Paragraphs (default)
2. Sentences
3. Size-based
Select strategy (1-3): 1

Parsing document: /path/to/document.md
Chunking with strategy: paragraphs
✓ Document added: Neural Networks Basics
  - Chunks: 12
  - Total words: 3,450
  - Document ID: doc_ai-research_0_1702900234
```

**Knowledge Base Commands:**
- `kb` - Open KB management menu
- Create collections for organizing documents
- Add documents from your filesystem
- View statistics and indexed documents
- Automatic integration with RAG for context enhancement

**KB Features:**
- **Collections**: Organize documents into logical groups
- **Automatic Chunking**: Documents split intelligently for embeddings
- **Multiple Formats**: Support TXT, Markdown, and PDF
- **Flexible Strategies**: Choose chunking method per document
- **Statistics**: Track KB size, document count, and indexing status
- **Index Management**: Auto-saves KB index to JSON
- **RAG Integration**: KB documents automatically included in RAG context (Phase 3b ✅)

### KB-RAG Integration (Phase 3b: Complete ✅)

Full integration between Knowledge Base and RAG for context-aware responses:

**How it works:**
1. Index KB documents with `index-kb` command
2. RAG automatically searches both conversations AND KB
3. Retrieved context includes both sources
4. LLM uses combined context for better responses
5. Each source is clearly labeled in the output

**Example Workflow:**
```
Enter your prompt (or command): index-kb

Indexing Knowledge Base documents...
  - Indexing Document 1 (4 chunks)...
    [+] Indexed successfully (4 chunks added)

Indexing complete:
  Documents indexed: 2
  Total chunks: 6

Enter your prompt (or command): what is the lda instruction?

[RAG] Found 3 relevant context(s):
  1. [KB Document] Relevance: 47.5% | 6502 Microprocessor Guide
  2. [Conversation] Relevance: 41.8% | gpt-4.1

The **LDA** instruction stands for **Load Accumulator**...
[Uses KB document context for accurate response]
```

**KB-RAG Features:**
- **Automatic Context Mixing**: Combines KB and conversation context
- **Source Attribution**: Shows which KB doc or conversation provided context
- **Relevance Ranking**: Results sorted by similarity score
- **Flexible Thresholds**: Adjust similarity threshold for more/fewer results
- **Separate Search**: `kb-search` command to search KB only
- **Index Status**: `embedding-stats` shows KB + conversation entries

**New Commands:**
- `index-kb` - Index all KB documents with embeddings
- `kb-search` - Search only KB documents

### Usage Statistics & Monitoring

Track your API usage and costs:

```
Enter your prompt (or command): stats

============================================================
Usage Statistics
============================================================

Options:
  1. View overall statistics
  2. Compare model usage
  3. Export statistics to CSV
  0. Back to main menu

Select option: 1

Overall Statistics:

Total Requests:            45
Total Tokens Used:         12,345
Average Tokens/Request:    274
Estimated Total Cost:      $0.018543

By Model:
  gpt-4o-mini
    - Requests: 30
    - Tokens: 8,200
    - Cost: $0.001230

  gpt-4.1
    - Requests: 15
    - Tokens: 4,145
    - Cost: $0.002493
```

## Understanding GitHub Models

**GitHub Models** provides free access to state-of-the-art AI models through GitHub. This project uses:

- **Endpoint**: `https://models.inference.ai.azure.com`
- **Authentication**: GitHub Personal Access Token with `repo` scope
- **Supported Models**: Claude, GPT-4, GPT-5, and more

When you call the OpenAI SDK with GitHub's endpoint and your token, requests are routed to GitHub's inference infrastructure, which provides the actual LLM responses.

### How It Works

1. The app initializes an OpenAI client pointing to GitHub's endpoint
2. Your `GITHUB_TOKEN` authenticates the request
3. Your chosen prompt is sent to the selected model
4. The generated response is returned and displayed

### Available Models

Your account may have access to different models based on availability. The currently supported models are configured in [src/config.py](src/config.py):

- **claude-3.5-haiku**: Anthropic's small, fast Claude model
- **gpt-4.1**: OpenAI's advanced GPT-4.1
- **gpt-4o**: OpenAI's full GPT-4o capability
- **gpt-4o-mini**: OpenAI's smaller, efficient GPT-4 variant (default)
- **gpt-5-mini**: OpenAI's latest GPT-5 mini variant

You can add or remove models by editing the `AVAILABLE_MODELS` dictionary in [src/config.py](src/config.py).

## Features

### Core Features
- **Multi-Model Support**: Choose from multiple GitHub Models (GPT-4, Claude, etc.)
- **Streaming Responses**: See responses appear word-by-word in real-time
- **Conversation History**: Maintain context across multiple messages in a single session
- **Custom System Prompts**: Define custom instructions to personalize AI behavior
- **Save/Load Conversations**: Save conversations to JSON files and resume them later
- **Interactive Commands**: Simple text commands for all functionality
- **Environment-based Configuration**: Secure API key management via `.env` file
- **Free Access**: Leverages GitHub Models for free tier availability

### Advanced Features
- **Prompt Templates**: 8 built-in templates + create custom templates with dynamic placeholders
- **Response Feedback**: 5-star rating system with issue flagging (accuracy, bias, harmful)
- **Conversation Search**: Search by content, system prompts, or model usage
- **Conversation Export**: Export to Markdown, CSV, Plain Text, or HTML formats
- **Conversation Analysis**: Detailed analysis including word frequency, quality metrics, and engagement
- **Model Parameters**: Fine-tune temperature, max tokens, top_p, frequency/presence penalties
- **Parameter Presets**: 5 pre-configured profiles (Precise, Balanced, Creative, Concise, Verbose)
- **User Profiles**: Save and switch between different role-based configurations
- **Batch Processing**: Process multiple prompts in batches with progress tracking
- **Usage Statistics**: Track API calls, token usage, cost estimates, and model comparison
- **Multiple Export Formats**: Export conversations and batch results to various formats
- **Semantic Search with Embeddings**: Find conversations by meaning using Azure OpenAI embeddings (Phase 1 ✅)
- **RAG (Retrieval-Augmented Generation)**: Automatic context retrieval augments LLM responses with relevant conversation history (Phase 2 ✅)
- **Knowledge Base Management**: Add and manage external documents for enhanced context (Phase 3 ✅)
- **KB-RAG Integration**: Search both conversations and KB documents for comprehensive context (Phase 3b ✅)

### Quality & Monitoring
- **Feedback System**: Rate and flag responses for quality assurance
- **Analytics**: Comprehensive conversation analysis and topic detection
- **Usage Tracking**: Monitor token consumption and estimated costs
- **Performance Monitoring**: Track response quality and engagement metrics

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.