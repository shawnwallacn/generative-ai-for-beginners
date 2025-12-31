# Phase B: Multi-Step Planning - Strategy & Implementation Guide

## Overview

**Phase B** implements multi-step task planning and execution, allowing the LLM agent to:
1. Plan complex multi-step workflows
2. Execute steps sequentially
3. Pass results between steps
4. Handle dependencies intelligently

This aligns with **Lesson 17 (AI Agents)** concepts like AutoGen's multi-agent coordination.

**Goal:** Enable the agent to handle complex queries that require multiple function calls in a coordinated sequence.

---

## What We're Building

### Example Workflow

**User Query:** "Summarize all 6502 documents and extract Python code examples"

**Current Behavior (Phase A):**
- LLM calls one function: `search_enterprise_kb`
- Returns results
- User asks follow-up for code extraction

**Phase B Behavior:**
```
User Query: "Summarize all 6502 documents and extract Python code"
  ↓
LLM Plans:
  Step 1: search_enterprise_kb("6502 documents")
  Step 2: extract_code_snippet(results from step 1)
  Step 3: create_summary(all results)
  ↓
Agent Executes All Steps:
  Step 1 → Results: Found 5 documents
  Step 2 → Results: Extracted 3 code snippets
  Step 3 → Results: Created comprehensive summary
  ↓
Final Response: Complete analysis with summary + code examples
```

---

## Architecture

### Current Function Calling Flow

```
User Input
    ↓
LLM Processes
    ↓
LLM Decides: Should I call a function?
    ↓
YES → Call Single Function
    ↓
Execute & Return Result
    ↓
Done
```

### Phase B: Multi-Step Planning Flow

```
User Input
    ↓
LLM Processes
    ↓
LLM Decides: Do I need multiple steps?
    ↓
YES → Create Plan:
      [
        {step: 1, function: "search_enterprise_kb", args: {...}, depends_on: []},
        {step: 2, function: "extract_code_snippet", args: {...}, depends_on: [1]},
        {step: 3, function: "create_summary", args: {...}, depends_on: [1, 2]}
      ]
    ↓
Agent Executor: Execute Plan
    For each step:
      - Wait for dependencies
      - Execute function
      - Store result
      - Pass to dependent steps
    ↓
Merge & Return All Results
    ↓
Done
```

---

## Implementation Components

### 1. Plan Parser (NEW)
**File:** `src/function_calling.py` (new class)

```python
class AgentPlanner:
    def parse_plan_from_llm(self, llm_response: str) -> List[Dict]:
        """
        Extract plan from LLM response.
        LLM returns something like:
        "I'll help you. First, I'll search for documents, then extract code, then summarize.
        
        PLAN:
        Step 1: search_enterprise_kb with query='6502 documents'
        Step 2: extract_code_snippet using results from step 1
        Step 3: create_summary using all results
        "
        
        Returns: [
          {
            'step': 1,
            'function': 'search_enterprise_kb',
            'args': {'query': '6502 documents'},
            'depends_on': []
          },
          ...
        ]
        """
        pass
    
    def validate_plan(self, plan: List[Dict]) -> bool:
        """Check if plan is valid (functions exist, dependencies valid)"""
        pass
```

### 2. Plan Executor (NEW)
**File:** `src/function_calling.py` (new class)

```python
class PlanExecutor:
    def __init__(self, executor: FunctionExecutor):
        self.executor = executor
        self.results = {}  # {step_num: result}
    
    def execute_plan(self, plan: List[Dict]) -> Dict:
        """
        Execute multi-step plan with result chaining.
        
        Returns: {
          'success': True,
          'steps': [
            {'step': 1, 'function': 'search_enterprise_kb', 'result': '...'},
            {'step': 2, 'function': 'extract_code_snippet', 'result': '...'},
            ...
          ],
          'final_response': 'Combined results and summary'
        }
        """
        pass
    
    def _execute_step(self, step: Dict, results: Dict) -> str:
        """Execute single step, potentially using results from previous steps"""
        pass
    
    def _inject_previous_results(self, args: Dict, results: Dict, 
                                 depends_on: List[int]) -> Dict:
        """Add previous step results to current step arguments"""
        pass
```

