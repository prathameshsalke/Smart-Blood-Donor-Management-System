# setup_template_filters.py
import os

def create_filters_file():
    """Create the filters.py file"""
    content = '''"""
Custom Jinja2 filters for templates
"""

from datetime import datetime

def current_year():
    """Return the current year"""
    return datetime.now().year

def register_filters(app):
    """Register all custom filters with the app"""
    app.jinja_env.globals.update(
        current_year=current_year
    )
'''
    
    with open('app/filters.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Created app/filters.py")

def update_init_py():
    """Update __init__.py to register filters"""
    init_path = 'app/__init__.py'
    
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if filters are already registered
    if 'register_filters' in content:
        print("ℹ️ Filters already registered in __init__.py")
        return
    
    # Find the right place to insert filter registration
    # Look for the line after extensions are initialized
    lines = content.split('\n')
    new_lines = []
    inserted = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Insert after CORS initialization
        if 'CORS(app)' in line and not inserted:
            new_lines.append('')
            new_lines.append('    # Register custom Jinja2 filters')
            new_lines.append('    from app.filters import register_filters')
            new_lines.append('    register_filters(app)')
            new_lines.append('')
            inserted = True
    
    if not inserted:
        # Fallback: insert before blueprint registration
        for i, line in enumerate(lines):
            if 'register_blueprints(app)' in line and not inserted:
                new_lines.insert(i-1, '    # Register custom Jinja2 filters')
                new_lines.insert(i, '    from app.filters import register_filters')
                new_lines.insert(i+1, '    register_filters(app)')
                inserted = True
    
    if inserted:
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print("✅ Updated app/__init__.py")
    else:
        print("❌ Could not find appropriate place to insert filter registration")

def verify_setup():
    """Verify that the setup is correct"""
    print("\n" + "="*50)
    print("VERIFICATION")
    print("="*50)
    
    # Check if filters.py exists
    if os.path.exists('app/filters.py'):
        print("✅ app/filters.py exists")
    else:
        print("❌ app/filters.py not found")
    
    # Check if current_year is defined in filters.py
    if os.path.exists('app/filters.py'):
        with open('app/filters.py', 'r') as f:
            content = f.read()
            if 'def current_year' in content:
                print("✅ current_year function defined")
            else:
                print("❌ current_year function not found in filters.py")
    
    # Check if __init__.py has the registration
    if os.path.exists('app/__init__.py'):
        with open('app/__init__.py', 'r') as f:
            content = f.read()
            if 'register_filters' in content:
                print("✅ Filters registered in __init__.py")
            else:
                print("❌ Filters not registered in __init__.py")

if __name__ == "__main__":
    print("="*50)
    print("SETTING UP TEMPLATE FILTERS")
    print("="*50)
    
    create_filters_file()
    update_init_py()
    verify_setup()
    
    print("\n" + "="*50)
    print("✅ Setup complete! Restart your Flask app.")
    print("="*50)