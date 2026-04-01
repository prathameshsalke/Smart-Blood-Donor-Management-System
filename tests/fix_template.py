# fix_template.py
import os

def fix_base_template():
    """Fix the base.html template by removing any extra endblock"""
    template_path = 'app/templates/base.html'
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count blocks and endblocks
    block_count = content.count('{% block ')
    endblock_count = content.count('{% endblock')
    
    print(f"Found {block_count} 'block' tags and {endblock_count} 'endblock' tags")
    
    if block_count == endblock_count:
        print("✅ Block counts match")
    else:
        print(f"❌ Mismatch: {block_count} blocks vs {endblock_count} endblocks")
    
    # Look for any endblock without a matching block
    lines = content.split('\n')
    fixed_lines = []
    block_stack = []
    
    for i, line in enumerate(lines):
        if '{% block ' in line:
            # Extract block name
            import re
            match = re.search(r'{% block (\w+)', line)
            if match:
                block_stack.append(match.group(1))
            fixed_lines.append(line)
        elif '{% endblock' in line:
            if block_stack:
                block_stack.pop()
                fixed_lines.append(line)
            else:
                print(f"⚠️ Extra endblock at line {i+1}, removing")
                # Skip this line (don't add it)
        else:
            fixed_lines.append(line)
    
    if block_stack:
        print(f"⚠️ Unclosed blocks: {block_stack}")
    
    # Write fixed content
    if len(fixed_lines) != len(lines):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("✅ Fixed template saved")
    else:
        print("✅ No issues found")

if __name__ == "__main__":
    fix_base_template()