"""
Test Summary Generator Component
Generates concise, actionable summaries of test execution
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TestSummaryGenerator:
    """
    Generates test execution summaries with key metrics and insights
    """
    
    def __init__(self):
        pass
    
    def create_summary(
        self,
        test_results: List[Any],
        hallucination_checks: List[Any],
        risk_assessment: Optional[Any]
    ) -> Dict[str, Any]:
        """Create comprehensive test summary"""
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(test_results)
        
        # Calculate accuracy metrics
        accuracy_metrics = self._calculate_accuracy_metrics(test_results)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(test_results)
        
        # Analyze failures
        failure_analysis = self._analyze_failures(test_results)
        
        # Analyze hallucinations
        hallucination_summary = self._summarize_hallucinations(hallucination_checks)
        
        # Generate insights
        insights = self._generate_insights(
            test_results, 
            accuracy_metrics, 
            hallucination_checks,
            risk_assessment
        )
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'overall_metrics': overall_metrics,
            'accuracy_metrics': accuracy_metrics,
            'performance_metrics': performance_metrics,
            'failure_analysis': failure_analysis,
            'hallucination_summary': hallucination_summary,
            'insights': insights,
            'risk_assessment_summary': self._summarize_risk(risk_assessment) if risk_assessment else None
        }
        
        logger.info("Test summary generated successfully")
        return summary
    
    def _calculate_overall_metrics(self, test_results: List[Any]) -> Dict[str, Any]:
        """Calculate overall test execution metrics"""
        from fraud_qa_agent import TestStatus
        
        total = len(test_results)
        passed = sum(1 for r in test_results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in test_results if r.status == TestStatus.FAILED)
        blocked = sum(1 for r in test_results if r.status == TestStatus.BLOCKED)
        skipped = sum(1 for r in test_results if r.status == TestStatus.SKIPPED)
        
        # Calculate total execution time
        total_time_ms = sum(r.execution_time_ms for r in test_results)
        avg_time_ms = total_time_ms / total if total > 0 else 0
        
        return {
            'total_test_cases': total,
            'passed': passed,
            'failed': failed,
            'blocked': blocked,
            'skipped': skipped,
            'pass_rate': round((passed / total * 100), 2) if total > 0 else 0,
            'fail_rate': round((failed / total * 100), 2) if total > 0 else 0,
            'total_execution_time_ms': round(total_time_ms, 2),
            'avg_execution_time_ms': round(avg_time_ms, 2),
            'execution_time_formatted': self._format_duration(total_time_ms)
        }
    
    def _calculate_accuracy_metrics(self, test_results: List[Any]) -> Dict[str, Any]:
        """Calculate fraud detection accuracy metrics"""
        from fraud_qa_agent import TestStatus
        
        # Separate fraud and legitimate test cases
        fraud_tests = [
            r for r in test_results 
            if 'fraud' in r.test_case_id.lower() 
            and 'neg' not in r.test_case_id.lower()
            and 'Performance' not in r.test_case_id
            and 'Compliance' not in r.test_case_id
        ]
        
        legit_tests = [
            r for r in test_results 
            if 'neg' in r.test_case_id.lower()
        ]
        
        # Calculate confusion matrix
        true_positives = sum(
            1 for r in fraud_tests 
            if r.status == TestStatus.PASSED
        )
        
        false_negatives = sum(
            1 for r in fraud_tests 
            if r.status == TestStatus.FAILED
        )
        
        true_negatives = sum(
            1 for r in legit_tests 
            if r.status == TestStatus.PASSED
        )
        
        false_positives = sum(
            1 for r in legit_tests 
            if r.status == TestStatus.FAILED
        )
        
        # Calculate derived metrics
        total_fraud = len(fraud_tests)
        total_legit = len(legit_tests)
        
        precision = (true_positives / (true_positives + false_positives)) if (true_positives + false_positives) > 0 else 0
        recall = (true_positives / (true_positives + false_negatives)) if (true_positives + false_negatives) > 0 else 0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
        
        return {
            'confusion_matrix': {
                'true_positives': true_positives,
                'false_positives': false_positives,
                'true_negatives': true_negatives,
                'false_negatives': false_negatives
            },
            'total_fraud_tests': total_fraud,
            'total_legitimate_tests': total_legit,
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1_score * 100, 2),
            'false_positive_rate': round((false_positives / total_legit * 100), 2) if total_legit > 0 else 0,
            'false_negative_rate': round((false_negatives / total_fraud * 100), 2) if total_fraud > 0 else 0
        }
    
    def _calculate_performance_metrics(self, test_results: List[Any]) -> Dict[str, Any]:
        """Calculate performance-related metrics"""
        
        # Get response times
        response_times = [r.execution_time_ms for r in test_results if r.execution_time_ms > 0]
        
        if not response_times:
            return {
                'avg_response_time_ms': 0,
                'min_response_time_ms': 0,
                'max_response_time_ms': 0,
                'p95_response_time_ms': 0,
                'p99_response_time_ms': 0
            }
        
        response_times.sort()
        
        avg_response = sum(response_times) / len(response_times)
        min_response = min(response_times)
        max_response = max(response_times)
        
        # Calculate percentiles
        p95_index = int(len(response_times) * 0.95)
        p99_index = int(len(response_times) * 0.99)
        
        p95_response = response_times[p95_index] if p95_index < len(response_times) else max_response
        p99_response = response_times[p99_index] if p99_index < len(response_times) else max_response
        
        return {
            'avg_response_time_ms': round(avg_response, 2),
            'min_response_time_ms': round(min_response, 2),
            'max_response_time_ms': round(max_response, 2),
            'p95_response_time_ms': round(p95_response, 2),
            'p99_response_time_ms': round(p99_response, 2)
        }
    
    def _analyze_failures(self, test_results: List[Any]) -> Dict[str, Any]:
        """Analyze test failures by category"""
        from fraud_qa_agent import TestStatus
        
        failed_tests = [r for r in test_results if r.status == TestStatus.FAILED]
        
        # Categorize failures
        categories = {}
        critical_failures = []
        
        for result in failed_tests:
            # Extract category from test ID
            parts = result.test_case_id.split('-')
            category = parts[1] if len(parts) > 1 else 'UNKNOWN'
            
            categories[category] = categories.get(category, 0) + 1
            
            # Check for critical failures
            if any('CRITICAL' in err or 'FALSE NEGATIVE' in err for err in result.errors):
                critical_failures.append({
                    'test_case_id': result.test_case_id,
                    'errors': result.errors
                })
        
        return {
            'total_failures': len(failed_tests),
            'by_category': categories,
            'critical_failures': critical_failures,
            'critical_count': len(critical_failures)
        }
    
    def _summarize_hallucinations(self, hallucination_checks: List[Any]) -> Dict[str, Any]:
        """Summarize hallucination detection results"""
        
        if not hallucination_checks:
            return {
                'total_checks': 0,
                'hallucinations_detected': 0,
                'hallucination_rate': 0.0,
                'by_severity': {},
                'critical_count': 0
            }
        
        total_hallucinations = sum(len(c.hallucinations_detected) for c in hallucination_checks)
        
        by_severity = {}
        for check in hallucination_checks:
            severity = check.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        critical_count = by_severity.get('CRITICAL', 0)
        
        return {
            'total_checks': len(hallucination_checks),
            'hallucinations_detected': total_hallucinations,
            'hallucination_rate': round((total_hallucinations / len(hallucination_checks) * 100), 2),
            'by_severity': by_severity,
            'critical_count': critical_count
        }
    
    def _generate_insights(
        self,
        test_results: List[Any],
        accuracy_metrics: Dict[str, Any],
        hallucination_checks: List[Any],
        risk_assessment: Optional[Any]
    ) -> List[str]:
        """Generate AI-powered insights from test results"""
        
        insights = []
        
        # Insight 1: Overall health
        pass_rate = accuracy_metrics.get('recall', 0)
        if pass_rate >= 95:
            insights.append("✅ Excellent fraud detection accuracy (>95% recall)")
        elif pass_rate >= 85:
            insights.append("⚠️ Good fraud detection accuracy, but room for improvement")
        else:
            insights.append("🔴 Fraud detection accuracy below target (<85% recall)")
        
        # Insight 2: False positive analysis
        fp_rate = accuracy_metrics.get('false_positive_rate', 0)
        if fp_rate > 15:
            insights.append(f"⚠️ High false positive rate ({fp_rate}%) may cause customer friction")
        elif fp_rate > 10:
            insights.append(f"⚠️ False positive rate ({fp_rate}%) approaching threshold")
        else:
            insights.append(f"✅ False positive rate ({fp_rate}%) within acceptable range")
        
        # Insight 3: False negative analysis
        fn_rate = accuracy_metrics.get('false_negative_rate', 0)
        if fn_rate > 10:
            insights.append(f"🔴 CRITICAL: High false negative rate ({fn_rate}%) - significant fraud being missed")
        elif fn_rate > 5:
            insights.append(f"⚠️ Elevated false negative rate ({fn_rate}%) - some fraud patterns not detected")
        
        # Insight 4: Hallucination analysis
        if hallucination_checks:
            hallucination_rate = len(hallucination_checks) / len(test_results) * 100
            if hallucination_rate > 10:
                insights.append(f"⚠️ High hallucination rate ({hallucination_rate:.1f}%) in AI outputs - review model reliability")
        
        # Insight 5: Performance insights
        from fraud_qa_agent import TestStatus
        perf_failures = sum(
            1 for r in test_results 
            if 'Performance' in r.test_case_id and r.status == TestStatus.FAILED
        )
        if perf_failures > 0:
            insights.append(f"⚠️ Performance issues detected in {perf_failures} test(s)")
        
        # Insight 6: Risk assessment
        if risk_assessment:
            from fraud_qa_agent import RiskLevel
            if risk_assessment.risk_level == RiskLevel.CRITICAL:
                insights.append("🔴 CRITICAL risk level - immediate action required before deployment")
            elif risk_assessment.risk_level == RiskLevel.HIGH:
                insights.append("⚠️ HIGH risk level - careful review and mitigation required")
        
        return insights
    
    def _summarize_risk(self, risk_assessment: Any) -> Dict[str, Any]:
        """Summarize risk assessment"""
        
        return {
            'overall_risk_score': risk_assessment.overall_risk_score,
            'risk_level': risk_assessment.risk_level.value,
            'top_risk': self._identify_top_risk(risk_assessment),
            'recommendations_count': len(risk_assessment.recommendations)
        }
    
    def _identify_top_risk(self, risk_assessment: Any) -> str:
        """Identify the highest risk component"""
        
        risks = {
            'Detection Risk': risk_assessment.detection_risk,
            'False Positive Risk': risk_assessment.false_positive_risk,
            'Compliance Risk': risk_assessment.compliance_risk,
            'System Risk': risk_assessment.system_risk
        }
        
        top_risk = max(risks.items(), key=lambda x: x[1])
        return f"{top_risk[0]} ({top_risk[1]:.1f})"
    
    def _format_duration(self, ms: float) -> str:
        """Format milliseconds into human-readable duration"""
        
        seconds = ms / 1000
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        
        minutes = int(seconds / 60)
        remaining_seconds = int(seconds % 60)
        
        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"
        
        hours = int(minutes / 60)
        remaining_minutes = int(minutes % 60)
        
        return f"{hours}h {remaining_minutes}m"
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print formatted summary to console"""
        
        print("\n" + "="*70)
        print("FRAUD INVESTIGATION QA - TEST EXECUTION SUMMARY")
        print("="*70)
        
        overall = summary['overall_metrics']
        print(f"\n📊 OVERALL METRICS")
        print(f"   Total Tests:     {overall['total_test_cases']}")
        print(f"   ✅ Passed:        {overall['passed']} ({overall['pass_rate']}%)")
        print(f"   ❌ Failed:        {overall['failed']} ({overall['fail_rate']}%)")
        print(f"   ⊗ Blocked:        {overall['blocked']}")
        print(f"   ⏱️  Execution Time: {overall['execution_time_formatted']}")
        
        accuracy = summary['accuracy_metrics']
        print(f"\n🎯 ACCURACY METRICS")
        print(f"   Precision:        {accuracy['precision']}%")
        print(f"   Recall:           {accuracy['recall']}%")
        print(f"   F1 Score:         {accuracy['f1_score']}%")
        print(f"   False Positives:  {accuracy['false_positive_rate']}%")
        print(f"   False Negatives:  {accuracy['false_negative_rate']}%")
        
        perf = summary['performance_metrics']
        print(f"\n⚡ PERFORMANCE METRICS")
        print(f"   Avg Response:     {perf['avg_response_time_ms']:.2f}ms")
        print(f"   P95 Response:     {perf['p95_response_time_ms']:.2f}ms")
        print(f"   P99 Response:     {perf['p99_response_time_ms']:.2f}ms")
        
        hallucinations = summary['hallucination_summary']
        if hallucinations['total_checks'] > 0:
            print(f"\n🔍 HALLUCINATION DETECTION")
            print(f"   Tests Checked:    {hallucinations['total_checks']}")
            print(f"   Issues Found:     {hallucinations['hallucinations_detected']}")
            print(f"   Hallucination Rate: {hallucinations['hallucination_rate']}%")
            if hallucinations['critical_count'] > 0:
                print(f"   🔴 Critical:      {hallucinations['critical_count']}")
        
        print(f"\n💡 KEY INSIGHTS")
        for insight in summary['insights']:
            print(f"   {insight}")
        
        print("\n" + "="*70)