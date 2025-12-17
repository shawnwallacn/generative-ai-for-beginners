"""
Usage statistics tracking for API calls, token counts, and model usage
"""
import json
import os
from datetime import datetime
from collections import defaultdict

STATS_DIR = "statistics"
STATS_FILE = "usage_stats.json"

def ensure_stats_dir():
    """Create statistics directory if it doesn't exist"""
    if not os.path.exists(STATS_DIR):
        os.makedirs(STATS_DIR)

def get_stats_filepath():
    """Get the path to the stats file"""
    return os.path.join(STATS_DIR, STATS_FILE)

def load_usage_stats():
    """Load usage statistics from file"""
    ensure_stats_dir()
    filepath = get_stats_filepath()
    
    if not os.path.exists(filepath):
        return {
            "created_at": datetime.now().isoformat(),
            "total_requests": 0,
            "total_tokens_used": 0,
            "total_cost_estimate": 0.0,
            "by_model": {},
            "by_date": {},
            "requests": []
        }
    
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading stats: {e}")
        return {}

def save_usage_stats(stats):
    """Save usage statistics to file"""
    ensure_stats_dir()
    filepath = get_stats_filepath()
    
    try:
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving stats: {e}")
        return False

def record_request(model, prompt_tokens, completion_tokens, system_prompt=""):
    """
    Record an API request
    
    Args:
        model: Model used
        prompt_tokens: Tokens in the prompt
        completion_tokens: Tokens in the completion
        system_prompt: The system prompt used
    """
    stats = load_usage_stats()
    
    total_tokens = prompt_tokens + completion_tokens
    
    # Estimate cost (rough approximation based on OpenAI pricing)
    # Note: GitHub Models may have different pricing
    cost_estimate = estimate_cost(model, prompt_tokens, completion_tokens)
    
    request_record = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": cost_estimate
    }
    
    # Update overall stats
    stats["total_requests"] += 1
    stats["total_tokens_used"] += total_tokens
    stats["total_cost_estimate"] += cost_estimate
    
    # Update by model
    if model not in stats["by_model"]:
        stats["by_model"][model] = {
            "requests": 0,
            "tokens": 0,
            "cost": 0.0
        }
    
    stats["by_model"][model]["requests"] += 1
    stats["by_model"][model]["tokens"] += total_tokens
    stats["by_model"][model]["cost"] += cost_estimate
    
    # Update by date
    date_key = datetime.now().strftime("%Y-%m-%d")
    if date_key not in stats["by_date"]:
        stats["by_date"][date_key] = {
            "requests": 0,
            "tokens": 0,
            "cost": 0.0
        }
    
    stats["by_date"][date_key]["requests"] += 1
    stats["by_date"][date_key]["tokens"] += total_tokens
    stats["by_date"][date_key]["cost"] += cost_estimate
    
    # Add to requests list (keep last 100)
    stats["requests"].append(request_record)
    if len(stats["requests"]) > 100:
        stats["requests"] = stats["requests"][-100:]
    
    save_usage_stats(stats)
    
    return request_record

def estimate_cost(model, prompt_tokens, completion_tokens):
    """
    Estimate cost for a request
    
    Note: These are approximate pricing models.
    GitHub Models may have different or free pricing.
    """
    # Pricing estimates (per 1K tokens)
    pricing = {
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4.1": {"prompt": 0.03, "completion": 0.06},
        "gpt-5-mini": {"prompt": 0.001, "completion": 0.004},
        "claude-3.5-haiku": {"prompt": 0.0008, "completion": 0.004},
        "default": {"prompt": 0.0015, "completion": 0.006}
    }
    
    model_pricing = pricing.get(model, pricing["default"])
    
    prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
    completion_cost = (completion_tokens / 1000) * model_pricing["completion"]
    
    return round(prompt_cost + completion_cost, 6)

def get_usage_summary():
    """Get summary of usage statistics"""
    stats = load_usage_stats()
    
    if not stats:
        return None
    
    summary = {
        "total_requests": stats.get("total_requests", 0),
        "total_tokens": stats.get("total_tokens_used", 0),
        "total_cost": stats.get("total_cost_estimate", 0.0),
        "by_model": stats.get("by_model", {}),
        "by_date": stats.get("by_date", {}),
        "average_tokens_per_request": 0
    }
    
    if summary["total_requests"] > 0:
        summary["average_tokens_per_request"] = summary["total_tokens"] // summary["total_requests"]
    
    return summary

