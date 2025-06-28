from flask import Flask, render_template, request, jsonify
import joblib
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)
model = joblib.load('solar_model.pkl')
WEATHER_API_KEY = "68689ce9502147d0bc444703252806"  

def get_weather(location, date):
    try:
        geo_url = f"http://api.weatherapi.com/v1/search.json?key={WEATHER_API_KEY}&q={location}"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()  # Raises HTTPError for bad responses
        geo_data = geo_response.json()
        
        if not geo_data or not isinstance(geo_data, list):
            raise ValueError(f"No location found for '{location}'")
        
        first_result = geo_data[0]
        lat, lon = first_result.get('lat'), first_result.get('lon')
        if not lat or not lon:
            raise ValueError("Lat/Lon missing in API response")
        
        forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={lat},{lon}&days=1&dt={date}"
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        weather_data = forecast_response.json()
        
        forecast_day = weather_data.get('forecast', {}).get('forecastday', [{}])[0]
        hour_data = next(
            (h for h in forecast_day.get('hour', []) if h.get('time', '').endswith('12:00')),
            {'temp_c': 25, 'solar_radiation': 800}  # Default values
        )
        
        return {
            'irradiance': hour_data.get('solar_radiation', 800),
            'temp': hour_data.get('temp_c', 25),
            'location': first_result.get('name', location),
            'date': date
        }
        
    except Exception as e:
        print(f"Weather API Error: {str(e)}")
        return {
            'irradiance': 800,  
            'temp': 25,
            'location': location,
            'date': date,
            'error': str(e) 
        }
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        location = request.form['location']
        date = request.form['date']
        
        weather = get_weather(location, date)
        prediction = model.predict([[weather['irradiance'], weather['temp']]])[0]
        
        return render_template('results.html', 
                            prediction=round(prediction, 2),
                            **weather)
    
    return render_template('index.html', 
                         default_date=datetime.now().strftime('%Y-%m-%d'))

if __name__ == '__main__':
    app.run(debug=True)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # For Render's port binding
    app.run(host='0.0.0.0', port=port)
