"""
Response Feedback System for rating and flagging responses
"""
import json
import os
from datetime import datetime

FEEDBACK_DIR = "feedback"

def ensure_feedback_dir():
    """Create feedback directory if it doesn't exist"""
    if not os.path.exists(FEEDBACK_DIR):
        os.makedirs(FEEDBACK_DIR)

def save_feedback(prompt, response, rating, flag=None, notes=""):
    """
    Save feedback for a response
    
    Args:
        prompt: The user's prompt
        response: The model's response
        rating: 1-5 stars (1=unhelpful, 5=very helpful)
        flag: Optional flag ('accuracy', 'bias', 'harmful', 'other')
        notes: Optional user notes
    """
    ensure_feedback_dir()
    
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "rating": rating,
        "flag": flag,
        "notes": notes
    }
    
    # Generate filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(FEEDBACK_DIR, f"feedback_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(feedback_data, f, indent=2)
    
    return filename

def get_feedback_summary():
    """Get summary statistics of all feedback"""
    ensure_feedback_dir()
    
    if not os.path.exists(FEEDBACK_DIR):
        return None
    
    ratings = []
    flags = {}
    total_feedback = 0
    
    for filename in os.listdir(FEEDBACK_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(FEEDBACK_DIR, filename), 'r') as f:
                    data = json.load(f)
                    total_feedback += 1
                    
                    # Collect ratings
                    rating = data.get('rating')
                    if rating:
                        ratings.append(rating)
                    
                    # Count flags
                    flag = data.get('flag')
                    if flag:
                        flags[flag] = flags.get(flag, 0) + 1
            except Exception as e:
                print(f"Error reading feedback file {filename}: {e}")
    
    # Calculate statistics
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    return {
        "total_feedback": total_feedback,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": {
            "5_stars": sum(1 for r in ratings if r == 5),
            "4_stars": sum(1 for r in ratings if r == 4),
            "3_stars": sum(1 for r in ratings if r == 3),
            "2_stars": sum(1 for r in ratings if r == 2),
            "1_star": sum(1 for r in ratings if r == 1)
        },
        "flags": flags
    }

def display_feedback_prompt():
    """Interactive prompt to collect feedback on a response"""
    print("\n" + "=" * 60)
    print("Rate this Response")
    print("=" * 60)
    
    # Ask for rating
    print("\nHow helpful was this response?")
    print("  1 - Not helpful at all")
    print("  2 - Somewhat unhelpful")
    print("  3 - Neutral")
    print("  4 - Helpful")
    print("  5 - Very helpful")
    
    while True:
        try:
            rating = int(input("\nEnter rating (1-5): ").strip())
            if 1 <= rating <= 5:
                break
            else:
                print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Ask if there's an issue
    flag = None
    has_issue = input("\nDoes this response have any issues? (y/n): ").strip().lower()
    
    if has_issue == 'y':
        print("\nWhat type of issue?")
        print("  1 - Accuracy (incorrect information)")
        print("  2 - Bias (biased perspective)")
        print("  3 - Harmful (contains harmful content)")
        print("  4 - Other")
        
        issue_choice = input("\nEnter choice (1-4): ").strip()
        issue_map = {
            "1": "accuracy",
            "2": "bias",
            "3": "harmful",
            "4": "other"
        }
        flag = issue_map.get(issue_choice)
    
    # Ask for notes
    notes = input("\nAny additional notes? (optional, press Enter to skip): ").strip()
    
    return rating, flag, notes

def list_feedback_by_rating(rating):
    """List all feedback with a specific rating"""
    ensure_feedback_dir()
    
    feedback_list = []
    
    if os.path.exists(FEEDBACK_DIR):
        for filename in os.listdir(FEEDBACK_DIR):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(FEEDBACK_DIR, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data.get('rating') == rating:
                            feedback_list.append((filename, data))
                except Exception as e:
                    print(f"Error reading feedback file {filename}: {e}")
    
    return sorted(feedback_list, reverse=True)

def display_flagged_feedback():
    """Display all flagged feedback"""
    ensure_feedback_dir()
    
    flagged = []
    
    if os.path.exists(FEEDBACK_DIR):
        for filename in os.listdir(FEEDBACK_DIR):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(FEEDBACK_DIR, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data.get('flag'):
                            flagged.append((filename, data))
                except Exception as e:
                    print(f"Error reading feedback file {filename}: {e}")
    
    if not flagged:
        print("\nNo flagged feedback.")
        return
    
    flagged = sorted(flagged, reverse=True)
    
    print("\n" + "=" * 60)
    print("Flagged Feedback:")
    print("=" * 60)
    
    for i, (filename, data) in enumerate(flagged, 1):
        flag_type = data.get('flag', 'Unknown')
        rating = data.get('rating', 'N/A')
        timestamp = data.get('timestamp', 'Unknown')
        prompt = data.get('prompt', '')[:50] + "..." if len(data.get('prompt', '')) > 50 else data.get('prompt', '')
        
        print(f"\n{i}. [{flag_type.upper()}] Rating: {rating}★ | {timestamp}")
        print(f"   Prompt: {prompt}")
        
        if data.get('notes'):
            print(f"   Notes: {data.get('notes')}")
    
    print("\n" + "=" * 60)

def display_feedback_summary():
    """Display feedback summary statistics"""
    summary = get_feedback_summary()
    
    if summary is None or summary['total_feedback'] == 0:
        print("\nNo feedback data available yet.")
        return
    
    print("\n" + "=" * 60)
    print("Feedback Summary Statistics")
    print("=" * 60)
    
    print(f"\nTotal Responses Rated: {summary['total_feedback']}")
    print(f"Average Rating: {summary['average_rating']}★ / 5★")
    
    print("\nRating Distribution:")
    dist = summary['rating_distribution']
    print(f"  ⭐⭐⭐⭐⭐ (5): {dist['5_stars']} responses")
    print(f"  ⭐⭐⭐⭐  (4): {dist['4_stars']} responses")
    print(f"  ⭐⭐⭐    (3): {dist['3_stars']} responses")
    print(f"  ⭐⭐      (2): {dist['2_stars']} responses")
    print(f"  ⭐        (1): {dist['1_star']} responses")
    
    if summary['flags']:
        print("\nFlagged Issues:")
        for flag_type, count in summary['flags'].items():
            print(f"  - {flag_type.capitalize()}: {count}")
    
    print("=" * 60)

def delete_feedback(filename):
    """Delete a feedback entry"""
    filepath = os.path.join(FEEDBACK_DIR, filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"Feedback deleted.")
            return True
        except Exception as e:
            print(f"Error deleting feedback: {e}")
            return False
    
    return False

