"""
ML Service for machine learning predictions
"""

import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import current_app
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

class MLService:
    """Service for machine learning operations"""
    
    def __init__(self):
        self.donor_model = None
        self.demand_model = None
        self.label_encoders = {}
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            model_dir = 'ml_models'
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            
            donor_model_path = os.path.join(model_dir, 'donor_model.pkl')
            demand_model_path = os.path.join(model_dir, 'demand_model.pkl')
            
            if os.path.exists(donor_model_path):
                self.donor_model = joblib.load(donor_model_path)
                
            if os.path.exists(demand_model_path):
                self.demand_model = joblib.load(demand_model_path)
                
            # Load encoders if they exist
            encoder_path = os.path.join(model_dir, 'donor_blood_encoder.pkl')
            if os.path.exists(encoder_path):
                self.label_encoders['blood_type'] = joblib.load(encoder_path)
            
            gender_encoder_path = os.path.join(model_dir, 'donor_gender_encoder.pkl')
            if os.path.exists(gender_encoder_path):
                self.label_encoders['gender'] = joblib.load(gender_encoder_path)
                
            self.models_loaded = True
            current_app.logger.info("ML models loaded successfully")
            
        except Exception as e:
            current_app.logger.error(f"Error loading ML models: {e}")
            self.models_loaded = False
    
    def predict_donor_availability(self, donor_data):
        """
        Predict donor availability probability
        This is the method called from routes.py
        """
        try:
            if not self.donor_model:
                return self._fallback_prediction(donor_data)
            
            # Get current time for temporal features
            current_time = datetime.now()
            
            # Prepare features matching what the model expects
            features = pd.DataFrame([{
                'days_since_last': donor_data.get('days_since_last', 999),
                'gender': donor_data.get('gender', 'unknown'),
                'total_donations': donor_data.get('total_donations', 0),
                'weight': donor_data.get('weight', 70),
                'age': donor_data.get('age', 30),
                'blood_type': donor_data.get('blood_type', 'O+'),
                'month': current_time.month,
                'day_of_week': current_time.weekday(),
                'hour': current_time.hour
            }])
            
            # Encode categorical variables if encoders exist
            if 'gender' in self.label_encoders:
                try:
                    features['gender'] = self.label_encoders['gender'].transform(
                        features['gender'].astype(str)
                    )[0]
                except:
                    features['gender'] = 0
            
            if 'blood_type' in self.label_encoders:
                try:
                    features['blood_type'] = self.label_encoders['blood_type'].transform(
                        features['blood_type'].astype(str)
                    )[0]
                except:
                    features['blood_type'] = 0
            
            # Ensure all expected features are present
            if hasattr(self.donor_model, 'feature_names_in_'):
                expected_features = self.donor_model.feature_names_in_
                
                # Add any missing features with default values
                for feature in expected_features:
                    if feature not in features.columns:
                        features[feature] = 0
                
                # Reorder columns to match model expectation
                features = features[expected_features]
            
            # Predict probability
            probability = self.donor_model.predict_proba(features)[0][1]
            
            # Determine confidence
            confidence = self._calculate_confidence(probability, donor_data)
            
            return {
                'probability': round(probability, 2),
                'confidence': confidence,
                'will_donate': probability > 0.5,
                'message': self._get_availability_message(probability)
            }
            
        except Exception as e:
            current_app.logger.error(f"Prediction error: {e}")
            return self._fallback_prediction(donor_data)
    
    def _calculate_confidence(self, probability, donor_data):
        """Calculate prediction confidence"""
        # More features = higher confidence
        feature_count = len([v for v in donor_data.values() if v is not None])
        
        if feature_count >= 5 and (probability > 0.8 or probability < 0.2):
            return 'high'
        elif feature_count >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _get_availability_message(self, probability):
        """Get human-readable message from probability"""
        if probability > 0.8:
            return "Highly likely to be available"
        elif probability > 0.6:
            return "Likely to be available"
        elif probability > 0.4:
            return "Uncertain availability"
        elif probability > 0.2:
            return "Unlikely to be available"
        else:
            return "Very unlikely to be available"
    
    def _fallback_prediction(self, donor_data):
        """Fallback prediction using simple rules when model not available"""
        # Simple rule-based prediction
        score = 0.5
        now = datetime.now()
        
        # Adjust based on time of day (9 AM - 5 PM are better)
        if 9 <= now.hour <= 17:
            score += 0.1
        elif now.hour < 6 or now.hour > 22:
            score -= 0.1
        
        # Adjust based on day of week (weekends are better)
        if now.weekday() >= 5:  # Weekend
            score += 0.1
        
        # Adjust based on donation history
        days_since_last = donor_data.get('days_since_last', 999)
        if days_since_last > 90:
            score += 0.1
        elif days_since_last < 90:
            score -= 0.2
        
        probability = max(0.1, min(0.9, score))
        
        return {
            'probability': round(probability, 2),
            'confidence': 'low',
            'will_donate': probability > 0.5,
            'message': 'Using fallback prediction (model needs retraining)'
        }
    
    def predict_demand(self, blood_type=None, months_ahead=1):
        """Predict blood demand for future months"""
        try:
            if not self.demand_model:
                return self._generate_fallback_forecast(blood_type)
            
            current_date = datetime.now()
            forecasts = []
            
            for i in range(months_ahead):
                forecast_date = current_date + timedelta(days=30*i)
                
                features = pd.DataFrame([{
                    'month': forecast_date.month,
                    'day_of_week': forecast_date.weekday(),
                    'blood_type': blood_type or 'O+',
                    'is_emergency': 0,
                    'previous_month_demand': 100,
                    'season': (forecast_date.month % 12 + 3) // 3
                }])
                
                # Encode categorical
                if 'blood_type' in self.label_encoders:
                    try:
                        features['blood_type'] = self.label_encoders['blood_type'].transform(
                            features['blood_type'].astype(str)
                        )[0]
                    except:
                        features['blood_type'] = 0
                
                # Predict
                demand = self.demand_model.predict(features)[0]
                
                forecasts.append({
                    'month': forecast_date.strftime('%Y-%m'),
                    'blood_type': blood_type or 'All',
                    'predicted_demand': int(demand),
                    'confidence': 'medium'
                })
            
            return forecasts
            
        except Exception as e:
            current_app.logger.error(f"Forecast error: {e}")
            return self._generate_fallback_forecast(blood_type)
    
    def _generate_fallback_forecast(self, blood_type):
        """Generate fallback forecast using simple statistics"""
        import random
        
        base_demand = {
            'A+': 120, 'A-': 30, 'B+': 100, 'B-': 25,
            'AB+': 40, 'AB-': 10, 'O+': 150, 'O-': 45
        }
        
        if blood_type and blood_type in base_demand:
            base = base_demand[blood_type]
        else:
            base = sum(base_demand.values()) // len(base_demand)
        
        # Add some random variation
        demand = base + random.randint(-20, 20)
        
        return [{
            'month': datetime.now().strftime('%Y-%m'),
            'blood_type': blood_type or 'All',
            'predicted_demand': max(0, demand),
            'confidence': 'low',
            'note': 'Using statistical fallback (model not trained)'
        }]