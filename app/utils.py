import joblib
import requests

def load_model(path):
    try:
        return joblib.load(path)
    except Exception as e:
        print(f"Model loading error: {str(e)}")
        return None

def get_weather(location, date):
    """For future API integration"""
    return {
        "irradiance": 800,
        "temp": 25
    }
