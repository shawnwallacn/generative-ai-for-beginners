import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub Models configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com"

# Available models on GitHub Models
AVAILABLE_MODELS = {
    "1": {
        "name": "claude-3.5-haiku",
        "description": "Claude Haiku 4.5 - Small, fast model"
    },
    "2": {
        "name": "gpt-4.1",
        "description": "GPT-4.1 - Advanced model"
    },
    "3": {
        "name": "gpt-4o",
        "description": "GPT-4o - Full GPT-4 capability"
    },
    "4": {
        "name": "gpt-4o-mini",
        "description": "GPT-4o Mini - Smaller, efficient variant"
    },
    "5": {
        "name": "gpt-5-mini",
        "description": "GPT-5 Mini - Latest GPT-5 variant"
    }
}

DEFAULT_MODEL = "gpt-4o-mini"

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in environment variables")