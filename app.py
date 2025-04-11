# app.py
from flask import Flask, request, jsonify, render_template
import requests
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Load ML model and scalers
print("Loading model and scalers...")
model = load_model("model/laundry_time_predictor_advanced.keras")
scaler_X = joblib.load("model/scaler_X_advanced.pkl")
scaler_y = joblib.load("model/scaler_y_advanced.pkl")
print("Model and scalers loaded successfully.")

# WeatherAPI key from environment
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# Utility: convert minutes to "X hr Y mins"
def format_minutes(total_minutes):
    hours = int(total_minutes) // 60
    minutes = int(total_minutes) % 60
    return f"{hours} hr {minutes} mins" if hours > 0 else f"{minutes} mins"

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Results page
@app.route("/result")
def result():
    return render_template("results.html")

# Prediction endpoint
@app.route("/predict", methods=["POST"])
def predict_drying_time():
    data = request.get_json()
    location = data.get("location")
    lat = data.get("lat")
    lng = data.get("lng")

    # Use lat/lng if available
    if lat and lng:
        query_param = f"{lat},{lng}"
    elif location:
        query_param = location
    else:
        return jsonify({"error": "No location or coordinates provided."}), 400

    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={query_param}"
        response = requests.get(url)
        weather_data = response.json()

        if "current" not in weather_data:
            return jsonify({"error": "Weather data not available for this location."}), 400

        current = weather_data["current"]
        temp = current["temp_c"]
        cloud = current["cloud"]
        wind = current["wind_mph"]
        precip = current["precip_mm"]

    except Exception as e:
        return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500

    if precip > 0.1:
        return jsonify({
            "error": "It is currently raining. Outdoor drying is not recommended.",
            "weather": {
                "temperature": float(temp),
                "cloud": float(cloud),
                "wind": float(wind),
                "precip": float(precip)
            }
        })

    # Make prediction
    X = np.array([[temp, cloud, wind]])
    X_scaled = scaler_X.transform(X)
    y_scaled = model.predict(X_scaled)
    y_pred = scaler_y.inverse_transform(y_scaled)

    tshirt_minutes = round(y_pred[0][0], 2)
    towel_minutes = round(y_pred[0][1], 2)

    return jsonify({
        "weather": {
            "temperature": float(temp),
            "cloud": float(cloud),
            "wind": float(wind),
            "precip": float(precip)
        },
        "prediction": {
            "tshirt_minutes": tshirt_minutes,
            "towel_minutes": towel_minutes,
            "tshirt_readable": format_minutes(tshirt_minutes),
            "towel_readable": format_minutes(towel_minutes)
        }
    })

# Production-ready run
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
