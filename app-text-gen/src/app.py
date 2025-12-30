import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from config import GITHUB_TOKEN, GITHUB_MODELS_ENDPOINT, AVAILABLE_MODELS, DEFAULT_MODEL
from github_models_api import get_available_models
from conversation_manager import save_conversation, load_conversation, display_saved_conversations, delete_conversation
from profile_manager import (
    load_profile, save_profile, create_default_profile, list_profiles,
    display_profiles, apply_profile_settings, update_profile_settings
)
from prompt_templates import (
    display_templates, get_template_by_index, fill_template, 
    save_custom_template, list_all_templates
)
from response_feedback import (
    display_feedback_prompt, save_feedback, display_feedback_summary,
    display_flagged_feedback
)
from conversation_search import (
    interactive_search, display_conversation_stats
)
from conversation_export import interactive_export
from model_parameters import ModelParameters, display_parameter_presets, apply_preset
from conversation_analysis import interactive_analysis
from batch_processing import interactive_batch_processor, process_batch_job, list_batch_jobs
from usage_stats import record_request, interactive_stats_menu
from semantic_search import EmbeddingIndex, interactive_semantic_search, display_search_results
from rag import RAGEngine, interactive_rag_settings
from kb_manager import KnowledgeBase, interactive_kb_menu
from image_generator import ImageGenerator, interactive_image_generator
from function_calling import FunctionDefinitions, FunctionExecutor
from ux_improvements import (
    ErrorMessages, ResponseTransparency, HelpfulTips, 
    DataTransparency, ConversationStarters
)
from privacy_settings import PrivacySettings
from security import (
    PromptInjectionDetector, SensitiveDataDetector, RateLimiter, 
    InputValidator, display_security_status
)
from audit_logger import AuditLogger, display_audit_summary, display_recent_events, display_security_incidents
import security  # For setting the audit_logger reference
import kb_manager  # For sharing audit_logger

load_dotenv()

# Initialize model parameters
model_params = ModelParameters()

# Initialize audit logger
audit_logger = AuditLogger()
security.audit_logger = audit_logger  # Share with security module
kb_manager.audit_logger = audit_logger  # Share with kb_manager module

# Initialize security components
prompt_injection_detector = PromptInjectionDetector()
sensitive_data_detector = SensitiveDataDetector()
rate_limiter = RateLimiter()
input_validator = InputValidator()

# Initialize embedding index for semantic search
try:
    embedding_index = EmbeddingIndex()
    semantic_search_available = True
except Exception as e:
    print(f"Warning: Semantic search not available: {e}")
    embedding_index = None
    semantic_search_available = False

# Initialize RAG engine
try:
    rag_engine = RAGEngine(embedding_index)
    # Enable RAG by default if available
    if embedding_index:
        rag_engine.enable()
except Exception as e:
    print(f"Warning: RAG engine not available: {e}")
    rag_engine = None

# Initialize Knowledge Base
try:
    knowledge_base = KnowledgeBase()
except Exception as e:
    print(f"Warning: Knowledge Base not available: {e}")
    knowledge_base = None

# Initialize Image Generator
try:
    image_generator = ImageGenerator()
    image_generation_available = True
except Exception as e:
    print(f"Warning: Image generation not available: {e}")
    image_generator = None
    image_generation_available = False

# Initialize Function Calling
try:
    function_executor = FunctionExecutor(
        kb_manager=knowledge_base,
        semantic_search_index=embedding_index
    )
    function_calling_available = True
except Exception as e:
    print(f"Warning: Function calling not available: {e}")
    function_executor = None
    function_calling_available = False

# Initialize Privacy Settings
try:
    privacy_settings = PrivacySettings()
except Exception as e:
    print(f"Warning: Privacy settings not available: {e}")
    privacy_settings = None

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

# Track last response for feedback
last_response = None
last_prompt = None

