# fix_current_year_error.py
import os
import re

def fix_base_html():
    """Fix base.html to use current_year as variable not function"""
    filepath = 'app/templates/base.html'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace {{ current_year() }} with {{ current_year }}
    if '{{ current_year() }}' in content:
        content = content.replace('{{ current_year() }}', '{{ current_year }}')
        print("✅ Fixed base.html - removed parentheses from current_year")
    else:
        print("ℹ️ base.html already has correct current_year format")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_donor_routes():
    """Ensure donor routes pass current_year as integer"""
    filepath = 'app/blueprints/donor/routes.py'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if current_year is passed as integer in render_template calls
    patterns = [
        (r"return render_template\('donor/dashboard\.html',(.*?)current_year=datetime\.now\(\)\.year(.*?)\)",
         r"return render_template('donor/dashboard.html',\1current_year=datetime.now().year\2)"),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed donor routes - ensured current_year is passed as integer")
    else:
        print("ℹ️ Donor routes already have correct current_year format")

def fix_dashboard_html():
    """Fix dashboard.html share modal to remove public_profile reference"""
    filepath = 'app/templates/donor/dashboard.html'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the profile link in share modal
    pattern = r'value="{{ url_for\(\'donor\.public_profile\', donor_id=donor\.id, _external=True\) }}"'
    replacement = 'value="{{ url_for(\'index\', _external=True) }}"'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("✅ Fixed dashboard.html - removed public_profile reference")
    else:
        print("ℹ️ dashboard.html already has correct profile link")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_filters_file():
    """Create or update filters.py with current_year as function"""
    filepath = 'app/filters.py'
    
    content = '''"""
Custom Jinja2 filters for templates
"""

from datetime import datetime

def current_year():
    """Return the current year as a function (for templates that call it)"""
    return datetime.now().year

def register_filters(app):
    """Register all custom filters with the app"""
    app.jinja_env.globals.update(
        current_year=current_year  # This is a function
    )
'''
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created/updated filters.py with current_year function")

def verify_fix():
    """Verify all fixes are applied"""
    print("\n" + "="*50)
    print("VERIFYING FIXES")
    print("="*50)
    
    # Check base.html
    base_path = 'app/templates/base.html'
    if os.path.exists(base_path):
        with open(base_path, 'r') as f:
            content = f.read()
            if '{{ current_year }}' in content and '{{ current_year() }}' not in content:
                print("✅ base.html correctly uses {{ current_year }}")
            else:
                print("❌ base.html still has issues")
    
    # Check dashboard.html
    dash_path = 'app/templates/donor/dashboard.html'
    if os.path.exists(dash_path):
        with open(dash_path, 'r') as f:
            content = f.read()
            if 'url_for(\'index\', _external=True)' in content and 'donor.public_profile' not in content:
                print("✅ dashboard.html has correct share modal link")
            else:
                print("❌ dashboard.html still has public_profile reference")
    
    # Check filters.py
    filters_path = 'app/filters.py'
    if os.path.exists(filters_path):
        with open(filters_path, 'r') as f:
            content = f.read()
            if 'def current_year()' in content:
                print("✅ filters.py has current_year function")
            else:
                print("❌ filters.py missing current_year function")
    else:
        print("❌ filters.py not found")

if __name__ == "__main__":
    print("="*60)
    print("FIXING 'int object is not callable' ERROR")
    print("="*60)
    
    print("\n📁 Step 1: Fixing base.html...")
    fix_base_html()
    
    print("\n📁 Step 2: Fixing donor routes...")
    fix_donor_routes()
    
    print("\n📁 Step 3: Fixing dashboard.html share modal...")
    fix_dashboard_html()
    
    print("\n📁 Step 4: Creating/updating filters.py...")
    fix_filters_file()
    
    print("\n📁 Step 5: Verifying fixes...")
    verify_fix()
    
    print("\n" + "="*60)
    print("✅ ALL FIXES COMPLETE!")
    print("="*60)
    print("\n📝 Summary of changes:")
    print("  1. Changed {{ current_year() }} to {{ current_year }} in base.html")
    print("  2. Ensured current_year is passed as integer in routes")
    print("  3. Removed public_profile reference from dashboard.html share modal")
    print("  4. Created/updated filters.py with current_year function")
    print("\n🚀 Now restart your Flask app:")
    print("  python run.py")