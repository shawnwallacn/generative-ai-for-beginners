"""
Security Module - Input/Output Validation and Protection

This module provides security functions for:
- Detecting prompt injection attempts
- Validating user inputs
- Detecting sensitive data in outputs
- Rate limiting protection
- File validation for KB uploads
"""

import re
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Import audit logger (will be initialized in app.py)
audit_logger = None


class PromptInjectionDetector:
    """Detects potential prompt injection attacks"""
    
    # Suspicious patterns that indicate injection attempts
    INJECTION_PATTERNS = [
        r'(?i)ignore.*previous',           # "ignore previous instructions"
        r'(?i)forget.*everything',         # "forget everything"
        r'(?i)disregard.*instructions',    # "disregard instructions"
        r'(?i)pretend.*you.*are',          # "pretend you are"
        r'(?i)system.*prompt',             # Attempts to access system prompt
        r'(?i)backdoor',                   # "backdoor"
        r'(?i)jailbreak',                  # "jailbreak"
        r'(?i)execute.*code',              # "execute code"
        r'(?i)run.*command',               # "run command"
        r'(?i)bypass.*security',           # "bypass security"
        r'(?i)reveal.*api.*key',           # "reveal API key"
        r'(?i)show.*secret',               # "show secret"
        r'(?i)admin.*mode',                # "admin mode"
        r'(?i)unlimited.*access',          # "unlimited access"
        r'(?i)DAN\b',                      # "DAN" (Do Anything Now jailbreak)
        r'(?i)repeat.*back',               # "repeat back" (information extraction)
        r'(?i)output.*raw',                # "output raw"
    ]
    
    # Suspicious character sequences
    SUSPICIOUS_SEQUENCES = [
        '<!--',                            # HTML comments
        '<?',                              # PHP tags
        '${',                              # Template injection
        '{{',                              # Template injection
        '<%',                              # ASP tags
    ]
    
    @staticmethod
    def check_prompt(prompt: str) -> dict:
        """
        Check if a prompt contains injection patterns
        
        Returns:
            {
                'is_suspicious': bool,
                'risk_level': 'safe' | 'warning' | 'danger',
                'detected_patterns': [list of detected patterns],
                'recommendation': str
            }
        """
        if not prompt or len(prompt) < 5:
            return {
                'is_suspicious': False,
                'risk_level': 'safe',
                'detected_patterns': [],
                'recommendation': None
            }
        
        detected = []
        risk_level = 'safe'
        
        # Check for injection patterns
        for pattern in PromptInjectionDetector.INJECTION_PATTERNS:
            if re.search(pattern, prompt):
                detected.append(pattern)
                risk_level = 'warning'
        
        # Check for suspicious sequences
        for seq in PromptInjectionDetector.SUSPICIOUS_SEQUENCES:
            if seq in prompt:
                detected.append(f"Suspicious sequence: {seq}")
                risk_level = 'danger'
        
        # Check for excessive special characters (potential encoding attacks)
        special_char_ratio = sum(1 for c in prompt if not c.isalnum() and c not in ' \n\t.,;:!?-()[]{}"\'/\\')
        if len(prompt) > 50 and special_char_ratio / len(prompt) > 0.3:
            detected.append("High ratio of special characters (possible encoding attack)")
            risk_level = 'warning'
        
        recommendation = None
        if detected:
            if risk_level == 'danger':
                recommendation = "[DANGER] This prompt contains suspicious patterns and may be a security attack. Proceed with caution."
            elif risk_level == 'warning':
                recommendation = "[WARNING] This prompt contains patterns commonly used in injection attacks. Review before sending?"
        
        # Log to audit trail if dangerous or warning
        if audit_logger and detected:
            audit_logger.log_prompt_injection(prompt, risk_level, detected)
        
        return {
            'is_suspicious': bool(detected),
            'risk_level': risk_level,
            'detected_patterns': detected,
            'recommendation': recommendation
        }