def handle_function_calls(messages, model_name):
    """
    Handle function calling in the chat flow.
    
    Steps:
    1. Call the LLM with function definitions
    2. Check if the LLM wants to call a function
    3. Execute the function if needed
    4. Call the LLM again with function results
    
    Returns:
        (final_response, function_calls_made)
    """
    if not function_executor or not function_calling_available:
        return None, False
    
    client = OpenAI(
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_MODELS_ENDPOINT
    )
    
    params = model_params.get_all_parameters()
    
    try:
        # Step 1: Call LLM with function definitions
        print("\n[FC] Checking if function calling is needed...")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            functions=FunctionDefinitions.get_all_functions(),
            function_call="auto",
            temperature=params['temperature'],
            max_tokens=params['max_tokens'],
            top_p=params['top_p'],
        )
        
        response_message = response.choices[0].message
        
        # Step 2: Check if LLM wants to call a function
        if not hasattr(response_message, 'function_call') or not response_message.function_call:
            return None, False
        
        # Step 3: Execute the function
        function_name = response_message.function_call.name
        function_args = json.loads(response_message.function_call.arguments)
        
        print(f"[FC] LLM requested function: {function_name}")
        function_result = function_executor.execute_function(function_name, function_args)
        print(f"[FC] Function result: {function_result[:200]}..." if len(function_result) > 200 else f"[FC] Function result: {function_result}")
        
        # Step 4: Add function call and result to messages
        messages.append({
            "role": "assistant",
            "function_call": {
                "name": function_name,
                "arguments": response_message.function_call.arguments,
            },
            "content": None
        })
        
        messages.append({
            "role": "function",
            "name": function_name,
            "content": function_result,
        })
        
        # Step 5: Call LLM again for natural language response with streaming
        print("[FC] Getting natural language response from LLM...")
        
        final_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            functions=FunctionDefinitions.get_all_functions(),
            function_call="auto",
            temperature=params['temperature'],
            max_tokens=params['max_tokens'],
            top_p=params['top_p'],
            stream=True  # Enable streaming for better UX
        )
        
        # Stream the response
        full_response = ""
        for chunk in final_response:
            try:
                if (chunk.choices and 
                    len(chunk.choices) > 0 and 
                    chunk.choices[0].delta and 
                    chunk.choices[0].delta.content):
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            except (AttributeError, IndexError, TypeError):
                continue
        
        print()  # New line at the end
        return full_response, True
    
    except Exception as e:
        print(f"[FC] Error in function calling: {e}")
        return None, False

