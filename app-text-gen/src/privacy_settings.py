"""
Privacy Settings Manager

Handles user privacy preferences and data control options.
"""

import json
import os
from typing import Dict
from datetime import datetime


class PrivacySettings:
    """Manages user privacy preferences"""
    
    def __init__(self):
        self.settings_file = "settings/privacy_settings.json"
        self.default_settings = {
            "auto_save_conversations": True,
            "auto_save_feedback": True,
            "auto_save_snippets": True,
            "auto_save_summaries": True,
            "track_usage_stats": True,
            "privacy_mode": False,
            "last_updated": datetime.now().isoformat()
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict:
        """Load privacy settings from file"""
        os.makedirs(os.path.dirname(self.settings_file) or ".", exist_ok=True)
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save privacy settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file) or ".", exist_ok=True)
            self.settings["last_updated"] = datetime.now().isoformat()
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving privacy settings: {e}")
            return False
    
    def interactive_menu(self) -> None:
        """Display interactive privacy settings menu"""
        while True:
            print("\n" + "="*70)
            print("Privacy & Data Settings")
            print("="*70)
            
            # Show current settings
            print("\nCurrent Settings:")
            print("-"*70)
            print(f"1. Auto-save conversations:     {'ON' if self.settings['auto_save_conversations'] else 'OFF'}")
            print(f"2. Auto-save feedback:          {'ON' if self.settings['auto_save_feedback'] else 'OFF'}")
            print(f"3. Auto-save code snippets:     {'ON' if self.settings['auto_save_snippets'] else 'OFF'}")
            print(f"4. Auto-save summaries:         {'ON' if self.settings['auto_save_summaries'] else 'OFF'}")
            print(f"5. Track usage statistics:      {'ON' if self.settings['track_usage_stats'] else 'OFF'}")
            print(f"6. Privacy Mode (no auto-save): {'ENABLED' if self.settings['privacy_mode'] else 'DISABLED'}")
            
            print("\nActions:")
            print("-"*70)
            print("7. View data collection info")
            print("8. View stored data locations")
            print("9. Reset to defaults")
            print("0. Back to main menu")
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.settings['auto_save_conversations'] = not self.settings['auto_save_conversations']
                self.save_settings()
                status = "ON" if self.settings['auto_save_conversations'] else "OFF"
                print(f"✓ Auto-save conversations: {status}")
            elif choice == "2":
                self.settings['auto_save_feedback'] = not self.settings['auto_save_feedback']
                self.save_settings()
                status = "ON" if self.settings['auto_save_feedback'] else "OFF"
                print(f"✓ Auto-save feedback: {status}")
            elif choice == "3":
                self.settings['auto_save_snippets'] = not self.settings['auto_save_snippets']
                self.save_settings()
                status = "ON" if self.settings['auto_save_snippets'] else "OFF"
                print(f"✓ Auto-save code snippets: {status}")
            elif choice == "4":
                self.settings['auto_save_summaries'] = not self.settings['auto_save_summaries']
                self.save_settings()
                status = "ON" if self.settings['auto_save_summaries'] else "OFF"
                print(f"✓ Auto-save summaries: {status}")
            elif choice == "5":
                self.settings['track_usage_stats'] = not self.settings['track_usage_stats']
                self.save_settings()
                status = "ON" if self.settings['track_usage_stats'] else "OFF"
                print(f"✓ Track usage statistics: {status}")
            elif choice == "6":
                self.settings['privacy_mode'] = not self.settings['privacy_mode']
                self.save_settings()
                if self.settings['privacy_mode']:
                    print("✓ Privacy Mode ENABLED (nothing will be auto-saved)")
                else:
                    print("✓ Privacy Mode DISABLED (normal auto-save restored)")
            elif choice == "7":
                self.show_data_info()
            elif choice == "8":
                self.show_data_locations()
            elif choice == "9":
                confirm = input("Reset all settings to defaults? (yes/no): ").strip().lower()
                if confirm == "yes":
                    self.settings = self.default_settings.copy()
                    self.save_settings()
                    print("✓ Settings reset to defaults")
            else:
                print("Invalid choice. Try again.")
    
    def show_data_info(self) -> None:
        """Show what data is being collected"""
        print("\n" + "="*70)
        print("Data Collection Information")
        print("="*70)
        
        print("\nData Currently Being Saved:")
        print("-"*70)
        
        items = [
            ("Conversations", self.settings['auto_save_conversations'], "Chat history for context and RAG"),
            ("Feedback Ratings", self.settings['auto_save_feedback'], "Response ratings for quality tracking"),
            ("Code Snippets", self.settings['auto_save_snippets'], "Extracted code for reference"),
            ("Summaries", self.settings['auto_save_summaries'], "Generated summaries for study"),
            ("Usage Statistics", self.settings['track_usage_stats'], "Token counts, costs, model usage"),
            ("Profiles", True, "User preferences (always saved)"),
            ("Knowledge Base", True, "Your documents (always saved)"),
        ]
        
        for name, enabled, description in items:
            status = "✓" if enabled else "✗"
            print(f"{status} {name:20} - {description}")
        
        if self.settings['privacy_mode']:
            print("\n⚠️  PRIVACY MODE ACTIVE - Nothing is being auto-saved")
        
        print("\n" + "="*70)
        print("Data Privacy Guarantee:")
        print("="*70)
        print("""
✓ All data stored LOCALLY on YOUR computer
✓ No data shared with anyone
✓ No analytics or tracking sent externally
✓ Only API requests sent to GitHub Models / Azure OpenAI
✓ You can delete any data anytime
✓ You have full control
""")
    
    def show_data_locations(self) -> None:
        """Show where data is stored"""
        print("\n" + "="*70)
        print("Where Your Data Is Stored")
        print("="*70)
        
        locations = {
            "Conversations": "conversations/",
            "User Profiles": "profiles/",
            "Feedback Ratings": "feedback/",
            "Code Snippets": "function_calling/code_snippets.json",
            "Summaries": "function_calling/summaries.json",
            "Batch Jobs": "batch_jobs/",
            "Export Files": "exports/",
            "Usage Statistics": "statistics/",
            "Embeddings": "embeddings/",
            "Knowledge Base": "knowledge_base/",
            "Generated Images": "generated_images/",
            "Privacy Settings": "settings/privacy_settings.json",
        }
        
        print("\nYour data is organized in these folders:\n")
        for data_type, location in locations.items():
            print(f"  {data_type:20} → {location}")
        
        print("\n" + "="*70)
        print("Full Path: " + os.path.abspath("."))
        print("="*70)
        print("\nYou can:")
        print("  • Browse these folders directly")
        print("  • Delete files manually if desired")
        print("  • Back up data to another location")
        print("  • Share data with others (it's all JSON/text)")
        print()
    
    def show_summary(self) -> str:
        """Return a text summary of privacy settings"""
        lines = [
            "\n" + "="*70,
            "Privacy Settings Summary",
            "="*70,
            "\nCurrent Configuration:",
            "-"*70,
        ]
        
        lines.append(f"Auto-save conversations:  {'ON' if self.settings['auto_save_conversations'] else 'OFF'}")
        lines.append(f"Auto-save feedback:       {'ON' if self.settings['auto_save_feedback'] else 'OFF'}")
        lines.append(f"Auto-save snippets:       {'ON' if self.settings['auto_save_snippets'] else 'OFF'}")
        lines.append(f"Auto-save summaries:      {'ON' if self.settings['auto_save_summaries'] else 'OFF'}")
        lines.append(f"Track usage stats:        {'ON' if self.settings['track_usage_stats'] else 'OFF'}")
        lines.append(f"Privacy Mode:             {'ENABLED' if self.settings['privacy_mode'] else 'DISABLED'}")
        
        lines.append("\nTo change settings: type 'privacy' and select the option")
        lines.append("="*70 + "\n")
        
        return "\n".join(lines)

