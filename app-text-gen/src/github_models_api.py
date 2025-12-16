"""
Utility to handle available GitHub Models
"""
from config import AVAILABLE_MODELS

def get_available_models():
    """
    Return the list of available models from config.
    These are models that your account has access to based on the config.
    """
    model_names = [model_info["name"] for model_info in AVAILABLE_MODELS.values()]
    return model_names

if __name__ == "__main__":
    models = get_available_models()
    if models:
        print(f"Available models ({len(models)}):")
        for model in models:
            print(f"  - {model}")
    else:
        print("No models found")