def generate_text_streaming(prompt, model_name):
    """Generate text using GitHub Models with streaming output and conversation context"""
    global last_response, last_prompt, rag_engine
    
    # Security Check 1: Check for prompt injection attempts
    injection_check = prompt_injection_detector.check_prompt(prompt)
    if injection_check['is_suspicious']:
        print(injection_check['recommendation'])
        if injection_check['risk_level'] == 'danger':
            print("[BLOCKED] Prompt blocked due to high security risk.")
            return
        elif injection_check['risk_level'] == 'warning':
            response = input("Continue anyway? (y/n): ").lower().strip()
            if response != 'y':
                print("Prompt cancelled.")
                return
    
    # Security Check 1b: Check for sensitive data in user input
    input_sensitivity_check = sensitive_data_detector.scan_input(prompt)
    if input_sensitivity_check['has_sensitive_data']:
        print(input_sensitivity_check['warning'])
        print("   Detected types:", ', '.join(input_sensitivity_check['detected_items'].keys()))
    
    # Security Check 2: Check rate limits
    rate_check = rate_limiter.check_limits()
    if rate_check['status'] == 'exceeded':
        print("\n".join(rate_check['warnings']))
        print("[BLOCKED] Rate limit exceeded. Wait a moment and try again.")
        return
    elif rate_check['warnings']:
        for warning in rate_check['warnings']:
            print(warning)
    
    client = OpenAI(
        api_key=GITHUB_TOKEN,
        base_url=GITHUB_MODELS_ENDPOINT
    )
    
    # Track prompt for feedback
    last_prompt = prompt
    
    # Add user message to conversation history
    conversation_history.append({
        "role": "user",
        "content": prompt
    })
    
    # Retrieve context if RAG is enabled
    context_results = []
    augmented_system_prompt = system_prompt
    if rag_engine and rag_engine.enabled:
        context_results, avg_similarity = rag_engine.retrieve_context(prompt)
        if context_results:
            augmented_system_prompt = rag_engine.get_augmented_system_prompt(
                system_prompt, context_results
            )
            rag_engine.display_context_info(context_results, prompt)
    
    try:
        # Step 1: Try function calling first
        messages_for_fc = [
            {"role": "system", "content": augmented_system_prompt},
            *conversation_history
        ]
        
        fc_response, function_was_called = handle_function_calls(messages_for_fc, model_name)
        
        if function_was_called and fc_response:
            # Function was called and LLM provided response
            # (Response already streamed to output, no need to print again)
            last_response = fc_response
            
            # Add to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": fc_response
            })
            
            # Record usage
            prompt_tokens = len(last_prompt.split()) if last_prompt else 0
            completion_tokens = len(fc_response.split())
            record_request(model=model_name, prompt_tokens=prompt_tokens, 
                         completion_tokens=completion_tokens, system_prompt=augmented_system_prompt)
            
            return
        
        # Step 2: If no function was called, use regular streaming response
        params = model_params.get_all_parameters()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": augmented_system_prompt},
                *conversation_history  # Include full conversation history
            ],
            temperature=params['temperature'],
            max_tokens=params['max_tokens'],
            top_p=params['top_p'],
            frequency_penalty=params['frequency_penalty'],
            presence_penalty=params['presence_penalty'],
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
        
        # Security Check 3: Scan response for sensitive data leakage
        sensitivity_check = sensitive_data_detector.scan_output(full_response)
        if sensitivity_check['has_sensitive_data']:
            print("\n" + sensitivity_check['warning'])
            print("   Detected types:", ', '.join(sensitivity_check['detected_items'].keys()))
        
        # Add assistant response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        # Track response for feedback
        last_response = full_response
        
        # Record usage statistics (rough token estimate)
        prompt_tokens = len(prompt.split()) + len(augmented_system_prompt.split())
        completion_tokens = len(full_response.split())
        record_request(model_name, prompt_tokens, completion_tokens, augmented_system_prompt)
        
        # Record for rate limiting
        rate_limiter.record_request(tokens_used=completion_tokens)
        
        return full_response
        
    except Exception as e:
        # Fallback to non-streaming if streaming fails
        print(f"(Streaming unavailable, using standard response)\n")
        print(f"[DEBUG] Error in generate_text_streaming: {type(e).__name__}: {str(e)}")
        params = model_params.get_all_parameters()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": augmented_system_prompt},
                *conversation_history
            ],
            temperature=params['temperature'],
            max_tokens=params['max_tokens'],
            top_p=params['top_p'],
            frequency_penalty=params['frequency_penalty'],
            presence_penalty=params['presence_penalty']
        )
        result = response.choices[0].message.content
        
        # Security Check 3: Scan response for sensitive data leakage
        sensitivity_check = sensitive_data_detector.scan_output(result)
        if sensitivity_check['has_sensitive_data']:
            print("\n" + sensitivity_check['warning'])
            print("   Detected types:", ', '.join(sensitivity_check['detected_items'].keys()))
        
        print(result)
        
        # Add to history
        conversation_history.append({
            "role": "assistant",
            "content": result
        })
        
        # Track response for feedback
        last_response = result
        
        # Record usage statistics (rough token estimate)
        prompt_tokens = len(prompt.split()) + len(system_prompt.split())
        completion_tokens = len(result.split())
        record_request(model_name, prompt_tokens, completion_tokens, system_prompt)
        
        # Record for rate limiting
        rate_limiter.record_request(tokens_used=completion_tokens)
        
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
            
            # Log user action
            if audit_logger:
                audit_logger.log_user_action('MODEL_CHANGED', {'new_model': selected_model})
            
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
    
    # Log user action
    if audit_logger:
        audit_logger.log_user_action('CONVERSATION_CLEARED')

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
        
        # Log user action
        if audit_logger:
            audit_logger.log_user_action('SYSTEM_PROMPT_CHANGED', {'new_prompt_length': len(custom_prompt)})
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
    
    # Check privacy settings
    if privacy_settings and not privacy_settings.settings['auto_save_conversations']:
        print("\n⚠️  Auto-save conversations is currently DISABLED in privacy settings.")
        confirm = input("Override and save anyway? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Save cancelled.")
            return
    
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
        print(f"✓ Conversation saved to: {saved_file}")
        
        # Log user action
        if audit_logger:
            audit_logger.log_user_action('CONVERSATION_SAVED', {
                'filename': saved_file,
                'message_count': len(conversation_history)
            })
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
        
        if not choice:
            # Empty input = use default
            profile_name = "default"
        else:
            # User selected a profile by number
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