def display_usage_stats():
    """Display usage statistics"""
    summary = get_usage_summary()
    
    if not summary or summary["total_requests"] == 0:
        print("\nNo usage statistics available yet.")
        return
    
    print("\n" + "=" * 60)
    print("Usage Statistics")
    print("=" * 60)
    
    print(f"\nOverall Statistics:")
    print(f"  Total Requests:            {summary['total_requests']}")
    print(f"  Total Tokens Used:         {summary['total_tokens']:,}")
    print(f"  Average Tokens/Request:    {summary['average_tokens_per_request']}")
    print(f"  Estimated Total Cost:      ${summary['total_cost']:.6f}")
    
    print(f"\nBy Model:")
    for model, data in sorted(summary['by_model'].items()):
        print(f"  {model}")
        print(f"    - Requests: {data['requests']}")
        print(f"    - Tokens: {data['tokens']:,}")
        print(f"    - Cost: ${data['cost']:.6f}")
    
    print(f"\nRecent Usage (Last 7 Days):")
    stats = load_usage_stats()
    dates = sorted(stats.get('by_date', {}).keys(), reverse=True)[:7]
    
    for date in reversed(dates):
        data = stats['by_date'][date]
        print(f"  {date}: {data['requests']} requests, {data['tokens']:,} tokens, ${data['cost']:.6f}")
    
    print("=" * 60)

def get_model_comparison():
    """Get comparison of model usage"""
    summary = get_usage_summary()
    
    if not summary:
        return None
    
    comparison = []
    
    for model, data in summary['by_model'].items():
        comparison.append({
            'model': model,
            'requests': data['requests'],
            'tokens': data['tokens'],
            'cost': data['cost'],
            'cost_per_request': data['cost'] / data['requests'] if data['requests'] > 0 else 0,
            'tokens_per_request': data['tokens'] // data['requests'] if data['requests'] > 0 else 0
        })
    
    return sorted(comparison, key=lambda x: x['requests'], reverse=True)

def display_model_comparison():
    """Display model usage comparison"""
    comparison = get_model_comparison()
    
    if not comparison:
        print("\nNo model usage data available.")
        return
    
    print("\n" + "=" * 60)
    print("Model Usage Comparison")
    print("=" * 60)
    
    print(f"\n{'Model':<20} {'Requests':<12} {'Tokens':<15} {'Cost':<12}")
    print("-" * 60)
    
    for item in comparison:
        print(f"{item['model']:<20} {item['requests']:<12} {item['tokens']:<15} ${item['cost']:<11.6f}")
    
    print("\nMost Cost-Effective Model:")
    best = min(comparison, key=lambda x: x['cost_per_request'])
    print(f"  {best['model']}: ${best['cost_per_request']:.6f} per request")
    
    print("\nMost Used Model:")
    most_used = max(comparison, key=lambda x: x['requests'])
    print(f"  {most_used['model']}: {most_used['requests']} requests")
    
    print("=" * 60)

def export_usage_stats_csv():
    """Export usage statistics to CSV"""
    import csv
    from datetime import datetime
    
    stats = load_usage_stats()
    
    if not stats.get('requests'):
        print("No requests to export.")
        return None
    
    ensure_stats_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(STATS_DIR, f"usage_export_{timestamp}.csv")
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Timestamp', 'Model', 'Prompt Tokens', 'Completion Tokens', 'Total Tokens', 'Estimated Cost'])
            
            # Write data
            for request in stats['requests']:
                writer.writerow([
                    request['timestamp'],
                    request['model'],
                    request['prompt_tokens'],
                    request['completion_tokens'],
                    request['total_tokens'],
                    f"${request['estimated_cost']:.6f}"
                ])
        
        return filepath
    
    except Exception as e:
        print(f"Error exporting stats: {e}")
        return None

def interactive_stats_menu():
    """Interactive statistics menu"""
    while True:
        print("\n" + "=" * 60)
        print("Usage Statistics")
        print("=" * 60)
        print("\nOptions:")
        print("  1. View overall statistics")
        print("  2. Compare model usage")
        print("  3. Export statistics to CSV")
        print("  0. Back to main menu")
        
        choice = input("\nSelect option (0-3): ").strip()
        
        if choice == "1":
            display_usage_stats()
        
        elif choice == "2":
            display_model_comparison()
        
        elif choice == "3":
            filepath = export_usage_stats_csv()
            if filepath:
                print(f"\n✓ Statistics exported to: {filepath}")
        
        elif choice == "0":
            break
        
        else:
            print("Invalid choice.")

