"""
Batch processing functionality for multiple prompts
"""
import json
import os
import csv
from datetime import datetime

BATCH_DIR = "batch_jobs"
RESULTS_DIR = "batch_results"

def ensure_batch_dirs():
    """Create batch directories if they don't exist"""
    if not os.path.exists(BATCH_DIR):
        os.makedirs(BATCH_DIR)
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

def create_batch_job(prompts, model, system_prompt="You are a helpful assistant.", job_name=None):
    """
    Create a batch job from a list of prompts
    
    Args:
        prompts: List of prompt strings
        model: Model name to use
        system_prompt: System prompt for all requests
        job_name: Optional name for the job
    """
    ensure_batch_dirs()
    
    if not job_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = f"batch_{timestamp}"
    
    job_data = {
        "name": job_name,
        "created_at": datetime.now().isoformat(),
        "model": model,
        "system_prompt": system_prompt,
        "prompts": [
            {
                "id": i + 1,
                "prompt": prompt,
                "status": "pending",
                "response": None,
                "timestamp": None
            }
            for i, prompt in enumerate(prompts)
        ],
        "statistics": {
            "total": len(prompts),
            "completed": 0,
            "failed": 0,
            "pending": len(prompts)
        }
    }
    
    filename = os.path.join(BATCH_DIR, f"{job_name}.json")
    
    with open(filename, 'w') as f:
        json.dump(job_data, f, indent=2)
    
    return filename, job_data

def load_batch_job(job_name):
    """Load a batch job"""
    filename = os.path.join(BATCH_DIR, f"{job_name}.json")
    
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading batch job: {e}")
        return None

def save_batch_job(job_data):
    """Save a batch job"""
    ensure_batch_dirs()
    
    job_name = job_data.get('name', 'batch')
    filename = os.path.join(BATCH_DIR, f"{job_name}.json")
    
    with open(filename, 'w') as f:
        json.dump(job_data, f, indent=2)
    
    return filename

def update_batch_response(job_name, prompt_id, response):
    """Update a response for a prompt in a batch job"""
    job_data = load_batch_job(job_name)
    
    if not job_data:
        return False
    
    # Find and update the prompt
    for prompt_item in job_data['prompts']:
        if prompt_item['id'] == prompt_id:
            prompt_item['status'] = 'completed'
            prompt_item['response'] = response
            prompt_item['timestamp'] = datetime.now().isoformat()
            
            # Update statistics
            job_data['statistics']['completed'] += 1
            job_data['statistics']['pending'] -= 1
            
            save_batch_job(job_data)
            return True
    
    return False

def list_batch_jobs():
    """List all batch jobs"""
    ensure_batch_dirs()
    
    jobs = []
    
    if os.path.exists(BATCH_DIR):
        for filename in os.listdir(BATCH_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(BATCH_DIR, filename), 'r') as f:
                        job = json.load(f)
                        jobs.append(job)
                except Exception as e:
                    print(f"Error reading job {filename}: {e}")
    
    return sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)

def display_batch_jobs():
    """Display all batch jobs"""
    jobs = list_batch_jobs()
    
    if not jobs:
        print("\nNo batch jobs found.")
        return None
    
    print("\n" + "=" * 60)
    print("Batch Jobs:")
    print("=" * 60)
    
    for i, job in enumerate(jobs, 1):
        name = job.get('name', 'Unknown')
        model = job.get('model', 'Unknown')
        total = job['statistics'].get('total', 0)
        completed = job['statistics'].get('completed', 0)
        created = job.get('created_at', 'Unknown')
        
        progress = f"{completed}/{total}"
        print(f"\n{i}. {name}")
        print(f"   Model: {model}")
        print(f"   Progress: {progress} | Created: {created}")
    
    print("\n" + "=" * 60)
    return jobs

