#!/usr/bin/env python
"""Test user input sensitive data detection and logging"""

import sys
sys.path.insert(0, 'src')

from security import SensitiveDataDetector
from audit_logger import AuditLogger
import security
import os

# Setup
audit = AuditLogger(audit_dir='test_input_security')
security.audit_logger = audit

# Test scanning user input for sensitive data
detector = SensitiveDataDetector()
result = detector.scan_input('my email is shawn.wall@accenture.com')

print('[Test Result]')
print(f'Has sensitive data: {result["has_sensitive_data"]}')
print(f'Detected types: {list(result["detected_items"].keys())}')
print(f'Warning: {result["warning"]}')

# Check audit log
events = audit.get_events(limit=10)
print(f'\n[Audit Log]')
print(f'Total events: {len(events)}')
if events:
    print(f'Event type: {events[0]["event_type"]}')
    print(f'Severity: {events[0]["severity"]}')

# List files
files = os.listdir('test_input_security')
print(f'\n[Files created]')
for f in sorted(files):
    print(f'  - {f}')
    
# Show security_events content
print(f'\n[security_events.jsonl]')
with open('test_input_security/security_events.jsonl', 'r') as f:
    print(f.read())

