#!/usr/bin/env python3
"""
Project Organization Verification Script
=========================================

Verifies that the StudyPro Hub project is properly organized
and production-ready.

Run with: python verify_organization.py
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class ProjectVerifier:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.successes = []

    def check_file_exists(self, path, critical=True):
        """Check if a file exists"""
        full_path = self.root / path
        exists = full_path.exists()
        
        if exists:
            self.successes.append(f"✅ {path}")
        else:
            msg = f"{'❌' if critical else '⚠️'} {path} (missing)"
            if critical:
                self.issues.append(msg)
            else:
                self.warnings.append(msg)
        
        return exists

    def check_directory_exists(self, path):
        """Check if a directory exists"""
        full_path = self.root / path
        exists = full_path.is_dir()
        
        if exists:
            self.successes.append(f"✅ {path}/")
        else:
            self.issues.append(f"❌ {path}/ (missing)")
        
        return exists

    def verify_project(self):
        """Run all verification checks"""
        print(f"{BLUE}=== StudyPro Hub Project Verification ==={RESET}\n")
        
        # Check frontend structure
        print(f"{BLUE}Checking Frontend...{RESET}")
        self.check_directory_exists("frontend")
        self.check_file_exists("frontend/quiz-aptitude.html")
        self.check_file_exists("frontend/quiz-technical.html")
        self.check_directory_exists("frontend/css")
        self.check_directory_exists("frontend/js")
        print()
        
        # Check backend structure
        print(f"{BLUE}Checking Backend...{RESET}")
        self.check_directory_exists("backend")
        self.check_file_exists("backend/manage.py")
        self.check_file_exists("backend/db.py")
        self.check_file_exists("backend/main.py")
        self.check_file_exists("backend/requirements.txt")
        print()
        
        # Check database layer
        print(f"{BLUE}Checking Database Layer...{RESET}")
        self.check_directory_exists("backend/database")
        self.check_file_exists("backend/database/__init__.py")
        self.check_file_exists("backend/database/init_db.py")
        self.check_file_exists("backend/database/config.py")
        self.check_file_exists("backend/database/utils.py")
        self.check_file_exists("backend/database/schema.sql")
        self.check_file_exists("backend/database/mongo.js")
        self.check_file_exists("backend/database/README.md")
        print()
        
        # Check Django structure
        print(f"{BLUE}Checking Django Structure...{RESET}")
        self.check_directory_exists("backend/djproject")
        self.check_file_exists("backend/djproject/settings.py")
        self.check_file_exists("backend/djproject/urls.py")
        self.check_file_exists("backend/djproject/wsgi.py")
        self.check_directory_exists("backend/accounts")
        self.check_file_exists("backend/accounts/models.py")
        self.check_file_exists("backend/accounts/views.py")
        self.check_file_exists("backend/accounts/api.py")
        print()
        
        # Check documentation
        print(f"{BLUE}Checking Documentation...{RESET}")
        self.check_file_exists("README.md")
        self.check_file_exists("QUICKSTART.md")
        self.check_file_exists("ORGANIZATION_SUMMARY.md")
        self.check_file_exists("MAINTENANCE_CHECKLIST.md")
        self.check_file_exists("PROJECT_ORGANIZATION_COMPLETE.md")
        self.check_file_exists("INDEX.md")
        self.check_file_exists("backend/DATABASE_SETUP.md")
        self.check_file_exists("backend/PRODUCTION_DEPLOYMENT.md")
        self.check_file_exists("backend/.env.example")
        print()
        
        # Check database file
        print(f"{BLUE}Checking Database File...{RESET}")
        db_file = self.root / "db.sqlite3"
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            self.successes.append(f"✅ db.sqlite3 ({size_mb:.2f} MB)")
        else:
            self.warnings.append("⚠️  db.sqlite3 (not yet created - normal on first run)")
        print()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print verification summary"""
        print(f"{BLUE}=== Verification Summary ==={RESET}\n")
        
        # Successes
        if self.successes:
            print(f"{GREEN}Passed ({len(self.successes)}){RESET}:")
            for item in self.successes[:10]:  # Show first 10
                print(f"  {item}")
            if len(self.successes) > 10:
                print(f"  ... and {len(self.successes) - 10} more")
            print()
        
        # Warnings
        if self.warnings:
            print(f"{YELLOW}Warnings ({len(self.warnings)}){RESET}:")
            for item in self.warnings:
                print(f"  {item}")
            print()
        
        # Issues
        if self.issues:
            print(f"{RED}Issues ({len(self.issues)}){RESET}:")
            for item in self.issues:
                print(f"  {item}")
            print()
        
        # Final status
        print(f"{BLUE}{'='*50}{RESET}")
        if not self.issues:
            print(f"{GREEN}✅ Project organization is COMPLETE!{RESET}")
            print(f"{GREEN}✅ All files and directories are in place.{RESET}")
            print()
            print("Next steps:")
            print("1. Read README.md")
            print("2. Follow QUICKSTART.md")
            print("3. Run: cd backend && python manage.py migrate")
            print("4. Run: python manage.py runserver")
            return True
        else:
            print(f"{RED}❌ Project has {len(self.issues)} critical issue(s).{RESET}")
            print(f"{YELLOW}⚠️  {len(self.warnings)} warning(s).{RESET}")
            return False

def main():
    """Main verification function"""
    # Get project root (current directory)
    project_root = Path.cwd()
    
    print(f"\n{BLUE}Project Root: {project_root}{RESET}\n")
    
    # Run verification
    verifier = ProjectVerifier(project_root)
    success = verifier.verify_project()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
