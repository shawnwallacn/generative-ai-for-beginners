import os
from dotenv import load_dotenv
from openai import OpenAI
from config import GITHUB_TOKEN, GITHUB_MODELS_ENDPOINT, AVAILABLE_MODELS, DEFAULT_MODEL
from github_models_api import get_available_models
from conversation_manager import save_conversation, load_conversation, display_saved_conversations, delete_conversation
from profile_manager import (
    load_profile, save_profile, create_default_profile, list_profiles,
    display_profiles, apply_profile_settings, update_profile_settings
)

load_dotenv()

# Conversation history storage
conversation_history = []

# System prompt/custom instructions
system_prompt = "You are a helpful assistant."
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

# Current model (will be set during initialization)
current_model = DEFAULT_MODEL

# Current profile
current_profile = None
profile_name = "default"

def generate_text_streaming(prompt, model_name):
    """Generate text using GitHub Models with streaming output and conversation context"""
    client = OpenAI(
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_MODELS_ENDPOINT
    )
    
    # Add user message to conversation history
    conversation_history.append({
        "role": "user",
        "content": prompt
    })
    
    try:
        # Use stream=True to get streaming response
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history  # Include full conversation history
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
        
        # Add assistant response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        return full_response
        
    except Exception as e:
        # Fallback to non-streaming if streaming fails
        print(f"(Streaming unavailable, using standard response)\n")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history
            ],
            temperature=0.7,
            max_tokens=500
        )
        result = response.choices[0].message.content
        print(result)
        
        # Add to history
        conversation_history.append({
            "role": "assistant",
            "content": result
        })
        
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

def display_conversation_history():
    """Display the current conversation history"""
    if not conversation_history:
        print("\nNo conversation history yet.")
        return
    
    print("\n" + "=" * 60)
    print("Conversation History:")
    print("=" * 60)
    for i, message in enumerate(conversation_history, 1):
        role = message["role"].upper()
        content = message["content"]
        # Truncate long messages for display
        if len(content) > 100:
            content = content[:100] + "..."
        print(f"{i}. [{role}]: {content}")
    print("=" * 60)

def clear_conversation_history():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    print("Conversation history cleared.")

def set_system_prompt():
    """Allow user to set a custom system prompt"""
    global system_prompt
    print("\n" + "=" * 60)
    print("Set Custom System Prompt")
    print("=" * 60)
    print(f"Current prompt: {system_prompt}\n")
    
    print("Examples:")
    print("  - 'You are a Python programming expert'")
    print("  - 'You are a creative writing assistant'")
    print("  - 'You are a helpful teacher explaining concepts simply'\n")
    
    custom_prompt = input("Enter your custom system prompt (or press Enter for default): ").strip()
    
    if custom_prompt:
        system_prompt = custom_prompt
        print(f"\nSystem prompt updated to: {system_prompt}")
    else:
        system_prompt = DEFAULT_SYSTEM_PROMPT
        print(f"\nSystem prompt reset to default: {system_prompt}")

def display_system_prompt():
    """Display the current system prompt"""
    print("\n" + "=" * 60)
    print("Current System Prompt:")
    print("=" * 60)
    print(system_prompt)
    print("=" * 60)

def save_current_conversation():
    """Save the current conversation to a file"""
    global current_model
    
    if not conversation_history:
        print("No conversation to save.")
        return
    
    name = input("Enter a name for this conversation (or press Enter for auto-generated): ").strip()
    
    if name:
        filename = os.path.join("conversations", f"{name}.json")
    else:
        filename = None
    
    try:
        saved_file = save_conversation(conversation_history, system_prompt, current_model, filename)
        print(f"Conversation saved to: {saved_file}")
    except Exception as e:
        print(f"Error saving conversation: {e}")

def load_saved_conversation():
    """Load a saved conversation"""
    global conversation_history, system_prompt
    
    files = display_saved_conversations()
    if not files:
        return
    
    try:
        choice = input("\nEnter the number of the conversation to load (or press Enter to cancel): ").strip()
        
        if not choice:
            return
        
        choice_num = int(choice) - 1
        if 0 <= choice_num < len(files):
            filename = os.path.join("conversations", files[choice_num])
            messages, prompt, model = load_conversation(filename)
            
            if messages is not None:
                conversation_history = messages
                system_prompt = prompt
                print(f"\nLoaded conversation with {len(messages)} messages")
                print(f"System prompt: {system_prompt}")
                print(f"Model: {model}")
            else:
                print("Error loading conversation.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error loading conversation: {e}")

def select_profile():
    """Select or create a user profile"""
    global current_profile, profile_name, current_model, system_prompt
    
    profiles = display_profiles()
    
    if not profiles:
        profile_name = "default"
        current_profile = create_default_profile()
        save_profile(current_profile, profile_name)
        return
    
    try:
        choice = input("\nEnter the number of the profile to load (or press Enter for default): ").strip()
        
        if not choice or choice == "1":
            profile_name = "default"
        else:
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(profiles):
                profile_name = profiles[choice_num]
            else:
                print("Invalid choice. Using default profile.")
                profile_name = "default"
    except ValueError:
        print("Invalid input. Using default profile.")
        profile_name = "default"
    
    # Load the profile
    current_profile = load_profile(profile_name)
    if current_profile is None:
        current_profile = create_default_profile()
    
    # Apply profile settings
    settings = apply_profile_settings(current_profile)
    current_model = settings["model"]
    system_prompt = settings["system_prompt"]
    
    print(f"\nLoaded profile: {profile_name}")
    print(f"  Model: {current_model}")
    print(f"  System Prompt: {system_prompt}")

