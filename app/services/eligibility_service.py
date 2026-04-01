"""
Eligibility Service for checking donor eligibility
"""

from datetime import datetime, timedelta
from flask import current_app
from app import db  # Add this for database operations
from app.models.donation import Donation  # Add this import

class EligibilityService:
    """Service for checking and managing donor eligibility"""
    
    # Donation rules
    MIN_AGE = 18
    MAX_AGE = 65
    MIN_WEIGHT_KG = 45
    DONATION_INTERVAL_DAYS = 90
    MAX_DONATIONS_PER_YEAR = 4
    
    # Disqualifying medical conditions
    DISQUALIFYING_CONDITIONS = [
        'hiv', 'aids', 'hepatitis b', 'hepatitis c', 'cancer', 'malignancy',
        'heart disease', 'cardiac', 'stroke', 'bleeding disorder', 'hemophilia',
        'diabetes uncontrolled', 'epilepsy', 'tuberculosis', 'malaria'
    ]
    
    # Temporary disqualifications (with waiting periods)
    TEMPORARY_CONDITIONS = {
        'pregnancy': 365,
        'surgery': 180,
        'dental': 7,
        'tattoo': 180,
        'vaccination': 28,
        'covid': 14,
        'flu': 7,
        'antibiotics': 14,
        'alcohol': 1
    }
    
    @classmethod
    def check_eligibility(cls, donor):
        """
        Comprehensive eligibility check for a donor
        Returns (is_eligible, message, next_eligible_date)
        """
        try:
            # Check availability
            if not donor.is_available:
                return False, "Donor is marked as unavailable", None
            
            # Check age
            age = donor.calculate_age()
            if age < cls.MIN_AGE:
                return False, f"Donor must be at least {cls.MIN_AGE} years old", None
            if age > cls.MAX_AGE:
                return False, f"Donor must be under {cls.MAX_AGE} years old", None
            
            # Check weight
            if donor.weight < cls.MIN_WEIGHT_KG:
                return False, f"Donor must weigh at least {cls.MIN_WEIGHT_KG} kg", None
            
            # Check donation interval
            if donor.last_donation_date:
                days_since = (datetime.now() - donor.last_donation_date).days
                if days_since < cls.DONATION_INTERVAL_DAYS:
                    next_date = donor.last_donation_date + timedelta(days=cls.DONATION_INTERVAL_DAYS)
                    return False, f"Must wait {cls.DONATION_INTERVAL_DAYS - days_since} more days", next_date.date()
            
            # Check annual limit
            current_year = datetime.now().year
            donations_this_year = donor.donation_history.filter(
                db.extract('year', Donation.donation_date) == current_year
            ).count()
            
            if donations_this_year >= cls.MAX_DONATIONS_PER_YEAR:
                next_year_date = datetime(current_year + 1, 1, 1)
                return False, f"Maximum {cls.MAX_DONATIONS_PER_YEAR} donations per year reached", next_year_date.date()
            
            # Check medical conditions
            if donor.medical_conditions:
                conditions_lower = donor.medical_conditions.lower()
                for condition in cls.DISQUALIFYING_CONDITIONS:
                    if condition in conditions_lower:
                        return False, f"Medical condition '{condition}' may prevent donation", None
                
                # Check temporary conditions
                for condition, wait_days in cls.TEMPORARY_CONDITIONS.items():
                    if condition in conditions_lower:
                        next_date = datetime.now() + timedelta(days=wait_days)
                        return False, f"Temporary deferral for {condition}", next_date.date()
            
            # All checks passed
            return True, "Donor is eligible", None
            
        except Exception as e:
            current_app.logger.error(f"Eligibility check error: {e}")
            return False, "Error checking eligibility", None
    
    @classmethod
    def get_eligibility_summary(cls, donor):
        """
        Get detailed eligibility summary
        """
        is_eligible, message, next_date = cls.check_eligibility(donor)
        
        summary = {
            'is_eligible': is_eligible,
            'message': message,
            'next_eligible_date': next_date,
            'age': donor.calculate_age(),
            'weight': donor.weight,
            'last_donation': donor.last_donation_date,
            'days_since_last_donation': None,
            'can_donate_now': is_eligible
        }
        
        if donor.last_donation_date:
            days_since = (datetime.now() - donor.last_donation_date).days
            summary['days_since_last_donation'] = days_since
            summary['days_until_eligible'] = max(0, cls.DONATION_INTERVAL_DAYS - days_since)
        
        return summary