class SensitiveDataDetector:
    """Detects sensitive data in outputs"""
    
    # Patterns for detecting sensitive information
    SENSITIVE_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'api_key': r'(?i)(?:api[_-]?key|secret|password|token|access[_-]?key)[:\s]*[\'"]?([A-Za-z0-9_-]{20,})[\'"]?',
        'aws_key': r'(?i)AKIA[0-9A-Z]{16}',
        'private_key': r'-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY',
        'ipv4': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    }
    
    @staticmethod
    def scan_output(text: str) -> dict:
        """
        Scan output for sensitive data patterns
        
        Returns:
            {
                'has_sensitive_data': bool,
                'detected_items': {
                    'type': [list of detected items],
                    ...
                },
                'warning': str or None
            }
        """
        detected_items = {}
        
        for data_type, pattern in SensitiveDataDetector.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_items[data_type] = matches if isinstance(matches[0], str) and not isinstance(matches[0], tuple) else [str(m) for m in matches]
        
        has_sensitive = bool(detected_items)
        warning = None
        
        if has_sensitive:
            types_found = ', '.join(detected_items.keys())
            warning = f"[ALERT] SENSITIVE DATA DETECTED: Found {types_found} in output. Review before sharing!"
            
            # Log to audit trail
            if audit_logger:
                audit_logger.log_sensitive_data_detected(text, detected_items)
        
        return {
            'has_sensitive_data': has_sensitive,
            'detected_items': detected_items,
            'warning': warning
        }
    
    @staticmethod
    def scan_input(text: str) -> dict:
        """
        Scan user INPUT for sensitive data patterns
        
        Returns:
            {
                'has_sensitive_data': bool,
                'detected_items': {
                    'type': [list of detected items],
                    ...
                },
                'warning': str or None
            }
        """
        detected_items = {}
        
        for data_type, pattern in SensitiveDataDetector.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_items[data_type] = matches if isinstance(matches[0], str) and not isinstance(matches[0], tuple) else [str(m) for m in matches]
        
        has_sensitive = bool(detected_items)
        warning = None
        
        if has_sensitive:
            types_found = ', '.join(detected_items.keys())
            warning = f"[WARNING] SENSITIVE DATA IN INPUT: Found {types_found}. Consider using generic placeholders instead."
            
            # Log to audit trail
            if audit_logger:
                audit_logger.log_sensitive_data_detected(text, detected_items)
        
        return {
            'has_sensitive_data': has_sensitive,
            'detected_items': detected_items,
            'warning': warning
        }


