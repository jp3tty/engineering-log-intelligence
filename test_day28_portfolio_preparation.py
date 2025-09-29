#!/usr/bin/env python3
"""
Day 28 Portfolio Preparation Test Suite
Tests the portfolio materials and case study documentation created for professional presentation.
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

class Day28PortfolioTest:
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent
        
    def run_all_tests(self):
        """Run all Day 28 portfolio preparation tests"""
        print("🚀 Starting Day 28 Portfolio Preparation Tests...")
        print("=" * 60)
        
        # Test portfolio materials
        self.test_portfolio_showcase_page()
        self.test_technical_case_study()
        self.test_demo_walkthrough_guide()
        self.test_skills_technologies_summary()
        self.test_portfolio_readme()
        self.test_documentation_integration()
        self.test_professional_presentation_readiness()
        self.test_business_value_documentation()
        self.test_learning_outcomes_summary()
        self.test_future_enhancement_roadmap()
        
        # Display results
        self.display_results()
        
    def test_portfolio_showcase_page(self):
        """Test Portfolio Showcase Page creation and content"""
        print("\n📋 Testing Portfolio Showcase Page...")
        
        showcase_file = self.project_root / "PORTFOLIO_SHOWCASE.md"
        
        if showcase_file.exists():
            content = showcase_file.read_text()
            
            # Check for key sections
            required_sections = [
                "Project Overview",
                "Key Features", 
                "Technology Stack",
                "Live Demo",
                "Performance Metrics",
                "Business Value",
                "Learning Outcomes"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if not missing_sections:
                self.test_results.append({
                    "test": "Portfolio Showcase Page",
                    "status": "✅ PASS",
                    "details": f"All required sections present ({len(required_sections)} sections)"
                })
            else:
                self.test_results.append({
                    "test": "Portfolio Showcase Page",
                    "status": "❌ FAIL",
                    "details": f"Missing sections: {', '.join(missing_sections)}"
                })
        else:
            self.test_results.append({
                "test": "Portfolio Showcase Page",
                "status": "❌ FAIL",
                "details": "Portfolio showcase file not found"
            })
    
    def test_technical_case_study(self):
        """Test Technical Case Study creation and content"""
        print("📊 Testing Technical Case Study...")
        
        case_study_file = self.project_root / "TECHNICAL_CASE_STUDY.md"
        
        if case_study_file.exists():
            content = case_study_file.read_text()
            
            # Check for key sections
            required_sections = [
                "Executive Summary",
                "Architecture Design",
                "Technical Implementation",
                "Performance Analysis",
                "Security Implementation",
                "Testing Strategy",
                "Business Impact",
                "Learning Outcomes",
                "Conclusion"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            # Check for code examples
            code_blocks = len(re.findall(r'```', content))
            
            if not missing_sections and code_blocks >= 10:
                self.test_results.append({
                    "test": "Technical Case Study",
                    "status": "✅ PASS",
                    "details": f"All sections present with {code_blocks} code examples"
                })
            else:
                self.test_results.append({
                    "test": "Technical Case Study",
                    "status": "❌ FAIL",
                    "details": f"Missing sections: {', '.join(missing_sections)} or insufficient code examples ({code_blocks})"
                })
        else:
            self.test_results.append({
                "test": "Technical Case Study",
                "status": "❌ FAIL",
                "details": "Technical case study file not found"
            })
    
    def test_demo_walkthrough_guide(self):
        """Test Demo Walkthrough Guide creation and content"""
        print("🎬 Testing Demo Walkthrough Guide...")
        
        demo_file = self.project_root / "DEMO_WALKTHROUGH.md"
        
        if demo_file.exists():
            content = demo_file.read_text()
            
            # Check for key sections
            required_sections = [
                "Demo Objectives",
                "Pre-Demo Setup",
                "Demo Script",
                "Key Messages",
                "Potential Questions",
                "Resources for Follow-up"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            # Check for timing information
            timing_mentions = len(re.findall(r'\d+\s+minute', content))
            
            if not missing_sections and timing_mentions >= 5:
                self.test_results.append({
                    "test": "Demo Walkthrough Guide",
                    "status": "✅ PASS",
                    "details": f"Complete guide with {timing_mentions} timing references"
                })
            else:
                self.test_results.append({
                    "test": "Demo Walkthrough Guide",
                    "status": "❌ FAIL",
                    "details": f"Missing sections: {', '.join(missing_sections)} or insufficient timing info ({timing_mentions})"
                })
        else:
            self.test_results.append({
                "test": "Demo Walkthrough Guide",
                "status": "❌ FAIL",
                "details": "Demo walkthrough guide file not found"
            })
    
    def test_skills_technologies_summary(self):
        """Test Skills & Technologies Summary creation and content"""
        print("🛠 Testing Skills & Technologies Summary...")
        
        skills_file = self.project_root / "SKILLS_TECHNOLOGIES_SUMMARY.md"
        
        if skills_file.exists():
            content = skills_file.read_text()
            
            # Check for key sections
            required_sections = [
                "Core Technical Skills",
                "Technology Stack Mastery",
                "Performance & Scalability",
                "Testing & Quality Assurance",
                "Learning Outcomes",
                "Portfolio Value"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            # Check for technology mentions
            technologies = ["Vue.js", "Python", "FastAPI", "PostgreSQL", "Elasticsearch", "Kafka", "Vercel"]
            tech_mentions = sum(1 for tech in technologies if tech in content)
            
            if not missing_sections and tech_mentions >= 6:
                self.test_results.append({
                    "test": "Skills & Technologies Summary",
                    "status": "✅ PASS",
                    "details": f"Comprehensive summary with {tech_mentions}/7 technologies covered"
                })
            else:
                self.test_results.append({
                    "test": "Skills & Technologies Summary",
                    "status": "❌ FAIL",
                    "details": f"Missing sections: {', '.join(missing_sections)} or insufficient tech coverage ({tech_mentions}/7)"
                })
        else:
            self.test_results.append({
                "test": "Skills & Technologies Summary",
                "status": "❌ FAIL",
                "details": "Skills & technologies summary file not found"
            })
    
    def test_portfolio_readme(self):
        """Test Portfolio README creation and content"""
        print("📄 Testing Portfolio README...")
        
        readme_file = self.project_root / "PORTFOLIO_README.md"
        
        if readme_file.exists():
            content = readme_file.read_text()
            
            # Check for key sections
            required_sections = [
                "Project Overview",
                "Key Features",
                "Technology Stack",
                "Live Demo",
                "Getting Started",
                "Performance Metrics",
                "Documentation",
                "Business Value"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            # Check for badges
            badge_count = len(re.findall(r'!\[.*\]\(.*\)', content))
            
            if not missing_sections and badge_count >= 4:
                self.test_results.append({
                    "test": "Portfolio README",
                    "status": "✅ PASS",
                    "details": f"Professional README with {badge_count} badges and all sections"
                })
            else:
                self.test_results.append({
                    "test": "Portfolio README",
                    "status": "❌ FAIL",
                    "details": f"Missing sections: {', '.join(missing_sections)} or insufficient badges ({badge_count})"
                })
        else:
            self.test_results.append({
                "test": "Portfolio README",
                "status": "❌ FAIL",
                "details": "Portfolio README file not found"
            })
    
    def test_documentation_integration(self):
        """Test documentation integration and cross-references"""
        print("🔗 Testing Documentation Integration...")
        
        # Check if portfolio files reference each other
        portfolio_files = [
            "PORTFOLIO_SHOWCASE.md",
            "TECHNICAL_CASE_STUDY.md", 
            "DEMO_WALKTHROUGH.md",
            "SKILLS_TECHNOLOGIES_SUMMARY.md",
            "PORTFOLIO_README.md"
        ]
        
        existing_files = [f for f in portfolio_files if (self.project_root / f).exists()]
        
        if len(existing_files) >= 4:
            # Check for cross-references
            cross_refs = 0
            for file in existing_files:
                content = (self.project_root / file).read_text()
                # Look for references to other portfolio files
                for other_file in existing_files:
                    if other_file != file and other_file.replace('.md', '') in content:
                        cross_refs += 1
            
            if cross_refs >= 5:
                self.test_results.append({
                    "test": "Documentation Integration",
                    "status": "✅ PASS",
                    "details": f"Good integration with {cross_refs} cross-references between {len(existing_files)} files"
                })
            else:
                self.test_results.append({
                    "test": "Documentation Integration",
                    "status": "⚠️ WARNING",
                    "details": f"Limited cross-references ({cross_refs}) between portfolio files"
                })
        else:
            self.test_results.append({
                "test": "Documentation Integration",
                "status": "❌ FAIL",
                "details": f"Only {len(existing_files)}/5 portfolio files created"
            })
    
    def test_professional_presentation_readiness(self):
        """Test professional presentation readiness"""
        print("🎯 Testing Professional Presentation Readiness...")
        
        # Check for demo script completeness
        demo_file = self.project_root / "DEMO_WALKTHROUGH.md"
        showcase_file = self.project_root / "PORTFOLIO_SHOWCASE.md"
        
        if demo_file.exists() and showcase_file.exists():
            demo_content = demo_file.read_text()
            showcase_content = showcase_file.read_text()
            
            # Check for presentation elements
            demo_elements = [
                "Demo Script",
                "Talking Points", 
                "Potential Questions",
                "Key Messages"
            ]
            
            showcase_elements = [
                "Live Demo",
                "Demo Credentials",
                "Business Value",
                "Performance Metrics"
            ]
            
            demo_score = sum(1 for elem in demo_elements if elem in demo_content)
            showcase_score = sum(1 for elem in showcase_elements if elem in showcase_content)
            
            total_score = demo_score + showcase_score
            
            if total_score >= 7:
                self.test_results.append({
                    "test": "Professional Presentation Readiness",
                    "status": "✅ PASS",
                    "details": f"Ready for presentations with {total_score}/8 key elements"
                })
            else:
                self.test_results.append({
                    "test": "Professional Presentation Readiness",
                    "status": "⚠️ WARNING",
                    "details": f"Some presentation elements missing ({total_score}/8)"
                })
        else:
            self.test_results.append({
                "test": "Professional Presentation Readiness",
                "status": "❌ FAIL",
                "details": "Demo or showcase files missing"
            })
    
    def test_business_value_documentation(self):
        """Test business value documentation"""
        print("💼 Testing Business Value Documentation...")
        
        # Check multiple files for business value content
        files_to_check = [
            "PORTFOLIO_SHOWCASE.md",
            "TECHNICAL_CASE_STUDY.md",
            "PORTFOLIO_README.md"
        ]
        
        business_value_sections = 0
        for file in files_to_check:
            file_path = self.project_root / file
            if file_path.exists():
                content = file_path.read_text()
                if "Business Value" in content or "Business Impact" in content:
                    business_value_sections += 1
        
        if business_value_sections >= 2:
            self.test_results.append({
                "test": "Business Value Documentation",
                "status": "✅ PASS",
                "details": f"Business value documented in {business_value_sections} files"
            })
        else:
            self.test_results.append({
                "test": "Business Value Documentation",
                "status": "⚠️ WARNING",
                "details": f"Limited business value documentation ({business_value_sections} files)"
            })
    
    def test_learning_outcomes_summary(self):
        """Test learning outcomes documentation"""
        print("🎓 Testing Learning Outcomes Summary...")
        
        # Check for learning outcomes in multiple files
        files_to_check = [
            "SKILLS_TECHNOLOGIES_SUMMARY.md",
            "TECHNICAL_CASE_STUDY.md",
            "PORTFOLIO_SHOWCASE.md"
        ]
        
        learning_sections = 0
        for file in files_to_check:
            file_path = self.project_root / file
            if file_path.exists():
                content = file_path.read_text()
                if "Learning Outcomes" in content or "Skills Development" in content:
                    learning_sections += 1
        
        if learning_sections >= 2:
            self.test_results.append({
                "test": "Learning Outcomes Summary",
                "status": "✅ PASS",
                "details": f"Learning outcomes documented in {learning_sections} files"
            })
        else:
            self.test_results.append({
                "test": "Learning Outcomes Summary",
                "status": "⚠️ WARNING",
                "details": f"Limited learning outcomes documentation ({learning_sections} files)"
            })
    
    def test_future_enhancement_roadmap(self):
        """Test future enhancement roadmap"""
        print("🚀 Testing Future Enhancement Roadmap...")
        
        # Check for future enhancements in portfolio files
        files_to_check = [
            "PORTFOLIO_SHOWCASE.md",
            "TECHNICAL_CASE_STUDY.md",
            "PORTFOLIO_README.md"
        ]
        
        future_sections = 0
        for file in files_to_check:
            file_path = self.project_root / file
            if file_path.exists():
                content = file_path.read_text()
                if "Future Enhancements" in content or "Future Opportunities" in content:
                    future_sections += 1
        
        if future_sections >= 2:
            self.test_results.append({
                "test": "Future Enhancement Roadmap",
                "status": "✅ PASS",
                "details": f"Future enhancements documented in {future_sections} files"
            })
        else:
            self.test_results.append({
                "test": "Future Enhancement Roadmap",
                "status": "⚠️ WARNING",
                "details": f"Limited future enhancement documentation ({future_sections} files)"
            })
    
    def display_results(self):
        """Display test results summary"""
        print("\n" + "=" * 60)
        print("📊 DAY 28 PORTFOLIO PREPARATION TEST RESULTS")
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
        
        print(f"\n🎯 **DAY 28 STATUS**: ", end="")
        if passed >= 8:
            print("✅ **PORTFOLIO PREPARATION COMPLETE** - Ready for professional use!")
        elif passed >= 6:
            print("⚠️ **MOSTLY COMPLETE** - Minor improvements needed")
        else:
            print("❌ **INCOMPLETE** - Significant work remaining")
        
        print(f"\n📚 **PORTFOLIO MATERIALS CREATED**:")
        portfolio_files = [
            "PORTFOLIO_SHOWCASE.md",
            "TECHNICAL_CASE_STUDY.md",
            "DEMO_WALKTHROUGH.md", 
            "SKILLS_TECHNOLOGIES_SUMMARY.md",
            "PORTFOLIO_README.md"
        ]
        
        for file in portfolio_files:
            if (self.project_root / file).exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} (missing)")
        
        print(f"\n🎉 **READY FOR**:")
        print(f"   • Technical interviews and presentations")
        print(f"   • Client demonstrations and portfolio showcases")
        print(f"   • GitHub portfolio and professional networking")
        print(f"   • Job applications and career advancement")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    print("🎨 Day 28 Portfolio Preparation Test Suite")
    print("Testing professional portfolio materials and case study documentation")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = Day28PortfolioTest()
    tester.run_all_tests()
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
