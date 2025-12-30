#!/usr/bin/env python3
"""Quick test of list_collections() fix"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kb_manager import KnowledgeBase

print("Testing list_collections() fix...")
kb = KnowledgeBase(use_cosmos_db=True)
collections = kb.list_collections()
print(f"[OK] list_collections() works!")
print(f"Found {len(collections)} collections:")
for c in collections:
    print(f"  - {c['name']}")

if len(collections) > 0:
    print("[OK] Regression fixed!")
    sys.exit(0)
else:
    print("[*] No collections (expected on fresh install)")
    sys.exit(0)

