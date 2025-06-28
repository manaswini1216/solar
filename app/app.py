import streamlit as st
from utils import load_model, get_weather
from datetime import datetime
from PIL import Image
import os

st.set_page_config(
    page_title="☀️ Solar Energy Predictor",
    page_icon="☀️",
    layout="centered"
)

@st.cache_resource
def load_assets():
    return {
        "header": Image.open("solar_header.png"),
        "plant_img": Image.open("plant_layout.jpg"),
        "model": load_model("solar_model.pkl")
    }

assets = load_assets()

def show_header():
    st.image(assets["header"], use_column_width=True)
    st.title("Solar Plant Energy Forecast")
    with st.expander("ℹ️ Plant Details"):
        st.write(f"""
        **Location:** Your Plant Name  
        **Capacity:** XX kW  
        **Panel Type:** Monocrystalline  
        """)
        st.image(assets["plant_img"], caption="Plant Overview")

# --- Prediction Logic ---
def predict_energy():
    with st.form("prediction_form"):
        date = st.date_input("Select Date", datetime.now())
        irradiance = st.slider("Solar Irradiance (W/m²)", 0, 1000, 800)
        temp = st.slider("Temperature (°C)", 0, 50, 25)
        
        if st.form_submit_button("Predict"):
            if assets["model"]:
                prediction = assets["model"].predict([[irradiance, temp]])[0]
                st.success(f"## Predicted Output: {prediction:.2f} kW")
                
                # Visual feedback
                col1, col2 = st.columns(2)
                col1.metric("Irradiance", f"{irradiance} W/m²")
                col2.metric("Temperature", f"{temp}°C")
                
                # Production gauge
                progress = min(int((prediction / 10)), 100)
                st.progress(progress, text=f"Capacity Utilization: {progress}%")

# --- Main App ---
show_header()
predict_energy()
st.markdown("---")
st.caption("♻️ Sustainable Energy Monitoring System | v1.0")
