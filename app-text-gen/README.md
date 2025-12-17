# Text Generation Application

This project is a text generation application that utilizes **GitHub Models** to generate text based on user-defined prompts. It leverages the OpenAI Python SDK to interact with GitHub's inference API, making it simple and easy to use for both beginners and experienced developers.

## Project Structure

The project is organized as follows:

```
app-text-gen
├── src
│   ├── app.py                    # Main entry point of the application
│   ├── config.py                 # Configuration settings and model definitions
│   ├── github_models_api.py      # GitHub Models API utilities
│   ├── conversation_manager.py   # Save/load conversation functionality
│   └── utils.py                  # Utility functions
├── conversations/                # Saved conversation files (JSON format)
├── .env                          # Environment variables (GITHUB_TOKEN, etc.)
├── requirements.txt              # List of dependencies
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # Documentation for the project
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- A GitHub account with access to GitHub Models
- A GitHub personal access token with `repo` scope

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
.\.venv\Scripts\Activate.ps1
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

#### Conversation Management
- **Conversation history**: Type `history` to view all messages in the current conversation
- **Save conversation**: Type `save` to save your conversation to a JSON file
- **Load conversation**: Type `load` to restore a previously saved conversation
- **Clear history**: Type `clear` to start a fresh conversation

#### Profile Management
- **Switch profile**: Type `profile` to load a different user profile
- **List profiles**: Type `profiles` to see all available profiles
- **View profile info**: Type `profile-info` to display current profile details
- **Create profile**: Type `new-profile` to create a new profile with custom settings
- **Save profile**: Type `save-profile` to save current model and system prompt to a profile

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

- **Multi-Model Support**: Choose from multiple GitHub Models (GPT-4, Claude, etc.)
- **Streaming Responses**: See responses appear word-by-word in real-time
- **Conversation History**: Maintain context across multiple messages in a single session
- **Custom System Prompts**: Define custom instructions to personalize AI behavior (e.g., "Act as a Python expert")
- **Save/Load Conversations**: Save conversations to JSON files and resume them later
- **Interactive Commands**: Simple text commands for all functionality
- **Environment-based Configuration**: Secure API key management via `.env` file
- **Free Access**: Leverages GitHub Models for free tier availability

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.