from flask import Flask, render_template, request, jsonify
import joblib
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)
model = joblib.load('solar_model.pkl')
WEATHER_API_KEY = "68689ce9502147d0bc444703252806"  

def get_weather(location, date):
    geo_url = f"http://api.weatherapi.com/v1/search.json?key={WEATHER_API_KEY}&q={location}"
    geo_data = requests.get(geo_url).json()
    lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
    
    forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={lat},{lon}&days=1&dt={date}"
    weather_data = requests.get(forecast_url).json()
    
    noon_condition = next(h for h in weather_data['forecast']['forecastday'][0]['hour'] 
                         if h['time'].endswith('12:00'))
    
    return {
        'irradiance': noon_condition.get('solar_radiation', 800),  # W/m² (default if missing)
        'temp': noon_condition['temp_c'],
        'location': geo_data[0]['name'],
        'date': date
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
