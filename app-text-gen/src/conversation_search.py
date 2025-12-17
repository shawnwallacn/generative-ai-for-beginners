"""
Search functionality for saved conversations
"""
import json
import os
from datetime import datetime

CONVERSATIONS_DIR = "conversations"

def search_conversations(query, search_type="content"):
    """
    Search through saved conversations
    
    Args:
        query: Search string
        search_type: 'content', 'prompt', 'model', or 'all'
    
    Returns:
        List of tuples (filename, data, matches)
    """
    results = []
    
    if not os.path.exists(CONVERSATIONS_DIR):
        return results
    
    query_lower = query.lower()
    
    for filename in os.listdir(CONVERSATIONS_DIR):
        if not filename.endswith('.json'):
            continue
        
        try:
            filepath = os.path.join(CONVERSATIONS_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            matches = []
            
            # Search in messages (content)
            if search_type in ['content', 'all']:
                messages = data.get('messages', [])
                for i, msg in enumerate(messages):
                    content = msg.get('content', '').lower()
                    if query_lower in content:
                        matches.append({
                            'type': 'message',
                            'index': i,
                            'role': msg.get('role'),
                            'snippet': msg.get('content')[:100] + "..." if len(msg.get('content', '')) > 100 else msg.get('content')
                        })
            
            # Search in prompts
            if search_type in ['prompt', 'all']:
                system_prompt = data.get('system_prompt', '').lower()
                if query_lower in system_prompt:
                    matches.append({
                        'type': 'system_prompt',
                        'content': data.get('system_prompt')
                    })
            
            # Search in model name
            if search_type in ['model', 'all']:
                model = data.get('model', '').lower()
                if query_lower in model:
                    matches.append({
                        'type': 'model',
                        'model': data.get('model')
                    })
            
            # Add result if there are matches
            if matches:
                results.append((filename, data, matches))
        
        except Exception as e:
            print(f"Error searching in {filename}: {e}")
    
    return results

def display_search_results(results):
    """Display search results in a formatted way"""
    if not results:
        print("\nNo results found.")
        return
    
    print("\n" + "=" * 60)
    print(f"Search Results ({len(results)} conversations found)")
    print("=" * 60)
    
    for i, (filename, data, matches) in enumerate(results, 1):
        timestamp = data.get('timestamp', 'Unknown')
        model = data.get('model', 'Unknown')
        msg_count = len(data.get('messages', []))
        
        print(f"\n{i}. {filename}")
        print(f"   Model: {model} | Messages: {msg_count} | Time: {timestamp}")
        print(f"   Matches: {len(matches)}")
        
        for j, match in enumerate(matches[:3]):  # Show first 3 matches
            if match['type'] == 'message':
                print(f"     - Message {match['index']} [{match['role'].upper()}]: {match['snippet']}")
            elif match['type'] == 'system_prompt':
                print(f"     - System Prompt: {match['content'][:50]}...")
            elif match['type'] == 'model':
                print(f"     - Model: {match['model']}")
        
        if len(matches) > 3:
            print(f"     ... and {len(matches) - 3} more matches")
    
    print("\n" + "=" * 60)
    
    return results

def interactive_search():
    """Interactive search interface"""
    print("\n" + "=" * 60)
    print("Search Conversations")
    print("=" * 60)
    
    print("\nSearch by:")
    print("  1. Content (search in all messages)")
    print("  2. Prompt (search in system prompts)")
    print("  3. Model (search by model name)")
    print("  4. All (search everywhere)")
    
    choice = input("\nSelect search type (1-4, default: 1): ").strip()
    
    search_type_map = {
        "1": "content",
        "2": "prompt",
        "3": "model",
        "4": "all",
        "": "content"
    }
    
    search_type = search_type_map.get(choice, "content")
    
    query = input(f"\nEnter search query: ").strip()
    
    if not query:
        print("Search query cannot be empty.")
        return None
    
    results = search_conversations(query, search_type)
    return display_search_results(results)

def search_by_date_range(start_date, end_date):
    """Search conversations within a date range"""
    results = []
    
    if not os.path.exists(CONVERSATIONS_DIR):
        return results
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        print("Invalid date format. Use ISO format (YYYY-MM-DD).")
        return results
    
    for filename in os.listdir(CONVERSATIONS_DIR):
        if not filename.endswith('.json'):
            continue
        
        try:
            filepath = os.path.join(CONVERSATIONS_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            timestamp_str = data.get('timestamp', '')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str)
                if start <= timestamp <= end:
                    results.append((filename, data, []))
        
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return results

def get_conversation_stats(filename):
    """Get detailed statistics for a specific conversation"""
    filepath = os.path.join(CONVERSATIONS_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        messages = data.get('messages', [])
        
        # Count messages by role
        user_messages = sum(1 for msg in messages if msg.get('role') == 'user')
        assistant_messages = sum(1 for msg in messages if msg.get('role') == 'assistant')
        
        # Calculate total tokens (rough estimate)
        total_words = sum(len(msg.get('content', '').split()) for msg in messages)
        estimated_tokens = int(total_words * 1.3)  # Rough estimate
        
        # Find longest message
        longest_msg = max(
            (msg for msg in messages),
            key=lambda msg: len(msg.get('content', '')),
            default=None
        )
        
        return {
            'filename': filename,
            'timestamp': data.get('timestamp'),
            'model': data.get('model'),
            'system_prompt': data.get('system_prompt'),
            'total_messages': len(messages),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'estimated_tokens': estimated_tokens,
            'longest_message_length': len(longest_msg.get('content', '')) if longest_msg else 0,
            'longest_message_role': longest_msg.get('role') if longest_msg else None
        }
    
    except Exception as e:
        print(f"Error reading conversation stats: {e}")
        return None

def display_conversation_stats(filename):
    """Display detailed statistics for a conversation"""
    stats = get_conversation_stats(filename)
    
    if not stats:
        print("Could not load conversation statistics.")
        return
    
    print("\n" + "=" * 60)
    print(f"Conversation Statistics: {filename}")
    print("=" * 60)
    
    print(f"\nTimestamp: {stats['timestamp']}")
    print(f"Model: {stats['model']}")
    print(f"System Prompt: {stats['system_prompt'][:50]}..." if len(stats['system_prompt']) > 50 else stats['system_prompt'])
    
    print(f"\nMessage Statistics:")
    print(f"  Total Messages: {stats['total_messages']}")
    print(f"  User Messages: {stats['user_messages']}")
    print(f"  Assistant Messages: {stats['assistant_messages']}")
    
    print(f"\nToken Statistics:")
    print(f"  Estimated Tokens: {stats['estimated_tokens']}")
    print(f"  Longest Message: {stats['longest_message_length']} characters ({stats['longest_message_role']})")
    
    print("=" * 60)