class RateLimiter:
    """Rate limiting to prevent abuse and cost attacks"""
    
    LIMITS = {
        'tokens_per_minute': 10000,
        'requests_per_minute': 30,
        'requests_per_hour': 200,
    }
    
    def __init__(self):
        self.stats_file = Path('statistics/rate_limit_stats.json')
        self.stats_file.parent.mkdir(exist_ok=True)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Load rate limit statistics"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {'tokens': [], 'requests': []}
    
    def _save_stats(self):
        """Save rate limit statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, default=str)
    
    def record_request(self, tokens_used: int = 0):
        """Record a request and tokens used"""
        now = datetime.now().isoformat()
        self.stats['requests'].append(now)
        if tokens_used > 0:
            self.stats['tokens'].append({
                'timestamp': now,
                'count': tokens_used
            })
        
        # Keep only recent data (last 24 hours)
        cutoff = datetime.now() - timedelta(days=1)
        self.stats['requests'] = [
            r for r in self.stats['requests']
            if datetime.fromisoformat(r) > cutoff
        ]
        self.stats['tokens'] = [
            t for t in self.stats['tokens']
            if datetime.fromisoformat(t['timestamp']) > cutoff
        ]
        
        self._save_stats()
    
    def check_limits(self) -> dict:
        """
        Check if we're approaching rate limits
        
        Returns:
            {
                'status': 'ok' | 'warning' | 'exceeded',
                'metrics': {
                    'requests_this_minute': int,
                    'tokens_this_minute': int,
                    'requests_this_hour': int,
                },
                'warnings': [list of warnings]
            }
        """
        now = datetime.now()
        one_min_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        
        # Count requests in last minute
        requests_this_minute = sum(
            1 for r in self.stats['requests']
            if datetime.fromisoformat(r) > one_min_ago
        )
        
        # Count tokens in last minute
        tokens_this_minute = sum(
            t['count'] for t in self.stats['tokens']
            if datetime.fromisoformat(t['timestamp']) > one_min_ago
        )
        
        # Count requests in last hour
        requests_this_hour = sum(
            1 for r in self.stats['requests']
            if datetime.fromisoformat(r) > one_hour_ago
        )
        
        warnings = []
        status = 'ok'
        
        # Check limits
        if requests_this_minute > self.LIMITS['requests_per_minute'] * 0.8:
            warnings.append(f"[WARNING] Approaching requests/minute limit: {requests_this_minute}/{self.LIMITS['requests_per_minute']}")
            status = 'warning'
        
        if tokens_this_minute > self.LIMITS['tokens_per_minute'] * 0.8:
            warnings.append(f"[WARNING] Approaching tokens/minute limit: {tokens_this_minute}/{self.LIMITS['tokens_per_minute']}")
            status = 'warning'
        
        if requests_this_hour > self.LIMITS['requests_per_hour'] * 0.8:
            warnings.append(f"[WARNING] Approaching requests/hour limit: {requests_this_hour}/{self.LIMITS['requests_per_hour']}")
            status = 'warning'
        
        if requests_this_minute > self.LIMITS['requests_per_minute']:
            warnings.append(f"[BLOCKED] RATE LIMIT EXCEEDED: Requests/minute ({requests_this_minute})")
            status = 'exceeded'
            
            # Log to audit trail
            if audit_logger:
                audit_logger.log_rate_limit_event('exceeded', {
                    'requests_this_minute': requests_this_minute,
                    'tokens_this_minute': tokens_this_minute,
                    'requests_this_hour': requests_this_hour,
                })
        
        if requests_this_hour > self.LIMITS['requests_per_hour']:
            warnings.append(f"[BLOCKED] RATE LIMIT EXCEEDED: Requests/hour ({requests_this_hour})")
            status = 'exceeded'
            
            # Log to audit trail
            if audit_logger:
                audit_logger.log_rate_limit_event('exceeded', {
                    'requests_this_minute': requests_this_minute,
                    'tokens_this_minute': tokens_this_minute,
                    'requests_this_hour': requests_this_hour,
                })
        
        elif status == 'warning' and audit_logger:
            audit_logger.log_rate_limit_event('warning', {
                'requests_this_minute': requests_this_minute,
                'tokens_this_minute': tokens_this_minute,
                'requests_this_hour': requests_this_hour,
            })
        
        return {
            'status': status,
            'metrics': {
                'requests_this_minute': requests_this_minute,
                'tokens_this_minute': tokens_this_minute,
                'requests_this_hour': requests_this_hour,
            },
            'warnings': warnings
        }


class InputValidator:
    """Validates file uploads and KB documents"""
    
    ALLOWED_FORMATS = {'.txt', '.md', '.markdown', '.pdf'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_CHUNK_SIZE = 1 * 1024 * 1024  # 1MB per chunk
    
    # Suspicious content patterns in uploaded files
    MALICIOUS_PATTERNS = [
        r'(?i)<script',                    # JavaScript
        r'(?i)onclick',                    # Event handlers
        r'(?i)onerror',
        r'(?i)onload',
        r'(?i)eval\(',                     # Code execution
        r'(?i)exec\(',
        r'(?i)system\(',
        r'(?i)__import__',                 # Python imports
        r'(?i)subprocess',
        r'os\.system',
    ]
    
    @staticmethod
    def validate_file(file_path: str) -> dict:
        """
        Validate a file for upload to KB
        
        Returns:
            {
                'is_valid': bool,
                'errors': [list of errors],
                'warnings': [list of warnings],
                'file_info': {
                    'size': int,
                    'format': str,
                    'lines': int
                }
            }
        """
        errors = []
        warnings = []
        
        try:
            path = Path(file_path)
            
            # Check file exists
            if not path.exists():
                errors.append(f"File not found: {file_path}")
                return {
                    'is_valid': False,
                    'errors': errors,
                    'warnings': warnings,
                    'file_info': None
                }
            
            # Check file format
            if path.suffix.lower() not in InputValidator.ALLOWED_FORMATS:
                errors.append(f"Unsupported file format: {path.suffix}. Allowed: {', '.join(InputValidator.ALLOWED_FORMATS)}")
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > InputValidator.MAX_FILE_SIZE:
                errors.append(f"File too large: {file_size / 1024 / 1024:.1f}MB (max: {InputValidator.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)")
            elif file_size > InputValidator.MAX_FILE_SIZE * 0.8:
                warnings.append(f"Large file: {file_size / 1024 / 1024:.1f}MB (may be slow to process)")
            
            # Read and scan content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                
                # Check for malicious patterns
                for pattern in InputValidator.MALICIOUS_PATTERNS:
                    if re.search(pattern, content):
                        warnings.append(f"Suspicious pattern detected: {pattern}")
                
                # Check content size
                if len(content) > InputValidator.MAX_CHUNK_SIZE:
                    warnings.append(f"Large content: {len(content) / 1024 / 1024:.1f}MB (will be chunked)")
                
            except Exception as e:
                errors.append(f"Error reading file: {str(e)}")
            
            file_info = {
                'size': file_size,
                'format': path.suffix.lower(),
                'lines': lines if 'lines' in locals() else 0
            }
            
            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'file_info': file_info
            }
        
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'file_info': None
            }


def display_security_status():
    """Display security status and recommendations"""
    print("\n" + "=" * 60)
    print("Security Status")
    print("=" * 60)
    print("✓ Prompt injection detection: ENABLED")
    print("✓ Sensitive data detection: ENABLED")
    print("✓ Rate limiting: ENABLED")
    print("✓ File validation: ENABLED")
    print("✓ Local-only storage: ENABLED")
    print("✓ Privacy controls: ENABLED")
    print("=" * 60 + "\n")

