"""
Prompt Templates for common use cases
"""
import json
import os
from datetime import datetime

TEMPLATES_DIR = "templates"

# Built-in templates
BUILTIN_TEMPLATES = {
    "coding_help": {
        "name": "Coding Help",
        "description": "Get help with programming problems",
        "system_prompt": "You are an expert programmer. Provide clear, well-commented code solutions with explanations.",
        "template": "I need help with {language} programming. {question}",
        "placeholders": ["language", "question"]
    },
    "creative_writing": {
        "name": "Creative Writing",
        "description": "Assist with creative writing tasks",
        "system_prompt": "You are a creative writing assistant. Help users craft engaging, well-structured narratives with vivid descriptions.",
        "template": "Write a {genre} story about {topic}. Length: {length} words.",
        "placeholders": ["genre", "topic", "length"]
    },
    "explain_concept": {
        "name": "Explain Concept",
        "description": "Explain complex concepts simply",
        "system_prompt": "You are an expert educator. Explain concepts clearly and simply, using analogies and examples.",
        "template": "Explain {concept} to me as if I'm a {audience}. Focus on: {focus_points}",
        "placeholders": ["concept", "audience", "focus_points"]
    },
    "code_review": {
        "name": "Code Review",
        "description": "Review and critique code",
        "system_prompt": "You are an experienced code reviewer. Analyze code for quality, performance, security, and best practices.",
        "template": "Please review this {language} code for quality and improvements:\n\n{code}",
        "placeholders": ["language", "code"]
    },
    "summarize_text": {
        "name": "Summarize Text",
        "description": "Summarize long text into key points",
        "system_prompt": "You are a skilled summarizer. Create concise, accurate summaries capturing all key points.",
        "template": "Summarize the following text in {style}:\n\n{text}",
        "placeholders": ["style", "text"]
    },
    "brainstorm_ideas": {
        "name": "Brainstorm Ideas",
        "description": "Generate creative ideas for projects",
        "system_prompt": "You are a creative brainstorming assistant. Generate diverse, innovative ideas with practical applications.",
        "template": "Generate {count} ideas for {project_type} about {topic}. Focus on: {criteria}",
        "placeholders": ["count", "project_type", "topic", "criteria"]
    },
    "debug_error": {
        "name": "Debug Error",
        "description": "Help debug error messages",
        "system_prompt": "You are a debugging expert. Help identify and fix errors, explaining the root cause.",
        "template": "I'm getting this error in {language}:\n\n{error_message}\n\nContext: {context}",
        "placeholders": ["language", "error_message", "context"]
    },
    "tutorial_writer": {
        "name": "Tutorial Writer",
        "description": "Create step-by-step tutorials",
        "system_prompt": "You are an excellent tutorial writer. Create clear, step-by-step guides with examples.",
        "template": "Write a tutorial on how to {task} using {tool}. Target audience: {audience}",
        "placeholders": ["task", "tool", "audience"]
    }
}

def ensure_templates_dir():
    """Create templates directory if it doesn't exist"""
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)

def save_custom_template(name, description, system_prompt, template, placeholders):
    """Save a custom template"""
    ensure_templates_dir()
    
    template_data = {
        "name": name,
        "description": description,
        "system_prompt": system_prompt,
        "template": template,
        "placeholders": placeholders,
        "created_at": datetime.now().isoformat(),
        "custom": True
    }
    
    filename = os.path.join(TEMPLATES_DIR, f"{name.lower().replace(' ', '_')}.json")
    
    with open(filename, 'w') as f:
        json.dump(template_data, f, indent=2)
    
    return filename

def load_custom_template(template_id):
    """Load a custom template"""
    filename = os.path.join(TEMPLATES_DIR, f"{template_id}.json")
    
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading template: {e}")
        return None

def list_all_templates():
    """Get all available templates (builtin + custom)"""
    all_templates = {}
    
    # Add builtin templates
    for template_id, template_data in BUILTIN_TEMPLATES.items():
        all_templates[template_id] = {
            **template_data,
            "custom": False,
            "id": template_id
        }
    
    # Add custom templates
    ensure_templates_dir()
    if os.path.exists(TEMPLATES_DIR):
        for filename in os.listdir(TEMPLATES_DIR):
            if filename.endswith('.json'):
                template_id = filename[:-5]
                try:
                    with open(os.path.join(TEMPLATES_DIR, filename), 'r') as f:
                        template_data = json.load(f)
                        template_data["id"] = template_id
                        all_templates[template_id] = template_data
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")
    
    return all_templates

def display_templates():
    """Display all available templates"""
    templates = list_all_templates()
    
    if not templates:
        print("\nNo templates available.")
        return None
    
    print("\n" + "=" * 60)
    print("Available Prompt Templates:")
    print("=" * 60)
    
    template_list = list(templates.items())
    for i, (template_id, template_data) in enumerate(template_list, 1):
        is_custom = " (custom)" if template_data.get("custom") else ""
        print(f"{i}. {template_data.get('name')}{is_custom}")
        print(f"   {template_data.get('description')}")
    
    print("=" * 60)
    return template_list

def get_template_by_index(index):
    """Get template by display index"""
    templates = list_all_templates()
    template_list = list(templates.items())
    
    if 0 <= index < len(template_list):
        template_id, template_data = template_list[index]
        return template_id, template_data
    
    return None, None

def fill_template(template_data):
    """Interactive function to fill in template placeholders"""
    print("\n" + "=" * 60)
    print(f"Using Template: {template_data.get('name')}")
    print("=" * 60)
    print(f"Description: {template_data.get('description')}")
    print(f"\nTemplate: {template_data.get('template')}\n")
    
    placeholders = template_data.get('placeholders', [])
    filled_values = {}
    
    if placeholders:
        print("Please fill in the following fields:")
        for placeholder in placeholders:
            value = input(f"  {placeholder}: ").strip()
            filled_values[placeholder] = value
    
    # Fill in the template
    prompt = template_data.get('template')
    for placeholder, value in filled_values.items():
        prompt = prompt.replace(f"{{{placeholder}}}", value)
    
    return prompt, template_data.get('system_prompt')

def delete_custom_template(template_id):
    """Delete a custom template"""
    filename = os.path.join(TEMPLATES_DIR, f"{template_id}.json")
    
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"Template '{template_id}' deleted.")
            return True
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    return False

