"""
Analysis tools for conversations: word frequency, tone, sentiment, etc.
"""
import json
import os
from collections import Counter
import re

CONVERSATIONS_DIR = "conversations"

def load_conversation(filename):
    """Load a conversation file"""
    filepath = os.path.join(CONVERSATIONS_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return None

def get_word_frequency(text, top_n=20, exclude_common=True):
    """Get word frequency from text"""
    # Common English stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'should',
        'would', 'could', 'will', 'shall', 'may', 'might', 'must', 'it', 'its',
        'as', 'if', 'that', 'this', 'which', 'who', 'what', 'where', 'when',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'same', 'so',
        'than', 'too', 'very', 'just', 'also', 'even', 'then', 'there'
    }
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter out stop words if requested
    if exclude_common:
        words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Count word frequencies
    word_freq = Counter(words)
    return word_freq.most_common(top_n)

def analyze_conversation_structure(conversation_data):
    """Analyze the structure of a conversation"""
    messages = conversation_data.get('messages', [])
    
    analysis = {
        'total_messages': len(messages),
        'user_messages': 0,
        'assistant_messages': 0,
        'average_user_message_length': 0,
        'average_assistant_message_length': 0,
        'longest_message': 0,
        'shortest_message': float('inf'),
        'conversation_turns': 0
    }
    
    user_lengths = []
    assistant_lengths = []
    
    for msg in messages:
        content_length = len(msg.get('content', ''))
        role = msg.get('role', '')
        
        analysis['longest_message'] = max(analysis['longest_message'], content_length)
        analysis['shortest_message'] = min(analysis['shortest_message'], content_length)
        
        if role == 'user':
            analysis['user_messages'] += 1
            user_lengths.append(content_length)
        elif role == 'assistant':
            analysis['assistant_messages'] += 1
            assistant_lengths.append(content_length)
    
    # Calculate averages
    if user_lengths:
        analysis['average_user_message_length'] = int(sum(user_lengths) / len(user_lengths))
    
    if assistant_lengths:
        analysis['average_assistant_message_length'] = int(sum(assistant_lengths) / len(assistant_lengths))
    
    # Count conversation turns (pairs of user/assistant messages)
    analysis['conversation_turns'] = min(analysis['user_messages'], analysis['assistant_messages'])
    
    analysis['shortest_message'] = 0 if analysis['shortest_message'] == float('inf') else analysis['shortest_message']
    
    return analysis

def analyze_conversation_topics(conversation_data):
    """Analyze topics in a conversation"""
    messages = conversation_data.get('messages', [])
    
    # Combine all messages
    all_text = ' '.join(msg.get('content', '') for msg in messages)
    
    # Get top words
    word_freq = get_word_frequency(all_text, top_n=20, exclude_common=True)
    
    return word_freq

def calculate_engagement_ratio(conversation_data):
    """Calculate engagement ratio (user vs assistant message lengths)"""
    analysis = analyze_conversation_structure(conversation_data)
    
    if analysis['average_assistant_message_length'] == 0:
        return 0
    
    ratio = analysis['average_user_message_length'] / analysis['average_assistant_message_length']
    return round(ratio, 2)

def detect_conversation_quality(conversation_data):
    """Detect quality metrics of conversation"""
    analysis = analyze_conversation_structure(conversation_data)
    
    quality = {
        'depth': 'shallow',
        'engagement': 'low',
        'length': 'short',
        'balance': 'unbalanced'
    }
    
    # Determine depth based on message lengths
    avg_length = (analysis['average_user_message_length'] + analysis['average_assistant_message_length']) / 2
    if avg_length > 500:
        quality['depth'] = 'deep'
    elif avg_length > 200:
        quality['depth'] = 'moderate'
    else:
        quality['depth'] = 'shallow'
    
    # Determine engagement based on number of turns
    if analysis['conversation_turns'] > 10:
        quality['engagement'] = 'high'
    elif analysis['conversation_turns'] > 5:
        quality['engagement'] = 'moderate'
    else:
        quality['engagement'] = 'low'
    
    # Determine length
    if analysis['total_messages'] > 20:
        quality['length'] = 'long'
    elif analysis['total_messages'] > 10:
        quality['length'] = 'medium'
    else:
        quality['length'] = 'short'
    
    # Determine balance
    if analysis['user_messages'] > 0 and analysis['assistant_messages'] > 0:
        ratio = min(analysis['user_messages'], analysis['assistant_messages']) / max(analysis['user_messages'], analysis['assistant_messages'])
        if ratio > 0.8:
            quality['balance'] = 'well-balanced'
        elif ratio > 0.5:
            quality['balance'] = 'moderately-balanced'
        else:
            quality['balance'] = 'unbalanced'
    
    return quality

