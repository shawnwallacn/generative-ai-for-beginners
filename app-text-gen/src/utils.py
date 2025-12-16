# Utility functions for text generation app
# Reserved for future helper functions

def format_prompt(prompt: str) -> str:
    """Format the prompt for the text generation API."""
    return prompt.strip()

def handle_api_response(response) -> str:
    """Process the API response and return the generated text."""
    if response and 'choices' in response:
        return response['choices'][0]['text']
    raise ValueError("Invalid API response format.")

def log_error(error: Exception) -> None:
    """Log errors for debugging purposes."""
    print(f"Error: {error}")

def validate_token(token: str) -> bool:
    """Validate the GITHUB_TOKEN format."""
    return isinstance(token, str) and len(token) > 0

def format_response(text):
    """Format the generated text response"""
    return text.strip()

def validate_prompt(prompt):
    """Validate user prompt is not empty"""
    return prompt.strip() != ""