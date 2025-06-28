import streamlit as st
import pandas as pd
import requests
from joblib import load
import numpy as np

st.title("☀️ Solar Forecast App")
st.write("This app predicts the expected solar power output(in Watts) for each hour of the selected day using weather forecast data.")

location = st.text_input("Enter location:", "Bhopal")
date = st.date_input("Select date for forecast:")

model = load("solar_model.pkl")

def get_lat_lon(city):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    response = requests.get(geo_url)
    data = response.json()
    if 'results' in data:
        return data['results'][0]['latitude'], data['results'][0]['longitude']
    else:
        return None, None

# On submit
if st.button("Get Forecast"):
    lat, lon = get_lat_lon(location)
    if lat is None:
        st.error("Location not found.")
    else:
        # Fetch weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,shortwave_radiation&start_date={date}&end_date={date}&timezone=auto"
        response = requests.get(weather_url)
        data = response.json()
        df = pd.DataFrame(data['hourly'])

        # Rename and estimate module temp
        df = df[['time', 'temperature_2m', 'shortwave_radiation']]
        df.rename(columns={
            'temperature_2m': 'AMBIENT_TEMPERATURE',
            'shortwave_radiation': 'IRRADIATION'
        }, inplace=True)
        df['MODULE_TEMPERATURE'] = df['AMBIENT_TEMPERATURE'] + 0.035 * df['IRRADIATION']

        df['DC_POWER'] = df['IRRADIATION'] * 500 * 0.18   
        df['DAILY_YIELD'] = df['DC_POWER'] / 1000         
        df['TOTAL_YIELD'] = 250000 + df['DAILY_YIELD'].cumsum()

        df_model_input = df[['DAILY_YIELD', 'TOTAL_YIELD', 'AMBIENT_TEMPERATURE',
                             'MODULE_TEMPERATURE', 'IRRADIATION', 'DC_POWER']]

        # Predict
        predictions = model.predict(df_model_input)
        df['Predicted_Output'] = predictions

        # Display
        st.success("Prediction completed!")
        st.write(df[['time', 'Predicted_Output']])

        # Plot
        st.line_chart(data=df, x='time', y='Predicted_Output')
        st.line_chart(data=df, x='time', y='IRRADIATION')

