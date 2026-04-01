# fix_donor_errors.py
import os
import re

def fix_donor_routes():
    """Update donor routes with all necessary template variables"""
    filepath = 'app/blueprints/donor/routes.py'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add datetime import if missing
    if 'from datetime import datetime, timedelta' not in content:
        content = content.replace(
            'from datetime import datetime',
            'from datetime import datetime, timedelta'
        )
    
    # Add public_profile route at the end
    public_profile_route = '''

@donor_bp.route('/public/<int:donor_id>')
def public_profile(donor_id):
    """Public donor profile - no login required"""
    donor = Donor.query.get_or_404(donor_id)
    
    # Get public donations (only verified ones)
    donations = Donation.query.filter_by(
        donor_id=donor.user_id,
        is_verified=True
    ).order_by(Donation.donation_date.desc()).limit(10).all()
    
    return render_template('donor/public_profile.html',
                         donor=donor,
                         donations=donations,
                         current_year=datetime.now().year,
                         title=f"{donor.user.name}'s Profile")'''
    
    if '@donor_bp.route(\'/public/<int:donor_id>\')' not in content:
        content += public_profile_route
        print("✅ Added public_profile route")
    
    # Update render_template calls to include current_year and now
    patterns = [
        (r"return render_template\('donor/dashboard\.html',(.*?)\)", 
         lambda m: add_template_vars(m, 'donor/dashboard.html', ['donor', 'total_donations', 'recent_donations', 'eligibility', 'nearby_requests'])),
        
        (r"return render_template\('donor/donation_history\.html',(.*?)\)",
         lambda m: add_template_vars(m, 'donor/donation_history.html', ['donations'])),
        
        (r"return render_template\('donor/eligibility_status\.html',(.*?)\)",
         lambda m: add_template_vars(m, 'donor/eligibility_status.html', ['donor', 'eligibility'])),
    ]
    
    for pattern, repl_func in patterns:
        content = re.sub(pattern, repl_func, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated donor routes with template variables")

def add_template_vars(match, template_name, existing_vars):
    """Helper function to add template variables"""
    existing = match.group(1)
    
    if 'current_year' not in existing:
        existing = existing.rstrip() + ',\n                         current_year=datetime.now().year'
    
    if 'now' not in existing and template_name != 'donor/edit_profile.html':
        existing = existing.rstrip() + ',\n                         now=datetime.now'
    
    if 'timedelta' not in existing and template_name == 'donor/dashboard.html':
        existing = existing.rstrip() + ',\n                         timedelta=timedelta'
    
    return f"return render_template('{template_name}',{existing})"

def fix_dashboard_html():
    """Fix dashboard.html share modal"""
    filepath = 'app/templates/donor/dashboard.html'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the profile link in share modal
    content = re.sub(
        r'value="{{ url_for\(\'donor\.public_profile\', donor_id=donor\.id, _external=True\) }}"',
        'value="{{ url_for(\'index\', _external=True) }}"',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed dashboard.html share modal")

def fix_donation_history_html():
    """Fix donation_history.html 'now' error"""
    filepath = 'app/templates/donor/donation_history.html'
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the year filter section
    pattern = r'<option value="\{\{ year \}\}">\{\{ year \}\}<\/option>\s*{% endfor %}'
    replacement = '<option value="{{ year }}">{{ year }}</option>\n                        {% endfor %}'
    content = re.sub(pattern, replacement, content)
    
    # Add current_year variable at the top
    if '{% set current_year = now().year %}' not in content:
        content = content.replace(
            '{% block content %}',
            '{% block content %}\n{% set current_year = now().year %}'
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed donation_history.html")

def create_public_profile_template():
    """Create public_profile.html template"""
    template_path = 'app/templates/donor/public_profile.html'
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    content = '''{% extends "base.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-4 mb-4">
            <div class="card shadow-sm">
                <div class="card-body text-center">
                    <img src="{{ url_for('static', filename='images/default-avatar.png') }}" 
                         class="rounded-circle img-fluid mb-3" style="width: 120px; height: 120px; object-fit: cover;">
                    <h4>{{ donor.user.name }}</h4>
                    <p class="text-muted">
                        <span class="badge bg-danger">{{ donor.blood_type }}</span>
                    </p>
                    <p>
                        <i class="fas fa-map-marker-alt text-danger me-1"></i>
                        {{ donor.city }}, {{ donor.state }}
                    </p>
                    <p>
                        <i class="fas fa-tint text-danger me-1"></i>
                        Total Donations: {{ donor.total_donations }}
                    </p>
                    {% if donor.last_donation_date %}
                    <p>
                        <i class="fas fa-calendar text-danger me-1"></i>
                        Last Donation: {{ donor.last_donation_date.strftime('%d %b, %Y') }}
                    </p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card shadow-sm">
                <div class="card-header bg-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-history text-danger me-2"></i>Recent Donations
                    </h5>
                </div>
                <div class="card-body">
                    {% if donations %}
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Location</th>
                                        <th>Units</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for donation in donations %}
                                    <tr>
                                        <td>{{ donation.donation_date.strftime('%d %b, %Y') }}</td>
                                        <td>{{ donation.donation_center or 'Blood Camp' }}</td>
                                        <td>{{ donation.units_donated }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    {% else %}
                        <p class="text-muted text-center py-4">No public donation history available.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created public_profile.html template")

if __name__ == "__main__":
    print("="*60)
    print("FIXING DONOR SECTION ERRORS")
    print("="*60)
    
    print("\n📁 Step 1: Fixing donor routes...")
    fix_donor_routes()
    
    print("\n📁 Step 2: Fixing dashboard.html...")
    fix_dashboard_html()
    
    print("\n📁 Step 3: Fixing donation_history.html...")
    fix_donation_history_html()
    
    print("\n📁 Step 4: Creating public profile template...")
    create_public_profile_template()
    
    print("\n" + "="*60)
    print("✅ ALL FIXES COMPLETE!")
    print("="*60)
    print("\nNow restart your Flask app:")
    print("python run.py")