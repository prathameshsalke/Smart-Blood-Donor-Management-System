"""
ML Prediction - Make predictions using trained models
"""

import joblib
import pandas as pd
import numpy as np
from flask import current_app
from datetime import datetime
from .preprocessing import prepare_donor_features, prepare_demand_features

class MLPredictor:
    """Machine Learning Predictor"""
    
    def __init__(self):
        self.donor_model = None
        self.demand_model = None
        self.donor_encoder = None
        self.demand_encoder = None
        self.load_models()
    
    def load_models(self):
        """Load trained models"""
        try:
            # Load donor model
            donor_model_path = current_app.config.get('DONOR_MODEL_PATH', 'ml_models/donor_model.pkl')
            donor_encoder_path = 'ml_models/donor_blood_encoder.pkl'
            
            if os.path.exists(donor_model_path):
                self.donor_model = joblib.load(donor_model_path)
            
            if os.path.exists(donor_encoder_path):
                self.donor_encoder = joblib.load(donor_encoder_path)
            
            # Load demand model
            demand_model_path = current_app.config.get('DEMAND_MODEL_PATH', 'ml_models/demand_model.pkl')
            demand_encoder_path = 'ml_models/demand_blood_encoder.pkl'
            
            if os.path.exists(demand_model_path):
                self.demand_model = joblib.load(demand_model_path)
            
            if os.path.exists(demand_encoder_path):
                self.demand_encoder = joblib.load(demand_encoder_path)
            
            current_app.logger.info("ML models loaded successfully")
            
        except Exception as e:
            current_app.logger.error(f"Error loading ML models: {str(e)}")
    
    def predict_donor_availability(self, donor_data):
        """Predict donor availability probability"""
        try:
            if not self.donor_model:
                return self._fallback_prediction(donor_data)
            
            # Prepare features
            features = prepare_donor_features(donor_data)
            
            # Encode blood type
            if self.donor_encoder and 'blood_type' in features:
                features['blood_type'] = self.donor_encoder.transform([features['blood_type']])[0]
            
            # Create DataFrame
            df = pd.DataFrame([features])
            
            # Predict
            probability = self.donor_model.predict_proba(df)[0][1]
            
            # Determine confidence
            confidence = self._calculate_confidence(probability, features)
            
            return {
                'probability': round(probability, 2),
                'confidence': confidence,
                'will_donate': probability > 0.5,
                'message': self._get_availability_message(probability)
            }
            
        except Exception as e:
            current_app.logger.error(f"Prediction error: {str(e)}")
            return self._fallback_prediction(donor_data)
    
    def predict_demand(self, blood_type=None, months_ahead=1):
        """Predict blood demand"""
        try:
            if not self.demand_model:
                return self._fallback_demand_forecast(blood_type)
            
            forecasts = []
            current_date = datetime.now()
            
            for i in range(months_ahead):
                forecast_date = current_date + pd.DateOffset(months=i)
                
                # Prepare features
                features = prepare_demand_features(
                    blood_type=blood_type,
                    date=forecast_date
                )
                
                # Encode categoricals
                if self.demand_encoder and 'blood_type' in features:
                    features['blood_type'] = self.demand_encoder.transform([features['blood_type']])[0]
                
                # Create DataFrame
                df = pd.DataFrame([features])
                
                # Predict
                demand = self.demand_model.predict(df)[0]
                
                forecasts.append({
                    'month': forecast_date.strftime('%Y-%m'),
                    'blood_type': blood_type or 'All',
                    'predicted_demand': int(max(0, demand)),
                    'confidence': 'medium'
                })
            
            return forecasts
            
        except Exception as e:
            current_app.logger.error(f"Demand prediction error: {str(e)}")
            return self._fallback_demand_forecast(blood_type)
    
    def _calculate_confidence(self, probability, features):
        """Calculate prediction confidence"""
        # More features = higher confidence
        feature_count = len([v for v in features.values() if v is not None])
        
        if feature_count >= 5 and (probability > 0.8 or probability < 0.2):
            return 'high'
        elif feature_count >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _get_availability_message(self, probability):
        """Get human-readable message"""
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
        """Fallback prediction when model not available"""
        # Simple rule-based prediction
        score = 0.5
        
        # Adjust based on last donation
        if donor_data.get('days_since_last'):
            if donor_data['days_since_last'] < 90:
                score -= 0.3
            elif donor_data['days_since_last'] > 180:
                score += 0.2
        
        # Adjust based on time of day
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            score += 0.1
        elif hour < 6 or hour > 22:  # Late night
            score -= 0.2
        
        # Adjust based on day of week
        if datetime.now().weekday() in [5, 6]:  # Weekend
            score += 0.1
        
        probability = max(0, min(1, score))
        
        return {
            'probability': round(probability, 2),
            'confidence': 'low',
            'will_donate': probability > 0.5,
            'message': 'Using fallback prediction (model not available)'
        }
    
    def _fallback_demand_forecast(self, blood_type):
        """Fallback demand forecast using statistics"""
        # Base demand by blood type (average monthly units)
        base_demand = {
            'A+': 120, 'A-': 30, 'B+': 100, 'B-': 25,
            'AB+': 40, 'AB-': 10, 'O+': 150, 'O-': 45
        }
        
        if blood_type and blood_type in base_demand:
            base = base_demand[blood_type]
        else:
            base = sum(base_demand.values()) // len(base_demand)
        
        # Add seasonal variation
        month = datetime.now().month
        if month in [12, 1, 2]:  # Winter
            multiplier = 1.2
        elif month in [6, 7, 8]:  # Summer
            multiplier = 0.9
        else:
            multiplier = 1.0
        
        demand = int(base * multiplier)
        
        return [{
            'month': datetime.now().strftime('%Y-%m'),
            'blood_type': blood_type or 'All',
            'predicted_demand': demand,
            'confidence': 'low',
            'note': 'Using statistical fallback'
        }]

# Create global predictor instance
predictor = MLPredictor()

def predict_donor_availability(donor_data):
    """Wrapper function for donor availability prediction"""
    return predictor.predict_donor_availability(donor_data)

def predict_demand(blood_type=None, months_ahead=1):
    """Wrapper function for demand prediction"""
    return predictor.predict_demand(blood_type, months_ahead)

import os