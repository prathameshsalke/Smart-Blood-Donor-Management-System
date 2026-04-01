# check_paths_fixed.py
import os

def verify_paths():
    """Verify all template paths"""
    print("="*50)
    print("VERIFYING TEMPLATE PATHS")
    print("="*50)
    
    # Check base.html
    base_path = 'app/templates/base.html'
    if os.path.exists(base_path):
        print("✅ base.html exists")
    else:
        print("❌ base.html missing")
    
    # Check admin layout in layouts folder
    layout_path = 'app/templates/layouts/admin_layout.html'
    if os.path.exists(layout_path):
        print("✅ admin_layout.html exists in layouts folder")
    else:
        print("❌ admin_layout.html missing from layouts folder")
    
    # Check dashboard
    dashboard_path = 'app/templates/admin/dashboard.html'
    if os.path.exists(dashboard_path):
        print("✅ dashboard.html exists")
        
        # Check what dashboard.html extends
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '{% extends "layouts/admin_layout.html" %}' in content:
                print("✅ dashboard.html correctly extends layouts/admin_layout.html")
            else:
                print("❌ dashboard.html has wrong extends path")
    else:
        print("❌ dashboard.html missing")
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if (os.path.exists(base_path) and 
        os.path.exists(layout_path) and 
        os.path.exists(dashboard_path)):
        print("✅ All files exist with correct paths!")
        print("\nYour folder structure is:")
        print("  📁 app/templates/")
        print("      📄 base.html")
        print("      📁 layouts/")
        print("          📄 admin_layout.html")
        print("      📁 admin/")
        print("          📄 dashboard.html")
    else:
        print("❌ Some files are missing. Please check above.")

if __name__ == "__main__":
    verify_paths()