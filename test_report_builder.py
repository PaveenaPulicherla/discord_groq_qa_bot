"""
Test Report Builder Component
Builds comprehensive, stakeholder-friendly test reports
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class TestReportBuilder:
    """
    Builds comprehensive test reports with visualizations and recommendations
    """
    
    def __init__(self):
        pass
    
    def generate_report(
        self,
        test_cases: List[Any],
        test_results: List[Any],
        summary: Dict[str, Any],
        hallucination_checks: List[Any],
        risk_assessment: Optional[Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        report = {
            'metadata': self._create_metadata(),
            'executive_summary': self._create_executive_summary(summary, risk_assessment),
            'test_execution_dashboard': self._create_dashboard(summary),
            'fraud_pattern_analysis': self._create_fraud_pattern_analysis(test_cases, test_results),
            'detailed_results': self._create_detailed_results(test_results),
            'hallucination_report': self._create_hallucination_report(hallucination_checks),
            'risk_assessment': self._create_risk_section(risk_assessment),
            'recommendations': self._create_recommendations(summary, risk_assessment),
            'compliance_section': self._create_compliance_section(test_results),
            'appendix': self._create_appendix(test_cases, test_results)
        }
        
        logger.info("Comprehensive report generated")
        return report
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Create report metadata"""
        return {
            'report_title': 'Fraud Investigation QA Test Report',
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'Fraud QA AI Agent v1.0',
            'report_version': '1.0.0'
        }
    
    def _create_executive_summary(self, summary: Dict[str, Any], risk_assessment: Optional[Any]) -> Dict[str, Any]:
        """Create executive summary for management"""
        
        overall = summary['overall_metrics']
        accuracy = summary['accuracy_metrics']
        
        # Determine overall status
        if overall['pass_rate'] >= 90 and accuracy['recall'] >= 90:
            status = 'EXCELLENT'
            status_icon = '✅'
        elif overall['pass_rate'] >= 75 and accuracy['recall'] >= 75:
            status = 'GOOD'
            status_icon = '⚠️'
        else:
            status = 'NEEDS IMPROVEMENT'
            status_icon = '🔴'
        
        # Create deployment recommendation
        if risk_assessment:
            from fraud_qa_agent import RiskLevel
            
            if risk_assessment.compliance_risk >= 60:
                deployment_rec = '🛑 DO NOT DEPLOY - Compliance violations'
            elif risk_assessment.risk_level == RiskLevel.CRITICAL:
                deployment_rec = '🛑 DO NOT DEPLOY - Critical risk'
            elif risk_assessment.risk_level == RiskLevel.HIGH:
                deployment_rec = '⚠️ DEPLOY WITH CAUTION - High risk'
            else:
                deployment_rec = '✅ APPROVED FOR DEPLOYMENT'
        else:
            deployment_rec = 'PENDING RISK ASSESSMENT'
        
        return {
            'overall_status': f"{status_icon} {status}",
            'deployment_recommendation': deployment_rec,
            'key_metrics': {
                'pass_rate': f"{overall['pass_rate']}%",
                'fraud_detection_accuracy': f"{accuracy['recall']}%",
                'false_positive_rate': f"{accuracy['false_positive_rate']}%",
                'execution_time': overall['execution_time_formatted']
            },
            'critical_issues': summary['failure_analysis']['critical_count'],
            'top_insights': summary['insights'][:3]  # Top 3 insights
        }
    
    def _create_dashboard(self, summary: Dict[str, Any]) -> str:
        """Create text-based execution dashboard"""
        
        overall = summary['overall_metrics']
        accuracy = summary['accuracy_metrics']
        perf = summary['performance_metrics']
        
        # Create progress bars
        def progress_bar(value: float, width: int = 20) -> str:
            filled = int((value / 100) * width)
            bar = '█' * filled + '░' * (width - filled)
            return f"{bar} {value:.1f}%"
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════╗
║     FRAUD DETECTION QA - TEST EXECUTION DASHBOARD                ║
║     Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  TEST EXECUTION SUMMARY                                          ║
║  ─────────────────────────────────────────────────────────────  ║
║  Total Tests:     {overall['total_test_cases']:>4}                                          ║
║  ✅ Passed:        {overall['passed']:>4} ({overall['pass_rate']:>5.1f}%)                                   ║
║  ❌ Failed:        {overall['failed']:>4} ({overall['fail_rate']:>5.1f}%)                                   ║
║  ⊗ Blocked:        {overall['blocked']:>4}                                            ║
║                                                                  ║
║  Pass Rate:       {progress_bar(overall['pass_rate'], 25)}            ║
║                                                                  ║
║  FRAUD DETECTION ACCURACY                                        ║
║  ─────────────────────────────────────────────────────────────  ║
║  Precision:       {progress_bar(accuracy['precision'], 25)}            ║
║  Recall:          {progress_bar(accuracy['recall'], 25)}            ║
║  F1 Score:        {progress_bar(accuracy['f1_score'], 25)}            ║
║                                                                  ║
║  False Positives: {accuracy['false_positive_rate']:>5.1f}%    (Target: <10%)                       ║
║  False Negatives: {accuracy['false_negative_rate']:>5.1f}%    (Target: <5%)                        ║
║                                                                  ║
║  PERFORMANCE METRICS                                             ║
║  ─────────────────────────────────────────────────────────────  ║
║  Avg Response:    {perf['avg_response_time_ms']:>7.2f}ms                                    ║
║  P95 Response:    {perf['p95_response_time_ms']:>7.2f}ms                                    ║
║  P99 Response:    {perf['p99_response_time_ms']:>7.2f}ms                                    ║
║  Max Response:    {perf['max_response_time_ms']:>7.2f}ms                                    ║
║                                                                  ║
║  Critical Issues: {summary['failure_analysis']['critical_count']:>3}                                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        return dashboard
    
    def _create_fraud_pattern_analysis(self, test_cases: List[Any], test_results: List[Any]) -> Dict[str, Any]:
        """Analyze fraud pattern detection performance"""
        from fraud_qa_agent import TestStatus
        
        # Group by fraud pattern
        pattern_stats = {}
        
        for i, test_case in enumerate(test_cases):
            if i >= len(test_results):
                continue
                
            result = test_results[i]
            
            # Skip non-fraud tests
            if not test_case.fraud_patterns_tested:
                continue
            
            for pattern in test_case.fraud_patterns_tested:
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {
                        'total': 0,
                        'detected': 0,
                        'missed': 0
                    }
                
                pattern_stats[pattern]['total'] += 1
                
                if result.status == TestStatus.PASSED:
                    pattern_stats[pattern]['detected'] += 1
                else:
                    pattern_stats[pattern]['missed'] += 1
        
        # Calculate detection rates
        pattern_analysis = {}
        for pattern, stats in pattern_stats.items():
            detection_rate = (stats['detected'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            pattern_analysis[pattern] = {
                'test_cases': stats['total'],
                'detected': stats['detected'],
                'missed': stats['missed'],
                'detection_rate': round(detection_rate, 2),
                'status': '✅' if detection_rate >= 90 else '⚠️' if detection_rate >= 75 else '🔴'
            }
        
        return pattern_analysis
    
    def _create_detailed_results(self, test_results: List[Any]) -> List[Dict[str, Any]]:
        """Create detailed test results"""
        
        detailed = []
        
        for result in test_results:
            detailed.append({
                'test_case_id': result.test_case_id,
                'status': result.status.value,
                'execution_time_ms': result.execution_time_ms,
                'timestamp': result.timestamp,
                'errors': result.errors,
                'warnings': result.warnings,
                'actual_result_summary': self._summarize_actual_result(result.actual_result)
            })
        
        return detailed
    
    def _summarize_actual_result(self, actual_result: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize actual result for reporting"""
        
        summary = {}
        
        if 'fraud_alert_triggered' in actual_result:
            summary['alert_triggered'] = actual_result['fraud_alert_triggered']
        
        if 'risk_score' in actual_result:
            summary['risk_score'] = actual_result['risk_score']
        
        if 'action' in actual_result:
            summary['action'] = actual_result['action']
        
        return summary
    
    def _create_hallucination_report(self, hallucination_checks: List[Any]) -> Dict[str, Any]:
        """Create hallucination detection report"""
        
        if not hallucination_checks:
            return {
                'total_checks': 0,
                'issues_found': 0,
                'hallucination_rate': 0.0,
                'by_severity': {},
                'examples': []
            }
        
        # Calculate statistics
        total_hallucinations = sum(len(c.hallucinations_detected) for c in hallucination_checks)
        
        by_severity = {}
        by_type = {}
        examples = []
        
        for check in hallucination_checks:
            severity = check.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            for h in check.hallucinations_detected:
                h_type = h['type']
                by_type[h_type] = by_type.get(h_type, 0) + 1
                
                # Add examples (limit to 5)
                if len(examples) < 5:
                    examples.append({
                        'test_case_id': check.test_case_id,
                        'type': h['type'],
                        'description': h['description'],
                        'severity': h['severity']
                    })
        
        return {
            'total_checks': len(hallucination_checks),
            'issues_found': total_hallucinations,
            'hallucination_rate': round((total_hallucinations / len(hallucination_checks) * 100), 2),
            'by_severity': by_severity,
            'by_type': by_type,
            'examples': examples
        }
    
    def _create_risk_section(self, risk_assessment: Optional[Any]) -> Dict[str, Any]:
        """Create risk assessment section"""
        
        if not risk_assessment:
            return {'available': False}
        
        from fraud_risk_analyzer import FraudRiskAnalyzer
        
        analyzer = FraudRiskAnalyzer()
        risk_report = analyzer.generate_risk_report(risk_assessment)
        
        # Add visualization and available flag
        risk_report['available'] = True
        risk_report['visualization'] = analyzer._create_risk_visualization(risk_assessment)
        
        return risk_report
    
    def _create_recommendations(self, summary: Dict[str, Any], risk_assessment: Optional[Any]) -> List[Dict[str, Any]]:
        """Create actionable recommendations"""
        
        recommendations = []
        
        # Add risk-based recommendations
        if risk_assessment and risk_assessment.recommendations:
            for rec in risk_assessment.recommendations:
                recommendations.append({
                    'source': 'Risk Analysis',
                    'recommendation': rec,
                    'priority': 'HIGH' if '🔴' in rec or '🛑' in rec else 'MEDIUM' if '⚠️' in rec else 'LOW'
                })
        
        # Add accuracy-based recommendations
        accuracy = summary['accuracy_metrics']
        
        if accuracy['false_negative_rate'] > 5:
            recommendations.append({
                'source': 'Accuracy Analysis',
                'recommendation': f"False negative rate ({accuracy['false_negative_rate']}%) exceeds target. "
                                 "Review and retrain fraud detection models with recent fraud cases.",
                'priority': 'HIGH'
            })
        
        if accuracy['false_positive_rate'] > 10:
            recommendations.append({
                'source': 'Accuracy Analysis',
                'recommendation': f"False positive rate ({accuracy['false_positive_rate']}%) exceeds target. "
                                 "Optimize risk thresholds to reduce customer friction.",
                'priority': 'MEDIUM'
            })
        
        # Add performance recommendations
        perf = summary['performance_metrics']
        if perf['p99_response_time_ms'] > 5000:
            recommendations.append({
                'source': 'Performance Analysis',
                'recommendation': f"P99 response time ({perf['p99_response_time_ms']:.0f}ms) exceeds SLA. "
                                 "Optimize slow queries and implement caching.",
                'priority': 'MEDIUM'
            })
        
        return recommendations
    
    def _create_compliance_section(self, test_results: List[Any]) -> Dict[str, Any]:
        """Create compliance validation section"""
        from fraud_qa_agent import TestStatus
        
        compliance_tests = [
            r for r in test_results 
            if 'Compliance' in r.test_case_id or 'COMP' in r.test_case_id
        ]
        
        if not compliance_tests:
            return {'available': False}
        
        passed = sum(1 for r in compliance_tests if r.status == TestStatus.PASSED)
        failed = sum(1 for r in compliance_tests if r.status == TestStatus.FAILED)
        
        violations = []
        for result in compliance_tests:
            if result.status == TestStatus.FAILED:
                violations.extend(result.errors)
        
        return {
            'available': True,
            'total_tests': len(compliance_tests),
            'passed': passed,
            'failed': failed,
            'compliance_rate': round((passed / len(compliance_tests) * 100), 2),
            'violations': violations,
            'status': '✅ COMPLIANT' if failed == 0 else '🔴 VIOLATIONS DETECTED'
        }
    
    def _create_appendix(self, test_cases: List[Any], test_results: List[Any]) -> Dict[str, Any]:
        """Create appendix with additional data"""
        
        return {
            'total_test_cases': len(test_cases),
            'total_test_results': len(test_results),
            'test_categories': self._categorize_tests(test_cases),
            'execution_timeline': self._create_timeline(test_results)
        }
    
    def _categorize_tests(self, test_cases: List[Any]) -> Dict[str, int]:
        """Categorize test cases"""
        
        categories = {}
        for tc in test_cases:
            category = tc.category
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _create_timeline(self, test_results: List[Any]) -> List[Dict[str, Any]]:
        """Create execution timeline"""
        
        timeline = []
        for result in test_results[:10]:  # First 10 for brevity
            timeline.append({
                'test_id': result.test_case_id,
                'timestamp': result.timestamp,
                'duration_ms': result.execution_time_ms,
                'status': result.status.value
            })
        
        return timeline
    
    def export_report_json(self, report: Dict[str, Any], filepath: str) -> None:
        """Export report as JSON"""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Report exported to {filepath}")
    
    def export_report_html(self, report: Dict[str, Any], filepath: str) -> None:
        """Export report as HTML"""
        
        html_content = self._generate_html(report)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report exported to {filepath}")
    
    def _generate_html(self, report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        
        # Simple HTML template
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report['metadata']['report_title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e3f2fd; border-radius: 5px; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
        .status-good {{ color: #4CAF50; }}
        .status-warning {{ color: #FF9800; }}
        .status-critical {{ color: #F44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .dashboard {{ background: #263238; color: #fff; padding: 20px; border-radius: 5px; font-family: monospace; white-space: pre; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report['metadata']['report_title']}</h1>
        <p>Generated: {report['metadata']['generated_at']}</p>
        
        <h2>Executive Summary</h2>
        <div class="metric">
            <div class="metric-label">Overall Status</div>
            <div class="metric-value">{report['executive_summary']['overall_status']}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Deployment</div>
            <div class="metric-value">{report['executive_summary']['deployment_recommendation']}</div>
        </div>
        
        <h2>Test Execution Dashboard</h2>
        <div class="dashboard">{report['test_execution_dashboard']}</div>
        
        <h2>Key Insights</h2>
        <ul>
"""
        
        for insight in report['executive_summary']['top_insights']:
            html += f"            <li>{insight}</li>\n"
        
        html += """
        </ul>
        
        <h2>Fraud Pattern Analysis</h2>
        <table>
            <tr>
                <th>Pattern</th>
                <th>Test Cases</th>
                <th>Detected</th>
                <th>Missed</th>
                <th>Detection Rate</th>
                <th>Status</th>
            </tr>
"""
        
        for pattern, stats in report['fraud_pattern_analysis'].items():
            html += f"""
            <tr>
                <td>{pattern}</td>
                <td>{stats['test_cases']}</td>
                <td>{stats['detected']}</td>
                <td>{stats['missed']}</td>
                <td>{stats['detection_rate']}%</td>
                <td>{stats['status']}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        return html