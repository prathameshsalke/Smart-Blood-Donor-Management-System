"""
ML Model Training Script
Run this script to train the ML models using real dataset files
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== FALLBACK SYNTHETIC DATA FUNCTIONS ====================
def generate_sample_donor_data(n_samples=1000):
    """Generate sample donor data for training (fallback if real data not available)"""
    print(f"📊 Generating {n_samples} synthetic donor records...")
    np.random.seed(42)
    
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    genders = ['male', 'female', 'other']
    
    data = {
        'age': np.random.randint(18, 65, n_samples),
        'weight': np.random.randint(45, 100, n_samples),
        'hemoglobin': np.random.uniform(11, 16, n_samples).round(1),
        'month': np.random.randint(1, 13, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'hour': np.random.randint(8, 20, n_samples),
        'blood_type': np.random.choice(blood_types, n_samples),
        'gender': np.random.choice(genders, n_samples),
        'is_first_donation': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'is_emergency': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'total_donations': np.random.randint(0, 20, n_samples),
        'days_since_last': np.random.randint(0, 200, n_samples),
        'will_donate_again': np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
    }
    
    return pd.DataFrame(data)

def generate_sample_demand_data(n_samples=500):
    """Generate sample demand data for training (fallback if real data not available)"""
    print(f"📊 Generating {n_samples} synthetic demand records...")
    np.random.seed(42)
    
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    seasons = ['winter', 'spring', 'summer', 'fall']
    
    data = {
        'month': np.random.randint(1, 13, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'blood_type': np.random.choice(blood_types, n_samples),
        'is_emergency': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'season': np.random.choice(seasons, n_samples),
        'is_weekend': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'is_holiday': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        'demand_units': np.random.randint(30, 300, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Map season to numeric
    season_map = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
    df['season_numeric'] = df['season'].map(season_map)
    
    return df

# ==================== DATA LOADING FUNCTIONS ====================
def load_donor_history_data():
    """Load and prepare donor history data from CSV"""
    csv_path = os.path.join('dataset', 'donor_history.csv')
    
    if not os.path.exists(csv_path):
        print(f"⚠️ Donor history CSV not found at {csv_path}")
        return None
    
    print(f"📊 Loading donor history data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   Loaded {len(df)} donation records")
    
    # Parse datetime - FIXED: Handle DD-MM-YYYY format
    try:
        df['donation_date'] = pd.to_datetime(df['donation_date'], format='%d-%m-%Y %H:%M:%S')
    except:
        try:
            df['donation_date'] = pd.to_datetime(df['donation_date'], format='%Y-%m-%d %H:%M:%S')
        except:
            df['donation_date'] = pd.to_datetime(df['donation_date'], dayfirst=True)
    
    # Extract features from datetime
    df['hour'] = df['donation_date'].dt.hour
    df['day_of_week'] = df['donation_date'].dt.dayofweek
    df['month'] = df['donation_date'].dt.month
    
    # Create target variable: whether donor will donate again within 90 days
    # Group by donor_id and sort by date to calculate next donation
    df_sorted = df.sort_values(['donor_id', 'donation_date'])
    df_sorted['next_donation_date'] = df_sorted.groupby('donor_id')['donation_date'].shift(-1)
    df_sorted['days_to_next'] = (df_sorted['next_donation_date'] - df_sorted['donation_date']).dt.days
    df_sorted['will_donate_again'] = (df_sorted['days_to_next'] <= 90).astype(int)
    
    # Fill NaN (last donation of each donor) with 0 (unknown if they'll donate again)
    df_sorted['will_donate_again'] = df_sorted['will_donate_again'].fillna(0)
    
    print(f"   Created {len(df_sorted)} training samples")
    return df_sorted

def load_blood_demand_data():
    """Load and prepare blood demand data from CSV"""
    csv_path = os.path.join('dataset', 'blood_demand.csv')
    
    if not os.path.exists(csv_path):
        print(f"⚠️ Blood demand CSV not found at {csv_path}")
        return None
    
    print(f"📊 Loading blood demand data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   Loaded {len(df)} demand records")
    
    # Parse date - FIXED: Handle DD-MM-YYYY format
    try:
        # Try DD-MM-YYYY format first
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    except:
        try:
            # Try YYYY-MM-DD format
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        except:
            # Let pandas infer the format
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    
    # Extract features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Map season to numeric if season column exists
    if 'season' in df.columns:
        season_map = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
        df['season_numeric'] = df['season'].map(season_map)
    
    # Ensure is_holiday is integer
    if 'is_holiday' in df.columns:
        df['is_holiday'] = df['is_holiday'].astype(int)
    
    print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    return df

def verify_dataset_files():
    """Verify that dataset files exist"""
    print("\n" + "="*50)
    print("🔍 VERIFYING DATASET FILES")
    print("="*50)
    
    dataset_dir = 'dataset'
    if not os.path.exists(dataset_dir):
        print(f"⚠️ Dataset directory not found: {dataset_dir}")
        print("   Will use synthetic data instead.")
        return False
    
    required_files = ['donor_history.csv', 'blood_demand.csv']
    all_exist = True
    
    for file in required_files:
        path = os.path.join(dataset_dir, file)
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024  # KB
            print(f"✅ {file} found ({size:.1f} KB)")
        else:
            print(f"❌ {file} not found")
            all_exist = False
    
    return all_exist

# ==================== MODEL TRAINING FUNCTIONS ====================
def train_donor_model():
    """Train donor availability prediction model using real data"""
    print("\n" + "="*50)
    print("Training Donor Availability Model")
    print("="*50)
    
    # Try to load real data
    df = load_donor_history_data()
    
    # Fall back to synthetic data if real data not available or insufficient
    using_synthetic = False
    if df is None or len(df) < 100:
        print("\n⚠️ Using synthetic donor data (real data not available or insufficient)")
        df = generate_sample_donor_data(5000)
        using_synthetic = True
    else:
        print("\n✅ Using real donor history data")
    
    # Prepare features
    feature_cols = ['age', 'weight', 'hemoglobin', 'month', 'day_of_week', 'hour', 
                    'blood_type', 'gender', 'is_first_donation', 'is_emergency']
    
    # Select available features
    available_features = [col for col in feature_cols if col in df.columns]
    print(f"\n📋 Using features: {available_features}")
    
    X = df[available_features].copy()
    y = df['will_donate_again']
    
    # Handle categorical variables
    categorical_cols = ['blood_type', 'gender']
    encoders = {}
    
    for col in categorical_cols:
        if col in X.columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
    
    # Handle missing values
    X = X.fillna(0)
    
    # Split data
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if not using_synthetic else None
        )
    except:
        # Fall back to non-stratified split if stratify fails
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    
    print(f"\n📊 Training set: {len(X_train)} samples")
    print(f"📊 Test set: {len(X_test)} samples")
    
    # Train model
    print("\n🔄 Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"\n✅ Model Accuracy: {accuracy:.3f}")
    
    # Feature importance
    importance = dict(zip(available_features, model.feature_importances_))
    print("\n📊 Feature Importance:")
    for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {imp:.3f}")
    
    # Save model and encoders
    os.makedirs('ml_models', exist_ok=True)
    joblib.dump(model, 'ml_models/donor_model.pkl')
    
    # Save encoders
    for name, encoder in encoders.items():
        joblib.dump(encoder, f'ml_models/donor_{name}_encoder.pkl')
    
    # Save feature list for inference
    joblib.dump(available_features, 'ml_models/donor_features.pkl')
    
    print(f"\n💾 Donor model saved to ml_models/donor_model.pkl")
    print(f"💾 Encoders and features saved to ml_models/")
    
    return model

def train_demand_model():
    """Train blood demand forecasting model using real data"""
    print("\n" + "="*50)
    print("Training Blood Demand Forecasting Model")
    print("="*50)
    
    # Try to load real data
    df = load_blood_demand_data()
    
    # Fall back to synthetic data if real data not available
    if df is None or len(df) < 50:
        print("\n⚠️ Using synthetic demand data (real data not available or insufficient)")
        df = generate_sample_demand_data(1000)
    else:
        print("\n✅ Using real blood demand data")
        print(f"   Total records: {len(df)}")
    
    # Prepare features
    feature_cols = ['month', 'day_of_week', 'blood_type', 'is_emergency', 
                    'season_numeric', 'is_weekend', 'is_holiday']
    
    # Select available features
    available_features = [col for col in feature_cols if col in df.columns]
    print(f"\n📋 Using features: {available_features}")
    
    X = df[available_features].copy()
    y = df['demand_units']
    
    # Handle categorical variables
    categorical_cols = ['blood_type']
    encoders = {}
    
    for col in categorical_cols:
        if col in X.columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
    
    # Handle missing values
    X = X.fillna(0)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n📊 Training set: {len(X_train)} samples")
    print(f"📊 Test set: {len(X_test)} samples")
    
    # Train model
    print("\n🔄 Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    score = model.score(X_test, y_test)
    print(f"\n✅ Model R² Score: {score:.3f}")
    
    # Feature importance
    importance = dict(zip(available_features, model.feature_importances_))
    print("\n📊 Feature Importance:")
    for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {imp:.3f}")
    
    # Save model and encoders
    os.makedirs('ml_models', exist_ok=True)
    joblib.dump(model, 'ml_models/demand_model.pkl')
    
    # Save encoders
    for name, encoder in encoders.items():
        joblib.dump(encoder, f'ml_models/demand_{name}_encoder.pkl')
    
    # Save feature list for inference
    joblib.dump(available_features, 'ml_models/demand_features.pkl')
    
    print(f"\n💾 Demand model saved to ml_models/demand_model.pkl")
    print(f"💾 Encoders and features saved to ml_models/")
    
    return model

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    print("="*60)
    print("🧠 SMART BLOOD DONOR SYSTEM - ML MODEL TRAINING")
    print("="*60)
    
    # Verify dataset files
    has_real_data = verify_dataset_files()
    
    if not has_real_data:
        print("\n⚠️ Some dataset files are missing.")
        print("   The script will use SYNTHETIC DATA for training.")
        print("   For best results, please add the CSV files to the dataset folder.")
    else:
        print("\n✅ All dataset files found. Will use REAL DATA for training.")
    
    print("\n" + "-"*60)
    
    # Train models
    donor_model = train_donor_model()
    demand_model = train_demand_model()
    
    # Summary
    print("\n" + "="*60)
    print("📋 TRAINING SUMMARY")
    print("="*60)
    
    if donor_model:
        print("✅ Donor Availability Model: Trained successfully")
    else:
        print("❌ Donor Availability Model: Failed")
    
    if demand_model:
        print("✅ Blood Demand Model: Trained successfully")
    else:
        print("❌ Blood Demand Model: Failed")
    
    # Data source used
    print(f"\n📊 Data Source: {'REAL DATA' if has_real_data else 'SYNTHETIC DATA'}")
    
    # List saved models
    print("\n📁 Models in ml_models directory:")
    if os.path.exists('ml_models'):
        for file in sorted(os.listdir('ml_models')):
            if file.endswith('.pkl'):
                size = os.path.getsize(f"ml_models/{file}") / 1024
                print(f"   📄 {file} ({size:.1f} KB)")
    
    print("\n" + "="*60)
    print("✅ Training complete!")
    print("="*60)