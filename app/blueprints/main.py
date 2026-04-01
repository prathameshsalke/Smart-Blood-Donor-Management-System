# """
# Main Blueprint - Public pages
# """

# from flask import render_template, request, Blueprint, current_app, redirect, url_for
# from app.models.donor import Donor
# from app.models.hospital import Hospital

# # No blueprint, just a function to register routes

# def register_main_routes(app):
#     """Register main routes with the app"""
    
#     @app.route('/')
#     def index():
#         """Home page"""
#         # Get statistics
#         total_donors = Donor.query.count()
#         eligible_donors = Donor.query.filter_by(is_eligible=True).count()
#         total_hospitals = Hospital.query.count()
        
#         stats = {
#             'total_donors': total_donors,
#             'eligible_donors': eligible_donors,
#             'total_hospitals': total_hospitals,
#             'lives_saved': total_donors * 3  # Estimate (each donation can save up to 3 lives)
#         }
        
#         return render_template('public/index.html', title='Home', stats=stats)
    
#     @app.route('/about')
#     def about():
#         """About page"""
#         return render_template('public/about.html', title='About Us')
    
#     @app.route('/contact')
#     def contact():
#         """Contact page"""
#         return render_template('public/contact.html', title='Contact Us')
    
#     @app.route('/faq')
#     def faq():
#         """FAQ page"""
#         return render_template('public/faq.html', title='FAQ')
    
#     @app.route('/search-donors')
#     def search_donors():
#         """Public donor search page - Redirects to donor nearby donors"""
#         # Redirect to the donor's nearby donors page
#         # This is a temporary solution until the public search page is implemented
#         return redirect(url_for('donor.nearby_donors'))
    
#     @app.route('/emergency')
#     def emergency():
#         """Emergency request page (public)"""
#         # This renders the emergency information page
#         # For actual emergency requests, users will be directed to login/register
#         return render_template('public/emergency.html', title='Emergency Request')

"""
Main Blueprint - Public pages
"""

from flask import render_template, request, Blueprint, current_app, redirect, url_for
from app.models.donor import Donor
from app.models.hospital import Hospital

# No blueprint, just a function to register routes

def register_main_routes(app):
    """Register main routes with the app"""
    
    @app.route('/')
    def index():
        """Home page"""
        # Get statistics
        total_donors = Donor.query.count()
        eligible_donors = Donor.query.filter_by(is_eligible=True).count()
        total_hospitals = Hospital.query.count()
        
        stats = {
            'total_donors': total_donors,
            'eligible_donors': eligible_donors,
            'total_hospitals': total_hospitals,
            'lives_saved': total_donors * 3  # Estimate
        }
        
        return render_template('public/index.html', title='Home', stats=stats)
    
    @app.route('/about')
    def about():
        """About page"""
        return render_template('public/about.html', title='About Us')
    
    @app.route('/contact')
    def contact():
        """Contact page"""
        return render_template('public/contact.html', title='Contact Us')
    
    @app.route('/faq')
    def faq():
        """FAQ page"""
        return render_template('public/faq.html', title='FAQ')
    
    @app.route('/search-donors')
    def search_donors():
        """Public donor search page"""
        # Redirect logged-in donors to their nearby donors page
        from flask_login import current_user
        if current_user.is_authenticated and current_user.is_donor():
            return redirect(url_for('donor.nearby_donors'))
        return render_template('public/search_donors.html', title='Find Donors')
    
    @app.route('/emergency')
    def emergency():
        """Emergency request page"""
        from flask_login import current_user
        # If user is logged in as donor, redirect to donor emergency search
        if current_user.is_authenticated and current_user.is_donor():
            return redirect(url_for('donor.emergency_search'))
        # Otherwise show public emergency page with instructions
        return render_template('public/emergency_public.html', title='Emergency Help')