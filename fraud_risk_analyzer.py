"""
Fraud Risk Analyzer Component
Assesses and quantifies fraud risk throughout the testing process
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FraudRiskAnalyzer:
    """
    Analyzes fraud risk based on test results
    """
    
    def __init__(self):
        self.risk_weights = {
            'detection_risk': 0.35,
            'false_positive_risk': 0.20,
            'compliance_risk': 0.30,
            'system_risk': 0.15
        }
    
    def calculate_risk(self, test_results: List[Any]) -> Any:
        """Calculate comprehensive fraud risk assessment"""
        from fraud_qa_agent import RiskAssessment, RiskLevel
        
        # Calculate individual risk components
        detection_risk = self._calculate_detection_risk(test_results)
        false_positive_risk = self._calculate_false_positive_risk(test_results)
        compliance_risk = self._calculate_compliance_risk(test_results)
        system_risk = self._calculate_system_risk(test_results)
        
        # Calculate weighted overall risk score
        overall_risk_score = (
            detection_risk * self.risk_weights['detection_risk'] +
            false_positive_risk * self.risk_weights['false_positive_risk'] +
            compliance_risk * self.risk_weights['compliance_risk'] +
            system_risk * self.risk_weights['system_risk']
        )
        
        # Determine risk level
        risk_level = self._categorize_risk(overall_risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            detection_risk, 
            false_positive_risk, 
            compliance_risk, 
            system_risk,
            test_results
        )
        
        assessment = RiskAssessment(
            overall_risk_score=round(overall_risk_score, 2),
            risk_level=risk_level,
            detection_risk=round(detection_risk, 2),
            false_positive_risk=round(false_positive_risk, 2),
            compliance_risk=round(compliance_risk, 2),
            system_risk=round(system_risk, 2),
            recommendations=recommendations
        )
        
        logger.info(f"Risk analysis complete: {risk_level.value} ({overall_risk_score}/100)")
        return assessment
    
    def _calculate_detection_risk(self, test_results: List[Any]) -> float:
        """Calculate risk from missed fraud (false negatives)"""
        from fraud_qa_agent import TestStatus
        
        fraud_tests = [
            r for r in test_results 
            if 'fraud' in r.test_case_id.lower() 
            and 'neg' not in r.test_case_id.lower()
            and 'Performance' not in r.test_case_id
            and 'Compliance' not in r.test_case_id
        ]
        
        if not fraud_tests:
            return 0.0
        
        # Count false negatives (fraud not detected when it should be)
        false_negatives = sum(
            1 for r in fraud_tests 
            if r.status == TestStatus.FAILED 
            and 'FALSE NEGATIVE' in ' '.join(r.errors)
        )
        
        # Calculate false negative rate
        fn_rate = false_negatives / len(fraud_tests) if fraud_tests else 0
        
        # Risk increases exponentially with FN rate
        # Target: <5% FN rate
        if fn_rate < 0.05:
            risk_score = fn_rate * 400  # Max 20 for <5%
        elif fn_rate < 0.10:
            risk_score = 20 + (fn_rate - 0.05) * 1200  # 20-80 for 5-10%
        else:
            risk_score = 80 + (fn_rate - 0.10) * 200  # 80-100 for >10%
        
        return min(100, risk_score)
    
    def _calculate_false_positive_risk(self, test_results: List[Any]) -> float:
        """Calculate risk from false positives (customer friction)"""
        from fraud_qa_agent import TestStatus
        
        # Find negative test cases (legitimate transactions)
        negative_tests = [
            r for r in test_results 
            if 'neg' in r.test_case_id.lower()
        ]
        
        if not negative_tests:
            return 0.0
        
        # Count false positives
        false_positives = sum(
            1 for r in negative_tests 
            if r.status == TestStatus.FAILED 
            and 'FALSE POSITIVE' in ' '.join(r.errors)
        )
        
        # Calculate false positive rate
        fp_rate = false_positives / len(negative_tests) if negative_tests else 0
        
        # Risk calculation (target: <10% FP rate)
        if fp_rate < 0.10:
            risk_score = fp_rate * 300  # Max 30 for <10%
        elif fp_rate < 0.20:
            risk_score = 30 + (fp_rate - 0.10) * 500  # 30-80 for 10-20%
        else:
            risk_score = 80 + (fp_rate - 0.20) * 100  # 80-100 for >20%
        
        return min(100, risk_score)
    
    def _calculate_compliance_risk(self, test_results: List[Any]) -> float:
        """Calculate compliance and regulatory risk"""
        from fraud_qa_agent import TestStatus
        
        compliance_tests = [
            r for r in test_results 
            if 'Compliance' in r.test_case_id or 'COMP' in r.test_case_id
        ]
        
        if not compliance_tests:
            return 0.0
        
        # Compliance failures are critical
        failed_compliance = sum(
            1 for r in compliance_tests 
            if r.status == TestStatus.FAILED
        )
        
        # Any compliance failure is high risk
        if failed_compliance == 0:
            return 0.0
        elif failed_compliance == 1:
            return 60.0
        elif failed_compliance == 2:
            return 85.0
        else:
            return 100.0
    
    def _calculate_system_risk(self, test_results: List[Any]) -> float:
        """Calculate system reliability and performance risk"""
        from fraud_qa_agent import TestStatus
        
        performance_tests = [
            r for r in test_results 
            if 'Performance' in r.test_case_id or 'PERF' in r.test_case_id
        ]
        
        if not performance_tests:
            return 0.0
        
        # Count performance failures
        perf_failures = sum(
            1 for r in performance_tests 
            if r.status == TestStatus.FAILED
        )
        
        # Count blocked tests (system errors)
        blocked_tests = sum(
            1 for r in test_results 
            if r.status == TestStatus.BLOCKED
        )
        
        total_tests = len(test_results)
        
        # Calculate failure rate
        failure_rate = (perf_failures + blocked_tests) / total_tests if total_tests else 0
        
        # Risk scoring
        if failure_rate < 0.02:  # <2% failure
            return failure_rate * 1000  # Max 20
        elif failure_rate < 0.05:  # 2-5% failure
            return 20 + (failure_rate - 0.02) * 1333  # 20-60
        else:  # >5% failure
            return 60 + (failure_rate - 0.05) * 800  # 60-100
        
        return min(100, failure_rate * 1000)
    
    def _categorize_risk(self, risk_score: float) -> Any:
        """Categorize risk level based on score"""
        from fraud_qa_agent import RiskLevel
        
        if risk_score >= 75:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_recommendations(
        self, 
        detection_risk: float,
        false_positive_risk: float,
        compliance_risk: float,
        system_risk: float,
        test_results: List[Any]
    ) -> List[str]:
        """Generate actionable risk mitigation recommendations"""
        
        recommendations = []
        
        # Detection risk recommendations
        if detection_risk >= 75:
            recommendations.append(
                "🔴 CRITICAL: High false negative rate detected. "
                "Immediately review and retrain fraud detection models. "
                "Consider deploying ensemble models for improved detection."
            )
        elif detection_risk >= 50:
            recommendations.append(
                "⚠️ HIGH: Elevated false negative rate. "
                "Review detection rules and thresholds. "
                "Analyze missed fraud patterns and update algorithms."
            )
        elif detection_risk >= 25:
            recommendations.append(
                "⚠️ MEDIUM: Some fraud patterns being missed. "
                "Fine-tune detection rules for identified gaps."
            )
        
        # False positive recommendations
        if false_positive_risk >= 75:
            recommendations.append(
                "🔴 CRITICAL: High false positive rate causing customer friction. "
                "Implement adaptive thresholds based on customer risk profiles. "
                "Review and adjust overly aggressive rules."
            )
        elif false_positive_risk >= 50:
            recommendations.append(
                "⚠️ HIGH: Elevated false positive rate. "
                "Optimize risk scoring algorithm to reduce false alerts. "
                "Consider implementing customer behavior learning."
            )
        
        # Compliance recommendations
        if compliance_risk >= 60:
            recommendations.append(
                "🛑 BLOCKING: Compliance violations detected. "
                "Fix all compliance gaps before production deployment. "
                "This is a go/no-go blocker."
            )
        elif compliance_risk >= 30:
            recommendations.append(
                "⚠️ Compliance concerns identified. "
                "Address all compliance issues and re-validate before deployment."
            )
        
        # System risk recommendations
        if system_risk >= 60:
            recommendations.append(
                "🔴 CRITICAL: System reliability issues detected. "
                "Performance degradation or failures under load. "
                "Conduct capacity planning and optimize critical paths."
            )
        elif system_risk >= 30:
            recommendations.append(
                "⚠️ System performance concerns. "
                "Optimize slow queries and implement caching strategies."
            )
        
        # General recommendations
        from fraud_qa_agent import TestStatus
        
        failed_count = sum(1 for r in test_results if r.status == TestStatus.FAILED)
        total_count = len(test_results)
        
        if failed_count / total_count > 0.15:
            recommendations.append(
                "⚠️ Overall test pass rate below 85%. "
                "Comprehensive review and remediation required before deployment."
            )
        
        # If no major issues
        if not recommendations:
            recommendations.append(
                "✅ All risk metrics within acceptable ranges. "
                "System appears ready for deployment pending final approvals."
            )
        
        return recommendations
    
    def generate_risk_report(self, assessment: Any) -> Dict[str, Any]:
        """Generate detailed risk report"""
        
        return {
            'overall_assessment': {
                'risk_score': assessment.overall_risk_score,
                'risk_level': assessment.risk_level.value,
                'deployment_recommendation': self._get_deployment_recommendation(assessment)
            },
            'risk_breakdown': {
                'detection_risk': {
                    'score': assessment.detection_risk,
                    'weight': self.risk_weights['detection_risk'],
                    'contribution': assessment.detection_risk * self.risk_weights['detection_risk']
                },
                'false_positive_risk': {
                    'score': assessment.false_positive_risk,
                    'weight': self.risk_weights['false_positive_risk'],
                    'contribution': assessment.false_positive_risk * self.risk_weights['false_positive_risk']
                },
                'compliance_risk': {
                    'score': assessment.compliance_risk,
                    'weight': self.risk_weights['compliance_risk'],
                    'contribution': assessment.compliance_risk * self.risk_weights['compliance_risk']
                },
                'system_risk': {
                    'score': assessment.system_risk,
                    'weight': self.risk_weights['system_risk'],
                    'contribution': assessment.system_risk * self.risk_weights['system_risk']
                }
            },
            'recommendations': assessment.recommendations,
            'risk_visualization': self._create_risk_visualization(assessment)
        }
    
    def _get_deployment_recommendation(self, assessment: Any) -> str:
        """Get deployment recommendation based on risk"""
        from fraud_qa_agent import RiskLevel
        
        if assessment.compliance_risk >= 60:
            return "🛑 DO NOT DEPLOY - Compliance violations (BLOCKING)"
        elif assessment.risk_level == RiskLevel.CRITICAL:
            return "🛑 DO NOT DEPLOY - Critical risk level"
        elif assessment.risk_level == RiskLevel.HIGH:
            return "⚠️ DEPLOY WITH CAUTION - High risk, requires executive approval"
        elif assessment.risk_level == RiskLevel.MEDIUM:
            return "⚠️ CONDITIONAL APPROVAL - Medium risk, monitor closely post-deployment"
        else:
            return "✅ APPROVED FOR DEPLOYMENT - Low risk"
    
    def _create_risk_visualization(self, assessment: Any) -> str:
        """Create text-based risk visualization"""
        
        def risk_bar(score: float, width: int = 20) -> str:
            filled = int((score / 100) * width)
            bar = '█' * filled + '░' * (width - filled)
            
            if score >= 75:
                symbol = '🔴'
            elif score >= 50:
                symbol = '🟡'
            else:
                symbol = '🟢'
            
            return f"{symbol} {bar} {score:.1f}/100"
        
        viz = f"""
╔══════════════════════════════════════════════════════════╗
║           FRAUD RISK ASSESSMENT DASHBOARD                ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Overall Risk:        {risk_bar(assessment.overall_risk_score, 30)}  ║
║                                                          ║
║  Detection Risk:      {risk_bar(assessment.detection_risk, 30)}  ║
║  False Positive Risk: {risk_bar(assessment.false_positive_risk, 30)}  ║
║  Compliance Risk:     {risk_bar(assessment.compliance_risk, 30)}  ║
║  System Risk:         {risk_bar(assessment.system_risk, 30)}  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
        return viz