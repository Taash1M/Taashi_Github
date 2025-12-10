#!/usr/bin/env python3
"""
Script to Move Implementation Code Subdirectories Up One Level

This script:
1. Moves all numbered project folders from "Implementation Code" to root
2. Leaves the original "Implementation Code" folder intact for manual deletion
3. Creates a log of all operations

Usage:
    python restructure_directories.py

Run this from your Taashi_Github repository root directory.
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class DirectoryRestructurer:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.impl_code_dir = self.repo_root / "Implementation Code"
        self.operations_log = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"restructure_log_{self.timestamp}.json"
        
        # Projects to move (based on your structure)
        self.project_folders = [
            "01_platform_modernization_blueprint",
            "02_data_quality_framework",
            "03_ai_ml_governance",
            "04_snowflake_end_to_end",
            "05_netflix_scale_pipeline",
            "06_dbt_warehouse_modeling",
            "07_airflow_orchestration",
            "08_spark_optimization",
            "09_observability_monitoring",
            "10_case_studies_portfolio",
            "11_adf_ci_cd_medallion",
            "12_platform_leadership_assets",
            "12_ml_linear_regression_house_prices",
            "13_ml_logistic_regression_churn",
            "14_ml_sentiment_analysis",
            "15_Streaming_Big_Data"
        ]
        
    def check_implementation_code_exists(self):
        """Check if Implementation Code directory exists"""
        if not self.impl_code_dir.exists():
            print(f"❌ 'Implementation Code' directory not found at: {self.impl_code_dir}")
            return False
        
        if not self.impl_code_dir.is_dir():
            print(f"❌ 'Implementation Code' exists but is not a directory")
            return False
        
        return True
    
    def find_projects_to_move(self):
        """Find which project folders exist in Implementation Code"""
        projects_found = []
        projects_missing = []
        
        for project in self.project_folders:
            source_path = self.impl_code_dir / project
            if source_path.exists() and source_path.is_dir():
                projects_found.append(project)
            else:
                projects_missing.append(project)
        
        return projects_found, projects_missing
    
    def move_project_folder(self, project_name):
        """Move a project folder from Implementation Code to root"""
        source = self.impl_code_dir / project_name
        destination = self.repo_root / project_name
        
        print(f"\n📁 Processing: {project_name}")
        print(f"   Source: {source.relative_to(self.repo_root)}")
        print(f"   Destination: {destination.relative_to(self.repo_root)}")
        
        # Check if destination already exists
        if destination.exists():
            print(f"   ⚠️  Skipping - {project_name} already exists at root level")
            return {
                'project': project_name,
                'status': 'skipped',
                'reason': 'Already exists at destination',
                'source': str(source.relative_to(self.repo_root)),
                'destination': str(destination.relative_to(self.repo_root))
            }
        
        # Move the entire project folder
        try:
            shutil.move(str(source), str(destination))
            print(f"   ✓ Successfully moved {project_name}")
            
            # Count files in moved directory
            file_count = sum(1 for _ in destination.rglob('*') if _.is_file())
            
            return {
                'project': project_name,
                'status': 'success',
                'source': str(source.relative_to(self.repo_root)),
                'destination': str(destination.relative_to(self.repo_root)),
                'file_count': file_count
            }
        except Exception as e:
            print(f"   ✗ Error moving {project_name}: {str(e)}")
            return {
                'project': project_name,
                'status': 'error',
                'reason': str(e),
                'source': str(source.relative_to(self.repo_root))
            }
    
    def create_backup_info(self):
        """Create a backup info file"""
        backup_info = {
            'timestamp': self.timestamp,
            'repo_root': str(self.repo_root),
            'note': 'Implementation Code directory left intact for manual deletion',
            'projects_moved': [op for op in self.operations_log if op['status'] == 'success']
        }
        
        backup_file = self.repo_root / f"restructure_backup_info_{self.timestamp}.txt"
        with open(backup_file, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("DIRECTORY RESTRUCTURE BACKUP INFORMATION\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Timestamp: {backup_info['timestamp']}\n")
            f.write(f"Repository: {backup_info['repo_root']}\n\n")
            f.write("PROJECTS MOVED:\n")
            f.write("-" * 70 + "\n")
            for project in backup_info['projects_moved']:
                f.write(f"✓ {project['project']}\n")
                f.write(f"  Files: {project.get('file_count', 'unknown')}\n")
            f.write("\n")
            f.write("IMPORTANT:\n")
            f.write("-" * 70 + "\n")
            f.write("- All project folders have been moved to root level\n")
            f.write("- Original 'Implementation Code' directory is still present\n")
            f.write("- You can safely delete it manually after verification\n\n")
            f.write("To delete 'Implementation Code' directory:\n")
            f.write("1. Verify the moved folders are working correctly\n")
            f.write("2. Check that all files are accessible\n")
            f.write("3. Run: rm -rf 'Implementation Code'\n")
            f.write("4. Or manually delete via file explorer\n\n")
            f.write("To commit changes:\n")
            f.write("  git add .\n")
            f.write("  git commit -m 'Restructure: Move projects from Implementation Code to root'\n")
            f.write("  git push origin main\n\n")
        
        print(f"\n📝 Backup info saved: {backup_file.name}")
        return str(backup_file)
    
    def save_log(self):
        """Save operations log to JSON file"""
        log_path = self.repo_root / self.log_file
        
        log_data = {
            'timestamp': self.timestamp,
            'repository': str(self.repo_root),
            'source_directory': str(self.impl_code_dir.relative_to(self.repo_root)),
            'operations': self.operations_log,
            'summary': {
                'total_projects': len(self.operations_log),
                'successful': len([op for op in self.operations_log if op['status'] == 'success']),
                'skipped': len([op for op in self.operations_log if op['status'] == 'skipped']),
                'errors': len([op for op in self.operations_log if op['status'] == 'error'])
            }
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"📝 Operations log saved: {self.log_file}")
        return str(log_path)
    
    def run(self):
        """Main execution function"""
        print("=" * 70)
        print("DIRECTORY RESTRUCTURE TOOL")
        print("=" * 70)
        print(f"\nRepository: {self.repo_root}")
        print(f"Timestamp: {self.timestamp}\n")
        
        # Check if Implementation Code exists
        if not self.check_implementation_code_exists():
            return
        
        # Find projects to move
        projects_found, projects_missing = self.find_projects_to_move()
        
        if not projects_found:
            print("❌ No project folders found in 'Implementation Code' directory.")
            return
        
        print(f"✓ Found {len(projects_found)} project folders to move")
        if projects_missing:
            print(f"ℹ️  {len(projects_missing)} projects not found (may already be at root)")
        
        # Show what will be moved
        print("\nProjects to be moved:")
        print("-" * 70)
        for project in projects_found:
            print(f"  • {project}")
        
        print("\n" + "=" * 70)
        print("This will move all projects from 'Implementation Code' to root level.")
        print("Original 'Implementation Code' folder will remain for manual deletion.")
        print("=" * 70 + "\n")
        
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("\n❌ Operation cancelled by user.")
            return
        
        # Process each project
        print("\n" + "=" * 70)
        print("MOVING PROJECTS")
        print("=" * 70)
        
        for project in projects_found:
            result = self.move_project_folder(project)
            self.operations_log.append(result)
        
        # Create backup info and save log
        backup_file = self.create_backup_info()
        log_file = self.save_log()
        
        # Summary
        successful = len([op for op in self.operations_log if op['status'] == 'success'])
        skipped = len([op for op in self.operations_log if op['status'] == 'skipped'])
        errors = len([op for op in self.operations_log if op['status'] == 'error'])
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"✓ Projects successfully moved: {successful}")
        print(f"⚠️  Projects skipped: {skipped}")
        print(f"✗ Errors: {errors}")
        print(f"\n📄 Log file: {self.log_file}")
        print(f"📄 Backup info: {Path(backup_file).name}")
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("1. Verify the moved folders at root level")
        print("2. Test that your projects work correctly")
        print("3. Update any absolute paths in your code if needed")
        print("4. Delete 'Implementation Code' folder when ready:")
        print("   rm -rf 'Implementation Code'")
        print("5. Commit changes:")
        print("   git add .")
        print("   git commit -m 'Restructure: Move projects to root level'")
        print("   git push origin main")
        print("=" * 70 + "\n")
        
        if successful > 0:
            print("🎉 Restructure completed successfully!")
            print("   Your projects are now at the root level for easy access.\n")

def main():
    restructurer = DirectoryRestructurer()
    restructurer.run()

if __name__ == "__main__":
    main()