def use_prompt_template():
    """Use a prompt template to generate a prompt"""
    global system_prompt
    
    template_list = display_templates()
    
    if not template_list:
        return
    
    try:
        choice = input("\nEnter the number of the template to use (or press Enter to cancel): ").strip()
        
        if not choice:
            return
        
        choice_num = int(choice) - 1
        if 0 <= choice_num < len(template_list):
            template_id, template_data = template_list[choice_num]
            prompt, template_system_prompt = fill_template(template_data)
            
            # Ask if user wants to override system prompt
            use_template_prompt = input("\nUse template's system prompt? (y/n, default: y): ").strip().lower()
            if use_template_prompt != 'n':
                system_prompt = template_system_prompt
                print(f"System prompt updated to template's prompt.")
            
            print(f"\nGenerated prompt:")
            print(f"'{prompt}'")
            
            # Ask if user wants to send this prompt
            send_prompt = input("\nSend this prompt to the model? (y/n): ").strip().lower()
            if send_prompt == 'y':
                print(f"\nGenerating response using {current_model}...\n")
                result = generate_text_streaming(prompt, current_model)
                print("\n" + "-" * 60)
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error using template: {e}")

def create_custom_template():
    """Create a new custom template"""
    print("\n" + "=" * 60)
    print("Create Custom Prompt Template")
    print("=" * 60)
    
    name = input("Template name (e.g., 'Python Expert'): ").strip()
    if not name:
        print("Template name is required.")
        return
    
    description = input("Description (brief explanation of the template): ").strip()
    if not description:
        print("Description is required.")
        return
    
    system_prompt_input = input("System prompt (instructions for the model): ").strip()
    if not system_prompt_input:
        print("System prompt is required.")
        return
    
    template = input("Template text (use {placeholder} for dynamic fields): ").strip()
    if not template:
        print("Template text is required.")
        return
    
    # Extract placeholders from template
    import re
    placeholders = re.findall(r'\{(\w+)\}', template)
    
    if placeholders:
        print(f"\nDetected placeholders: {', '.join(placeholders)}")
    
    try:
        save_custom_template(name, description, system_prompt_input, template, placeholders)
        print(f"\nTemplate '{name}' created successfully!")
    except Exception as e:
        print(f"Error creating template: {e}")

def rate_last_response():
    """Rate the last response"""
    global last_response, last_prompt
    
    # Check privacy settings
    if privacy_settings and not privacy_settings.settings['auto_save_feedback']:
        print("\n⚠️  Auto-save feedback is currently DISABLED in privacy settings.")
        confirm = input("Override and save feedback anyway? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Feedback cancelled - not saved.")
            return
    
    if last_response is None:
        print("\nNo response to rate. Generate a response first.")
        return
    
    print(f"\nResponse to rate:")
    print("-" * 60)
    print(last_response[:200] + "..." if len(last_response) > 200 else last_response)
    print("-" * 60)
    
    rating, flag, notes = display_feedback_prompt()
    
    try:
        save_feedback(last_prompt, last_response, rating, flag, notes)
        print(f"\n✓ Feedback saved! Thank you for your rating.")
    except Exception as e:
        print(f"Error saving feedback: {e}")

def view_feedback_stats():
    """View feedback statistics"""
    display_feedback_summary()

def view_flagged_responses():
    """View flagged feedback"""
    display_flagged_feedback()

def search_conversations():
    """Search through saved conversations"""
    interactive_search()

def export_conversation():
    """Export a conversation to different formats"""
    interactive_export()

def analyze_conversation():
    """Analyze a saved conversation"""
    interactive_analysis()

def batch_process():
    """Process batch jobs"""
    interactive_batch_processor()

def run_batch_job():
    """Run/execute a batch job"""
    jobs = list_batch_jobs()
    
    if not jobs:
        print("\nNo batch jobs available.")
        return
    
    print("\n" + "=" * 60)
    print("Run Batch Job")
    print("=" * 60)
    print("\nAvailable batch jobs:")
    
    for i, job in enumerate(jobs, 1):
        progress = job['statistics']['completed']
        total = job['statistics']['total']
        pending = job['statistics']['pending']
        print(f"{i}. {job['name']} ({progress}/{total} completed, {pending} pending)")
    
    try:
        choice = input("\nSelect job number to run (or press Enter to cancel): ").strip()
        
        if not choice:
            return
        
        job_idx = int(choice) - 1
        if 0 <= job_idx < len(jobs):
            job_name = jobs[job_idx]['name']
            process_batch_job(job_name, generate_text_streaming, model_params)
        else:
            print("Invalid choice.")
    
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error processing batch: {e}")

def view_usage_stats():
    """View usage statistics"""
    interactive_stats_menu()

def semantic_search():
    """Perform semantic search on conversations"""
    global embedding_index
    
    if not semantic_search_available or embedding_index is None:
        print("\n❌ Semantic search is not available.")
        print("Please ensure Azure OpenAI credentials are configured in .env")
        return
    
    interactive_semantic_search(embedding_index)

