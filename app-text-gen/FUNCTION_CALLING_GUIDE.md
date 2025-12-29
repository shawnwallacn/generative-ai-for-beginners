# Function Calling Integration Guide

## Overview

This guide explains how function calling has been integrated into your app and how to test it. Function calling enables the LLM to intelligently call tools based on user requests.

## What is Function Calling?

Function calling allows:
1. **LLM Decision Making**: The LLM decides WHEN to call a function based on user input
2. **Consistent Responses**: Structured data back from the LLM via function definitions
3. **External Tool Integration**: Call APIs, databases, or custom functions
4. **Multi-turn Conversations**: Function results can feed back into the conversation

### How It Works (3-Step Process)

```
User Message
    ↓
1. LLM receives message + function definitions
    ↓
2a. If LLM decides to call a function:
    - Extract function name and arguments
    - Execute the Python function
    - Add result to conversation
    ↓
2b. If no function needed:
    - Continue with normal response
    ↓
3. Final response sent to user
```

## Implemented Functions

### Phase 1: Knowledge Base Query Functions

These functions let the LLM search and retrieve from your KB automatically.

#### 1. `search_knowledge_base(query, collection="")`
**When LLM calls this**: When user asks about topics in your KB

**Example triggers**:
- "Tell me about the 6502 instruction set"
- "What's in our knowledge base about assembly?"
- "Search KB for memory addressing modes"

**What happens**:
1. LLM extracts `query="6502 instruction set"`
2. Function searches embeddings with `similarity_threshold=0.15`
3. Returns top 3 matching KB documents
4. LLM uses results to provide better answer

#### 2. `get_kb_document(document_id)`
**When LLM calls this**: When user wants full document content

**Example triggers**:
- "Show me the full 6502 guide"
- "Get the complete assembly document"

**What happens**:
1. LLM extracts `document_id="6502 Microprocessor Guide"`
2. Function retrieves all chunks and combines them
3. Returns full document with metadata
4. LLM presents this to user

#### 3. `get_kb_stats(collection="")`
**When LLM calls this**: When user asks about KB contents/statistics

**Example triggers**:
- "How many documents are in our KB?"
- "What collections do we have?"
- "Tell me about the KB size"

**What happens**:
1. LLM decides statistics would help
2. Function returns KB statistics
3. LLM provides formatted information to user

### Phase 2: Data Extraction Functions

These functions let the LLM extract and store structured data from conversations.

#### 4. `extract_code_snippet(language, title, code, description="")`
**When LLM calls this**: When user asks to save code or LLM identifies useful code

**Example triggers**:
- "Save this code snippet for later"
- "Extract the assembly code we discussed"
- User shares code that LLM recognizes as important

**What happens**:
1. LLM extracts: `language="6502_asm"`, `title="Stack Operations"`, `code="..."`
2. Function stores snippet with metadata and timestamp
3. Returns confirmation with snippet ID
4. Snippet saved to `function_calling/code_snippets.json`

**Use case**: Build a personal code library from conversations

#### 5. `create_summary(topic, key_points, explanation="")`
**When LLM calls this**: When user asks for summary or structured notes

**Example triggers**:
- "Create a summary of what we discussed"
- "Generate study notes for 6502 assembly"
- "Summarize the key concepts"

**What happens**:
1. LLM extracts: `topic="6502 Assembly"`, `key_points=["Addressing modes", "Stack operations", ...]`
2. Function stores structured summary with timestamp
3. Returns confirmation with summary ID
4. Summary saved to `function_calling/summaries.json`

**Use case**: Generate structured learning materials

## How the Integration Works

### 1. Function Definitions

File: `src/function_calling.py` - `FunctionDefinitions` class

Defines what functions exist and their parameters:
```python
functions = [
    {
        "name": "search_knowledge_base",
        "description": "Search the Knowledge Base...",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", ...},
                "collection": {"type": "string", ...}
            },
            "required": ["query"]
        }
    },
    # ... more functions
]
```

The LLM learns these definitions and decides when each makes sense.

### 2. Function Execution

File: `src/function_calling.py` - `FunctionExecutor` class

Handles the actual execution:
```python
def execute_function(function_name, arguments):
    if function_name == "search_knowledge_base":
        return self._search_knowledge_base(**arguments)
    elif function_name == "extract_code_snippet":
        return self._extract_code_snippet(**arguments)
    # ... etc
```

### 3. Chat Integration

File: `src/app.py` - `handle_function_calls()` function

Main flow:
1. Create messages with function definitions
2. Call OpenAI API with `functions=` parameter
3. Check response for `function_call` attribute
4. Execute function if LLM requested it
5. Call OpenAI again with function results
6. Return final natural language response

### 4. Data Storage

Extracted data is stored as JSON:
- **Code Snippets**: `function_calling/code_snippets.json`
- **Summaries**: `function_calling/summaries.json`

Persistent across sessions - your extracted knowledge is saved!

## Testing Function Calling

### Test 1: KB Query (Easiest Start)

```bash
python src/app.py

# Load your profile with 6502 knowledge (profile 1 or 2)
Enter your prompt (or command): 1

# Then prompt that triggers KB search:
Enter your prompt (or command): Tell me about 6502 instruction set
```

