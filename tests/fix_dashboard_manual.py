# fix_dashboard_manual.py
import os
import re

def manually_fix_dashboard():
    """Manually fix dashboard.html by directly replacing the problematic line"""
    
    filepath = 'app/templates/donor/dashboard.html'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the problematic line
    pattern = r'value="{{ url_for\(\'donor\.public_profile\', donor_id=donor\.id, _external=True\) }}"'
    
    if re.search(pattern, content):
        # Replace with corrected version
        new_content = re.sub(
            pattern,
            'value="{{ url_for(\'index\', _external=True) }}"',
            content
        )
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully fixed dashboard.html - removed public_profile reference")
        return True
    else:
        print("ℹ️ The pattern was not found. Let's check what's actually in the file...")
        
        # Let's find what's actually there
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'profileLink' in line and 'value=' in line:
                print(f"Line {i+1}: {line.strip()}")
                return False
        
        print("Could not find the profileLink line. Manual check needed.")
        return False

def check_current_status():
    """Check current status of dashboard.html"""
    filepath = 'app/templates/donor/dashboard.html'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the share modal section
    share_modal_pattern = r'<div class="modal fade" id="shareModal".*?</div>\s*</div>\s*</div>'
    share_modal = re.search(share_modal_pattern, content, re.DOTALL)
    
    if share_modal:
        print("📋 Current share modal content:")
        print("-" * 40)
        print(share_modal.group(0)[:500] + "...")  # Show first 500 chars
        print("-" * 40)
        
        # Check if public_profile is still there
        if 'public_profile' in share_modal.group(0):
            print("❌ 'public_profile' still found in share modal")
        else:
            print("✅ No 'public_profile' found in share modal")
        
        # Check what's in the value attribute
        value_match = re.search(r'value="([^"]+)"', share_modal.group(0))
        if value_match:
            print(f"📝 Current profile link value: {value_match.group(1)}")
    else:
        print("❌ Could not find share modal in dashboard.html")

if __name__ == "__main__":
    print("="*60)
    print("MANUAL FIX FOR DASHBOARD.HTML")
    print("="*60)
    
    print("\n📋 Current status:")
    check_current_status()
    
    print("\n🔧 Attempting fix...")
    result = manually_fix_dashboard()
    
    if result:
        print("\n✅ Fix applied successfully!")
        print("\n📋 New status:")
        check_current_status()
    else:
        print("\n❌ Automatic fix failed. Please manually edit the file:")
        print("   File: app/templates/donor/dashboard.html")
        print("   Find the line with 'profileLink' and change it to:")
        print('   value="{{ url_for(\'index\', _external=True) }}" readonly>')
    
    print("\n" + "="*60)