"""
Retrain ML model with features that match your actual donor data
Run: python ml/retrain_with_your_data.py
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def retrain_with_real_data():
    """Retrain model using actual donor data from database"""
    
    try:
        from app import create_app, db
        from app.models.donor import Donor
        from app.models.donation import Donation
        
        app = create_app()
        
        with app.app_context():
            print("📊 Loading donor data from database...")
            
            # Get all donors
            donors = Donor.query.all()
            
            if len(donors) < 100:
                print(f"⚠️ Only {len(donors)} donors found. Using synthetic data instead.")
                return retrain_with_synthetic_data()
            
            # Prepare training data
            data = []
            for donor in donors:
                # Get their donation history
                donations = Donation.query.filter_by(donor_id=donor.user_id).count()
                
                # Calculate days since last donation
                days_since_last = 999
                if donor.last_donation_date:
                    days_since_last = (datetime.now() - donor.last_donation_date).days
                
                # Determine if they would donate (based on eligibility and availability)
                would_donate = 1 if donor.is_eligible and donor.is_available else 0
                
                data.append({
                    'age': donor.calculate_age(),
                    'gender': donor.gender,
                    'weight': donor.weight,
                    'blood_type': donor.blood_type,
                    'total_donations': donor.total_donations,
                    'days_since_last': days_since_last,
                    'month': datetime.now().month,
                    'day_of_week': datetime.now().weekday(),
                    'hour': datetime.now().hour,
                    'would_donate': would_donate
                })
            
            df = pd.DataFrame(data)
            print(f"✅ Loaded {len(df)} donor records")
            
            # Prepare features
            features = ['age', 'gender', 'weight', 'blood_type', 
                       'total_donations', 'days_since_last', 
                       'month', 'day_of_week', 'hour']
            
            X = df[features].copy()
            y = df['would_donate']
            
            # Encode categorical variables
            encoders = {}
            
            # Encode gender
            le_gender = LabelEncoder()
            X['gender'] = le_gender.fit_transform(X['gender'].astype(str))
            encoders['gender'] = le_gender
            
            # Encode blood type
            le_blood = LabelEncoder()
            X['blood_type'] = le_blood.fit_transform(X['blood_type'].astype(str))
            encoders['blood_type'] = le_blood
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            print("🔄 Training Random Forest model...")
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            accuracy = model.score(X_test, y_test)
            print(f"\n✅ Model accuracy: {accuracy:.3f}")
            
            # Feature importance
            importance = dict(zip(features, model.feature_importances_))
            print("\n📊 Feature Importance:")
            for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                print(f"   {feature}: {imp:.3f}")
            
            # Save model and encoders
            os.makedirs('ml_models', exist_ok=True)
            
            model_path = 'ml_models/donor_model.pkl'
            joblib.dump(model, model_path)
            print(f"\n✅ Model saved to {model_path}")
            
            # Save encoders
            for name, encoder in encoders.items():
                encoder_path = f'ml_models/donor_{name}_encoder.pkl'
                joblib.dump(encoder, encoder_path)
                print(f"✅ {name} encoder saved")
            
            print(f"\n🎯 Features used: {features}")
            
            return model, encoders
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return retrain_with_synthetic_data()

def retrain_with_synthetic_data():
    """Fallback: Retrain with synthetic data"""
    print("\n🔄 Generating synthetic training data...")
    
    np.random.seed(42)
    n_samples = 5000
    
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    genders = ['male', 'female', 'other']
    
    data = pd.DataFrame({
        'age': np.random.randint(18, 65, n_samples),
        'gender': np.random.choice(genders, n_samples),
        'weight': np.random.randint(45, 100, n_samples),
        'blood_type': np.random.choice(blood_types, n_samples),
        'total_donations': np.random.randint(0, 20, n_samples),
        'days_since_last': np.random.randint(0, 365, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'hour': np.random.randint(8, 20, n_samples),
    })
    
    # Create target based on realistic rules
    data['would_donate'] = (
        (data['days_since_last'] > 90) & 
        (data['age'].between(20, 55)) &
        (data['weight'] > 50)
    ).astype(int)
    
    features = ['age', 'gender', 'weight', 'blood_type', 
                'total_donations', 'days_since_last', 
                'month', 'day_of_week', 'hour']
    
    X = data[features].copy()
    y = data['would_donate']
    
    # Encode categorical
    encoders = {}
    
    le_gender = LabelEncoder()
    X['gender'] = le_gender.fit_transform(X['gender'])
    encoders['gender'] = le_gender
    
    le_blood = LabelEncoder()
    X['blood_type'] = le_blood.fit_transform(X['blood_type'])
    encoders['blood_type'] = le_blood
    
    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"✅ Model trained with accuracy: {accuracy:.3f}")
    
    # Save
    os.makedirs('ml_models', exist_ok=True)
    joblib.dump(model, 'ml_models/donor_model.pkl')
    
    for name, encoder in encoders.items():
        joblib.dump(encoder, f'ml_models/donor_{name}_encoder.pkl')
    
    print(f"✅ Features used: {features}")
    
    return model, encoders

if __name__ == "__main__":
    print("="*60)
    print("🔄 RETRAINING ML MODEL WITH YOUR DATA")
    print("="*60)
    
    retrain_with_real_data()
    
    print("\n" + "="*60)
    print("✅ Model retraining complete!")
    print("="*60)