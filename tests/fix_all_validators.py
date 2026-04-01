# fix_all_validators.py
import os
import re

def fix_all_validator_files():
    """Fix all marshmallow validator files by replacing 'missing' with 'load_default'"""
    
    # Directories to check
    directories = [
        'app/validators',
        'app/schemas'  # Also check schemas folder
    ]
    
    total_fixed = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"⚠️ Directory not found: {directory}")
            continue
            
        print(f"\n📁 Checking {directory}...")
        
        for filename in os.listdir(directory):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(directory, filename)
                fixed = fix_file(filepath)
                if fixed:
                    print(f"  ✅ Fixed: {filename}")
                    total_fixed += 1
    
    print(f"\n🎯 Total files fixed: {total_fixed}")
    
    # Also check for any other files that might have the issue
    print("\n📝 Additional files to check manually:")
    print("   - app/blueprints/api/*.py")
    print("   - app/forms/*.py (if exists)")

def fix_file(filepath):
    """Fix a single file by replacing 'missing' with 'load_default'"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find fields.Bool(missing=...), fields.Int(missing=...), etc.
        pattern = r'fields\.(\w+)\(missing=([^,)]+)([^)]*)\)'
        
        def replacement(match):
            field_type = match.group(1)
            missing_value = match.group(2)
            rest_params = match.group(3)
            return f'fields.{field_type}(load_default={missing_value}{rest_params})'
        
        new_content = re.sub(pattern, replacement, content)
        
        # Also handle cases with multiple parameters
        pattern2 = r'fields\.(\w+)\(([^)]*?)missing=([^,)]+)([^)]*)\)'
        
        def replacement2(match):
            field_type = match.group(1)
            before = match.group(2)
            missing_value = match.group(3)
            after = match.group(4)
            
            # Remove trailing comma if needed
            if before and not before.endswith(', '):
                before += ', '
            
            return f'fields.{field_type}({before}load_default={missing_value}{after})'
        
        new_content = re.sub(pattern2, replacement2, new_content)
        
        # Also handle simple missing without field specification
        new_content = re.sub(r'(\s+)missing=(\d+)', r'\1load_default=\2', new_content)
        new_content = re.sub(r'(\s+)missing=([\'"])([^\'"]+)([\'"])', r'\1load_default=\2\3\4', new_content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
        
    except Exception as e:
        print(f"  ❌ Error fixing {os.path.basename(filepath)}: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("🔧 Marshmallow Validator Fix Tool")
    print("="*50)
    fix_all_validator_files()
    print("\n✅ Fix complete! Try running your app now.")