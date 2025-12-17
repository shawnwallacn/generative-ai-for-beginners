"""
Conversation file management utilities
"""
import json
import os
from datetime import datetime

CONVERSATIONS_DIR = "conversations"

def ensure_conversations_dir():
    """Create conversations directory if it doesn't exist"""
    if not os.path.exists(CONVERSATIONS_DIR):
        os.makedirs(CONVERSATIONS_DIR)

def get_conversation_filename(name=None):
    """Generate a conversation filename"""
    if name:
        return os.path.join(CONVERSATIONS_DIR, f"{name}.json")
    
    # Use timestamp for auto-generated names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(CONVERSATIONS_DIR, f"conversation_{timestamp}.json")

def save_conversation(conversation_history, system_prompt, model_name, filename=None):
    """Save conversation to a JSON file"""
    ensure_conversations_dir()
    
    if not filename:
        filename = get_conversation_filename()
    
    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "system_prompt": system_prompt,
        "messages": conversation_history
    }
    
    with open(filename, 'w') as f:
        json.dump(conversation_data, f, indent=2)
    
    return filename

def load_conversation(filename):
    """Load conversation from a JSON file"""
    if not os.path.exists(filename):
        return None, None, None
    
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return (data.get("messages", []), 
            data.get("system_prompt", "You are a helpful assistant."),
            data.get("model", "gpt-4o-mini"))

def list_saved_conversations():
    """List all saved conversations"""
    ensure_conversations_dir()
    
    files = []
    if os.path.exists(CONVERSATIONS_DIR):
        files = [f for f in os.listdir(CONVERSATIONS_DIR) if f.endswith('.json')]
    
    return sorted(files, reverse=True)  # Most recent first

def display_saved_conversations():
    """Display saved conversations in a nice format"""
    files = list_saved_conversations()
    
    if not files:
        print("\nNo saved conversations found.")
        return None
    
    print("\n" + "=" * 60)
    print("Saved Conversations:")
    print("=" * 60)
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(CONVERSATIONS_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                model = data.get("model", "Unknown")
                timestamp = data.get("timestamp", "Unknown")
                msg_count = len(data.get("messages", []))
                
            print(f"{i}. {filename}")
            print(f"   Model: {model} | Messages: {msg_count} | Time: {timestamp}")
        except Exception as e:
            print(f"{i}. {filename} (Error reading: {e})")
    
    print("=" * 60)
    return files

def delete_conversation(filename):
    """Delete a saved conversation"""
    filepath = os.path.join(CONVERSATIONS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Deleted: {filename}")
        return True
    return False
