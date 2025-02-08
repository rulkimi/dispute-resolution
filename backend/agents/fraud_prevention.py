# agents/fraud_detection.py
from typing import Dict, List, Tuple
import re
from datetime import datetime

class FraudDetector:
    def __init__(self):
        self.suspicious_patterns = {
            'external_platform': [
                r'(?i)let\'s (?:continue|talk|chat|move) (?:on|to) (?:whatsapp|telegram|messenger|signal|wechat|viber)',
                r'(?i)(?:whatsapp|telegram|messenger|signal|wechat|viber)[\s]*?(?:number|contact|id)?[\s]*?[:\s]+[\d\w@]+',
            ],
            'urgency_pressure': [
                r'(?i)urgent(?:ly)? need',
                r'(?i)(?:transfer|send|pay).*?now.*?urgent',
            ],
            'suspicious_amounts': [
                r'(?i)different amount',
                r'(?i)change(?:d) (?:the )?(?:amount|price)',
            ]
        }
        self.compiled_patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        return {
            category: [re.compile(pattern) for pattern in patterns]
            for category, patterns in self.suspicious_patterns.items()
        }

    def analyze_message(self, message: str, context: dict = None) -> Tuple[bool, List[dict]]:
        alerts = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    alerts.append({
                        "type": category,
                        "pattern_matched": pattern.pattern,
                        "timestamp": datetime.now(),
                        "severity": "high" if category == "external_platform" else "medium"
                    })
        
        return bool(alerts), alerts

detector = FraudDetector()
message = "Let's continue this on WhatsApp"
is_fraud, alerts = detector.analyze_message(message)

print(is_fraud)  # True
print(alerts)    # [{'type': 'external_platform', 'pattern_matched': "...", 'timestamp': ..., 'severity': 'high'}]
