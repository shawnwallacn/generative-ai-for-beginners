import os
from dotenv import load_dotenv
from openai import OpenAI
from config import GITHUB_TOKEN, GITHUB_MODELS_ENDPOINT, AVAILABLE_MODELS, DEFAULT_MODEL
from github_models_api import get_available_models

load_dotenv()

def generate_text_streaming(prompt, model_name):
    """Generate text using GitHub Models with streaming output"""
    client = OpenAI(
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_MODELS_ENDPOINT
    )
    
    try:
        # Use stream=True to get streaming response
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            stream=True  # Enable streaming
        )
        
        full_response = ""
        for chunk in response:
            try:
                # Safely check for content
                if (chunk.choices and 
                    len(chunk.choices) > 0 and 
                    chunk.choices[0].delta and 
                    chunk.choices[0].delta.content):
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            except (AttributeError, IndexError, TypeError):
                # Skip chunks without content
                continue
        
        print()  # New line at the end
        return full_response
        
    except Exception as e:
        # Fallback to non-streaming if streaming fails
        print(f"(Streaming unavailable, using standard response)\n")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        result = response.choices[0].message.content
        print(result)
        return result

def display_model_options(available_models):
    """Display available models and return user choice"""
    print("\n" + "=" * 60)
    print("Available Models:")
    print("=" * 60)
    
    model_mapping = {}
    
    for choice_num, model_name in enumerate(available_models, 1):
        model_mapping[str(choice_num)] = model_name
        # Check if model is in our predefined list for description
        description = "GitHub Model"
        for key, model_info in AVAILABLE_MODELS.items():
            if model_info["name"] == model_name:
                description = model_info["description"]
                break
        print(f"{choice_num}. {model_name}")
        print(f"   {description}")
    
    if not model_mapping:
        print("No models available for your account.")
        print(f"Using default: {DEFAULT_MODEL}")
        return None
    
    print(f"\nDefault model: {DEFAULT_MODEL}")
    print("=" * 60)
    return model_mapping

def select_model(available_models):
    """Let user select a model"""
    model_mapping = display_model_options(available_models)
    
    if not model_mapping:
        return DEFAULT_MODEL
    
    while True:
        max_choice = len(model_mapping)
        choice = input(f"\nSelect a model (1-{max_choice}) or press Enter for default: ").strip()
        
        if choice == "":
            print(f"Selected model: {DEFAULT_MODEL}")
            return DEFAULT_MODEL
        
        if choice in model_mapping:
            selected_model = model_mapping[choice]
            print(f"Selected model: {selected_model}")
            return selected_model
        else:
            print(f"Invalid choice. Please select a number between 1-{max_choice}.")

def main():
    """Main interactive loop for the text generation app"""
    print("=" * 60)
    print("Welcome to the GitHub Models Text Generation App!")
    print("=" * 60)
    print("\nThis app uses GitHub Models to generate text based on your prompts.")
    print("Type 'exit' or 'quit' to end the program.")
    print("Type 'model' to change the AI model.\n")
    
    # Get available models from config
    available_models = get_available_models()
    
    if not available_models:
        print("Error: No models configured.")
        return
    
    # Initial model selection
    current_model = select_model(available_models)
    
    while True:
        try:
            # Get user input
            user_input = input("\nEnter your prompt (or command): ").strip()
            
            # Check for commands
            if user_input.lower() in ['exit', 'quit']:
                print("\nThank you for using the Text Generation App. Goodbye!")
                break
            
            if user_input.lower() == 'model':
                current_model = select_model(available_models)
                continue
            
            # Validate input
            if not user_input:
                print("Please enter a valid prompt.")
                continue
            
            # Generate text
            print(f"\nGenerating response using {current_model}...\n")
            result = generate_text_streaming(user_input, current_model)
            print("\n" + "-" * 60)
            
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()