def index_conversation_embeddings():
    """Index the current conversation with embeddings"""
    global embedding_index, conversation_history, system_prompt, current_model
    
    if not semantic_search_available or embedding_index is None:
        print("\n❌ Embedding indexing is not available.")
        return
    
    if not conversation_history:
        print("\nNo conversation to index.")
        return
    
    # Generate a conversation ID based on timestamp and model
    conversation_id = f"conv_{current_model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    proceed = input(f"\nIndex current conversation as '{conversation_id}'? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    try:
        embedding_index.index_conversation(
            conversation_id=conversation_id,
            messages=conversation_history,
            system_prompt=system_prompt,
            model=current_model
        )
        print("✓ Conversation indexed successfully!")
    except Exception as e:
        print(f"Error indexing conversation: {e}")

def view_embedding_stats():
    """View embedding index statistics"""
    global embedding_index
    
    if not semantic_search_available or embedding_index is None:
        print("\n❌ Semantic search is not available.")
        return
    
    embedding_index.display_index_stats()

def manage_model_parameters():
    """Interactive model parameter management"""
    global model_params
    
    while True:
        print("\n" + "=" * 60)
        print("Model Parameters")
        print("=" * 60)
        print("\nOptions:")
        print("  1. View current parameters")
        print("  2. Set temperature")
        print("  3. Set max tokens")
        print("  4. Set top_p (nucleus sampling)")
        print("  5. Set frequency penalty")
        print("  6. Set presence penalty")
        print("  7. Configure all parameters")
        print("  8. Apply preset")
        print("  9. Reset to defaults")
        print("  0. Back to main menu")
        
        choice = input("\nSelect option (0-9): ").strip()
        
        if choice == "1":
            model_params.display_parameters()
        
        elif choice == "2":
            value = input("Enter temperature (0.0-2.0): ").strip()
            success, msg = model_params.set_temperature(value)
            print(f"  {msg}")
        
        elif choice == "3":
            value = input("Enter max tokens (1-4000): ").strip()
            success, msg = model_params.set_max_tokens(value)
            print(f"  {msg}")
        
        elif choice == "4":
            value = input("Enter top_p (0.0-1.0): ").strip()
            success, msg = model_params.set_top_p(value)
            print(f"  {msg}")
        
        elif choice == "5":
            value = input("Enter frequency penalty (-2.0 to 2.0): ").strip()
            success, msg = model_params.set_frequency_penalty(value)
            print(f"  {msg}")
        
        elif choice == "6":
            value = input("Enter presence penalty (-2.0 to 2.0): ").strip()
            success, msg = model_params.set_presence_penalty(value)
            print(f"  {msg}")
        
        elif choice == "7":
            model_params.interactive_setup()
        
        elif choice == "8":
            presets = display_parameter_presets()
            preset_choice = input("\nSelect preset (1-5): ").strip()
            success, msg = apply_preset(model_params, preset_choice, presets)
            print(f"  {msg}")
        
        elif choice == "9":
            success, msg = model_params.reset_to_defaults()
            print(f"  {msg}")
        
        elif choice == "0":
            break
        
        else:
            print("Invalid choice.")

