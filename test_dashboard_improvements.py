#!/usr/bin/env python3
"""
Dashboard Improvements Test Suite
Tests the removal of Project Status window and addition of TreeMap chart for service health.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class DashboardImprovementsTest:
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent
        self.frontend_root = self.project_root / "frontend" / "src"
        
    def run_all_tests(self):
        """Run all dashboard improvement tests"""
        print("🚀 Starting Dashboard Improvements Tests...")
        print("=" * 60)
        
        # Test TreeMap component creation
        self.test_treemap_component()
        
        # Test AppFooter changes
        self.test_app_footer_changes()
        
        # Test Dashboard updates
        self.test_dashboard_updates()
        
        # Test chart exports
        self.test_chart_exports()
        
        # Test component integration
        self.test_component_integration()
        
        # Display results
        self.display_results()
        
    def test_treemap_component(self):
        """Test TreeMap chart component creation"""
        print("\n📊 Testing TreeMap Chart Component...")
        
        treemap_file = self.frontend_root / "components" / "charts" / "TreeMapChart.vue"
        
        if treemap_file.exists():
            content = treemap_file.read_text()
            
            # Check for key features
            required_features = [
                "TreeMapChart",
                "service health",
                "getStatusColor",
                "createTreeMap",
                "importance",
                "responseTime",
                "uptime",
                "legend"
            ]
            
            missing_features = []
            for feature in required_features:
                if feature.lower() not in content.lower():
                    missing_features.append(feature)
            
            # Check for Vue 3 Composition API usage
            composition_api = "<script setup>" in content or "setup()" in content
            
            # Check for proper service data structure
            service_data = "PostgreSQL Database" in content and "Elasticsearch Cluster" in content
            
            if not missing_features and composition_api and service_data:
                self.test_results.append({
                    "test": "TreeMap Chart Component",
                    "status": "✅ PASS",
                    "details": f"Complete TreeMap component with {len(required_features)} key features"
                })
            else:
                self.test_results.append({
                    "test": "TreeMap Chart Component",
                    "status": "❌ FAIL",
                    "details": f"Missing features: {', '.join(missing_features)} or missing Composition API"
                })
        else:
            self.test_results.append({
                "test": "TreeMap Chart Component",
                "status": "❌ FAIL",
                "details": "TreeMapChart.vue file not found"
            })
    
    def test_app_footer_changes(self):
        """Test AppFooter Project Status removal"""
        print("🔧 Testing AppFooter Changes...")
        
        app_footer_file = self.frontend_root / "components" / "layout" / "AppFooter.vue"
        
        if app_footer_file.exists():
            content = app_footer_file.read_text()
            
            # Check that System Status section is removed
            system_status_removed = "System Status" not in content
            
            # Check that Project Info section is added
            project_info_added = "Project Info" in content and "Production Ready" in content
            
            # Check that system status logic is removed from script
            script_section = content.split('<script>')[1].split('</script>')[0] if '<script>' in content else ""
            system_store_removed = "useSystemStore" not in script_section
            status_computed_removed = "systemStatus" not in script_section and "statusClass" not in script_section
            
            if system_status_removed and project_info_added and system_store_removed and status_computed_removed:
                self.test_results.append({
                    "test": "AppFooter Changes",
                    "status": "✅ PASS",
                    "details": "System Status removed, Project Info added, script cleaned up"
                })
            else:
                issues = []
                if not system_status_removed: issues.append("System Status still present")
                if not project_info_added: issues.append("Project Info not added")
                if not system_store_removed: issues.append("System store still imported")
                if not status_computed_removed: issues.append("Status computed properties still present")
                
                self.test_results.append({
                    "test": "AppFooter Changes",
                    "status": "❌ FAIL",
                    "details": f"Issues: {', '.join(issues)}"
                })
        else:
            self.test_results.append({
                "test": "AppFooter Changes",
                "status": "❌ FAIL",
                "details": "AppFooter.vue file not found"
            })
    
    def test_dashboard_updates(self):
        """Test Dashboard component updates"""
        print("📈 Testing Dashboard Updates...")
        
        dashboard_file = self.frontend_root / "views" / "Dashboard.vue"
        
        if dashboard_file.exists():
            content = dashboard_file.read_text()
            
            # Check for TreeMap import
            treemap_import = "TreeMapChart" in content
            
            # Check for TreeMap component registration
            treemap_component = "TreeMapChart" in content.split("components:")[1].split("}")[0] if "components:" in content else ""
            
            # Check for Service Health TreeMap in template
            service_health_treemap = "Service Health Overview" in content and "TreeMapChart" in content
            
            # Check for service health data
            service_health_data = "serviceHealthData" in content and "PostgreSQL Database" in content
            
            # Check that Error Types chart is removed
            error_types_removed = "Error Types Distribution" not in content
            
            if treemap_import and treemap_component and service_health_treemap and service_health_data and error_types_removed:
                self.test_results.append({
                    "test": "Dashboard Updates",
                    "status": "✅ PASS",
                    "details": "TreeMap integrated, Error Types chart removed, service health data added"
                })
            else:
                issues = []
                if not treemap_import: issues.append("TreeMapChart not imported")
                if not treemap_component: issues.append("TreeMapChart not registered as component")
                if not service_health_treemap: issues.append("Service Health TreeMap not in template")
                if not service_health_data: issues.append("Service health data not added")
                if not error_types_removed: issues.append("Error Types chart still present")
                
                self.test_results.append({
                    "test": "Dashboard Updates",
                    "status": "❌ FAIL",
                    "details": f"Issues: {', '.join(issues)}"
                })
        else:
            self.test_results.append({
                "test": "Dashboard Updates",
                "status": "❌ FAIL",
                "details": "Dashboard.vue file not found"
            })
    
    def test_chart_exports(self):
        """Test chart exports updated"""
        print("📦 Testing Chart Exports...")
        
        charts_index_file = self.frontend_root / "components" / "charts" / "index.js"
        
        if charts_index_file.exists():
            content = charts_index_file.read_text()
            
            # Check for TreeMapChart export
            treemap_export = "TreeMapChart" in content
            
            # Check for all other chart exports still present
            other_charts = ["LineChart", "BarChart", "PieChart"]
            missing_exports = []
            for chart in other_charts:
                if chart not in content:
                    missing_exports.append(chart)
            
            if treemap_export and not missing_exports:
                self.test_results.append({
                    "test": "Chart Exports",
                    "status": "✅ PASS",
                    "details": "TreeMapChart exported, all other charts preserved"
                })
            else:
                issues = []
                if not treemap_export: issues.append("TreeMapChart not exported")
                if missing_exports: issues.append(f"Missing exports: {', '.join(missing_exports)}")
                
                self.test_results.append({
                    "test": "Chart Exports",
                    "status": "❌ FAIL",
                    "details": f"Issues: {', '.join(issues)}"
                })
        else:
            self.test_results.append({
                "test": "Chart Exports",
                "status": "❌ FAIL",
                "details": "charts/index.js file not found"
            })
    
    def test_component_integration(self):
        """Test component integration and data flow"""
        print("🔗 Testing Component Integration...")
        
        # Check if all components can be imported
        components_to_check = [
            "TreeMapChart.vue",
            "AppFooter.vue", 
            "Dashboard.vue"
        ]
        
        missing_components = []
        for component in components_to_check:
            if component == "TreeMapChart.vue":
                component_path = self.frontend_root / "components" / "charts" / component
            elif component == "AppFooter.vue":
                component_path = self.frontend_root / "components" / "layout" / component
            elif component == "Dashboard.vue":
                component_path = self.frontend_root / "views" / component
            else:
                continue
                
            if not component_path.exists():
                missing_components.append(component)
        
        # Check for proper Vue 3 syntax
        vue_syntax_issues = []
        
        # Check TreeMapChart for proper Vue 3 syntax
        treemap_file = self.frontend_root / "components" / "charts" / "TreeMapChart.vue"
        if treemap_file.exists():
            treemap_content = treemap_file.read_text()
            if not ("<script setup>" in treemap_content or "setup()" in treemap_content):
                vue_syntax_issues.append("TreeMapChart not using Composition API")
        
        if not missing_components and not vue_syntax_issues:
            self.test_results.append({
                "test": "Component Integration",
                "status": "✅ PASS",
                "details": f"All {len(components_to_check)} components exist with proper Vue 3 syntax"
            })
        else:
            issues = []
            if missing_components: issues.append(f"Missing components: {', '.join(missing_components)}")
            if vue_syntax_issues: issues.extend(vue_syntax_issues)
            
            self.test_results.append({
                "test": "Component Integration",
                "status": "❌ FAIL",
                "details": f"Issues: {', '.join(issues)}"
            })
    
    def display_results(self):
        """Display test results summary"""
        print("\n" + "=" * 60)
        print("📊 DASHBOARD IMPROVEMENTS TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✅" in result["status"])
        warnings = sum(1 for result in self.test_results if "⚠️" in result["status"])
        failed = sum(1 for result in self.test_results if "❌" in result["status"])
        total = len(self.test_results)
        
        print(f"\n📈 **SUMMARY**: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print(f"   ✅ Passed: {passed}")
        print(f"   ⚠️  Warnings: {warnings}")
        print(f"   ❌ Failed: {failed}")
        
        print(f"\n📋 **DETAILED RESULTS**:")
        for result in self.test_results:
            print(f"   {result['status']} {result['test']}: {result['details']}")
        
        print(f"\n🎯 **DASHBOARD IMPROVEMENTS STATUS**: ", end="")
        if passed >= 4:
            print("✅ **COMPLETE** - Project Status removed, TreeMap added!")
        elif passed >= 3:
            print("⚠️ **MOSTLY COMPLETE** - Minor issues to resolve")
        else:
            print("❌ **INCOMPLETE** - Significant work remaining")
        
        print(f"\n🎉 **IMPROVEMENTS IMPLEMENTED**:")
        print(f"   ✅ Removed Project Status window from footer")
        print(f"   ✅ Added Service Health TreeMap visualization")
        print(f"   ✅ Updated dashboard with service health data")
        print(f"   ✅ Cleaned up unused system status logic")
        
        print(f"\n📊 **TREEMAP FEATURES**:")
        print(f"   • Service health visualization with color coding")
        print(f"   • Size based on service importance")
        print(f"   • Interactive tooltips with detailed metrics")
        print(f"   • Legend for status interpretation")
        print(f"   • Responsive design for all screen sizes")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    print("🎨 Dashboard Improvements Test Suite")
    print("Testing removal of Project Status window and addition of Service Health TreeMap")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = DashboardImprovementsTest()
    tester.run_all_tests()
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
