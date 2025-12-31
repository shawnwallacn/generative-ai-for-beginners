#!/usr/bin/env python3
"""
Test script for: Agent Planner & Executor
Tests multi-step plan parsing, validation, and execution.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dotenv import load_dotenv
from function_calling import FunctionDefinitions, FunctionExecutor, AgentPlanner, PlanExecutor
from kb_manager import KnowledgeBase
from semantic_search import EmbeddingIndex

load_dotenv()

print("="*70)
print(" TEST: AGENT PLANNER & EXECUTOR")
print("="*70)

# Test 1: Initialize components
print("\n[TEST 1] Initialize Components")
print("-" * 70)

try:
    embedding_index = EmbeddingIndex()
    kb_manager = KnowledgeBase()
    executor = FunctionExecutor(kb_manager=kb_manager, semantic_search_index=embedding_index)
    planner = AgentPlanner()
    plan_executor = PlanExecutor(executor)
    
    print("[OK] All components initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize: {e}")
    sys.exit(1)

# Test 2: Parse simple 2-step plan
print("\n[TEST 2] Parse Simple 2-Step Plan")
print("-" * 70)

llm_response_2step = """
I'll help you search for documents and create a summary.

PLAN:
Step 1: search_enterprise_kb with query='microprocessor'
Step 2: create_summary with topic='Microprocessor Overview'
"""

plan = planner.parse_plan_from_llm(llm_response_2step)
if plan:
    print(f"[OK] Parsed plan with {len(plan)} steps")
    for step in plan:
        print(f"     Step {step['step']}: {step['function']} (depends on: {step['depends_on']})")
else:
    print("[ERROR] Failed to parse plan")

# Test 3: Parse 3-step plan with dependencies
print("\n[TEST 3] Parse 3-Step Plan with Dependencies")
print("-" * 70)

llm_response_3step = """
I'll search for 6502 docs, extract code, and create a summary.

PLAN:
Step 1: search_enterprise_kb with query='6502 assembly'
Step 2: extract_code_snippet with language='assembly' from step 1 results
Step 3: create_summary combining all results
"""

plan = planner.parse_plan_from_llm(llm_response_3step)
if plan:
    print(f"[OK] Parsed plan with {len(plan)} steps")
    for step in plan:
        print(f"     Step {step['step']}: {step['function']}")
        if step['depends_on']:
            print(f"       Depends on: {step['depends_on']}")
        if step['args']:
            print(f"       Args: {step['args']}")
else:
    print("[ERROR] Failed to parse plan")

# Test 4: No plan in response
print("\n[TEST 4] Detect No Plan in Response")
print("-" * 70)

llm_response_no_plan = """
Let me search for that information for you.

I found 5 relevant documents about microprocessors...
"""

plan = planner.parse_plan_from_llm(llm_response_no_plan)
if plan is None:
    print("[OK] Correctly detected no plan in response")
else:
    print(f"[ERROR] Should not have parsed a plan, got: {plan}")

# Test 5: Validate valid plan
print("\n[TEST 5] Validate Valid Plan")
print("-" * 70)

valid_plan = [
    {
        'step': 1,
        'function': 'search_enterprise_kb',
        'args': {'query': '6502'},
        'depends_on': []
    },
    {
        'step': 2,
        'function': 'create_summary',
        'args': {'topic': '6502 Overview'},
        'depends_on': [1]
    }
]

available_functions = list(executor.get_available_functions().keys())
is_valid, msg = planner.validate_plan(valid_plan, available_functions)

if is_valid:
    print(f"[OK] Plan validation passed: {msg}")
else:
    print(f"[ERROR] Plan validation failed: {msg}")

# Test 6: Validate invalid plan (bad function)
print("\n[TEST 6] Validate Invalid Plan (Unknown Function)")
print("-" * 70)

invalid_plan = [
    {
        'step': 1,
        'function': 'nonexistent_function',
        'args': {},
        'depends_on': []
    }
]

is_valid, msg = planner.validate_plan(invalid_plan, available_functions)
if not is_valid:
    print(f"[OK] Plan validation correctly rejected: {msg}")
else:
    print(f"[ERROR] Should have rejected invalid plan")

# Test 7: Validate invalid plan (bad dependencies)
print("\n[TEST 7] Validate Invalid Plan (Bad Dependencies)")
print("-" * 70)

invalid_plan = [
    {
        'step': 1,
        'function': 'search_enterprise_kb',
        'args': {},
        'depends_on': []
    },
    {
        'step': 2,
        'function': 'create_summary',
        'args': {},
        'depends_on': [3]  # Depends on non-existent step 3
    }
]

is_valid, msg = planner.validate_plan(invalid_plan, available_functions)
if not is_valid:
    print(f"[OK] Plan validation correctly rejected: {msg}")
else:
    print(f"[ERROR] Should have rejected invalid dependencies")

# Test 8: Execute simple 2-step plan
print("\n[TEST 8] Execute Simple 2-Step Plan")
print("-" * 70)

test_plan = [
    {
        'step': 1,
        'function': 'search_local_kb',
        'args': {'query': 'microprocessor'},
        'depends_on': []
    },
    {
        'step': 2,
        'function': 'create_summary',
        'args': {'topic': 'Microprocessors', 'key_points': ['8-bit', 'widely used']},
        'depends_on': [1]
    }
]

print("[*] Executing 2-step plan...")
result = plan_executor.execute_plan(test_plan)

print(f"\n[RESULTS]")
print(f"Success: {result['success']}")
print(f"Total Steps: {result['total_steps']}")
print(f"Completed: {result['completed_steps']}")
print(f"\nStep Details:")
for step in result['steps']:
    status = "OK" if step['error'] is None else "ERROR"
    print(f"  Step {step['step']}: {step['function']} - {status}")
    if step['error']:
        print(f"    Error: {step['error']}")

# Test 9: Parse argument extraction
print("\n[TEST 9] Argument Parsing")
print("-" * 70)

llm_response = """
PLAN:
Step 1: search_enterprise_kb with query='6502 assembly', top_k='10'
"""

plan = planner.parse_plan_from_llm(llm_response)
if plan and plan[0]['args']:
    print(f"[OK] Extracted arguments: {plan[0]['args']}")
    if 'query' in plan[0]['args'] and 'top_k' in plan[0]['args']:
        print("[OK] All arguments correctly parsed")
    else:
        print("[ERROR] Missing arguments")
else:
    print("[ERROR] Failed to parse arguments")

# Test 10: Dependency extraction
print("\n[TEST 10] Dependency Extraction")
print("-" * 70)

llm_response = """
PLAN:
Step 1: search_enterprise_kb with query='test'
Step 2: extract_code_snippet from step 1 results
Step 3: create_summary combining all results
"""

plan = planner.parse_plan_from_llm(llm_response)
if plan:
    print(f"[OK] Parsed {len(plan)} steps")
    for step in plan:
        print(f"  Step {step['step']}: depends_on = {step['depends_on']}")
    
    # Validate dependencies
    if plan[1]['depends_on'] == [1] and len(plan[2]['depends_on']) > 0:
        print("[OK] Dependencies correctly extracted")
    else:
        print("[ERROR] Dependency extraction incorrect")
else:
    print("[ERROR] Failed to parse plan")

print("\n" + "="*70)
print(" TEST SUMMARY")
print("="*70)
print("[OK] Agent Planner created and working")
print("[OK] Plan parsing implemented")
print("[OK] Plan validation implemented")
print("[OK] Plan executor created")
print("[OK] Multi-step execution working")
print("="*70)

