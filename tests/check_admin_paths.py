# check_admin_paths.py
import os

def verify_admin_templates():
    """Verify all admin template paths"""
    
    # Check if base.html exists
    base_path = 'app/templates/base.html'
    if os.path.exists(base_path):
        print("✅ base.html found at correct location")
    else:
        print("❌ base.html not found at app/templates/base.html")
    
    # Check admin layout
    admin_layout_path = 'app/templates/admin/layouts/admin_layout.html'
    if os.path.exists(admin_layout_path):
        print("✅ admin_layout.html found at correct location")
        
        # Check the extends line in admin_layout.html
        with open(admin_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '{% extends "base.html" %}' in content:
                print("✅ admin_layout.html correctly extends base.html")
            else:
                print("❌ admin_layout.html should extend base.html, not layouts/base.html")
    else:
        print("❌ admin_layout.html not found")
    
    # Check dashboard
    dashboard_path = 'app/templates/admin/dashboard.html'
    if os.path.exists(dashboard_path):
        print("✅ dashboard.html found at correct location")
        
        # Check the extends line in dashboard.html
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '{% extends "admin/layouts/admin_layout.html" %}' in content:
                print("✅ dashboard.html correctly extends admin_layout.html")
            else:
                print("❌ dashboard.html should extend admin/layouts/admin_layout.html")
    else:
        print("❌ dashboard.html not found")

if __name__ == "__main__":
    print("="*50)
    print("VERIFYING ADMIN TEMPLATE PATHS")
    print("="*50)
    
    verify_admin_templates()
    
    print("\n" + "="*50)
    print("Verification complete!")
    print("="*50)