"""
Audit Trail & Logging Module

Provides comprehensive logging of all security-related events for compliance,
debugging, and threat analysis. All events are timestamped and stored locally.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class AuditLogger:
    """Logs all security events to audit trail"""
    
    # Event types
    EVENT_TYPES = {
        'PROMPT_INJECTION_DETECTED': 'security.injection.detected',
        'PROMPT_INJECTION_BLOCKED': 'security.injection.blocked',
        'PROMPT_INJECTION_WARNED': 'security.injection.warned',
        'SENSITIVE_DATA_DETECTED': 'security.data.detected',
        'SENSITIVE_DATA_TYPES': 'security.data.types',
        'RATE_LIMIT_WARNING': 'security.ratelimit.warning',
        'RATE_LIMIT_EXCEEDED': 'security.ratelimit.exceeded',
        'FILE_VALIDATION_FAILED': 'security.file.failed',
        'FILE_VALIDATION_WARNING': 'security.file.warning',
        'KB_DOCUMENT_ADDED': 'kb.document.added',
        'KB_DOCUMENT_INDEXED': 'kb.document.indexed',
        'PROFILE_CHANGED': 'user.profile.changed',
        'SYSTEM_PROMPT_CHANGED': 'user.system_prompt.changed',
        'PRIVACY_SETTING_CHANGED': 'user.privacy.changed',
        'MODEL_CHANGED': 'user.model.changed',
        'CONVERSATION_SAVED': 'conversation.saved',
        'CONVERSATION_CLEARED': 'conversation.cleared',
        'CONVERSATION_LOADED': 'conversation.loaded',
    }
    
    # Event severity levels
    SEVERITY_LEVELS = {
        'INFO': 'info',          # Informational
        'WARNING': 'warning',    # Potential issue
        'CRITICAL': 'critical',  # Security threat
        'ERROR': 'error',        # System error
    }
    
    def __init__(self, audit_dir: str = "audit_logs"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        
        # Create separate log files
        self.security_log = self.audit_dir / "security_events.jsonl"
        self.user_log = self.audit_dir / "user_actions.jsonl"
        self.summary_file = self.audit_dir / "audit_summary.json"
        
        # Load or initialize summary
        self.summary = self._load_summary()
    
    def _load_summary(self) -> Dict[str, Any]:
        """Load audit summary statistics"""
        if self.summary_file.exists():
            with open(self.summary_file, 'r') as f:
                return json.load(f)
        
        return {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'first_event': None,
            'last_event': None,
            'critical_count': 0,
        }
    
    def _save_summary(self):
        """Save audit summary statistics"""
        with open(self.summary_file, 'w') as f:
            json.dump(self.summary, f, indent=2)
    
    def log_event(
        self, 
        event_type: str, 
        severity: str = 'INFO',
        description: str = "",
        details: Optional[Dict[str, Any]] = None,
        user_input: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log a security or user event
        
        Args:
            event_type: Type of event (from EVENT_TYPES)
            severity: Severity level (INFO, WARNING, CRITICAL, ERROR)
            description: Human-readable description
            details: Additional event details
            user_input: Truncated user input (for context)
        
        Returns:
            The logged event dictionary
        """
        timestamp = datetime.now().isoformat()
        
        event = {
            'timestamp': timestamp,
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'details': details or {},
        }
        
        # Add user input preview (truncated for privacy)
        if user_input:
            event['user_input_preview'] = user_input[:100] + "..." if len(user_input) > 100 else user_input
        
        # Determine which log file to write to
        if 'security' in event_type.lower() or 'data' in event_type.lower() or 'ratelimit' in event_type.lower() or 'file' in event_type.lower():
            log_file = self.security_log
        else:
            log_file = self.user_log
        
        # Write event (JSONL format - one JSON per line)
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Update summary
        self.summary['total_events'] += 1
        self.summary['events_by_type'][event_type] = self.summary['events_by_type'].get(event_type, 0) + 1
        self.summary['events_by_severity'][severity] = self.summary['events_by_severity'].get(severity, 0) + 1
        
        if severity == 'CRITICAL':
            self.summary['critical_count'] += 1
        
        if not self.summary['first_event']:
            self.summary['first_event'] = timestamp
        self.summary['last_event'] = timestamp
        
        self._save_summary()
        
        return event
    
    def log_prompt_injection(self, prompt: str, risk_level: str, patterns: List[str]):
        """Log a prompt injection detection"""
        action = 'BLOCKED' if risk_level == 'DANGER' else 'WARNED'
        severity = 'CRITICAL' if risk_level == 'DANGER' else 'WARNING'
        
        self.log_event(
            event_type=f'PROMPT_INJECTION_{action}',
            severity=severity,
            description=f"Prompt injection attempt detected ({risk_level} level)",
            details={
                'risk_level': risk_level,
                'patterns_detected': patterns,
                'pattern_count': len(patterns),
            },
            user_input=prompt,
        )
    
    def log_sensitive_data_detected(self, response: str, data_types: Dict[str, List[str]]):
        """Log sensitive data detection in response"""
        self.log_event(
            event_type='SENSITIVE_DATA_DETECTED',
            severity='WARNING',
            description=f"Sensitive data detected in LLM response ({len(data_types)} types)",
            details={
                'data_types': list(data_types.keys()),
                'type_count': len(data_types),
                'total_matches': sum(len(v) for v in data_types.values()),
            },
            user_input=response[:50],
        )
    
    def log_rate_limit_event(self, status: str, metrics: Dict[str, int]):
        """Log rate limit warning or exceeded"""
        if status == 'exceeded':
            event_type = 'RATE_LIMIT_EXCEEDED'
            severity = 'CRITICAL'
            description = "Rate limit exceeded - request blocked"
        else:
            event_type = 'RATE_LIMIT_WARNING'
            severity = 'WARNING'
            description = "Approaching rate limit threshold"
        
        self.log_event(
            event_type=event_type,
            severity=severity,
            description=description,
            details=metrics,
        )
    
    def log_file_validation_error(self, filename: str, errors: List[str]):
        """Log file validation failure"""
        self.log_event(
            event_type='FILE_VALIDATION_FAILED',
            severity='WARNING',
            description=f"File validation failed: {filename}",
            details={
                'filename': filename,
                'error_count': len(errors),
                'errors': errors[:5],  # Keep first 5 errors
            },
        )
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user actions (profile changes, settings, etc.)"""
        self.log_event(
            event_type=action,
            severity='INFO',
            description=f"User action: {action}",
            details=details or {},
        )
    
    def get_events(
        self, 
        event_type: Optional[str] = None, 
        severity: Optional[str] = None,
        limit: int = 100,
        days_back: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events from audit trail with optional filtering
        
        Args:
            event_type: Filter by specific event type
            severity: Filter by severity level
            limit: Maximum number of events to return
            days_back: Only return events from last N days
        
        Returns:
            List of matching events
        """
        events = []
        cutoff_date = datetime.now().timestamp() - (days_back * 24 * 3600)
        
        # Read from both log files
        for log_file in [self.security_log, self.user_log]:
            if not log_file.exists():
                continue
            
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        
                        # Check time filter
                        event_ts = datetime.fromisoformat(event['timestamp']).timestamp()
                        if event_ts < cutoff_date:
                            continue
                        
                        # Apply filters
                        if event_type and event['event_type'] != event_type:
                            continue
                        if severity and event['severity'] != severity:
                            continue
                        
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        return events[:limit]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get audit trail summary statistics"""
        return self.summary.copy()
    
    def get_security_incidents(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get critical security incidents from the last N hours"""
        cutoff_date = datetime.now().timestamp() - (hours * 3600)
        incidents = []
        
        for log_file in [self.security_log, self.user_log]:
            if not log_file.exists():
                continue
            
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_ts = datetime.fromisoformat(event['timestamp']).timestamp()
                        
                        if event_ts < cutoff_date:
                            continue
                        if event['severity'] == 'CRITICAL':
                            incidents.append(event)
                    except json.JSONDecodeError:
                        continue
        
        incidents.sort(key=lambda x: x['timestamp'], reverse=True)
        return incidents
    
    def export_audit_report(self, output_file: str = "audit_report.json"):
        """Export complete audit trail to a file"""
        all_events = self.get_events(limit=10000)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'critical_incidents': self.get_security_incidents(hours=24*30),
            'all_events': all_events,
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_file


