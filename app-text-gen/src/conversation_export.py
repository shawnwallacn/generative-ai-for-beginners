"""
Export conversations to different formats (CSV, Markdown, etc.)
"""
import json
import os
import csv
from datetime import datetime

CONVERSATIONS_DIR = "conversations"
EXPORTS_DIR = "exports"

def ensure_exports_dir():
    """Create exports directory if it doesn't exist"""
    if not os.path.exists(EXPORTS_DIR):
        os.makedirs(EXPORTS_DIR)

def load_conversation_data(filename):
    """Load conversation from file"""
    filepath = os.path.join(CONVERSATIONS_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return None

def export_to_markdown(conversation_data, filename=None):
    """Export conversation to Markdown format"""
    ensure_exports_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.md"
    else:
        # Replace .json with .md if needed
        filename = filename.replace('.json', '') + ".md"
    
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Conversation Export\n\n")
            f.write(f"**Exported:** {datetime.now().isoformat()}\n\n")
            
            # Write metadata
            f.write("## Metadata\n\n")
            f.write(f"- **Model:** {conversation_data.get('model', 'Unknown')}\n")
            f.write(f"- **Timestamp:** {conversation_data.get('timestamp', 'Unknown')}\n")
            f.write(f"- **Messages:** {len(conversation_data.get('messages', []))}\n\n")
            
            # Write system prompt
            system_prompt = conversation_data.get('system_prompt', '')
            if system_prompt:
                f.write("## System Prompt\n\n")
                f.write(f"> {system_prompt}\n\n")
            
            # Write conversation
            f.write("## Conversation\n\n")
            messages = conversation_data.get('messages', [])
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                
                f.write(f"### {i}. {role}\n\n")
                f.write(f"{content}\n\n")
            
            f.write("---\n")
            f.write(f"*Exported on {datetime.now().isoformat()}*\n")
        
        return filepath
    
    except Exception as e:
        print(f"Error exporting to Markdown: {e}")
        return None

def export_to_csv(conversation_data, filename=None):
    """Export conversation to CSV format"""
    ensure_exports_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.csv"
    else:
        # Replace .json with .csv if needed
        filename = filename.replace('.json', '') + ".csv"
    
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    try:
        messages = conversation_data.get('messages', [])
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['#', 'Role', 'Message', 'Model', 'Timestamp'])
            
            model = conversation_data.get('model', 'Unknown')
            timestamp = conversation_data.get('timestamp', '')
            
            # Write messages
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                writer.writerow([i, role, content, model, timestamp])
        
        return filepath
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def export_to_plain_text(conversation_data, filename=None):
    """Export conversation to plain text format"""
    ensure_exports_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
    else:
        # Replace .json with .txt if needed
        filename = filename.replace('.json', '') + ".txt"
    
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 60 + "\n")
            f.write("CONVERSATION EXPORT\n")
            f.write("=" * 60 + "\n\n")
            
            # Write metadata
            f.write(f"Model: {conversation_data.get('model', 'Unknown')}\n")
            f.write(f"Timestamp: {conversation_data.get('timestamp', 'Unknown')}\n")
            f.write(f"Total Messages: {len(conversation_data.get('messages', []))}\n\n")
            
            # Write system prompt
            system_prompt = conversation_data.get('system_prompt', '')
            if system_prompt:
                f.write("System Prompt:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{system_prompt}\n")
                f.write("-" * 60 + "\n\n")
            
            # Write conversation
            f.write("Conversation:\n")
            f.write("=" * 60 + "\n\n")
            messages = conversation_data.get('messages', [])
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                
                f.write(f"{role}:\n")
                f.write(f"{content}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write(f"Exported: {datetime.now().isoformat()}\n")
        
        return filepath
    
    except Exception as e:
        print(f"Error exporting to plain text: {e}")
        return None

def export_to_html(conversation_data, filename=None):
    """Export conversation to HTML format"""
    ensure_exports_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.html"
    else:
        # Replace .json with .html if needed
        filename = filename.replace('.json', '') + ".html"
    
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write HTML header
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write("  <meta charset='UTF-8'>\n")
            f.write("  <title>Conversation Export</title>\n")
            f.write("  <style>\n")
            f.write("    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }\n")
            f.write("    .container { max-width: 900px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; }\n")
            f.write("    .metadata { background-color: #f0f0f0; padding: 10px; border-radius: 3px; margin-bottom: 20px; }\n")
            f.write("    .system-prompt { background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 20px; }\n")
            f.write("    .message { margin-bottom: 15px; padding: 10px; border-radius: 3px; }\n")
            f.write("    .user { background-color: #e3f2fd; border-left: 4px solid #2196F3; }\n")
            f.write("    .assistant { background-color: #f3e5f5; border-left: 4px solid #9c27b0; }\n")
            f.write("    .role { font-weight: bold; color: #333; }\n")
            f.write("    .content { margin-top: 5px; white-space: pre-wrap; word-wrap: break-word; }\n")
            f.write("    .footer { text-align: center; margin-top: 30px; color: #999; font-size: 12px; }\n")
            f.write("  </style>\n")
            f.write("</head>\n")
            f.write("<body>\n")
            f.write("  <div class='container'>\n")
            
            # Write header
            f.write("    <h1>Conversation Export</h1>\n")
            
            # Write metadata
            f.write("    <div class='metadata'>\n")
            f.write(f"      <p><strong>Model:</strong> {conversation_data.get('model', 'Unknown')}</p>\n")
            f.write(f"      <p><strong>Timestamp:</strong> {conversation_data.get('timestamp', 'Unknown')}</p>\n")
            f.write(f"      <p><strong>Messages:</strong> {len(conversation_data.get('messages', []))}</p>\n")
            f.write("    </div>\n")
            
            # Write system prompt
            system_prompt = conversation_data.get('system_prompt', '')
            if system_prompt:
                f.write("    <div class='system-prompt'>\n")
                f.write("      <strong>System Prompt:</strong>\n")
                f.write(f"      <p>{system_prompt}</p>\n")
                f.write("    </div>\n")
            
            # Write conversation
            f.write("    <h2>Conversation</h2>\n")
            messages = conversation_data.get('messages', [])
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                css_class = 'user' if role == 'user' else 'assistant'
                f.write(f"    <div class='message {css_class}'>\n")
                f.write(f"      <span class='role'>{role.upper()}</span>\n")
                f.write(f"      <div class='content'>{content}</div>\n")
                f.write("    </div>\n")
            
            # Write footer
            f.write("    <div class='footer'>\n")
            f.write(f"      <p>Exported on {datetime.now().isoformat()}</p>\n")
            f.write("    </div>\n")
            
            f.write("  </div>\n")
            f.write("</body>\n")
            f.write("</html>\n")
        
        return filepath
    
    except Exception as e:
        print(f"Error exporting to HTML: {e}")
        return None

def export_conversation(conversation_filename, export_format):
    """
    Main export function
    
    Args:
        conversation_filename: The conversation file to export
        export_format: 'markdown', 'csv', 'txt', 'html', or 'all'
    """
    conversation_data = load_conversation_data(conversation_filename)
    
    if not conversation_data:
        print(f"Could not load conversation: {conversation_filename}")
        return None
    
    exported_files = []
    base_filename = conversation_filename.replace('.json', '')
    
    if export_format in ['markdown', 'all']:
        file = export_to_markdown(conversation_data, base_filename)
        if file:
            exported_files.append(file)
    
    if export_format in ['csv', 'all']:
        file = export_to_csv(conversation_data, base_filename)
        if file:
            exported_files.append(file)
    
    if export_format in ['txt', 'all']:
        file = export_to_plain_text(conversation_data, base_filename)
        if file:
            exported_files.append(file)
    
    if export_format in ['html', 'all']:
        file = export_to_html(conversation_data, base_filename)
        if file:
            exported_files.append(file)
    
    return exported_files

def interactive_export():
    """Interactive export interface"""
    from conversation_manager import display_saved_conversations
    
    print("\n" + "=" * 60)
    print("Export Conversation")
    print("=" * 60)
    
    files = display_saved_conversations()
    
    if not files:
        return
    
    try:
        choice = input("\nEnter conversation number to export (or press Enter to cancel): ").strip()
        
        if not choice:
            return
        
        choice_num = int(choice) - 1
        if 0 <= choice_num < len(files):
            conversation_file = files[choice_num]
            
            print("\nExport format:")
            print("  1. Markdown")
            print("  2. CSV")
            print("  3. Plain Text")
            print("  4. HTML")
            print("  5. All formats")
            
            format_choice = input("\nSelect format (1-5): ").strip()
            
            format_map = {
                "1": "markdown",
                "2": "csv",
                "3": "txt",
                "4": "html",
                "5": "all"
            }
            
            export_format = format_map.get(format_choice, "markdown")
            
            exported = export_conversation(conversation_file, export_format)
            
            if exported:
                print(f"\n✓ Successfully exported {len(exported)} file(s):")
                for filepath in exported:
                    print(f"  - {filepath}")
            else:
                print("\nExport failed.")
        else:
            print("Invalid choice.")
    
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error during export: {e}")

