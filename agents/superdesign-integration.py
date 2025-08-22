#!/usr/bin/env python3
"""
Superdesign Integration for Essential Agents
Integrates code-validator, accessibility-auditor, performance-analyzer, and asset-manager
into the superdesign workflow
"""

import json
import os
import sys
from typing import Dict, Any, List

# Import the agent modules
import importlib.util

def load_agent_module(module_name, file_name):
    """Dynamically load agent modules"""
    module_path = os.path.join(os.path.dirname(__file__), file_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load agent modules
code_validator_module = load_agent_module("code_validator", "code-validator.py")
accessibility_auditor_module = load_agent_module("accessibility_auditor", "accessibility-auditor.py")
performance_analyzer_module = load_agent_module("performance_analyzer", "performance-analyzer.py")
asset_manager_module = load_agent_module("asset_manager", "asset-manager.py")

CodeValidator = code_validator_module.CodeValidator
AccessibilityAuditor = accessibility_auditor_module.AccessibilityAuditor
PerformanceAnalyzer = performance_analyzer_module.PerformanceAnalyzer
AssetManager = asset_manager_module.AssetManager

class SuperdesignQualityAssurance:
    def __init__(self):
        self.code_validator = CodeValidator()
        self.accessibility_auditor = AccessibilityAuditor()
        self.performance_analyzer = PerformanceAnalyzer()
        self.asset_manager = AssetManager()
    
    def validate_design_file(self, file_path: str) -> Dict[str, Any]:
        """Run all quality checks on a design file"""
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f"File not found: {file_path}",
                'results': {}
            }
        
        # Run all agents
        results = {}
        
        print(f"🔍 Running quality assurance on {os.path.basename(file_path)}...")
        
        # 1. Code Validation
        print("  ✅ Validating code syntax and structure...")
        results['code_validation'] = self.code_validator.validate_html_file(file_path)
        
        # 2. Accessibility Audit
        print("  ♿ Auditing accessibility compliance...")
        results['accessibility_audit'] = self.accessibility_auditor.audit_html_file(file_path)
        
        # 3. Performance Analysis
        print("  ⚡ Analyzing performance optimizations...")
        results['performance_analysis'] = self.performance_analyzer.analyze_html_file(file_path)
        
        # 4. Asset Management
        print("  🖼️  Managing and validating assets...")
        results['asset_management'] = self.asset_manager.manage_assets_in_file(file_path)
        
        # Generate overall report
        overall_report = self._generate_overall_report(results, file_path)
        
        return {
            'success': True,
            'file_path': file_path,
            'results': results,
            'overall_report': overall_report
        }
    
    def _generate_overall_report(self, results: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Generate an overall quality report"""
        # Collect all issues
        total_errors = 0
        total_warnings = 0
        total_suggestions = 0
        
        all_errors = []
        all_warnings = []
        all_suggestions = []
        
        for agent_name, result in results.items():
            if result.get('success', False):
                errors = result.get('errors', [])
                warnings = result.get('warnings', [])
                suggestions = result.get('suggestions', [])
                
                total_errors += len(errors)
                total_warnings += len(warnings)
                total_suggestions += len(suggestions)
                
                # Prefix with agent name for clarity
                all_errors.extend([f"[{agent_name}] {error}" for error in errors])
                all_warnings.extend([f"[{agent_name}] {warning}" for warning in warnings])
                all_suggestions.extend([f"[{agent_name}] {suggestion}" for suggestion in suggestions])
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(results)
        
        # Determine readiness for deployment
        ready_for_deployment = total_errors == 0 and total_warnings <= 3
        
        # Generate recommendations
        recommendations = self._generate_recommendations(results)
        
        return {
            'quality_score': quality_score,
            'ready_for_deployment': ready_for_deployment,
            'summary': {
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'total_suggestions': total_suggestions,
                'total_issues': total_errors + total_warnings
            },
            'all_errors': all_errors,
            'all_warnings': all_warnings,
            'all_suggestions': all_suggestions,
            'recommendations': recommendations,
            'agent_scores': {
                'code_quality': 100 - (len(results.get('code_validation', {}).get('errors', [])) * 20),
                'accessibility': results.get('accessibility_audit', {}).get('accessibility_score', 0),
                'performance': results.get('performance_analysis', {}).get('performance_score', 0),
                'asset_management': 100 - (len(results.get('asset_management', {}).get('errors', [])) * 25)
            }
        }
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall quality score (0-100)"""
        scores = []
        
        # Code validation score
        code_result = results.get('code_validation', {})
        if code_result.get('success'):
            code_score = 100 - (len(code_result.get('errors', [])) * 20) - (len(code_result.get('warnings', [])) * 10)
            scores.append(max(0, code_score))
        
        # Accessibility score
        accessibility_result = results.get('accessibility_audit', {})
        if accessibility_result.get('accessibility_score'):
            scores.append(accessibility_result['accessibility_score'])
        
        # Performance score
        performance_result = results.get('performance_analysis', {})
        if performance_result.get('performance_score'):
            scores.append(performance_result['performance_score'])
        
        # Asset management score
        asset_result = results.get('asset_management', {})
        if asset_result.get('success') is not False:
            asset_score = 100 - (len(asset_result.get('errors', [])) * 25) - (len(asset_result.get('warnings', [])) * 10)
            scores.append(max(0, asset_score))
        
        return int(sum(scores) / len(scores)) if scores else 0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # High priority - errors that must be fixed
        code_errors = results.get('code_validation', {}).get('errors', [])
        if code_errors:
            recommendations.append("🚨 HIGH PRIORITY: Fix code validation errors before deployment")
        
        accessibility_errors = results.get('accessibility_audit', {}).get('errors', [])
        if accessibility_errors:
            recommendations.append("🚨 HIGH PRIORITY: Fix accessibility errors for compliance")
        
        asset_errors = results.get('asset_management', {}).get('errors', [])
        if asset_errors:
            recommendations.append("🚨 HIGH PRIORITY: Fix broken asset URLs")
        
        # Medium priority - performance and warnings
        performance_score = results.get('performance_analysis', {}).get('performance_score', 100)
        if performance_score < 70:
            recommendations.append("⚠️ MEDIUM PRIORITY: Optimize performance for better user experience")
        
        accessibility_score = results.get('accessibility_audit', {}).get('accessibility_score', 100)
        if accessibility_score < 80:
            recommendations.append("⚠️ MEDIUM PRIORITY: Improve accessibility for better compliance")
        
        # Low priority - suggestions for enhancement
        total_suggestions = sum(len(result.get('suggestions', [])) for result in results.values())
        if total_suggestions > 5:
            recommendations.append("💡 LOW PRIORITY: Consider implementing suggestions for optimization")
        
        if not recommendations:
            recommendations.append("✅ Great job! No major issues found. Ready for deployment.")
        
        return recommendations
    
    def generate_report_html(self, qa_result: Dict[str, Any]) -> str:
        """Generate an HTML report of the quality assessment"""
        if not qa_result.get('success'):
            return f"<html><body><h1>Error</h1><p>{qa_result.get('error', 'Unknown error')}</p></body></html>"
        
        overall = qa_result['overall_report']
        quality_score = overall['quality_score']
        
        # Determine color based on score
        if quality_score >= 90:
            score_color = "#22c55e"  # green
        elif quality_score >= 70:
            score_color = "#f59e0b"  # yellow
        else:
            score_color = "#ef4444"  # red
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Superdesign Quality Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; color: {score_color}; }}
        .status {{ font-size: 18px; color: #64748b; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-top: 0; color: #1e293b; }}
        .error {{ color: #dc2626; }}
        .warning {{ color: #d97706; }}
        .suggestion {{ color: #2563eb; }}
        .recommendation {{ padding: 10px; margin: 5px 0; border-radius: 8px; background: #f1f5f9; }}
        .high {{ border-left: 4px solid #dc2626; }}
        .medium {{ border-left: 4px solid #d97706; }}
        .low {{ border-left: 4px solid #2563eb; }}
        .success {{ border-left: 4px solid #16a34a; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Superdesign Quality Report</h1>
            <p><strong>File:</strong> {os.path.basename(qa_result['file_path'])}</p>
            <div class="score">{quality_score}/100</div>
            <div class="status">{'✅ Ready for deployment' if overall['ready_for_deployment'] else '⚠️ Needs attention before deployment'}</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Overall Summary</h3>
                <p><strong>Errors:</strong> <span class="error">{overall['summary']['total_errors']}</span></p>
                <p><strong>Warnings:</strong> <span class="warning">{overall['summary']['total_warnings']}</span></p>
                <p><strong>Suggestions:</strong> <span class="suggestion">{overall['summary']['total_suggestions']}</span></p>
            </div>
            
            <div class="card">
                <h3>🎯 Agent Scores</h3>
                <p><strong>Code Quality:</strong> {overall['agent_scores']['code_quality']}/100</p>
                <p><strong>Accessibility:</strong> {overall['agent_scores']['accessibility']}/100</p>
                <p><strong>Performance:</strong> {overall['agent_scores']['performance']}/100</p>
                <p><strong>Asset Management:</strong> {overall['agent_scores']['asset_management']}/100</p>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h3>💡 Recommendations</h3>
            {self._format_recommendations_html(overall['recommendations'])}
        </div>
        
        {self._format_issues_html(overall)}
        
    </div>
</body>
</html>
        """
        
        return html
    
    def _format_recommendations_html(self, recommendations: List[str]) -> str:
        """Format recommendations as HTML"""
        html = ""
        for rec in recommendations:
            css_class = "success"
            if "HIGH PRIORITY" in rec:
                css_class = "high"
            elif "MEDIUM PRIORITY" in rec:
                css_class = "medium"
            elif "LOW PRIORITY" in rec:
                css_class = "low"
            
            html += f'<div class="recommendation {css_class}">{rec}</div>'
        
        return html
    
    def _format_issues_html(self, overall: Dict[str, Any]) -> str:
        """Format issues as HTML"""
        html = ""
        
        if overall['all_errors']:
            html += '<div class="card" style="margin-top: 20px;"><h3>❌ Errors</h3>'
            for error in overall['all_errors']:
                html += f'<p class="error">• {error}</p>'
            html += '</div>'
        
        if overall['all_warnings']:
            html += '<div class="card" style="margin-top: 20px;"><h3>⚠️ Warnings</h3>'
            for warning in overall['all_warnings']:
                html += f'<p class="warning">• {warning}</p>'
            html += '</div>'
        
        if overall['all_suggestions']:
            html += '<div class="card" style="margin-top: 20px;"><h3>💡 Suggestions</h3>'
            for suggestion in overall['all_suggestions'][:10]:  # Limit to first 10
                html += f'<p class="suggestion">• {suggestion}</p>'
            if len(overall['all_suggestions']) > 10:
                html += f'<p class="suggestion">... and {len(overall["all_suggestions"]) - 10} more suggestions</p>'
            html += '</div>'
        
        return html

def main():
    """Main function for CLI usage"""
    if len(sys.argv) != 2:
        print("Usage: python superdesign-integration.py <html_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    qa = SuperdesignQualityAssurance()
    result = qa.validate_design_file(file_path)
    
    if result['success']:
        print("\n" + "="*60)
        print("SUPERDESIGN QUALITY ASSURANCE REPORT")
        print("="*60)
        
        overall = result['overall_report']
        print(f"📁 File: {os.path.basename(file_path)}")
        print(f"📊 Quality Score: {overall['quality_score']}/100")
        print(f"🚀 Ready for deployment: {'Yes' if overall['ready_for_deployment'] else 'No'}")
        
        print(f"\n📋 Summary:")
        print(f"   Errors: {overall['summary']['total_errors']}")
        print(f"   Warnings: {overall['summary']['total_warnings']}")
        print(f"   Suggestions: {overall['summary']['total_suggestions']}")
        
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(overall['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
        
        # Generate HTML report
        report_path = file_path.replace('.html', '_quality_report.html')
        html_report = qa.generate_report_html(result)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        # Exit code based on quality
        exit_code = 0 if overall['ready_for_deployment'] else 1
        sys.exit(exit_code)
    else:
        print(f"❌ Error: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()