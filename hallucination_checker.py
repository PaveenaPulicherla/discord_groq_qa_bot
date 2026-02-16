"""
Hallucination Checker Component
Detects hallucinations and incorrect inferences in AI/ML fraud detection outputs
"""

import random
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HallucinationChecker:
    """
    Detects hallucinations in fraud detection AI/ML outputs
    """
    
    def __init__(self):
        self.hallucination_patterns = self._load_hallucination_patterns()
    
    def _load_hallucination_patterns(self) -> List[str]:
        """Load known hallucination patterns"""
        return [
            'fabricated_transaction_details',
            'incorrect_calculations',
            'invalid_logic',
            'misattributed_factors',
            'contradictory_statements',
            'invented_historical_data',
            'false_pattern_recognition'
        ]
    
    def verify_results(self, test_results: List[Any]) -> List[Any]:
        """Verify test results for hallucinations"""
        from fraud_qa_agent import HallucinationCheck
        
        checks = []
        
        for result in test_results:
            # Skip non-fraud detection tests
            if 'Performance' in result.test_case_id or 'Compliance' in result.test_case_id:
                continue
            
            hallucinations = self._detect_hallucinations(result)
            
            if hallucinations:
                severity = self._calculate_severity(hallucinations)
                confidence = self._calculate_confidence(hallucinations)
                
                check = HallucinationCheck(
                    test_case_id=result.test_case_id,
                    hallucinations_detected=hallucinations,
                    severity=severity,
                    confidence_score=confidence
                )
                checks.append(check)
        
        logger.info(f"Hallucination check completed: {len(checks)} tests with issues")
        return checks
    
    def _detect_hallucinations(self, test_result: Any) -> List[Dict[str, Any]]:
        """Detect hallucinations in a test result"""
        
        hallucinations = []
        actual = test_result.actual_result
        
        # Check 1: Validate fraud indicators against actual data
        if 'fraud_indicators' in actual:
            indicators = actual['fraud_indicators']
            invalid_indicators = self._validate_fraud_indicators(indicators, actual)
            
            for invalid in invalid_indicators:
                hallucinations.append({
                    'type': 'misattributed_factors',
                    'description': f"Fraud indicator '{invalid}' cited but not present in data",
                    'severity': 'HIGH',
                    'field': 'fraud_indicators'
                })
        
        # Check 2: Validate risk score calculation
        if 'risk_score' in actual:
            score = actual['risk_score']
            score_hallucination = self._validate_risk_score(score, actual)
            
            if score_hallucination:
                hallucinations.append(score_hallucination)
        
        # Check 3: Check for contradictory statements
        contradictions = self._detect_contradictions(actual)
        hallucinations.extend(contradictions)
        
        # Check 4: Validate confidence calibration
        if 'confidence' in actual:
            confidence_issue = self._validate_confidence(actual)
            if confidence_issue:
                hallucinations.append(confidence_issue)
        
        # Simulate realistic hallucination detection (5% hallucination rate)
        if random.random() < 0.05 and not hallucinations:
            hallucinations.append({
                'type': random.choice(self.hallucination_patterns),
                'description': 'Detected potential hallucination in AI reasoning',
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'field': 'explanation'
            })
        
        return hallucinations
    
    def _validate_fraud_indicators(self, indicators: List[str], actual_result: Dict) -> List[str]:
        """Validate that fraud indicators are grounded in actual data"""
        
        invalid_indicators = []
        
        # Simulate validation logic
        # In production, this would check against actual transaction data
        
        for indicator in indicators:
            # Example: Check if "high_value" indicator is justified
            if indicator == 'high_value':
                # In real implementation, would check actual transaction amount
                # Here we simulate occasional false attribution (10% chance)
                if random.random() < 0.10:
                    invalid_indicators.append(indicator)
            
            # Example: Check if "unusual_time" is accurate
            elif indicator == 'unusual_time':
                if random.random() < 0.08:
                    invalid_indicators.append(indicator)
        
        return invalid_indicators
    
    def _validate_risk_score(self, score: float, actual_result: Dict) -> Dict[str, Any]:
        """Validate risk score calculation logic"""
        
        # Check if score is within valid range
        if score < 0 or score > 100:
            return {
                'type': 'incorrect_calculations',
                'description': f'Risk score {score} outside valid range [0-100]',
                'severity': 'CRITICAL',
                'field': 'risk_score'
            }
        
        # Check for unjustified high scores
        alert_triggered = actual_result.get('fraud_alert_triggered', False)
        
        if score > 90 and not alert_triggered:
            return {
                'type': 'invalid_logic',
                'description': f'Risk score {score} very high but no alert triggered - logical inconsistency',
                'severity': 'HIGH',
                'field': 'risk_score'
            }
        
        if score < 30 and alert_triggered:
            return {
                'type': 'invalid_logic',
                'description': f'Risk score {score} low but alert triggered - logical inconsistency',
                'severity': 'HIGH',
                'field': 'risk_score'
            }
        
        return None
    
    def _detect_contradictions(self, actual_result: Dict) -> List[Dict[str, Any]]:
        """Detect contradictory statements in results"""
        
        contradictions = []
        
        # Example: Check if fraud indicators contradict each other
        if 'fraud_indicators' in actual_result:
            indicators = actual_result['fraud_indicators']
            
            # Check for contradictory patterns
            if 'first_international' in indicators and 'high_international_volume' in indicators:
                contradictions.append({
                    'type': 'contradictory_statements',
                    'description': 'Claims both "first international transfer" and "high international volume"',
                    'severity': 'HIGH',
                    'field': 'fraud_indicators'
                })
        
        # Simulate additional contradiction detection (3% chance)
        if random.random() < 0.03:
            contradictions.append({
                'type': 'contradictory_statements',
                'description': 'Detected logical contradiction in fraud reasoning',
                'severity': 'MEDIUM',
                'field': 'explanation'
            })
        
        return contradictions
    
    def _validate_confidence(self, actual_result: Dict) -> Dict[str, Any]:
        """Validate confidence score calibration"""
        
        confidence = actual_result.get('confidence', 0)
        risk_score = actual_result.get('risk_score', 0)
        
        # Confidence should correlate with risk score
        # High risk should have high confidence, low risk should have lower confidence
        
        if risk_score > 80 and confidence < 0.5:
            return {
                'type': 'invalid_logic',
                'description': f'High risk score ({risk_score}) but low confidence ({confidence}) - poor calibration',
                'severity': 'MEDIUM',
                'field': 'confidence'
            }
        
        if risk_score < 30 and confidence > 0.9:
            return {
                'type': 'invalid_logic',
                'description': f'Low risk score ({risk_score}) but very high confidence ({confidence}) - overconfident',
                'severity': 'MEDIUM',
                'field': 'confidence'
            }
        
        return None
    
    def _calculate_severity(self, hallucinations: List[Dict[str, Any]]) -> str:
        """Calculate overall severity of hallucinations"""
        
        if not hallucinations:
            return 'NONE'
        
        severities = [h['severity'] for h in hallucinations]
        
        if 'CRITICAL' in severities:
            return 'CRITICAL'
        elif 'HIGH' in severities:
            return 'HIGH'
        elif 'MEDIUM' in severities:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_confidence(self, hallucinations: List[Dict[str, Any]]) -> float:
        """Calculate confidence in hallucination detection"""
        
        # Higher confidence for more severe/obvious hallucinations
        if not hallucinations:
            return 0.0
        
        severity_scores = {
            'CRITICAL': 0.95,
            'HIGH': 0.85,
            'MEDIUM': 0.70,
            'LOW': 0.60
        }
        
        avg_confidence = sum(
            severity_scores.get(h['severity'], 0.5) 
            for h in hallucinations
        ) / len(hallucinations)
        
        return round(avg_confidence, 2)
    
    def generate_hallucination_report(self, checks: List[Any]) -> Dict[str, Any]:
        """Generate summary report of hallucinations"""
        
        total_checks = len(checks)
        if total_checks == 0:
            return {
                'total_tests_checked': 0,
                'hallucinations_found': 0,
                'hallucination_rate': 0.0,
                'by_severity': {},
                'by_type': {}
            }
        
        total_hallucinations = sum(len(c.hallucinations_detected) for c in checks)
        
        # Group by severity
        by_severity = {}
        by_type = {}
        
        for check in checks:
            severity = check.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            for h in check.hallucinations_detected:
                h_type = h['type']
                by_type[h_type] = by_type.get(h_type, 0) + 1
        
        return {
            'total_tests_checked': total_checks,
            'hallucinations_found': total_hallucinations,
            'hallucination_rate': round(total_hallucinations / total_checks * 100, 2),
            'by_severity': by_severity,
            'by_type': by_type,
            'critical_issues': sum(1 for c in checks if c.severity == 'CRITICAL')
        }