def save_current_profile():
    """Save current settings to the active profile or a new named profile"""
    global current_profile, profile_name, current_model, system_prompt
    
    if not current_profile:
        print("No profile loaded.")
        return
    
    # Ask user if they want to save to current profile or save as a new name
    print("\n" + "=" * 60)
    print("Save Profile")
    print("=" * 60)
    print(f"Current profile: {profile_name}")
    print("\nOptions:")
    print("  1. Save to current profile (overwrite)")
    print("  2. Save as a new profile name")
    
    choice = input("\nEnter your choice (1 or 2, or press Enter for option 1): ").strip()
    
    # Update current profile with latest settings
    current_profile = update_profile_settings(
        current_profile,
        model=current_model,
        system_prompt=system_prompt
    )
    
    if choice == "2":
        # Save as new profile
        new_name = input("Enter the new profile name: ").strip()
        
        if not new_name or new_name == "default":
            print("Invalid profile name. Profile not saved.")
            return
        
        if new_name in list_profiles():
            overwrite = input(f"Profile '{new_name}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Profile not saved.")
                return
        
        current_profile["name"] = new_name
        save_profile(current_profile, new_name)
        profile_name = new_name
        print(f"Profile saved as '{new_name}'.")
    else:
        # Save to current profile (default)
        save_profile(current_profile, profile_name)
        print(f"Profile '{profile_name}' saved.")
def view_profile_details():
    """Display detailed information about the current profile"""
    global current_profile, profile_name
    
    if not current_profile:
        print("No profile loaded.")
        return
    
    print("\n" + "=" * 60)
    print(f"Profile: {profile_name}")
    print("=" * 60)
    print(f"Model: {current_profile.get('favorite_model', 'Unknown')}")
    print(f"System Prompt: {current_profile.get('system_prompt', 'Unknown')}")
    print(f"Streaming: {current_profile.get('streaming_enabled', True)}")
    print(f"Created: {current_profile.get('created_at', 'Unknown')}")
    print(f"Last Used: {current_profile.get('last_used', 'Unknown')}")
    print("=" * 60)
def create_new_profile():
    """Create a new user profile"""
    global current_profile, profile_name, current_model, system_prompt
    
    new_name = input("Enter a name for the new profile: ").strip()
    
    if not new_name or new_name == "default":
        print("Invalid profile name.")
        return
    
    if new_name in list_profiles():
        print(f"Profile '{new_name}' already exists.")
        return
    
    # Create new profile with current settings
    new_profile = create_default_profile()
    new_profile["name"] = new_name
    new_profile["favorite_model"] = current_model
    new_profile["system_prompt"] = system_prompt
    
    save_profile(new_profile, new_name)
    print(f"Profile '{new_name}' created and activated.")
    
    current_profile = new_profile
    profile_name = new_name

def main():
    """Main interactive loop for the text generation app"""
    global current_model, current_profile, profile_name
    
    print("=" * 60)
    print("Welcome to the GitHub Models Text Generation App!")
    print("=" * 60)
    print("\nLoading user profile...")
    
    # Load user profile (automatically sets current_model and system_prompt from profile)
    select_profile()
    
    print("\nThis app uses GitHub Models to generate text based on your prompts.")
    print("Commands:")
    print("  - Type your prompt and press Enter to chat")
    print("  - Type 'model' to change the AI model")
    print("  - Type 'profile' to switch user profiles")
    print("  - Type 'profiles' to list all available profiles")
    print("  - Type 'profile-info' to view current profile details")
    print("  - Type 'new-profile' to create a new profile")
    print("  - Type 'save-profile' to save profile settings")
    print("  - Type 'system' to set custom system prompt/instructions")
    print("  - Type 'prompt' to view current system prompt")
    print("  - Type 'history' to view conversation history")
    print("  - Type 'save' to save current conversation")
    print("  - Type 'load' to load a saved conversation")
    print("  - Type 'clear' to clear conversation history")
    print("  - Type 'exit' or 'quit' to end the program\n")
    
    # Get available models from config
    available_models = get_available_models()
    
    if not available_models:
        print("Error: No models configured.")
        return
    
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
            
            if user_input.lower() == 'system':
                set_system_prompt()
                continue
            
            if user_input.lower() == 'prompt':
                display_system_prompt()
                continue
            
            if user_input.lower() == 'history':
                display_conversation_history()
                continue
            
            if user_input.lower() == 'clear':
                clear_conversation_history()
                continue
            
            if user_input.lower() == 'save':
                save_current_conversation()
                continue
            
            if user_input.lower() == 'load':
                load_saved_conversation()
                continue
            
            if user_input.lower() == 'profile':
                select_profile()
                continue
            
            if user_input.lower() == 'new-profile':
                create_new_profile()
                continue
            
            if user_input.lower() == 'save-profile':
                save_current_profile()
                continue
            
            if user_input.lower() == 'profiles':
                display_profiles()
                continue
            
            if user_input.lower() == 'profile-info':
                view_profile_details()
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