def export_batch_results(job_name, format='csv'):
    """Export batch results to file"""
    job_data = load_batch_job(job_name)
    
    if not job_data:
        print(f"Job '{job_name}' not found.")
        return None
    
    ensure_batch_dirs()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{job_name}_results_{timestamp}"
    
    if format == 'csv':
        filename = os.path.join(RESULTS_DIR, f"{base_name}.csv")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['ID', 'Status', 'Prompt', 'Response', 'Timestamp'])
                
                # Write data
                for prompt_item in job_data['prompts']:
                    writer.writerow([
                        prompt_item['id'],
                        prompt_item['status'],
                        prompt_item['prompt'],
                        prompt_item.get('response', ''),
                        prompt_item.get('timestamp', '')
                    ])
            
            return filename
        
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return None
    
    elif format == 'json':
        filename = os.path.join(RESULTS_DIR, f"{base_name}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            return filename
        
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return None

def create_batch_from_file(filepath, model, system_prompt="You are a helpful assistant."):
    """
    Create a batch job from a file of prompts
    
    Args:
        filepath: Path to file containing prompts (one per line for TXT, or JSON array)
        model: Model to use
        system_prompt: System prompt
    """
    prompts = []
    
    try:
        # Try JSON format first
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    prompts = data
                elif isinstance(data, dict) and 'prompts' in data:
                    prompts = data['prompts']
        
        # Try text format
        elif filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                prompts = [line.strip() for line in f if line.strip()]
        
        # Try CSV format
        elif filepath.endswith('.csv'):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                prompts = [row[0] for row in reader if row]
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    if not prompts:
        print("No prompts found in file.")
        return None
    
    # Create batch job
    job_name = os.path.splitext(os.path.basename(filepath))[0]
    filename, job_data = create_batch_job(prompts, model, system_prompt, job_name)
    
    return filename, job_data

def get_batch_statistics(job_name):
    """Get statistics for a batch job"""
    job_data = load_batch_job(job_name)
    
    if not job_data:
        return None
    
    return {
        'name': job_data.get('name'),
        'created_at': job_data.get('created_at'),
        'model': job_data.get('model'),
        'statistics': job_data.get('statistics'),
        'prompts_count': len(job_data.get('prompts', []))
    }

def display_batch_job_details(job_name):
    """Display detailed information about a batch job"""
    job_data = load_batch_job(job_name)
    
    if not job_data:
        print(f"Job '{job_name}' not found.")
        return
    
    print("\n" + "=" * 60)
    print(f"Batch Job: {job_name}")
    print("=" * 60)
    
    print(f"\nCreated: {job_data.get('created_at')}")
    print(f"Model: {job_data.get('model')}")
    print(f"System Prompt: {job_data.get('system_prompt', '')[:80]}...")
    
    stats = job_data['statistics']
    print(f"\nStatistics:")
    print(f"  Total Prompts: {stats['total']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Failed: {stats['failed']}")
    
    progress_percent = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  Progress: {progress_percent:.1f}%")
    
    print(f"\nPrompts:")
    for prompt_item in job_data['prompts'][:10]:  # Show first 10
        status = prompt_item['status']
        prompt_text = prompt_item['prompt'][:50] + "..." if len(prompt_item['prompt']) > 50 else prompt_item['prompt']
        print(f"  [{status.upper()}] {prompt_item['id']}. {prompt_text}")
    
    if len(job_data['prompts']) > 10:
        print(f"  ... and {len(job_data['prompts']) - 10} more")
    
    print("=" * 60)

def process_batch_job(job_name, generate_function, model_params):
    """
    Execute/process a batch job
    
    Args:
        job_name: Name of the batch job
        generate_function: Function to call for text generation (generate_text_streaming)
        model_params: Model parameters object for configuration
    """
    job_data = load_batch_job(job_name)
    
    if not job_data:
        print(f"Job '{job_name}' not found.")
        return False
    
    print("\n" + "=" * 60)
    print(f"Processing Batch: {job_name}")
    print("=" * 60)
    
    stats = job_data['statistics']
    total = stats['total']
    completed = stats['completed']
    pending = stats['pending']
    
    print(f"\nJob Status: {completed}/{total} completed")
    
    if pending == 0:
        print("All prompts have already been processed!")
        return True
    
    proceed = input(f"\nProcess {pending} pending prompt(s)? (y/n): ").strip().lower()
    if proceed != 'y':
        return False
    
    # Process each pending prompt
    processed_count = 0
    for i, prompt_item in enumerate(job_data['prompts'], 1):
        if prompt_item['status'] == 'pending':
            prompt_id = prompt_item['id']
            prompt_text = prompt_item['prompt']
            
            print(f"\n[{i}/{total}] Processing: {prompt_text[:60]}...")
            
            try:
                # Generate response using the provided function
                response = generate_function(prompt_text, job_data['model'])
                
                # Update the job with the response
                update_batch_response(job_name, prompt_id, response)
                processed_count += 1
                
                print(f"✓ Complete")
            
            except Exception as e:
                print(f"✗ Error: {e}")
                # Mark as failed
                job_data = load_batch_job(job_name)
                for item in job_data['prompts']:
                    if item['id'] == prompt_id:
                        item['status'] = 'failed'
                        job_data['statistics']['failed'] += 1
                        job_data['statistics']['pending'] -= 1
                save_batch_job(job_data)
    
    print(f"\n{'=' * 60}")
    print(f"Batch Processing Complete!")
    print(f"✓ Processed: {processed_count} prompts")
    print(f"{'=' * 60}")
    
    return True

def interactive_batch_processor():
    """Interactive batch processing menu"""
    while True:
        print("\n" + "=" * 60)
        print("Batch Processing")
        print("=" * 60)
        print("\nOptions:")
        print("  1. Create batch from text input")
        print("  2. Create batch from file")
        print("  3. View batch jobs")
        print("  4. View job details")
        print("  5. Process batch job")
        print("  6. Export results")
        print("  0. Back to main menu")
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == "1":
            print("\nEnter prompts (type 'DONE' on a new line to finish):")
            prompts = []
            while True:
                prompt = input("Prompt: ").strip()
                if prompt.upper() == 'DONE':
                    break
                if prompt:
                    prompts.append(prompt)
            
            if prompts:
                model = input("Enter model name (default: gpt-4o-mini): ").strip() or "gpt-4o-mini"
                filename, job_data = create_batch_job(prompts, model)
                print(f"\n✓ Batch job created: {filename}")
                print(f"  Total prompts: {len(prompts)}")
        
        elif choice == "2":
            filepath = input("Enter file path: ").strip()
            if os.path.exists(filepath):
                model = input("Enter model name (default: gpt-4o-mini): ").strip() or "gpt-4o-mini"
                result = create_batch_from_file(filepath, model)
                if result:
                    filename, job_data = result
                    print(f"\n✓ Batch job created from file: {filename}")
                    print(f"  Total prompts: {len(job_data['prompts'])}")
            else:
                print("File not found.")
        
        elif choice == "3":
            display_batch_jobs()
        
        elif choice == "4":
            jobs = list_batch_jobs()
            if jobs:
                for i, job in enumerate(jobs, 1):
                    print(f"{i}. {job['name']}")
                job_choice = input("Select job number: ").strip()
                try:
                    job_idx = int(job_choice) - 1
                    if 0 <= job_idx < len(jobs):
                        display_batch_job_details(jobs[job_idx]['name'])
                except ValueError:
                    print("Invalid choice.")
        
        elif choice == "5":
            jobs = list_batch_jobs()
            if jobs:
                print("\nSelect batch job to process:")
                for i, job in enumerate(jobs, 1):
                    progress = job['statistics']['completed']
                    total = job['statistics']['total']
                    print(f"{i}. {job['name']} ({progress}/{total} completed)")
                job_choice = input("\nSelect job number: ").strip()
                try:
                    job_idx = int(job_choice) - 1
                    if 0 <= job_idx < len(jobs):
                        job_name = jobs[job_idx]['name']
                        # Note: This is a placeholder - the actual processing is called from app.py
                        # where we have access to the generate_text_streaming function
                        print(f"\nNote: Use 'batch-run {job_name}' from main menu or call from app context")
                        print(f"For now, please use the main menu to process: {job_name}")
                except ValueError:
                    print("Invalid choice.")
        
        elif choice == "6":
            jobs = list_batch_jobs()
            if jobs:
                print("\nSelect batch job to export:")
                for i, job in enumerate(jobs, 1):
                    print(f"{i}. {job['name']}")
                job_choice = input("\nSelect job number: ").strip()
                try:
                    job_idx = int(job_choice) - 1
                    if 0 <= job_idx < len(jobs):
                        job_name = jobs[job_idx]['name']
                        format_choice = input("Export format (csv/json): ").strip() or "csv"
                        filepath = export_batch_results(job_name, format_choice)
                        if filepath:
                            print(f"✓ Results exported to: {filepath}")
                except ValueError:
                    print("Invalid choice.")
        
        elif choice == "0":
            break
        
        else:
            print("Invalid choice.")

