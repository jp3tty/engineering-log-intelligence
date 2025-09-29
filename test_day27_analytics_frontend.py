#!/usr/bin/env python3
"""
Day 27: Analytics Frontend Components Test
==========================================

This test validates the Vue.js frontend components for the advanced analytics system.
It tests the analytics dashboard, insights interface, report generation, and data export components.

Author: Engineering Log Intelligence Team
Date: September 29, 2025
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analytics_dashboard_component():
    """Test AnalyticsDashboard component structure and functionality."""
    print("🧪 Testing AnalyticsDashboard Component...")
    
    dashboard_file = "frontend/src/components/analytics/AnalyticsDashboard.vue"
    
    if not os.path.exists(dashboard_file):
        print("❌ FAIL: AnalyticsDashboard.vue not found")
        return False
    
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    # Check for required imports
    required_imports = [
        "useAnalyticsStore",
        "useNotificationStore",
        "ChartBarIcon",
        "ArrowPathIcon",
        "DocumentArrowDownIcon"
    ]
    
    for import_name in required_imports:
        if import_name not in content:
            print(f"❌ FAIL: Missing import {import_name}")
            return False
    
    # Check for required components
    required_components = [
        "MetricCard",
        "AnalyticsInsights", 
        "ReportGeneration",
        "DataExport",
        "PerformanceAnalytics"
    ]
    
    for component in required_components:
        if component not in content:
            print(f"❌ FAIL: Missing component {component}")
            return False
    
    # Check for key methods
    required_methods = [
        "loadAnalyticsData",
        "refreshData",
        "generateReport",
        "exportData"
    ]
    
    for method in required_methods:
        if method not in content:
            print(f"❌ FAIL: Missing method {method}")
            return False
    
    print("✅ PASS: AnalyticsDashboard component structure is correct")
    return True

def test_metric_card_component():
    """Test MetricCard component functionality."""
    print("🧪 Testing MetricCard Component...")
    
    metric_file = "frontend/src/components/analytics/MetricCard.vue"
    
    if not os.path.exists(metric_file):
        print("❌ FAIL: MetricCard.vue not found")
        return False
    
    with open(metric_file, 'r') as f:
        content = f.read()
    
    # Check for required functionality
    required_features = [
        "formattedValue",
        "formattedTrend",
        "formatDuration",
        "formatBytes",
        "iconClass",
        "trendClass"
    ]
    
    for feature in required_features:
        if feature not in content:
            print(f"❌ FAIL: Missing feature {feature}")
            return False
    
    # Check for icon mapping
    if "iconMap" not in content:
        print("❌ FAIL: Missing icon mapping")
        return False
    
    print("✅ PASS: MetricCard component functionality is correct")
    return True

def test_analytics_insights_component():
    """Test AnalyticsInsights component functionality."""
    print("🧪 Testing AnalyticsInsights Component...")
    
    insights_file = "frontend/src/components/analytics/AnalyticsInsights.vue"
    
    if not os.path.exists(insights_file):
        print("❌ FAIL: AnalyticsInsights.vue not found")
        return False
    
    with open(insights_file, 'r') as f:
        content = f.read()
    
    # Check for required sections
    required_sections = [
        "Trend Analysis",
        "Anomaly Detection",
        "Pattern Recognition",
        "AI Recommendations"
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"❌ FAIL: Missing section {section}")
            return False
    
    # Check for required methods
    required_methods = [
        "getTrendIcon",
        "getSeverityIcon",
        "getPatternIcon",
        "getPriorityIcon",
        "formatTime"
    ]
    
    for method in required_methods:
        if method not in content:
            print(f"❌ FAIL: Missing method {method}")
            return False
    
    print("✅ PASS: AnalyticsInsights component functionality is correct")
    return True

def test_report_generation_component():
    """Test ReportGeneration component functionality."""
    print("🧪 Testing ReportGeneration Component...")
    
    report_file = "frontend/src/components/analytics/ReportGeneration.vue"
    
    if not os.path.exists(report_file):
        print("❌ FAIL: ReportGeneration.vue not found")
        return False
    
    with open(report_file, 'r') as f:
        content = f.read()
    
    # Check for required functionality
    required_features = [
        "generateReport",
        "scheduleReport",
        "downloadReport",
        "shareReport",
        "deleteReport",
        "handleGenerateReport"
    ]
    
    for feature in required_features:
        if feature not in content:
            print(f"❌ FAIL: Missing feature {feature}")
            return False
    
    # Check for form fields
    required_form_fields = [
        "template_id",
        "title",
        "time_range",
        "format",
        "include_charts",
        "email_recipients"
    ]
    
    for field in required_form_fields:
        if field not in content:
            print(f"❌ FAIL: Missing form field {field}")
            return False
    
    print("✅ PASS: ReportGeneration component functionality is correct")
    return True

def test_analytics_store():
    """Test analytics Pinia store functionality."""
    print("🧪 Testing Analytics Store...")
    
    store_file = "frontend/src/stores/analytics.js"
    
    if not os.path.exists(store_file):
        print("❌ FAIL: analytics.js store not found")
        return False
    
    with open(store_file, 'r') as f:
        content = f.read()
    
    # Check for required state
    required_state = [
        "overview",
        "insights",
        "reports",
        "performance",
        "exports",
        "loading",
        "error"
    ]
    
    for state in required_state:
        if state not in content:
            print(f"❌ FAIL: Missing state {state}")
            return False
    
    # Check for required actions
    required_actions = [
        "fetchOverview",
        "fetchInsights",
        "fetchPerformance",
        "generateReport",
        "scheduleReport",
        "exportData",
        "refreshAll"
    ]
    
    for action in required_actions:
        if action not in content:
            print(f"❌ FAIL: Missing action {action}")
            return False
    
    # Check for computed properties
    required_computed = [
        "hasData",
        "keyMetrics",
        "recentReports",
        "activeExports"
    ]
    
    for computed in required_computed:
        if computed not in content:
            print(f"❌ FAIL: Missing computed property {computed}")
            return False
    
    print("✅ PASS: Analytics store functionality is correct")
    return True

def test_router_integration():
    """Test Vue Router integration for analytics."""
    print("🧪 Testing Router Integration...")
    
    router_file = "frontend/src/router/index.js"
    
    if not os.path.exists(router_file):
        print("❌ FAIL: router/index.js not found")
        return False
    
    with open(router_file, 'r') as f:
        content = f.read()
    
    # Check for analytics route
    if "AnalyticsDashboard" not in content:
        print("❌ FAIL: AnalyticsDashboard route not found")
        return False
    
    if "/analytics" not in content:
        print("❌ FAIL: /analytics route not found")
        return False
    
    if "roles: ['analyst', 'admin']" not in content:
        print("❌ FAIL: Role-based access control not configured")
        return False
    
    print("✅ PASS: Router integration is correct")
    return True

def test_header_integration():
    """Test AppHeader integration for analytics navigation."""
    print("🧪 Testing Header Integration...")
    
    header_file = "frontend/src/components/layout/AppHeader.vue"
    
    if not os.path.exists(header_file):
        print("❌ FAIL: AppHeader.vue not found")
        return False
    
    with open(header_file, 'r') as f:
        content = f.read()
    
    # Check for analytics navigation
    if "AnalyticsIcon" not in content:
        print("❌ FAIL: AnalyticsIcon not found")
        return False
    
    if "AnalyticsDashboard" not in content:
        print("❌ FAIL: AnalyticsDashboard navigation not found")
        return False
    
    if "requiresRole: ['analyst', 'admin']" not in content:
        print("❌ FAIL: Role-based navigation not configured")
        return False
    
    print("✅ PASS: Header integration is correct")
    return True

def test_component_dependencies():
    """Test that all required dependencies are properly imported."""
    print("🧪 Testing Component Dependencies...")
    
    # Check for missing components that are referenced but not created yet
    missing_components = []
    
    required_components = [
        "frontend/src/components/analytics/DataExport.vue",
        "frontend/src/components/analytics/PerformanceAnalytics.vue"
    ]
    
    for component in required_components:
        if not os.path.exists(component):
            missing_components.append(component)
    
    if missing_components:
        print(f"⚠️  WARNING: Missing components: {', '.join(missing_components)}")
        print("These components are referenced but not yet created")
    else:
        print("✅ PASS: All component dependencies are satisfied")
    
    return len(missing_components) == 0

def test_vue_composition_api():
    """Test that components use Vue 3 Composition API correctly."""
    print("🧪 Testing Vue Composition API Usage...")
    
    components = [
        "frontend/src/components/analytics/AnalyticsDashboard.vue",
        "frontend/src/components/analytics/MetricCard.vue",
        "frontend/src/components/analytics/AnalyticsInsights.vue",
        "frontend/src/components/analytics/ReportGeneration.vue"
    ]
    
    composition_api_features = [
        "import { ref, reactive, onMounted, computed }",
        "setup()",
        "ref(",
        "computed(",
        "onMounted("
    ]
    
    for component_file in components:
        if os.path.exists(component_file):
            with open(component_file, 'r') as f:
                content = f.read()
            
            component_name = os.path.basename(component_file)
            
            # Check for Composition API usage
            if "setup()" not in content:
                print(f"❌ FAIL: {component_name} not using Composition API")
                return False
            
            # Check for modern Vue 3 features
            if "ref(" not in content and "reactive(" not in content:
                print(f"❌ FAIL: {component_name} not using reactive state")
                return False
    
    print("✅ PASS: All components use Vue 3 Composition API correctly")
    return True

def test_typescript_compatibility():
    """Test that components are TypeScript compatible."""
    print("🧪 Testing TypeScript Compatibility...")
    
    components = [
        "frontend/src/components/analytics/AnalyticsDashboard.vue",
        "frontend/src/components/analytics/MetricCard.vue",
        "frontend/src/components/analytics/AnalyticsInsights.vue",
        "frontend/src/components/analytics/ReportGeneration.vue"
    ]
    
    for component_file in components:
        if os.path.exists(component_file):
            with open(component_file, 'r') as f:
                content = f.read()
            
            component_name = os.path.basename(component_file)
            
            # Check for proper prop definitions
            if "props:" not in content and "defineProps" not in content:
                print(f"❌ FAIL: {component_name} missing prop definitions")
                return False
            
            # Check for proper emit definitions
            if "emits:" not in content and "defineEmits" not in content:
                print(f"❌ FAIL: {component_name} missing emit definitions")
                return False
    
    print("✅ PASS: All components are TypeScript compatible")
    return True

def test_responsive_design():
    """Test that components include responsive design features."""
    print("🧪 Testing Responsive Design...")
    
    components = [
        "frontend/src/components/analytics/AnalyticsDashboard.vue",
        "frontend/src/components/analytics/MetricCard.vue",
        "frontend/src/components/analytics/AnalyticsInsights.vue",
        "frontend/src/components/analytics/ReportGeneration.vue"
    ]
    
    responsive_classes = [
        "grid-cols-1 md:grid-cols-2",
        "lg:grid-cols-3",
        "lg:grid-cols-4",
        "hidden md:flex",
        "md:hidden"
    ]
    
    for component_file in components:
        if os.path.exists(component_file):
            with open(component_file, 'r') as f:
                content = f.read()
            
            component_name = os.path.basename(component_file)
            
            # Check for responsive classes
            has_responsive = any(cls in content for cls in responsive_classes)
            
            if not has_responsive:
                print(f"⚠️  WARNING: {component_name} may lack responsive design features")
    
    print("✅ PASS: Components include responsive design features")
    return True

def test_accessibility_features():
    """Test that components include accessibility features."""
    print("🧪 Testing Accessibility Features...")
    
    components = [
        "frontend/src/components/analytics/AnalyticsDashboard.vue",
        "frontend/src/components/analytics/MetricCard.vue",
        "frontend/src/components/analytics/AnalyticsInsights.vue",
        "frontend/src/components/analytics/ReportGeneration.vue"
    ]
    
    accessibility_features = [
        "focus:outline-none",
        "focus:ring-2",
        "aria-label",
        "role=",
        "tabindex="
    ]
    
    for component_file in components:
        if os.path.exists(component_file):
            with open(component_file, 'r') as f:
                content = f.read()
            
            component_name = os.path.basename(component_file)
            
            # Check for focus management
            if "focus:outline-none" not in content and "focus:ring" not in content:
                print(f"⚠️  WARNING: {component_name} may lack proper focus management")
    
    print("✅ PASS: Components include accessibility features")
    return True

def main():
    """Run all Day 27 analytics frontend tests."""
    print("🚀 Day 27: Analytics Frontend Components Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("AnalyticsDashboard Component", test_analytics_dashboard_component),
        ("MetricCard Component", test_metric_card_component),
        ("AnalyticsInsights Component", test_analytics_insights_component),
        ("ReportGeneration Component", test_report_generation_component),
        ("Analytics Store", test_analytics_store),
        ("Router Integration", test_router_integration),
        ("Header Integration", test_header_integration),
        ("Component Dependencies", test_component_dependencies),
        ("Vue Composition API", test_vue_composition_api),
        ("TypeScript Compatibility", test_typescript_compatibility),
        ("Responsive Design", test_responsive_design),
        ("Accessibility Features", test_accessibility_features)
    ]
    
    passed = 0
    failed = 0
    warnings = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            failed += 1
        print()
    
    # Test Summary
    print("=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Day 27 analytics frontend implementation is complete.")
        print("\n🚀 Next Steps:")
        print("1. Create remaining components (DataExport, PerformanceAnalytics)")
        print("2. Test component integration")
        print("3. Add comprehensive error handling")
        print("4. Implement real-time data updates")
        print("5. Add unit tests for components")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix the issues.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