def cosmos_kb_search(knowledge_base):
    """Search Knowledge Base using Cosmos DB with embeddings (Enterprise RAG)"""
    try:
        from embedding_generator import EmbeddingGenerator
        
        print("\n" + "="*70)
        print("ENTERPRISE KB SEARCH - Cosmos DB + Embeddings")
        print("="*70)
        print("\nSearching across dual sources:")
        print("  - Local Knowledge Base (JSONL)")
        print("  - Azure Cosmos DB (Cloud Vector Database)")
        print("="*70)
        
        query = input("\nEnter your search query: ").strip()
        if not query:
            print("Search cancelled.")
            return
        
        # Initialize embedding generator
        embedding_gen = EmbeddingGenerator()
        
        if not embedding_gen.is_available():
            print("[WARNING] Embedding generator not available.")
            print("Ensure AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are set.")
            return
        
        print(f"\n[*] Generating embedding for query...")
        query_embedding = embedding_gen.generate_embedding(query)
        
        if not query_embedding:
            print("[ERROR] Failed to generate query embedding.")
            return
        
        print(f"[+] Query embedding generated (dimension: {len(query_embedding)})")
        
        # Perform dual-source search
        print(f"\n[*] Searching dual sources...")
        print("    [1] Searching local KB...")
        print("    [2] Searching Cosmos DB...")
        
        if hasattr(knowledge_base, 'search_dual_source'):
            results = knowledge_base.search_dual_source(
                query=query,
                query_embedding=query_embedding,
                top_k=5
            )
        else:
            print("[WARNING] Dual-source search not available.")
            print("Using local KB search only...")
            results = knowledge_base.search(query, top_k=5) if hasattr(knowledge_base, 'search') else []
        
        # Display results
        if results:
            print(f"\n[+] Found {len(results)} results from dual sources:\n")
            print("="*70)
            
            for i, result in enumerate(results, 1):
                source = result.get('source', 'Unknown')
                similarity = result.get('similarity', 0)
                doc_title = result.get('title', 'Unknown')
                chunk_text = result.get('text', 'N/A')[:200]
                
                sim_pct = similarity * 100 if isinstance(similarity, float) else similarity
                
                print(f"\n{i}. [{source}] Relevance: {sim_pct:.1f}%")
                print(f"   Document: {doc_title}")
                print(f"   Collection: {result.get('collection_id', 'Unknown')}")
                print(f"   Text: {chunk_text}...")
                if source == 'Cosmos DB':
                    print(f"   Strategy: {result.get('strategy', 'unknown')}")
            
            print("\n" + "="*70)
            
            # Show cache statistics if available
            try:
                if hasattr(embedding_gen, 'cache') and hasattr(embedding_gen.cache, 'get_stats'):
                    cache_stats = embedding_gen.cache.get_stats()
                    if cache_stats:
                        print(f"\n[*] Embedding Cache Statistics:")
                        print(f"    Size: {cache_stats['size']} items")
                        print(f"    Hits: {cache_stats['hits']}")
                        print(f"    Misses: {cache_stats['misses']}")
                        print(f"    Hit Rate: {cache_stats['hit_rate']:.1f}%")
            except Exception as cache_err:
                # Cache stats not available, continue without them
                pass
        else:
            print("[*] No results found matching your query.")
            print("\nTips:")
            print("  - Try different keywords")
            print("  - Ensure KB documents are indexed to Cosmos DB")
            print("  - Use 'kb' command to view/manage documents")
    
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Ensure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()

def display_help():
    """Display all available commands organized by category"""
    print("\n" + "="*70)
    print("AVAILABLE COMMANDS")
    print("="*70)
    
    commands = {
        "Profile Management": [
            ("profile", "Switch to a different user profile"),
            ("new-profile", "Create a new user profile"),
            ("save-profile", "Save current profile settings"),
            ("profiles", "List all available profiles"),
            ("profile-info", "View current profile details"),
        ],
        "Chat & Conversation": [
            ("model", "Switch to a different AI model"),
            ("system", "Set a custom system prompt/instructions"),
            ("prompt", "Display the current system prompt"),
            ("history", "View conversation history"),
            ("save", "Save current conversation"),
            ("load", "Load a saved conversation"),
            ("clear", "Clear conversation history"),
        ],
        "Prompt Management": [
            ("template", "Use a pre-built prompt template"),
            ("create-template", "Create a custom prompt template"),
        ],
        "Response Feedback": [
            ("rate", "Rate the last response (1-5 stars)"),
            ("feedback-stats", "View feedback statistics"),
            ("flagged", "View flagged responses"),
        ],
        "Search & Analysis": [
            ("search", "Search saved conversations by keywords"),
            ("analyze", "Analyze a conversation"),
        ],
        "Semantic Search & Embeddings": [
            ("semantic-search", "AI-powered search of conversations"),
            ("index", "Index current conversation with embeddings"),
            ("index-kb", "Index Knowledge Base documents"),
            ("kb-search", "Search Knowledge Base documents"),
            ("cosmos-search", "Enterprise KB search (Cosmos DB + Embeddings)"),
            ("embedding-stats", "View embedding index statistics"),
        ],
        "Knowledge Base": [
            ("kb", "Manage Knowledge Base documents"),
        ],
        "Image Generation": [
            ("image", "Generate images with DALL-E 3"),
        ],
        "RAG & Context": [
            ("rag", "Configure RAG settings"),
        ],
        "Function Calling": [
            ("fc-snippets", "View extracted code snippets"),
            ("fc-summaries", "View extracted summaries"),
        ],
        "Batch Processing": [
            ("batch", "Manage batch jobs"),
            ("batch-run", "Execute a batch job"),
        ],
        "Data Export & Statistics": [
            ("export", "Export a conversation"),
            ("stats", "View usage statistics"),
            ("params", "Manage model parameters"),
        ],
        "Program Control": [
            ("help", "Display this help message"),
            ("security", "View model security status and settings"),
            ("audit", "View security audit trail and incidents"),
            ("privacy", "View privacy and data collection settings"),
            ("exit / quit", "End the program"),
        ],
    }
    
    for category, cmds in commands.items():
        print(f"\n{category}:")
        print("-" * 70)
        for cmd, desc in cmds:
            print(f"  {cmd:<20} {desc}")
    
    print("\n" + "="*70 + "\n")