def display_audit_summary(audit_logger: AuditLogger):
    """Display audit trail summary to user"""
    summary = audit_logger.get_summary()
    
    print("\n" + "=" * 70)
    print("AUDIT TRAIL SUMMARY")
    print("=" * 70)
    print(f"\nTotal Events Logged: {summary['total_events']}")
    print(f"Critical Incidents: {summary['critical_count']}")
    print(f"First Event: {summary['first_event'] or 'None'}")
    print(f"Last Event: {summary['last_event'] or 'None'}")
    
    print("\nEvents by Severity:")
    for severity, count in sorted(summary['events_by_severity'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {severity:<12} : {count:>4} events")
    
    print("\nTop Event Types:")
    sorted_types = sorted(summary['events_by_type'].items(), key=lambda x: x[1], reverse=True)[:10]
    for event_type, count in sorted_types:
        print(f"  {event_type:<40} : {count:>4} events")
    
    print("\n" + "=" * 70 + "\n")


def display_recent_events(audit_logger: AuditLogger, limit: int = 20):
    """Display recent audit events"""
    events = audit_logger.get_events(limit=limit)
    
    if not events:
        print("\n[No audit events found]\n")
        return
    
    print("\n" + "=" * 120)
    print("RECENT AUDIT EVENTS (Latest 20)")
    print("=" * 120)
    
    for i, event in enumerate(events, 1):
        timestamp = event['timestamp'].split('T')[1][:8]  # HH:MM:SS
        severity = event['severity']
        event_type = event['event_type']
        description = event['description'][:60]
        
        print(f"\n{i}. [{timestamp}] [{severity:<8}] {event_type}")
        print(f"   {description}")
        
        if event.get('user_input_preview'):
            print(f"   Input: {event['user_input_preview']}")
        
        if event.get('details'):
            details_str = str(event['details'])[:100]
            print(f"   Details: {details_str}")
    
    print("\n" + "=" * 120 + "\n")


def display_security_incidents(audit_logger: AuditLogger, hours: int = 24):
    """Display critical security incidents"""
    incidents = audit_logger.get_security_incidents(hours=hours)
    
    print("\n" + "=" * 70)
    print(f"SECURITY INCIDENTS (Last {hours} hours)")
    print("=" * 70)
    
    if not incidents:
        print(f"\n[No critical incidents in the last {hours} hours]\n")
        return
    
    print(f"\nTotal Incidents: {len(incidents)}\n")
    
    for i, incident in enumerate(incidents, 1):
        timestamp = incident['timestamp']
        event_type = incident['event_type']
        description = incident['description']
        
        print(f"{i}. [{timestamp}] {event_type}")
        print(f"   {description}")
        
        if incident.get('details'):
            for key, value in incident['details'].items():
                if isinstance(value, (str, int, float, bool)):
                    print(f"   - {key}: {value}")
        print()
    
    print("=" * 70 + "\n")

