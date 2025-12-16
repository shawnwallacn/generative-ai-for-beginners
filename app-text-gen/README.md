# Text Generation Application

This project is a text generation application that utilizes **GitHub Models** to generate text based on user-defined prompts. It leverages the OpenAI Python SDK to interact with GitHub's inference API, making it simple and easy to use for both beginners and experienced developers.

## Project Structure

The project is organized as follows:

```
app-text-gen
├── src
│   ├── app.py          # Main entry point of the application
│   ├── config.py       # Configuration settings and environment variable loading
│   └── utils.py        # Utility functions for API calls and response handling
├── .env                # Environment variables (GITHUB_TOKEN, etc.)
├── requirements.txt    # List of dependencies
├── tsconfig.json       # TypeScript configuration (if applicable)
└── README.md           # Documentation for the project
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

- **Generate text**: Type any prompt and press Enter
- **Switch model**: Type `model` to select a different AI model
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

- Generate text based on user-defined prompts using GitHub Models
- Configurable through environment variables for security
- Uses OpenAI Python SDK for simple, familiar API interactions
- Free tier available through GitHub Models

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.