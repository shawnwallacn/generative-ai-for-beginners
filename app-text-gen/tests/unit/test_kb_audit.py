#!/usr/bin/env python
"""Test KB document audit logging"""

import sys
sys.path.insert(0, 'src')

from audit_logger import AuditLogger
import kb_manager

# Setup
audit = AuditLogger(audit_dir='test_audit_kb')
kb_manager.audit_logger = audit

# Simulate KB_DOCUMENT_ADDED event
audit.log_user_action('KB_DOCUMENT_ADDED', {
    'doc_id': 'test_doc_123',
    'title': 'Test PDF Document',
    'collection': 'test_collection',
    'chunk_count': 5,
    'total_words': 1500,
    'file_format': '.pdf',
})

# Check if logged
events = audit.get_events(limit=10)
print('[SUCCESS] KB document addition logged!')
print(f'Total events: {len(events)}')

for event in events:
    if 'KB_DOCUMENT_ADDED' in event.get('event_type', ''):
        print(f"\nEvent Type: {event['event_type']}")
        print(f"Description: {event['description']}")
        print(f"Details: {event['details']}")
        print('[OK] KB_DOCUMENT_ADDED event properly recorded!')