def display_conversation_analysis(filename):
    """Display comprehensive analysis of a conversation"""
    conversation_data = load_conversation(filename)
    
    if not conversation_data:
        print("Could not load conversation.")
        return
    
    print("\n" + "=" * 60)
    print(f"Conversation Analysis: {filename}")
    print("=" * 60)
    
    # Structure analysis
    structure = analyze_conversation_structure(conversation_data)
    print("\n--- Structure ---")
    print(f"Total Messages:                {structure['total_messages']}")
    print(f"User Messages:                 {structure['user_messages']}")
    print(f"Assistant Messages:            {structure['assistant_messages']}")
    print(f"Conversation Turns:            {structure['conversation_turns']}")
    print(f"Average User Message Length:   {structure['average_user_message_length']} characters")
    print(f"Average Assistant Message:     {structure['average_assistant_message_length']} characters")
    print(f"Longest Message:               {structure['longest_message']} characters")
    print(f"Shortest Message:              {structure['shortest_message']} characters")
    
    # Quality metrics
    quality = detect_conversation_quality(conversation_data)
    print("\n--- Quality Metrics ---")
    print(f"Depth:                         {quality['depth']}")
    print(f"Engagement:                    {quality['engagement']}")
    print(f"Length:                        {quality['length']}")
    print(f"Balance:                       {quality['balance']}")
    
    # Engagement ratio
    engagement_ratio = calculate_engagement_ratio(conversation_data)
    print(f"\nEngagement Ratio:              {engagement_ratio} (User:Assistant)")
    if engagement_ratio > 1:
        print(f"  Users are asking longer questions than responses")
    elif engagement_ratio < 1:
        print(f"  Assistant is providing longer responses than user queries")
    
    # Top words
    topics = analyze_conversation_topics(conversation_data)
    print("\n--- Top Words (Content Frequency) ---")
    for i, (word, count) in enumerate(topics[:10], 1):
        print(f"{i:2d}. {word:20s} ({count} times)")
    
    # Metadata
    print("\n--- Metadata ---")
    print(f"Model:     {conversation_data.get('model', 'Unknown')}")
    print(f"Timestamp: {conversation_data.get('timestamp', 'Unknown')}")
    
    print("=" * 60)

def display_conversation_summary(filename):
    """Display a quick summary of conversation"""
    conversation_data = load_conversation(filename)
    
    if not conversation_data:
        print("Could not load conversation.")
        return
    
    structure = analyze_conversation_structure(conversation_data)
    quality = detect_conversation_quality(conversation_data)
    
    print(f"\n{filename}")
    print(f"  Messages: {structure['total_messages']} | Turns: {structure['conversation_turns']} | Depth: {quality['depth']} | Engagement: {quality['engagement']}")

def interactive_analysis():
    """Interactive conversation analysis"""
    from conversation_manager import display_saved_conversations
    
    print("\n" + "=" * 60)
    print("Analyze Conversation")
    print("=" * 60)
    
    files = display_saved_conversations()
    
    if not files:
        return
    
    try:
        choice = input("\nEnter conversation number to analyze (or press Enter to cancel): ").strip()
        
        if not choice:
            return
        
        choice_num = int(choice) - 1
        if 0 <= choice_num < len(files):
            filename = files[choice_num]
            display_conversation_analysis(filename)
        else:
            print("Invalid choice.")
    
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error: {e}")