def main():
    """Main interactive loop for the text generation app"""
    global current_model, current_profile, profile_name
    
    print("=" * 60)
    print("Welcome to the GitHub Models Text Generation App!")
    print("=" * 60)
    print("\nLoading user profile...")
    
    # Load user profile (automatically sets current_model and system_prompt from profile)
    select_profile()
    
    print("\nThis app uses GitHub Models to generate text based on your prompts. Type 'help' at any time to see all available commands.")
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
    print("  - Type 'template' to use a prompt template")
    print("  - Type 'create-template' to create a custom template")
    print("  - Type 'rate' to rate the last response")
    print("  - Type 'feedback-stats' to view feedback statistics")
    print("  - Type 'flagged' to view flagged responses")
    print("  - Type 'search' to search saved conversations (keyword)")
    print("  - Type 'semantic-search' to search conversations (AI-powered)")
    print("  - Type 'index' to index current conversation with embeddings")
    print("  - Type 'index-kb' to index Knowledge Base documents")
    print("  - Type 'kb-search' to search Knowledge Base documents")
    print("  - Type 'cosmos-search' to search with Cosmos DB (Enterprise RAG)")
    print("  - Type 'embedding-stats' to view embedding index statistics")
    print("  - Type 'export' to export a conversation")
    print("  - Type 'analyze' to analyze a conversation")
    print("  - Type 'batch' to manage batch jobs")
    print("  - Type 'batch-run' to execute a batch job")
    print("  - Type 'stats' to view usage statistics")
    print("  - Type 'params' to manage model parameters")
    print("  - Type 'rag' to configure RAG settings")
    print("  - Type 'kb' to manage knowledge base documents")
    print("  - Type 'image' to generate images with DALL-E 3")
    print("  - Type 'fc-snippets' to view extracted code snippets")
    print("  - Type 'fc-summaries' to view extracted summaries")
    print("  - Type 'history' to view conversation history")
    print("  - Type 'save' to save current conversation")
    print("  - Type 'load' to load a saved conversation")
    print("  - Type 'clear' to clear conversation history")
    print("  - Type 'help' to see all available commands")
    print("  - Type 'privacy' to review data collection settings")
    print("  - Type 'security' to view model security status and settings")
    print("  - Type 'audit' to view security audit trail and incidents")
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
            
            if user_input.lower() == 'help':
                display_help()
                continue
            
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
            
            if user_input.lower() == 'template':
                use_prompt_template()
                continue
            
            if user_input.lower() == 'create-template':
                create_custom_template()
                continue
            
            if user_input.lower() == 'rate':
                rate_last_response()
                continue
            
            if user_input.lower() == 'feedback-stats':
                view_feedback_stats()
                continue
            
            if user_input.lower() == 'flagged':
                view_flagged_responses()
                continue
            
            if user_input.lower() == 'search':
                search_conversations()
                continue
            
            if user_input.lower() == 'semantic-search':
                semantic_search()
                continue
            
            if user_input.lower() == 'index':
                index_conversation_embeddings()
                continue
            
            if user_input.lower() == 'index-kb':
                if embedding_index and knowledge_base:
                    print("\nIndexing Knowledge Base documents...")
                    embedding_index.index_kb_documents(knowledge_base)
                else:
                    print("Error: Embeddings or KB not available")
                continue
            
            if user_input.lower() == 'kb-search':
                if embedding_index:
                    print("\n" + "="*60)
                    print("Knowledge Base Search")
                    print("="*60)
                    query = input("\nEnter search query: ").strip()
                    if query:
                        results = embedding_index.search_kb_only(query, top_k=5, similarity_threshold=0.15)
                        if results:
                            print(f"\nFound {len(results)} KB results:")
                            for i, r in enumerate(results, 1):
                                sim_pct = r['similarity_score'] * 100
                                print(f"\n{i}. Relevance: {sim_pct:.1f}%")
                                print(f"   Document: {r.get('doc_title', 'Unknown')}")
                                print(f"   Collection: {r.get('collection', 'Unknown')}")
                                print(f"   Text: {r.get('text', '')[:200]}...")
                        else:
                            print("No KB results found for this query")
                else:
                    print("Error: Embeddings not available")
                continue
            
            if user_input.lower() == 'cosmos-search':
                if knowledge_base:
                    cosmos_kb_search(knowledge_base)
                else:
                    print("Error: Knowledge Base not available")
                continue
            
            if user_input.lower() == 'embedding-stats':
                view_embedding_stats()
                continue
            
            if user_input.lower() == 'export':
                export_conversation()
                continue
            
            if user_input.lower() == 'analyze':
                analyze_conversation()
                continue
            
            if user_input.lower() == 'batch':
                batch_process()
                continue
            
            if user_input.lower() == 'batch-run':
                run_batch_job()
                continue
            
            if user_input.lower() == 'stats':
                view_usage_stats()
                continue
            
            if user_input.lower() == 'params':
                manage_model_parameters()
                continue
            
            if user_input.lower() == 'rag':
                interactive_rag_settings(rag_engine)
                continue
            
            if user_input.lower() == 'kb':
                if knowledge_base:
                    interactive_kb_menu(knowledge_base)
                else:
                    print("Knowledge Base not available")
                continue
            
            if user_input.lower() == 'image':
                if image_generator:
                    interactive_image_generator(image_generator)
                else:
                    print("Image generation not available")
                continue
            
            if user_input.lower() == 'fc-snippets':
                if function_executor:
                    snippets = function_executor.list_code_snippets()
                    if not snippets:
                        print("\nNo code snippets extracted yet.")
                    else:
                        print(f"\n[Function Calling] Extracted Code Snippets ({len(snippets)} total):")
                        print("=" * 70)
                        for snippet in snippets:
                            print(f"\nTitle: {snippet['title']}")
                            print(f"Language: {snippet['language']}")
                            print(f"Description: {snippet.get('description', 'N/A')}")
                            print(f"ID: {snippet['id']}")
                            print(f"Created: {snippet['created_at']}")
                            print(f"Code:\n{snippet['code']}")
                            print("-" * 70)
                else:
                    print("Function calling not available")
                continue
            
            if user_input.lower() == 'fc-summaries':
                if function_executor:
                    summaries = function_executor.list_summaries()
                    if not summaries:
                        print(ErrorMessages.no_summaries_created())
                    else:
                        print(f"\n[Function Calling] Extracted Summaries ({len(summaries)} total):")
                        print("=" * 70)
                        for summary in summaries:
                            print(f"\nTopic: {summary['topic']}")
                            print(f"ID: {summary['id']}")
                            print(f"Created: {summary['created_at']}")
                            print(f"Key Points: {', '.join(summary['key_points'])}")
                            if summary.get('explanation'):
                                print(f"Explanation: {summary['explanation']}")
                            print("-" * 70)
                else:
                    print("Function calling not available")
                continue
            
            if user_input.lower() == 'security':
                display_security_status()
                continue
            
            if user_input.lower() == 'audit':
                # Show audit menu - loop until user exits
                while True:
                    print("\n" + "=" * 70)
                    print("AUDIT TRAIL OPTIONS")
                    print("=" * 70)
                    print("1. View audit summary")
                    print("2. View recent events (last 20)")
                    print("3. View security incidents (last 24 hours)")
                    print("4. View all security incidents (last 30 days)")
                    print("5. Export audit report")
                    print("0. Back to main menu")
                    choice = input("\nSelect option (0-5): ").strip()
                    
                    if choice == '0':
                        break
                    elif choice == '1':
                        display_audit_summary(audit_logger)
                    elif choice == '2':
                        display_recent_events(audit_logger, limit=20)
                    elif choice == '3':
                        display_security_incidents(audit_logger, hours=24)
                    elif choice == '4':
                        display_security_incidents(audit_logger, hours=24*30)
                    elif choice == '5':
                        export_file = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        audit_logger.export_audit_report(export_file)
                        print(f"\nAudit report exported to: {export_file}\n")
                    else:
                        print("Invalid option. Please select 0-5.")
                
                continue
            
            if user_input.lower() == 'privacy':
                if privacy_settings:
                    privacy_settings.interactive_menu()
                else:
                    print(DataTransparency.data_collection_summary())
                continue
            
            # Validate input
            if not user_input:
                print(ErrorMessages.empty_input())
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