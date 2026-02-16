"""
Groq LLM-Powered Test Case Designer
Uses Groq's fast inference API to generate intelligent test cases
"""

import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GroqTestCaseDesigner:
    """
    Test case designer powered by Groq LLM
    Uses llama-3.3-70b-versatile for fast, intelligent test generation
    """
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_url = 'https://api.groq.com/openai/v1/chat/completions'
        self.model = 'llama-3.3-70b-versatile'  # Fast and powerful
        self.test_case_counter = 1
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set. Using rule-based fallback.")
            self.use_llm = False
        else:
            self.use_llm = True
            logger.info(f"Groq LLM enabled with model: {self.model}")
    
    def generate_test_cases(self, requirements: Dict[str, Any]) -> List[Any]:
        """
        Generate test cases using Groq LLM
        """
        if not self.use_llm:
            logger.warning("Groq API key not set, using basic rule-based generation")
            return self._fallback_generation(requirements)
        
        try:
            # Generate test cases using Groq
            test_cases = self._generate_with_groq(requirements)
            logger.info(f"Generated {len(test_cases)} test cases using Groq LLM")
            return test_cases
            
        except Exception as e:
            logger.error(f"Groq generation failed: {e}. Falling back to rules.")
            return self._fallback_generation(requirements)
    
    def _generate_with_groq(self, requirements: Dict[str, Any]) -> List[Any]:
        """Use Groq LLM to generate intelligent test cases"""
        
        fraud_types = requirements.get('fraud_types', [])
        detection_rules = requirements.get('detection_rules', {})
        
        # Build prompt for Groq
        prompt = self._build_prompt(fraud_types, detection_rules)
        
        # Call Groq API
        llm_response = self._call_groq(prompt)
        
        # Parse and convert to test cases
        test_cases = self._parse_groq_response(llm_response, requirements)
        
        return test_cases
    
    def _build_prompt(self, fraud_types: List[str], detection_rules: Dict[str, Any]) -> str:
        """Build detailed prompt for Groq"""
        
        prompt = f"""You are an expert fraud detection QA engineer. Generate comprehensive test cases for a fraud detection system.

**Fraud Types to Test:**
{json.dumps(fraud_types, indent=2)}

**Detection Rules:**
{json.dumps(detection_rules, indent=2)}

**Requirements:**
1. Generate 8-12 test cases per fraud type
2. Include positive tests (fraud should be detected)
3. Include negative tests (legitimate transactions should pass)
4. Include edge cases (boundary conditions)
5. Include adversarial cases (fraud evasion attempts)
6. Use realistic transaction data

**Output Format (JSON only, no markdown):**
```json
[
  {{
    "test_id": "TC-WIRE-001",
    "fraud_type": "wire_transfer_fraud",
    "category": "High Value Wire Transfer",
    "priority": "P1",
    "description": "Detect large wire transfer from dormant account to high-risk country",
    "test_data": {{
      "amount": 45000,
      "source_account": {{
        "id": "ACC-12345",
        "dormant_days": 180,
        "avg_balance": 8000
      }},
      "destination": {{
        "country": "NG",
        "bank": "Unknown Bank",
        "account_name": "New Beneficiary"
      }},
      "timestamp": "2026-02-15T03:45:00Z",
      "device": {{
        "id": "NEW_DEVICE_001",
        "ip": "203.0.113.45",
        "user_agent": "Unknown"
      }}
    }},
    "expected_result": {{
      "should_detect": true,
      "risk_score_min": 85,
      "risk_score_max": 100,
      "alert_priority": "HIGH",
      "action": "block_and_notify"
    }},
    "fraud_indicators": ["high_value", "dormant_account", "high_risk_destination", "new_device", "unusual_time"],
    "rationale": "Dormant account suddenly active with large international transfer to high-risk country"
  }}
]
```

Generate test cases now. Return ONLY valid JSON, no explanations."""

        return prompt
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a fraud detection QA expert. Generate test cases in JSON format only.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 8000,
            'top_p': 0.9
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            logger.info(f"Groq API call successful. Tokens used: {result.get('usage', {})}")
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            raise
    
    def _parse_groq_response(self, response: str, requirements: Dict[str, Any]) -> List[Any]:
        """Parse Groq JSON response and convert to TestCase objects"""
        from fraud_qa_agent import TestCase
        
        # Clean response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        try:
            test_cases_json = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response as JSON: {e}")
            logger.debug(f"Response was: {response[:500]}...")
            raise
        
        test_cases = []
        
        for case_data in test_cases_json:
            try:
                test_case = TestCase(
                    test_case_id=case_data.get('test_id', f'TC-GROQ-{self.test_case_counter:03d}'),
                    category=case_data.get('category', case_data.get('fraud_type', 'Unknown')),
                    priority=case_data.get('priority', 'P2'),
                    description=case_data.get('description', 'Generated by Groq'),
                    preconditions=case_data.get('preconditions', []),
                    test_data=case_data.get('test_data', {}),
                    expected_result={
                        'fraud_alert_triggered': case_data.get('expected_result', {}).get('should_detect', True),
                        'risk_score': case_data.get('expected_result', {}).get('risk_score_min', 75),
                        'alert_priority': case_data.get('expected_result', {}).get('alert_priority', 'HIGH'),
                        'action': case_data.get('expected_result', {}).get('action', 'review')
                    },
                    fraud_patterns_tested=case_data.get('fraud_indicators', []),
                    validation_points=[case_data.get('rationale', '')]
                )
                test_cases.append(test_case)
                self.test_case_counter += 1
                
            except Exception as e:
                logger.warning(f"Failed to create test case from: {case_data}. Error: {e}")
                continue
        
        return test_cases
    
    def _fallback_generation(self, requirements: Dict[str, Any]) -> List[Any]:
        """Fallback to basic rule-based generation if Groq fails"""
        from fraud_qa_agent import TestCase
        import random
        
        logger.info("Using fallback rule-based test generation")
        
        test_cases = []
        fraud_types = requirements.get('fraud_types', ['card_fraud'])
        
        for fraud_type in fraud_types:
            # Generate 3 basic test cases per fraud type
            for i in range(3):
                test_case = TestCase(
                    test_case_id=f'TC-{fraud_type.upper()}-{self.test_case_counter:03d}',
                    category=fraud_type.replace('_', ' ').title(),
                    priority='P2',
                    description=f'Basic {fraud_type} test case',
                    preconditions=[],
                    test_data={
                        'amount': random.randint(1000, 50000),
                        'fraud_type': fraud_type
                    },
                    expected_result={
                        'fraud_alert_triggered': True,
                        'risk_score': random.randint(70, 95),
                        'alert_priority': 'HIGH'
                    },
                    fraud_patterns_tested=[fraud_type],
                    validation_points=['Basic validation']
                )
                test_cases.append(test_case)
                self.test_case_counter += 1
        
        return test_cases


# Test the designer
if __name__ == "__main__":
    print("🤖 Groq LLM Test Case Designer")
    print("="*60)
    
    # Check if API key is set
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ GROQ_API_KEY is set (length: {len(api_key)})")
    else:
        print("❌ GROQ_API_KEY not set")
        print("\nTo enable Groq:")
        print("  1. Get API key from: https://console.groq.com")
        print("  2. export GROQ_API_KEY='gsk_...'")
    
    print("\nModel: llama-3.3-70b-versatile")
    print("Speed: ~750 tokens/second (very fast!)")
    print("Cost: Free tier available")
    print("="*60)