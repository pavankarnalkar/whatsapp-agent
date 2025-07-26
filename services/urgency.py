"""Urgency detection logic for WhatsApp messages."""

import re
from typing import List, Dict, Any
from config import settings


class UrgencyDetector:
    """Detects urgency in WhatsApp messages using keywords and patterns."""
    
    def __init__(self):
        self.urgency_keywords = {
            'critical': 1.0,
            'emergency': 1.0,
            'urgent': 0.9,
            'asap': 0.8,
            'immediately': 0.8,
            'help': 0.7,
            'problem': 0.6,
            'issue': 0.5,
            'quick': 0.4,
            'soon': 0.3,
        }
        
        self.urgency_patterns = [
            (r'\b(right now|immediately|asap)\b', 0.9),
            (r'\b(urgent|emergency)\b', 0.9),
            (r'\b(help.*me|need.*help)\b', 0.8),
            (r'\b(broken|not working|error)\b', 0.7),
            (r'!{2,}', 0.6),  # Multiple exclamation marks
            (r'\b(please.*urgent|urgent.*please)\b', 0.8),
        ]
    
    def calculate_urgency_score(self, message: str) -> float:
        """Calculate urgency score based on keywords and patterns."""
        if not message:
            return 0.0
        
        message_lower = message.lower()
        max_score = 0.0
        
        # Check keywords
        for keyword, score in self.urgency_keywords.items():
            if keyword in message_lower:
                max_score = max(max_score, score)
        
        # Check patterns
        for pattern, score in self.urgency_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                max_score = max(max_score, score)
        
        # Check for time-sensitive language
        time_patterns = [
            r'\b(today|tonight|now)\b',
            r'\b(deadline|due)\b',
            r'\b(expires?|expir(ed|ing))\b',
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                max_score = max(max_score, 0.6)
        
        return min(max_score, 1.0)
    
    def should_notify(self, urgency_score: float, threshold: float = 0.7) -> bool:
        """Determine if a message should trigger immediate notification."""
        return urgency_score >= threshold
    
    def get_urgency_level(self, urgency_score: float) -> str:
        """Get human-readable urgency level."""
        if urgency_score >= 0.9:
            return "Critical"
        elif urgency_score >= 0.7:
            return "High"
        elif urgency_score >= 0.5:
            return "Medium"
        elif urgency_score >= 0.3:
            return "Low"
        else:
            return "Normal"


# Global urgency detector instance
urgency_detector = UrgencyDetector()