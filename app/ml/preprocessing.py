"""
ML Preprocessing - Feature engineering for ML models
"""

import pandas as pd
import numpy as np
from datetime import datetime

def prepare_donor_features(donor_data):
    """Prepare features for donor availability prediction"""
    features = {}
    
    # Temporal features
    now = datetime.now()
    features['day_of_week'] = now.weekday()
    features['hour'] = now.hour
    features['month'] = now.month
    features['is_weekend'] = 1 if now.weekday() >= 5 else 0
    
    # Donor features
    features['age'] = donor_data.get('age', 30)
    features['blood_type'] = donor_data.get('blood_type', 'O+')
    features['previous_donations'] = donor_data.get('total_donations', 0)
    
    # Donation history features
    days_since_last = donor_data.get('days_since_last', 999)
    features['days_since_last_donation'] = min(days_since_last, 365)
    features['has_donated_before'] = 1 if donor_data.get('last_donation_date') else 0
    
    # Derived features
    if days_since_last < 90:
        features['recently_donated'] = 1
    else:
        features['recently_donated'] = 0
    
    if donor_data.get('total_donations', 0) > 5:
        features['is_regular_donor'] = 1
    else:
        features['is_regular_donor'] = 0
    
    # Time of day category
    if 5 <= now.hour <= 11:
        features['time_category'] = 'morning'
    elif 12 <= now.hour <= 16:
        features['time_category'] = 'afternoon'
    elif 17 <= now.hour <= 20:
        features['time_category'] = 'evening'
    else:
        features['time_category'] = 'night'
    
    return features

def prepare_demand_features(blood_type=None, date=None):
    """Prepare features for demand prediction"""
    if date is None:
        date = datetime.now()
    
    features = {}
    
    # Temporal features
    features['month'] = date.month
    features['day_of_week'] = date.weekday()
    features['quarter'] = (date.month - 1) // 3 + 1
    
    # Season
    if date.month in [12, 1, 2]:
        features['season'] = 'winter'
    elif date.month in [3, 4, 5]:
        features['season'] = 'spring'
    elif date.month in [6, 7, 8]:
        features['season'] = 'summer'
    else:
        features['season'] = 'fall'
    
    # Blood type
    features['blood_type'] = blood_type if blood_type else 'O+'
    
    # Holiday season
    if date.month == 12 and date.day >= 20:
        features['is_holiday_season'] = 1
    elif date.month == 1 and date.day <= 5:
        features['is_holiday_season'] = 1
    else:
        features['is_holiday_season'] = 0
    
    # Weekend
    features['is_weekend'] = 1 if date.weekday() >= 5 else 0
    
    return features

def create_donor_training_dataset(donors, donations):
    """Create training dataset for donor model"""
    data = []
    
    for donor in donors:
        # Get donor's donation history
        donor_donations = [d for d in donations if d['donor_id'] == donor['id']]
        
        # Calculate features
        features = {
            'donor_id': donor['id'],
            'age': donor['age'],
            'blood_type': donor['blood_type'],
            'gender': donor['gender'],
            'weight': donor['weight'],
            'total_donations': len(donor_donations),
            'city': donor['city'],
            'state': donor['state']
        }
        
        # Add temporal features for each donation
        for donation in donor_donations[-10:]:  # Last 10 donations
            donation_features = features.copy()
            donation_features.update({
                'donation_date': donation['donation_date'],
                'day_of_week': donation['donation_date'].weekday(),
                'month': donation['donation_date'].month,
                'days_since_last': donation.get('days_since_last', 0),
                'is_emergency': donation.get('is_emergency', 0)
            })
            data.append(donation_features)
    
    return pd.DataFrame(data)

def create_demand_training_dataset(requests):
    """Create training dataset for demand model"""
    data = []
    
    # Group requests by date and blood type
    for request in requests:
        features = {
            'date': request['created_at'].date(),
            'month': request['created_at'].month,
            'day_of_week': request['created_at'].weekday(),
            'blood_type': request['blood_type_needed'],
            'is_emergency': 1 if request['urgency'] == 'emergency' else 0,
            'units': request['units_needed']
        }
        data.append(features)
    
    df = pd.DataFrame(data)
    
    # Aggregate by date and blood type
    aggregated = df.groupby(['date', 'blood_type']).agg({
        'units': 'sum',
        'is_emergency': 'sum',
        'month': 'first',
        'day_of_week': 'first'
    }).reset_index()
    
    # Add seasonal features
    aggregated['season'] = aggregated['date'].apply(
        lambda x: (x.month % 12 + 3) // 3
    )
    
    # Add lag features
    for blood_type in aggregated['blood_type'].unique():
        mask = aggregated['blood_type'] == blood_type
        values = aggregated.loc[mask, 'units'].values
        aggregated.loc[mask, 'lag_1'] = np.roll(values, 1)
        aggregated.loc[mask, 'lag_7'] = np.roll(values, 7)
    
    return aggregated

def normalize_features(df, feature_cols):
    """Normalize numerical features"""
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    
    return df, scaler

def encode_categorical(df, categorical_cols):
    """Encode categorical features"""
    from sklearn.preprocessing import LabelEncoder
    
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    
    return df, encoders