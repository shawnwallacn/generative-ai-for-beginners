"""
User profile management for saving preferences and settings
"""
import json
import os
from datetime import datetime

PROFILES_DIR = "profiles"

def ensure_profiles_dir():
    """Create profiles directory if it doesn't exist"""
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)

def create_default_profile():
    """Create a default profile structure"""
    return {
        "name": "default",
        "created_at": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat(),
        "favorite_model": "gpt-4o-mini",
        "system_prompt": "You are a helpful assistant.",
        "streaming_enabled": True,
        "preferences": {
            "theme": "default",
            "auto_save": False
        }
    }

def get_profile_path(profile_name):
    """Get the file path for a profile"""
    return os.path.join(PROFILES_DIR, f"{profile_name}.json")

def save_profile(profile_data, profile_name="default"):
    """Save a user profile to a JSON file"""
    ensure_profiles_dir()
    
    profile_path = get_profile_path(profile_name)
    profile_data["last_used"] = datetime.now().isoformat()
    
    with open(profile_path, 'w') as f:
        json.dump(profile_data, f, indent=2)
    
    return profile_path

def load_profile(profile_name="default"):
    """Load a user profile from a JSON file"""
    profile_path = get_profile_path(profile_name)
    
    if not os.path.exists(profile_path):
        return None
    
    try:
        with open(profile_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None

def list_profiles():
    """List all available profiles"""
    ensure_profiles_dir()
    
    files = []
    if os.path.exists(PROFILES_DIR):
        files = [f[:-5] for f in os.listdir(PROFILES_DIR) if f.endswith('.json')]
    
    return sorted(files)

def delete_profile(profile_name):
    """Delete a user profile"""
    if profile_name == "default":
        print("Cannot delete the default profile.")
        return False
    
    profile_path = get_profile_path(profile_name)
    if os.path.exists(profile_path):
        os.remove(profile_path)
        print(f"Profile '{profile_name}' deleted.")
        return True
    
    return False

def display_profiles():
    """Display all available profiles"""
    profiles = list_profiles()
    
    if not profiles:
        print("\nNo profiles found. Using default profile.")
        return profiles
    
    print("\n" + "=" * 60)
    print("Available Profiles:")
    print("=" * 60)
    
    for i, profile_name in enumerate(profiles, 1):
        profile = load_profile(profile_name)
        if profile:
            model = profile.get("favorite_model", "Unknown")
            last_used = profile.get("last_used", "Never")
            marker = " (current)" if profile_name == "default" else ""
            print(f"{i}. {profile_name}{marker}")
            print(f"   Model: {model} | Last used: {last_used}")
    
    print("=" * 60)
    return profiles

def update_profile_settings(profile_data, model=None, system_prompt=None, 
                           streaming=None, preferences=None):
    """Update specific settings in a profile"""
    if model:
        profile_data["favorite_model"] = model
    
    if system_prompt:
        profile_data["system_prompt"] = system_prompt
    
    if streaming is not None:
        profile_data["streaming_enabled"] = streaming
    
    if preferences:
        profile_data["preferences"].update(preferences)
    
    return profile_data

def apply_profile_settings(profile_data):
    """Extract settings from a profile to apply to the app"""
    return {
        "model": profile_data.get("favorite_model", "gpt-4o-mini"),
        "system_prompt": profile_data.get("system_prompt", "You are a helpful assistant."),
        "streaming_enabled": profile_data.get("streaming_enabled", True),
        "preferences": profile_data.get("preferences", {})
    }
