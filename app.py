# app.py
from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get API key from environment variables
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# Convert minutes to readable string
def format_minutes(total_minutes):
    hours = int(total_minutes) // 60
    minutes = int(total_minutes) % 60
    return f"{hours} hr {minutes} mins" if hours > 0 else f"{minutes} mins"

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Results route
@app.route("/result")
def result():
    return render_template("results.html")

# Prediction route (dummy)
@app.route("/predict", methods=["POST"])
def predict_drying_time():
    data = request.get_json()
    location = data.get("location")
    lat = data.get("lat")
    lng = data.get("lng")

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

    # If raining, return notice without predictions
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

    # Dummy predictions for testing
    tshirt_minutes = 90
    towel_minutes = 130

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

# Use Waitress to serve in production
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