### 3. LLM System Prompt Update (NEW)
**File:** `src/app.py`

```python
MULTI_STEP_SYSTEM_PROMPT = """
You are an intelligent agent with access to multiple tools.

For complex queries that need multiple steps:
1. Analyze what needs to be done
2. Break it into logical steps
3. Return a plan before executing

PLAN FORMAT (when you need multiple steps):
PLAN:
Step 1: function_name with arg1='value1', arg2='value2'
Step 2: another_function using results from step 1
Step 3: final_function combining all results

Available functions:
- search_local_kb(query, top_k=5)
- search_enterprise_kb(query, top_k=5)
- extract_code_snippet(language, title, code, description='')
- create_summary(topic, key_points, explanation='')
- get_kb_document(document_id)
- get_kb_stats(collection='')

For single-step queries, execute the function directly.
For multi-step queries, return the PLAN: section, then I'll execute it.
"""
```

### 4. Integration in Main App (UPDATE)
**File:** `src/app.py` - chat function

```python
def chat_with_rag(prompt: str, ...):
    """Enhanced chat with multi-step planning support"""
    
    # ... existing code ...
    
    # Check if LLM response includes a PLAN
    if "PLAN:" in fc_response:
        # Parse plan
        plan = planner.parse_plan_from_llm(fc_response)
        
        # Validate plan
        if not planner.validate_plan(plan):
            return "Plan validation failed"
        
        # Execute plan
        result = executor.execute_plan(plan)
        
        # Get natural language response
        plan_results = result['steps']
        response = llm.get_response_for_plan_results(plan_results)
        return response
    else:
        # Single-step execution (Phase A behavior)
        return execute_single_function(fc_response)
```

---

## Implementation Phases

### Phase B.1: Plan Parser & Executor
- [ ] Create `AgentPlanner` class
- [ ] Create `PlanExecutor` class
- [ ] Implement plan parsing from LLM response
- [ ] Implement plan validation
- [ ] Implement result passing between steps
- [ ] Test with simple 2-step plans

### Phase B.2: System Prompt & LLM Integration
- [ ] Update system prompt for multi-step planning
- [ ] Update chat function to detect and route plans
- [ ] Integrate plan parser/executor
- [ ] Test with various query types
- [ ] Handle error cases (invalid plans, execution failures)

### Phase B.3: Testing & Refinement
- [ ] Create comprehensive test suite
- [ ] Test 2-step, 3-step workflows
- [ ] Test dependency handling
- [ ] Test error recovery
- [ ] Performance optimization

### Phase B.4: Documentation
- [ ] Document multi-step workflow
- [ ] Add examples
- [ ] Update README
- [ ] Create quick reference guide

---

## Design Decisions

### 1. Plan Format: Simple Text-Based
**Why:** Easy for LLM to generate, easy to parse, human-readable

```
PLAN:
Step 1: search_enterprise_kb with query='6502 assembly'
Step 2: extract_code_snippet from results
Step 3: create_summary of findings
```

**Alternative (JSON):** More structured but harder for LLM to consistently generate

### 2. Result Passing: Via Dictionary
**Why:** Simple, scalable, supports complex data

```python
results = {
    1: search_result_object,
    2: extracted_code_list,
    3: summary_dict
}
```

### 3. Dependency Handling: Explicit Depends_On
**Why:** Clear execution order, error handling

```python
{
    'step': 2,
    'function': 'extract_code_snippet',
    'depends_on': [1],  # Wait for step 1
    'args': {}
}
```

### 4. Error Handling: Fail-Fast or Continue?
**Decision:** Fail on first error, report clearly