**Expected behavior**:
```
[FC] Checking if function calling is needed...
[FC] LLM requested function: search_knowledge_base
[FC] Function result: Found 3 KB documents matching '6502 instruction set':
1. **6502 Microprocessor Guide**
   Relevance: 45.5%
   Preview: xed: Indirect addressing with Y indexing...
   
[FC] Getting natural language response from LLM...

Here's what I found in our knowledge base about the 6502 instruction set...
```

### Test 2: Code Extraction

```bash
Enter your prompt (or command): Create a summary of the 6502 instruction set with key points
```

**Expected behavior**:
```
[FC] LLM requested function: create_summary
[FC] Function result: [+] Summary created: '6502 Instruction Set'
Key Points: 8
Summary ID: summary_0_1734697200

Then view the summaries:
Enter your prompt (or command): fc-summaries
```

### Test 3: Manual KB Search

```bash
# Users can still manually search:
Enter your prompt (or command): kb-search
Enter search query: addressing modes
```

### Test 4: View Extracted Data

```bash
Enter your prompt (or command): fc-snippets
# Shows all extracted code snippets

Enter your prompt (or command): fc-summaries
# Shows all extracted summaries
```

## Key Learning Concepts

### 1. Function Definitions Are Important
The quality of function descriptions determines when the LLM calls them. Better descriptions = better decisions.

### 2. The LLM Decides
The `function_call="auto"` setting lets the LLM decide:
- **When** to call functions
- **Which** function to use
- **What** arguments to pass

You as the developer don't force this - the LLM figures it out from context!

### 3. Error Handling
Functions should gracefully handle errors:
```python
try:
    # Function logic
except Exception as e:
    return f"Error: {str(e)}"
```

### 4. Function Arguments Are Parsed
The LLM returns arguments as a JSON string:
```python
function_args = json.loads(response_message.function_call.arguments)
# Now you have a Python dict
```

### 5. Round-Trip Processing
The pattern is:
1. Call LLM with functions + user message
2. Execute function with LLM's arguments
3. Call LLM again with function results
4. Get final natural language response

This ensures natural, conversational responses!

## Extending Function Calling

### Adding a New Function

1. **Define it** in `FunctionDefinitions`:
```python
@staticmethod
def my_new_function() -> Dict[str, Any]:
    return {
        "name": "my_new_function",
        "description": "What this function does",
        "parameters": { ... }
    }
```

2. **Add to get_all_functions()**:
```python
def get_all_functions() -> List[Dict[str, Any]]:
    return [
        # ... existing functions
        FunctionDefinitions.my_new_function(),  # Add here
    ]
```

3. **Implement it** in `FunctionExecutor`:
```python
def _my_new_function(self, arg1: str, arg2: int) -> str:
    # Do the work
    return "Result"
```

4. **Add to execute_function()**:
```python
elif function_name == "my_new_function":
    return self._my_new_function(**arguments)
```

5. **Add commands** in `app.py` if user-facing:
```python
if user_input.lower() == 'my-command':
    # Display results
```

### Example: Add Email Function

```python
@staticmethod
def send_email() -> Dict[str, Any]:
    return {
        "name": "send_email",
        "description": "Send an email based on user request",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Email recipient"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body"}
            },
            "required": ["to", "subject", "body"]
        }
    }

def _send_email(self, to: str, subject: str, body: str) -> str:
    # Use your email library
    # send_email_impl(to, subject, body)
    return f"[+] Email sent to {to}"
```

Then users can say: "Send an email to my instructor about needing help"

## Common Issues & Debugging

### Issue 1: Function Never Called
**Cause**: LLM doesn't recognize function as useful
**Solution**: Improve function description to be more specific

### Issue 2: Wrong Arguments Passed
**Cause**: Ambiguous parameter descriptions
**Solution**: Add more detail to parameter `description`

### Issue 3: "function_call" attribute missing
**Cause**: LLM decided not to call any function (normal!)
**Solution**: This is expected - code handles it with `function_was_called` check

### Issue 4: JSON parse error
**Cause**: Function arguments not valid JSON
**Solution**: Wrap in try-except, add debug logging

### Debugging Tips

Enable debug output by checking the logs:
```
[FC] Checking if function calling is needed...
[FC] LLM requested function: function_name
[FC] Arguments: { arguments as JSON }
[FC] Function result: result preview...
```

Look for these signs:
- ✅ No function called = normal, LLM handled directly
- ✅ Function called with correct args = working perfectly
- ❌ Function called with wrong args = adjust descriptions
- ❌ Errors in execution = fix function implementation

## Files Reference

- **`src/function_calling.py`** (390 lines)
  - `FunctionDefinitions`: Static method definitions
  - `FunctionExecutor`: Runtime execution engine

- **`src/app.py`** (modified)
  - `handle_function_calls()`: Main orchestration
  - `generate_text_streaming()`: Integration point
  - New commands: `fc-snippets`, `fc-summaries`

- **`function_calling/`** (auto-created)
  - `code_snippets.json`: Extracted snippets
  - `summaries.json`: Extracted summaries

## Next Steps

1. **Test thoroughly**: Run through Test 1-4 above
2. **Experiment**: Trigger functions with different prompts
3. **Extend**: Add your own functions based on your needs
4. **Refine**: Improve function descriptions based on LLM behavior

## Questions to Ask Yourself

- When should a user prompt trigger function calling?
- What information needs to be extracted automatically?
- What structured data would be useful to store?
- How can functions improve your application's capabilities?

The beauty of function calling is that the LLM intelligently decides - you just need to define what's available! 🎯

