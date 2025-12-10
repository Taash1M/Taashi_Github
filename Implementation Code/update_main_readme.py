#!/usr/bin/env python3
"""
Script to Update Main README with Professional Content

This script:
1. Backs up your current README.md
2. Validates all project folder links (at root level after restructure)
3. Generates a comprehensive, Director-level README
4. Verifies all links work before finalizing

Usage:
    python update_main_readme.py

Run this from your Taashi_Github repository root directory.
Run AFTER restructure_directories.py has moved projects to root.
"""

import os
from pathlib import Path
from datetime import datetime
import shutil

class ReadmeUpdater:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.readme_path = self.repo_root / "README.md"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.repo_root / f"README_backup_{self.timestamp}.md"
        
        # Your information
        self.info = {
            'name': 'Taashi Manyanga',
            'title': 'Snr Data Engineering Manager - Data Platforms & Systems',
            'email': 'taashir@gmail.com',
            'phone': '(323) 794-6425',
            'linkedin': 'https://linkedin.com/in/taashi-m-74b14a161',
            'location': 'Seattle, WA (Remote)',
            'github_username': 'Taash1M'
        }
        
        # Core data engineering projects (numbered 01-12)
        self.core_projects = [
            {
                'folder': '01_platform_modernization_blueprint',
                'title': 'Platform Modernization Blueprint',
                'description': 'Complete Oracle to multi-cloud migration with Azure, AWS, and GCP implementations',
                'tech': 'Azure (Databricks, Synapse, ADF) • AWS (Glue, Athena) • GCP (BigQuery, Dataflow)',
                'impact': '70% performance improvement, 30% cost reduction, zero downtime'
            },
            {
                'folder': '02_data_quality_framework',
                'title': 'Data Quality Framework',
                'description': 'Production Python validation framework with automated testing',
                'tech': 'Python • Great Expectations • pytest • CI/CD',
                'impact': '60% reduction in data quality incidents, 99.5% reliability'
            },
            {
                'folder': '03_ai_ml_governance',
                'title': 'AI/ML Governance Framework',
                'description': 'Production ML governance with policy enforcement and monitoring',
                'tech': 'GPT APIs • LangChain • MCP • Python • YAML configs',
                'impact': 'Enterprise-grade AI governance with measurable ROI'
            },
            {
                'folder': '04_snowflake_end_to_end',
                'title': 'Snowflake End-to-End Implementation',
                'description': 'Complete Snowflake data warehouse with dbt transformations',
                'tech': 'Snowflake • dbt • SQL • Data modeling',
                'impact': 'Scalable analytics platform serving 200+ users'
            },
            {
                'folder': '05_netflix_scale_pipeline',
                'title': 'Real-Time Streaming Pipeline',
                'description': 'Netflix-scale event processing with Spark Streaming',
                'tech': 'Apache Spark Streaming • Kafka • Real-time processing',
                'impact': 'Millions of manufacturing events processed daily'
            },
            {
                'folder': '06_dbt_warehouse_modeling',
                'title': 'dbt Warehouse Modeling',
                'description': 'Dimensional modeling with dbt for analytics',
                'tech': 'dbt • SQL • Dimensional modeling • Testing',
                'impact': 'Maintainable, tested data transformations'
            },
            {
                'folder': '07_airflow_orchestration',
                'title': 'Airflow Orchestration',
                'description': 'Production workflow orchestration patterns and DAGs',
                'tech': 'Apache Airflow • Python • Workflow management',
                'impact': 'Reliable, observable data pipelines'
            },
            {
                'folder': '08_spark_optimization',
                'title': 'Spark Performance Optimization',
                'description': 'Advanced Spark tuning techniques and comparisons',
                'tech': 'Apache Spark • PySpark • Performance tuning',
                'impact': 'Query time reduced from 45min to 15min (67% faster)'
            },
            {
                'folder': '09_observability_monitoring',
                'title': 'Observability & Monitoring',
                'description': 'Production monitoring with CloudWatch metrics',
                'tech': 'AWS CloudWatch • Azure Monitor • Metrics • Alerting',
                'impact': '99.5% system reliability achieved'
            },
            {
                'folder': '10_case_studies_portfolio',
                'title': 'Case Studies Portfolio',
                'description': 'Detailed platform transformation stories with real metrics',
                'tech': 'Platform migrations • Team leadership • Business impact',
                'impact': 'Real-world results from Fortune 500 implementations'
            },
            {
                'folder': '11_adf_ci_cd_medallion',
                'title': 'Azure Data Factory CI/CD',
                'description': 'Medallion architecture with automated deployments',
                'tech': 'Azure Data Factory • GitHub Actions • Databricks • CI/CD',
                'impact': 'Automated, testable data pipelines'
            },
            {
                'folder': '12_platform_leadership_assets',
                'title': 'Platform Leadership Assets',
                'description': 'Engineering standards, metrics, roadmaps, and team onboarding',
                'tech': 'Leadership • Team development • Standards • Metrics',
                'impact': '95%+ retention through strong engineering culture'
            }
        ]
        
        # ML/Advanced projects (bonus content)
        self.ml_projects = [
            {
                'folder': '12_ml_linear_regression_house_prices',
                'title': 'ML: Linear Regression (House Prices)',
                'description': 'Predictive modeling with linear regression'
            },
            {
                'folder': '13_ml_logistic_regression_churn',
                'title': 'ML: Logistic Regression (Churn Prediction)',
                'description': 'Customer churn prediction with classification'
            },
            {
                'folder': '14_ml_sentiment_analysis',
                'title': 'ML: Sentiment Analysis',
                'description': 'NLP sentiment analysis implementation'
            },
            {
                'folder': '15_Streaming_Big_Data',
                'title': 'Streaming Big Data Systems',
                'description': 'Real-world streaming patterns (DoorDash, Uber, Netflix, Snapchat, X, Facebook)',
                'subfolder_note': 'Contains 6 production-inspired streaming architectures'
            }
        ]
    
    def backup_current_readme(self):
        """Create backup of current README"""
        if self.readme_path.exists():
            shutil.copy2(self.readme_path, self.backup_path)
            print(f"✓ Backed up current README to: {self.backup_path.name}")
            return True
        else:
            print("ℹ️  No existing README.md found - will create new one")
            return False
    
    def validate_project_folders(self, projects):
        """Check which project folders exist at root level"""
        existing = []
        missing = []
        
        for project in projects:
            folder_path = self.repo_root / project['folder']
            if folder_path.exists() and folder_path.is_dir():
                existing.append(project)
            else:
                missing.append(project['folder'])
        
        return existing, missing
    
    def generate_readme_content(self, core_existing, ml_existing):
        """Generate the comprehensive README content"""
        
        content = f"""# {self.info['name']}
## {self.info['title']}

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)]({self.info['linkedin']})
[![Email](https://img.shields.io/badge/Email-Contact-red)](mailto:{self.info['email']})
[![Location](https://img.shields.io/badge/Location-{self.info['location'].replace(' ', '%20').replace(',', '%2C')}-green)]()

---

## 🎯 Leadership Philosophy

*"Great engineering teams ship reliably at scale by balancing technical excellence with velocity, embracing failure as learning, and empowering individual ownership. I build high-trust cultures where engineers thrive, systems are designed for resilience, and customer impact drives every decision."*

I specialize in building and scaling distributed data platforms, leading cross-functional engineering teams, and driving platform transformations that deliver measurable business impact while maintaining operational excellence.

---

## 💼 Career Highlights

### Platform Transformation & Delivery at Fluke Corporation
- 🚀 **Cloud platform transformation**: Migrated from legacy Oracle to cloud-native architecture (Databricks, Synapse, BigQuery) serving 200+ customers
- ⚡ **Performance impact**: Achieved **70% latency reduction** and **zero downtime** for millions of daily manufacturing events
- 💰 **Cost & efficiency**: Delivered **30% cost reduction** with **70% performance improvement**
- 📊 **Query optimization**: Reduced critical pipeline execution from **45min to 15min** (67% improvement)

### Team Leadership & Organizational Impact
- 👥 **Team building**: Led distributed engineering teams of **12-14 engineers**, maintaining **95%+ retention**
- 📈 **System reliability**: Achieved **99.5% reliability** through automated testing (pytest, Great Expectations) and CI/CD
- 🎓 **Technical excellence**: Established culture of operational rigor with blameless post-mortems and on-call practices
- 🔧 **Data quality**: Reduced data quality incidents by **60%** through Python validation frameworks

### Innovation & Technical Leadership
- 🤖 **AI/ML integration**: Shipped production AI solutions in 2024 with GPT APIs, LangChain, and MCP integrations
- 📊 **Platform adoption**: Drove **3x increase** in platform usage through modern architecture and user-centric design
- 🔄 **Streaming at scale**: Built real-time pipelines processing millions of manufacturing events daily
- 💡 **Cross-functional impact**: Strong partnerships with product, operations, and analytics teams

---

## 🏗️ Featured Projects

### Core Data Engineering Portfolio

"""
        
        # Add core projects
        for project in core_existing:
            content += f"""#### [{project['title']}](./{project['folder']})
{project['description']}

**Tech Stack:** {project['tech']}  
**Impact:** {project['impact']}

"""
        
        # Add ML/Advanced section if projects exist
        if ml_existing:
            content += """---

### Machine Learning & Advanced Topics

"""
            for project in ml_existing:
                desc = project['description']
                if 'subfolder_note' in project:
                    desc += f" • {project['subfolder_note']}"
                content += f"""#### [{project['title']}](./{project['folder']})
{desc}

"""
        
        content += f"""---

## 🛠️ Technical Leadership Areas

### Data Platform Architecture
- **Cloud Platforms:** AWS, Azure, GCP (BigQuery), Multi-cloud strategy
- **Data Warehouses:** Snowflake, Databricks, Synapse Analytics, BigQuery
- **Processing:** Apache Spark, Kafka streaming, Airflow orchestration, dbt
- **Migrations:** Oracle to cloud, Legacy modernization, Zero-downtime transitions

### Data Engineering & Quality
- **Real-time Processing:** Spark Streaming, Kafka, High-volume event pipelines
- **ETL/ELT:** Python frameworks, Distributed processing, Incremental loads
- **Data Modeling:** Dimensional modeling, Star/Snowflake schemas, Medallion architecture
- **Quality:** pytest, Great Expectations, Automated validation, CI/CD pipelines

### AI/ML & Emerging Tech
- **Production AI:** GPT APIs, LangChain, Custom MCP integrations
- **ML Operations:** Model monitoring, Governance, Bias detection
- **Streaming ML:** Real-time feature engineering, Online prediction
- **Innovation:** Rapid prototyping, Measurable ROI, Production-grade reliability

### DevOps & Operational Excellence
- **CI/CD:** GitHub Actions, Azure DevOps, Automated deployments
- **Monitoring:** CloudWatch, Azure Monitor, Metrics, Alerting, Dashboards
- **Languages:** Python, SQL, PySpark, Bash
- **Reliability:** 99.5%+ SLAs, Incident management, Blameless culture

---

## 📊 By the Numbers

```
💰 30%        cost reduction with 70% performance improvement
⚡ 67%        query execution time reduction (45min → 15min)  
📈 99.5%      system reliability across all pipelines
👥 12-14      engineers led across distributed teams
🚀 3x         platform adoption increase
📉 60%        reduction in data quality incidents
🔄 0          downtime during critical migrations
📦 200+       internal customers served daily
```

---

## 🎓 Education

- **Master of Science in Information Systems** - Foster Business School, University of Washington (2025-2026)
- **Bachelor of Science in Economics** (Applied Statistics and Econometrics ) - UZ

---

## 💼 Professional Experience

### Snr Data Engineering Manager - Data Platform & Analytics
**Fluke Corporation** (Fortune 500, $2B+ Industrial Technology) | April 2018 - Present

- Built and scaled distributed data platform serving 200+ internal customers
- Drove end-to-end Oracle to multi-cloud migration (AWS, Azure, GCP)
- Achieved 70% performance improvement and 30% cost reduction
- Led team of 12 engineers with 95%+ retention through mentorship and transparency

### Engineering Manager - Business Intelligence Platform
**Gilbarco AFS** (Vontier Corp) | February 2013 - March 2018

- Led cross-functional team of 14 engineers building scalable BI platform
- Achieved >98% data accuracy serving 500+ global users
- Drove technical excellence through hands-on architecture and code reviews

---

## 📫 Let's Connect

I'm interested in discussing:
- **Data platform architecture** and cloud migration strategies
- **Building high-performing teams** and engineering culture
- **Operational excellence** and reliability at scale
- **Leadership opportunities** in data platforms and engineering management

**Email:** {self.info['email']}  
**Phone:** {self.info['phone']}  
**LinkedIn:** [linkedin.com/in/taashi-m-74b14a161]({self.info['linkedin']})  
**Location:** {self.info['location']}

---

## 🌟 Current Focus

- 🎓 Pursuing **MS in Information Systems** at UW Foster Business School
- 🔭 Exploring **AI/ML integration** in data platforms (GPT APIs, LangChain)
- 🌱 Building **next-generation cloud architectures** with medallion patterns
- 👯 **Mentoring engineering leaders** and growing technical talent
- 💬 Open to **leadership opportunities** in data engineering and platform teams

---

## 🏆 Key Achievements

- ✅ **Zero downtime** migration of business-critical manufacturing systems
- ✅ **99.5% system reliability** with comprehensive monitoring and alerting
- ✅ **3x platform adoption** through user-centric design and partnerships
- ✅ **95%+ team retention** through transparent leadership and empowerment
- ✅ **60% fewer data incidents** through automated quality frameworks
- ✅ **Production AI** with measurable business ROI in 2024

---

## 📚 Repository Structure

This repository showcases production-grade implementations across:
- **Platform modernization** (Azure, AWS, GCP)
- **Data quality** and testing frameworks
- **Real-time streaming** at scale
- **ML governance** and operations
- **Leadership assets** (standards, metrics, onboarding)

Each project includes:
- ✅ Working code with detailed comments
- ✅ Sample data and test cases
- ✅ Architecture documentation
- ✅ CI/CD pipelines and automation
- ✅ README with context and outcomes

---

<div align="center">

**Building resilient systems and empowered teams that deliver business impact**

[![GitHub followers](https://img.shields.io/github/followers/{self.info['github_username']}?style=social)](https://github.com/{self.info['github_username']})
[![GitHub stars](https://img.shields.io/github/stars/{self.info['github_username']}/Taashi_Github?style=social)](https://github.com/{self.info['github_username']}/Taashi_Github)

*Last updated: {datetime.now().strftime("%B %d, %Y")}*

</div>
"""
        
        return content
    
    def write_readme(self, content):
        """Write the new README content"""
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ New README.md created successfully ({len(content)} characters)")
    
    def create_summary_report(self, core_existing, ml_existing, core_missing, ml_missing):
        """Create a summary report"""
        report_path = self.repo_root / f"readme_update_report_{self.timestamp}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("README UPDATE REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Repository: {self.repo_root}\n\n")
            
            f.write("CORE DATA ENGINEERING PROJECTS (Validated):\n")
            f.write("-" * 70 + "\n")
            for project in core_existing:
                f.write(f"✓ {project['folder']}\n")
            
            if ml_existing:
                f.write("\nML/ADVANCED PROJECTS (Validated):\n")
                f.write("-" * 70 + "\n")
                for project in ml_existing:
                    f.write(f"✓ {project['folder']}\n")
            
            if core_missing or ml_missing:
                f.write("\nMISSING PROJECTS (excluded from README):\n")
                f.write("-" * 70 + "\n")
                for folder in core_missing + ml_missing:
                    f.write(f"✗ {folder}\n")
            
            f.write("\nCONTENT SUMMARY:\n")
            f.write("-" * 70 + "\n")
            f.write(f"- Core projects included: {len(core_existing)}\n")
            f.write(f"- ML/Advanced projects: {len(ml_existing)}\n")
            f.write(f"- Total validated links: {len(core_existing) + len(ml_existing)}\n")
            f.write(f"- Projects missing: {len(core_missing) + len(ml_missing)}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("NEXT STEPS:\n")
            f.write("=" * 70 + "\n")
            f.write("1. Review the updated README.md\n")
            f.write("2. Click each project link to verify they work\n")
            f.write("3. Customize any sections with additional details\n")
            f.write("4. Add screenshots/diagrams to project folders\n")
            f.write("5. Commit and push:\n")
            f.write("   git add README.md\n")
            f.write("   git commit -m 'Update README with comprehensive Director-level content'\n")
            f.write("   git push origin main\n\n")
        
        print(f"📝 Summary report: {report_path.name}")
    
    def run(self):
        """Main execution function"""
        print("=" * 70)
        print("README UPDATE TOOL")
        print("=" * 70)
        print(f"\nRepository: {self.repo_root}\n")
        
        # Backup
        self.backup_current_readme()
        
        # Validate projects
        print("\n📁 Validating project folders at root level...")
        core_existing, core_missing = self.validate_project_folders(self.core_projects)
        ml_existing, ml_missing = self.validate_project_folders(self.ml_projects)
        
        print(f"   ✓ Core projects found: {len(core_existing)}/12")
        print(f"   ✓ ML/Advanced projects found: {len(ml_existing)}/4")
        
        if core_missing:
            print(f"   ⚠️  Core projects missing: {len(core_missing)}")
        if ml_missing:
            print(f"   ⚠️  ML projects missing: {len(ml_missing)}")
        
        # Confirm
        print("\nThis will replace your README.md with comprehensive content.")
        print("All links will point to folders at root level.")
        print("A backup has been created.\n")
        
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\n❌ Cancelled. Your original README is safe.")
            return
        
        # Generate
        print("\n✍️  Generating README content...")
        content = self.generate_readme_content(core_existing, ml_existing)
        
        # Write
        self.write_readme(content)
        
        # Report
        self.create_summary_report(core_existing, ml_existing, core_missing, ml_missing)
        
        # Summary
        total_projects = len(core_existing) + len(ml_existing)
        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"✓ README.md updated ({len(content):,} characters)")
        print(f"✓ Backup: {self.backup_path.name}")
        print(f"✓ Projects included: {total_projects}")
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. Review README.md")
        print("2. Test project links")
        print("3. Commit:")
        print("   git add README.md")
        print("   git commit -m 'Update README to Director level'")
        print("   git push origin main")
        print("=" * 70 + "\n")

def main():
    updater = ReadmeUpdater()
    updater.run()

if __name__ == "__main__":
    main()