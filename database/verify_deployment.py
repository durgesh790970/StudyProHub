#!/usr/bin/env python
"""
Deployment Verification Script
Checks that all components are in place and operational
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_deployment():
    """Verify all deployment components."""
    print("=" * 70)
    print("🎉 DEPLOYMENT VERIFICATION")
    print("=" * 70)
    
    # Check files
    print("\n✅ Required Files:")
    files = {
        'config/db.py': 'Database Connection Module',
        'config/api.py': 'REST API Endpoints',
        'seeds/seed.py': 'Sample Data Script',
        'database/app.db': 'SQLite Database',
    }
    
    all_exist = True
    for file_path, description in files.items():
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {file_path:<25} - {description}")
        all_exist = all_exist and exists
    
    if not all_exist:
        print("\n❌ Some files are missing!")
        return False
    
    # Check database
    print("\n✅ Database Information:")
    try:
        from config.db import get_database_info, verify_database
        
        info = get_database_info()
        print(f"   Path: {info['database']}")
        print(f"   Size: {info['file_size_kb']} KB")
        print(f"   Type: {info['type']}")
        
        print("\n✅ Database Schema:")
        print(f"   Tables: {len(info['tables'])}")
        print(f"   Total Records: {info['total_records']}")
        
        print("\n✅ Tables & Record Count:")
        for table, count in sorted(info['table_records'].items()):
            print(f"   • {table:<20} {count:>3} records")
        
        print("\n✅ Database Integrity:")
        is_healthy = verify_database()
        status = "✅ Healthy" if is_healthy else "❌ Error"
        print(f"   Status: {status}")
        
        if not is_healthy:
            return False
        
    except Exception as e:
        print(f"\n❌ Database check failed: {e}")
        return False
    
    # Check sample data
    print("\n✅ Sample Data Verification:")
    try:
        from config.db import execute_query
        
        users = execute_query("SELECT COUNT(*) FROM users")
        transactions = execute_query("SELECT COUNT(*) FROM transactions")
        logs = execute_query("SELECT COUNT(*) FROM activity_logs")
        
        print(f"   Users: {users[0][0]} records")
        print(f"   Transactions: {transactions[0][0]} records")
        print(f"   Activity Logs: {logs[0][0]} records")
        
    except Exception as e:
        print(f"\n❌ Sample data check failed: {e}")
        return False
    
    # Success
    print("\n" + "=" * 70)
    print("🚀 DEPLOYMENT VERIFICATION PASSED")
    print("=" * 70)
    
    print("\n📍 Quick Start Commands:")
    print("\n   # Initialize database (if needed)")
    print("   python config/db.py")
    print("\n   # Seed sample data (if needed)")
    print("   python seeds/seed.py")
    print("\n   # Start API server")
    print("   python config/api.py")
    print("\n   # Test API health")
    print("   curl http://localhost:5000/api/v1/health")
    
    print("\n📚 Documentation:")
    print("   • DATABASE_INITIALIZATION_COMPLETE.md")
    print("   • SQLITE_DATABASE_GUIDE.md")
    print("   • API_USAGE_GUIDE.md")
    print("   • QUICK_REFERENCE.md")
    
    print("\n🔑 Test Credentials:")
    print("   Email: raj.kumar@gmail.com")
    print("   Password: Raj@12345")
    
    print("\n" + "=" * 70)
    
    return True


if __name__ == '__main__':
    success = verify_deployment()
    sys.exit(0 if success else 1)
