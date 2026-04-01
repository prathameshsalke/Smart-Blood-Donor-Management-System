# debug_ml_model.py
import joblib
import pandas as pd
import os

def debug_model():
    """Debug the ML model to see what features it expects"""
    
    model_path = 'ml_models/donor_model.pkl'
    
    if not os.path.exists(model_path):
        print("❌ Model file not found!")
        return
    
    # Load the model
    model = joblib.load(model_path)
    
    print("="*60)
    print("🔍 ML MODEL DEBUG INFORMATION")
    print("="*60)
    
    # Check if model has feature_names_in_ attribute
    if hasattr(model, 'feature_names_in_'):
        print("\n✅ Model has feature_names_in_ attribute")
        print("\n📊 Features the model expects (in exact order):")
        for i, feature in enumerate(model.feature_names_in_):
            print(f"   {i+1}. {feature}")
    else:
        print("\n❌ Model does not have feature_names_in_ attribute")
        print("   This means the model was trained with an older version of sklearn")
        
        # Try to infer features from model structure
        if hasattr(model, 'n_features_in_'):
            print(f"\nModel was trained with {model.n_features_in_} features")
    
    # Check if there are any encoders
    encoder_path = 'ml_models/donor_blood_encoder.pkl'
    if os.path.exists(encoder_path):
        encoder = joblib.load(encoder_path)
        print(f"\n✅ Blood type encoder found with classes: {encoder.classes_}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    debug_model()