```python
if step_execution_fails:
    return {
        'success': False,
        'failed_at_step': 2,
        'error': 'Function X failed with...',
        'partial_results': {...}
    }
```

---

## Key Challenges & Solutions

### Challenge 1: LLM Plan Format Consistency
**Problem:** LLM might generate different plan formats

**Solution:** 
1. Clear prompt with examples
2. Plan parser with fuzzy matching
3. Validation step to catch errors early
4. Fallback to single-step execution

### Challenge 2: Result Context Growing Too Large
**Problem:** After step 1, context gets huge. Step 3 needs summary of step 1, not full results

**Solution:**
1. Summarize results before passing
2. Limit result size (first 500 chars)
3. Store full results separately, pass key points

### Challenge 3: Handling Function Failures
**Problem:** Step 2 depends on Step 1, but Step 1 fails

**Solution:**
1. Report error clearly
2. Return partial results
3. Allow LLM to decide next action
4. Don't cascade failures

### Challenge 4: LLM Overcomplicating Plans
**Problem:** LLM creates unnecessary 5-step plans for simple queries

**Solution:**
1. Prompt guidance: "Use multiple steps only when necessary"
2. Examples showing when NOT to plan
3. Reward simple solutions in system prompt

---

## Testing Strategy

### Test Cases

**Test 1: Simple 2-Step Plan**
```
Query: "Search for microprocessors and summarize findings"
Expected: 
  Step 1: search_enterprise_kb
  Step 2: create_summary
```

**Test 2: 3-Step Plan with Dependencies**
```
Query: "Find 6502 docs, extract code, create summary"
Expected:
  Step 1: search_enterprise_kb
  Step 2: extract_code_snippet (depends on 1)
  Step 3: create_summary (depends on 1, 2)
```

**Test 3: Single Step (No Planning)**
```
Query: "What's in the 6502 collection?"
Expected:
  Step 1: get_kb_stats
  (No PLAN: section)
```

**Test 4: Error Handling**
```
Query: "Search for X and extract from invalid doc"
Expected:
  Step 1: search_enterprise_kb → Success
  Step 2: extract_code_snippet → Error
  Response: Partial results + error message
```

### Test File
`tests/integration/test_phase_b_multi_step.py`

---

## Timeline & Dependencies

### Prerequisites
- ✅ Phase A complete (search functions available)
- ✅ Function executor working
- ✅ System prompt guidance in place

### Implementation Order
1. Create `AgentPlanner` class (1-2 hours)
2. Create `PlanExecutor` class (2-3 hours)
3. Integrate into main app (1-2 hours)
4. Update system prompt (30 min)
5. Comprehensive testing (2-3 hours)
6. Documentation (1-2 hours)

**Total Estimated:** 8-13 hours

### Parallel vs Sequential
- Planner & Executor can be built in parallel
- Both depend on existing function infrastructure
- Integration and testing sequential

---

## Success Criteria

✅ **Phase B is complete when:**

1. Multi-step plans are parsed correctly
2. Results pass between steps
3. Complex queries execute successfully
4. Error handling works
5. All tests pass
6. Documentation complete
7. Performance acceptable (<5s for 3-step workflows)

---

## Next Steps

1. Start with **Phase B.1: Parser & Executor**
2. Implement `AgentPlanner.parse_plan_from_llm()`
3. Implement `PlanExecutor.execute_plan()`
4. Move to integration and testing

---

## Alignment with Lesson 17

### AI Agents Concepts Demonstrated

✅ **State Management:** Tracking results across steps
✅ **Tool Access:** Using multiple functions in sequence
✅ **Planning:** LLM creates multi-step plans
✅ **Orchestration:** Coordinating complex workflows
✅ **Similar to AutoGen:** Multi-agent coordination (steps as mini-agents)

This implementation teaches enterprise AI agent patterns through practical application!

---

**Ready to implement Phase B? Let's build intelligent, multi-step agent workflows!** 🚀


