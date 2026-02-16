"""
Fraud Investigation QA AI Agent
Main orchestration module that coordinates all testing components
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


@dataclass
class TestCase:
    """Represents a single test case"""
    test_case_id: str
    category: str
    priority: str
    description: str
    preconditions: List[str]
    test_data: Dict[str, Any]
    expected_result: Dict[str, Any]
    fraud_patterns_tested: List[str]
    validation_points: List[str]


@dataclass
class TestResult:
    """Represents test execution result"""
    test_case_id: str
    status: TestStatus
    actual_result: Dict[str, Any]
    execution_time_ms: float
    timestamp: str
    errors: List[str]
    warnings: List[str]
    performance_metrics: Dict[str, Any]


@dataclass
class HallucinationCheck:
    """Represents hallucination detection result"""
    test_case_id: str
    hallucinations_detected: List[Dict[str, Any]]
    severity: str
    confidence_score: float


@dataclass
class RiskAssessment:
    """Represents fraud risk assessment"""
    overall_risk_score: float
    risk_level: RiskLevel
    detection_risk: float
    false_positive_risk: float
    compliance_risk: float
    system_risk: float
    recommendations: List[str]


class FraudQAAgent:
    """
    Main QA AI Agent for Fraud Investigation Workflow Testing
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the QA Agent"""
        self.config = config or {}
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestResult] = []
        self.hallucination_checks: List[HallucinationCheck] = []
        self.risk_assessment: Optional[RiskAssessment] = None
        
        logger.info("Fraud QA Agent initialized")
    
    def run_full_qa_cycle(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete QA cycle: design -> execute -> analyze -> report
        """
        logger.info("Starting full QA cycle")
        
        # Step 1: Design test cases
        logger.info("Step 1: Designing test cases")
        self.test_cases = self.design_test_cases(requirements)
        
        # Step 2: Execute tests
        logger.info("Step 2: Executing tests")
        self.test_results = self.execute_tests(self.test_cases)
        
        # Step 3: Check for hallucinations
        logger.info("Step 3: Checking for hallucinations")
        self.hallucination_checks = self.check_hallucinations(self.test_results)
        
        # Step 4: Analyze fraud risk
        logger.info("Step 4: Analyzing fraud risk")
        self.risk_assessment = self.analyze_fraud_risk(self.test_results)
        
        # Step 5: Generate summary
        logger.info("Step 5: Generating test summary")
        summary = self.generate_summary()
        
        # Step 6: Build report
        logger.info("Step 6: Building comprehensive report")
        report = self.build_report(summary)
        
        logger.info("Full QA cycle completed")
        return report
    
    def design_test_cases(self, requirements: Dict[str, Any]) -> List[TestCase]:
        """
        Component 1: Test Case Designer
        Generate test cases based on requirements using Groq LLM
        """
        # Try Groq LLM first, fall back to rule-based if unavailable
        try:
            from groq_test_designer import GroqTestCaseDesigner
            designer = GroqTestCaseDesigner()
        except ImportError:
            logger.warning("Groq designer not available, using rule-based")
            from test_case_designer import TestCaseDesigner
            designer = TestCaseDesigner()
        
        test_cases = designer.generate_test_cases(requirements)
        
        logger.info(f"Generated {len(test_cases)} test cases")
        return test_cases
    
    def execute_tests(self, test_cases: List[TestCase]) -> List[TestResult]:
        """
        Component 2: Test Execution Engine
        Execute test cases and capture results
        """
        from test_execution_engine import TestExecutionEngine
        
        engine = TestExecutionEngine()
        results = engine.execute_test_suite(test_cases)
        
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        
        logger.info(f"Test execution completed: {passed} passed, {failed} failed")
        return results
    
    def check_hallucinations(self, test_results: List[TestResult]) -> List[HallucinationCheck]:
        """
        Component 5: Hallucination Checker
        Detect hallucinations in AI/ML outputs
        """
        from hallucination_checker import HallucinationChecker
        
        checker = HallucinationChecker()
        checks = checker.verify_results(test_results)
        
        total_hallucinations = sum(len(c.hallucinations_detected) for c in checks)
        logger.info(f"Hallucination check completed: {total_hallucinations} issues detected")
        
        return checks
    
    def analyze_fraud_risk(self, test_results: List[TestResult]) -> RiskAssessment:
        """
        Component 6: Fraud Risk Analyzer
        Assess overall fraud risk based on test results
        """
        from fraud_risk_analyzer import FraudRiskAnalyzer
        
        analyzer = FraudRiskAnalyzer()
        assessment = analyzer.calculate_risk(test_results)
        
        logger.info(f"Risk assessment completed: {assessment.risk_level.value} risk ({assessment.overall_risk_score}/100)")
        
        return assessment
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Component 3: Test Summary Generator
        Generate concise summary of test execution
        """
        from test_summary_generator import TestSummaryGenerator
        
        generator = TestSummaryGenerator()
        summary = generator.create_summary(
            test_results=self.test_results,
            hallucination_checks=self.hallucination_checks,
            risk_assessment=self.risk_assessment
        )
        
        logger.info("Test summary generated")
        return summary
    
    def build_report(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Component 4: Test Report Builder
        Build comprehensive test report
        """
        from test_report_builder import TestReportBuilder
        
        builder = TestReportBuilder()
        report = builder.generate_report(
            test_cases=self.test_cases,
            test_results=self.test_results,
            summary=summary,
            hallucination_checks=self.hallucination_checks,
            risk_assessment=self.risk_assessment
        )
        
        logger.info("Comprehensive report built")
        return report
    
    def get_deployment_recommendation(self) -> str:
        """Get deployment recommendation based on test results"""
        if not self.risk_assessment:
            return "UNKNOWN - Risk assessment not completed"
        
        risk_score = self.risk_assessment.overall_risk_score
        critical_failures = sum(
            1 for r in self.test_results 
            if r.status == TestStatus.FAILED and any('CRITICAL' in str(e) for e in r.errors)
        )
        
        if critical_failures > 0:
            return "🛑 DO NOT DEPLOY - Critical failures detected"
        elif risk_score >= 75:
            return "⚠️ DO NOT DEPLOY - High risk score"
        elif risk_score >= 50:
            return "⚠️ DEPLOY WITH CAUTION - Medium risk, requires approval"
        else:
            return "✅ APPROVED FOR DEPLOYMENT - Low risk"
    
    def export_results(self, filepath: str, format: str = 'json') -> None:
        """Export test results to file"""
        
        # Helper function to convert dataclass with enums to dict
        def convert_to_dict(obj):
            """Convert dataclass to dict, handling enums properly"""
            if obj is None:
                return None
            result = asdict(obj)
            # Convert enum values to strings
            for key, value in result.items():
                if hasattr(value, 'value'):  # It's an enum
                    result[key] = value.value
                elif hasattr(value, 'name'):  # Also an enum
                    result[key] = value.name
            return result
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_cases': [convert_to_dict(tc) for tc in self.test_cases],
            'test_results': [convert_to_dict(tr) for tr in self.test_results],
            'hallucination_checks': [convert_to_dict(hc) for hc in self.hallucination_checks],
            'risk_assessment': convert_to_dict(self.risk_assessment) if self.risk_assessment else None,
            'deployment_recommendation': self.get_deployment_recommendation()
        }
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results exported to {filepath}")
        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """Main execution function"""
    # Example usage
    agent = FraudQAAgent()
    
    # Define fraud investigation requirements
    requirements = {
        'fraud_types': [
            'wire_transfer_fraud',
            'account_takeover',
            'card_fraud',
            'identity_theft',
            'money_laundering'
        ],
        'detection_rules': {
            'high_value_threshold': 10000,
            'velocity_check_window': 3600,  # 1 hour
            'geographic_risk_countries': ['NG', 'RU', 'CN'],
            'max_failed_logins': 3
        },
        'compliance_requirements': [
            'AML_KYC',
            'PCI_DSS',
            'GDPR'
        ],
        'performance_requirements': {
            'max_response_time_ms': 5000,
            'min_throughput_tps': 1000,
            'max_false_positive_rate': 0.10,
            'max_false_negative_rate': 0.05
        }
    }
    
    # Run full QA cycle
    report = agent.run_full_qa_cycle(requirements)
    
    # Export results
    agent.export_results('fraud_qa_results.json')
    
    # Print deployment recommendation
    print("\n" + "="*60)
    print("DEPLOYMENT RECOMMENDATION")
    print("="*60)
    print(agent.get_deployment_recommendation())
    print("="*60)


if __name__ == "__main__":
    main()