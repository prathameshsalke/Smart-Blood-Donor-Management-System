"""
Model Retraining Task - Periodically retrain ML models
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import current_app
from app import create_app
from app.models.donor import Donor
from app.models.donation import Donation
from app.models.blood_request import BloodRequest
from app.ml.train_model import train_donor_model, train_demand_model
from app.utils.logger import logger

def retrain_models():
    """Retrain all ML models with latest data"""
    app = create_app()
    with app.app_context():
        try:
            logger.info("Starting model retraining...")
            
            # Retrain donor model
            donor_success = retrain_donor_model()
            
            # Retrain demand model
            demand_success = retrain_demand_model()
            
            if donor_success and demand_success:
                logger.info("Model retraining completed successfully")
                return True
            else:
                logger.error("Model retraining failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in model retraining: {str(e)}")
            return False

def retrain_donor_model():
    """Retrain donor availability prediction model"""
    try:
        # Get training data
        training_data = prepare_donor_training_data()
        
        if len(training_data) < 100:
            logger.warning(f"Insufficient training data: {len(training_data)} samples")
            return False
        
        # Train model
        model, accuracy = train_donor_model(training_data)
        
        logger.info(f"Donor model retrained with accuracy: {accuracy}")
        return True
        
    except Exception as e:
        logger.error(f"Error retraining donor model: {str(e)}")
        return False

def retrain_demand_model():
    """Retrain demand forecasting model"""
    try:
        # Get training data
        training_data = prepare_demand_training_data()
        
        if len(training_data) < 50:
            logger.warning(f"Insufficient training data: {len(training_data)} samples")
            return False
        
        # Train model
        model, score = train_demand_model(training_data)
        
        logger.info(f"Demand model retrained with R² score: {score}")
        return True
        
    except Exception as e:
        logger.error(f"Error retraining demand model: {str(e)}")
        return False

def prepare_donor_training_data():
    """Prepare training data for donor model"""
    data = []
    
    # Get all donors
    donors = Donor.query.all()
    
    for donor in donors:
        # Get donation history
        donations = Donation.query.filter_by(donor_id=donor.user_id)\
                                 .order_by(Donation.donation_date).all()
        
        # Create training samples
        for i, donation in enumerate(donations):
            # Features
            sample = {
                'donor_id': donor.id,
                'age': donor.calculate_age(),
                'blood_type': donor.blood_type,
                'gender': donor.gender,
                'weight': donor.weight,
                'donation_month': donation.donation_date.month,
                'donation_day': donation.donation_date.weekday(),
                'donation_hour': donation.donation_date.hour,
                'previous_donations': i,
                'is_weekend': 1 if donation.donation_date.weekday() >= 5 else 0
            }
            
            # Target: whether they donated again within 90 days
            if i < len(donations) - 1:
                next_donation = donations[i + 1]
                days_between = (next_donation.donation_date - donation.donation_date).days
                sample['donated_again'] = 1 if days_between <= 90 else 0
            else:
                sample['donated_again'] = 0
            
            data.append(sample)
    
    return pd.DataFrame(data)

def prepare_demand_training_data():
    """Prepare training data for demand model"""
    # Get all blood requests
    requests = BloodRequest.query.all()
    
    if not requests:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        'date': r.created_at.date(),
        'month': r.created_at.month,
        'day_of_week': r.created_at.weekday(),
        'blood_type': r.blood_type_needed,
        'units': r.units_needed,
        'is_emergency': 1 if r.urgency == 'emergency' else 0
    } for r in requests])
    
    # Aggregate by date and blood type
    aggregated = df.groupby(['date', 'blood_type']).agg({
        'units': 'sum',
        'is_emergency': 'sum',
        'month': 'first',
        'day_of_week': 'first'
    }).reset_index()
    
    # Sort by date
    aggregated = aggregated.sort_values('date')
    
    # Add lag features
    for blood_type in aggregated['blood_type'].unique():
        mask = aggregated['blood_type'] == blood_type
        values = aggregated.loc[mask, 'units'].values
        
        if len(values) > 7:
            # 7-day lag
            aggregated.loc[mask, 'lag_7'] = np.roll(values, 7)
            # 30-day lag
            aggregated.loc[mask, 'lag_30'] = np.roll(values, 30)
    
    return aggregated

def schedule_retraining():
    """Schedule periodic model retraining"""
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Retrain every Sunday at 2 AM
    scheduler.add_job(
        func=retrain_models,
        trigger="cron",
        day_of_week='sun',
        hour=2,
        minute=0
    )
    
    scheduler.start()
    logger.info("Model retraining scheduled")

if __name__ == "__main__":
    # Run retraining immediately
    retrain_models()