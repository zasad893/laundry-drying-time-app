# app.py
from flask import Flask, request, jsonify, render_template
import requests
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# ──────────────────────────────────────────────────────────────
# Initialise Flask application
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)

# ──────────────────────────────────────────────────────────────
# Load pre-trained model and associated scalers
# ──────────────────────────────────────────────────────────────
print("Loading model and scalers...")
model = load_model("model/laundry_time_predictor_advanced.keras")
scaler_X = joblib.load("model/scaler_X_advanced.pkl")
scaler_y = joblib.load("model/scaler_y_advanced.pkl")
print("Model and scalers loaded successfully.")

# ──────────────────────────────────────────────────────────────
# WeatherAPI Key – replace with a secure version in production
# ──────────────────────────────────────────────────────────────
WEATHER_API_KEY = "d9a856a9d1114367bb4130233250904"

# ──────────────────────────────────────────────────────────────
# Convert drying time in minutes into hours + minutes format
# ──────────────────────────────────────────────────────────────
def format_minutes(total_minutes):
    hours = int(total_minutes) // 60
    minutes = int(total_minutes) % 60
    return f"{hours} hr {minutes} mins" if hours > 0 else f"{minutes} mins"

# ──────────────────────────────────────────────────────────────
# MVC: View – Route to render the home (input) page
# ──────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

# ──────────────────────────────────────────────────────────────
# MVC: View – Route to render the results display page
# ──────────────────────────────────────────────────────────────
@app.route("/result")
def result():
    return render_template("results.html")

# ──────────────────────────────────────────────────────────────
# MVC: Controller – API endpoint to handle prediction requests
# ──────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict_drying_time():
    try:
        # same weather fetching logic...

        # Instead of ML prediction:
        tshirt_minutes = 89
        towel_minutes = 129

        return jsonify({
            "weather": {
                "temperature": float(temp),
                "cloud": float(cloud),
                "wind": float(wind),
                "precip": float(precip)
            },
            "prediction": {
                "tshirt_minutes": float(tshirt_minutes),
                "towel_minutes": float(towel_minutes),
                "tshirt_readable": format_minutes(tshirt_minutes),
                "towel_readable": format_minutes(towel_minutes)
            }
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal server error"}), 500
# def predict_drying_time():
#     # Get data from POST request (JSON format)
#     data = request.get_json()
#     location = data.get("location")
#     lat = data.get("lat")
#     lng = data.get("lng")

#     # Use lat/lng if available, otherwise fallback to address
#     if lat and lng:
#         query_param = f"{lat},{lng}"
#     elif location:
#         query_param = location
#     else:
#         return jsonify({"error": "No location or coordinates provided."}), 400

#     # ──────────────────────────────────────────────────────────
#     # Fetch current weather data using WeatherAPI
#     # ──────────────────────────────────────────────────────────
#     try:
#         url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={query_param}"
#         response = requests.get(url)
#         weather_data = response.json()

#         if "current" not in weather_data:
#             return jsonify({"error": "Weather data not available for this location."}), 400

#         current = weather_data["current"]
#         temp = current["temp_c"]
#         cloud = current["cloud"]
#         wind = current["wind_mph"]
#         precip = current["precip_mm"]

#     except Exception as e:
#         return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500

#     # ──────────────────────────────────────────────────────────
#     # Rule: If it's currently raining, don't proceed with prediction
#     # ──────────────────────────────────────────────────────────
#     if precip > 0.1:
#         return jsonify({
#             "error": "It is currently raining. Outdoor drying is not recommended.",
#             "weather": {
#                 "temperature": float(temp),
#                 "cloud": float(cloud),
#                 "wind": float(wind),
#                 "precip": float(precip)
#             }
#         })

#     # ──────────────────────────────────────────────────────────
#     # Predict drying time using the trained model
#     # ──────────────────────────────────────────────────────────
#     X = np.array([[temp, cloud, wind]])
#     X_scaled = scaler_X.transform(X)
#     y_scaled = model.predict(X_scaled)
#     y_pred = scaler_y.inverse_transform(y_scaled)

#     # Extract predicted drying times (in minutes)
#     tshirt_minutes = round(y_pred[0][0], 2)
#     towel_minutes = round(y_pred[0][1], 2)

#     # ──────────────────────────────────────────────────────────
#     # Return response in JSON format
#     # ──────────────────────────────────────────────────────────
#     return jsonify({
#         "weather": {
#             "temperature": float(temp),
#             "cloud": float(cloud),
#             "wind": float(wind),
#             "precip": float(precip)
#         },
#         "prediction": {
#             "tshirt_minutes": float(tshirt_minutes),
#             "towel_minutes": float(towel_minutes),
#             "tshirt_readable": format_minutes(tshirt_minutes),
#             "towel_readable": format_minutes(towel_minutes)
#         }
#     })

# ──────────────────────────────────────────────────────────────
# Run the Flask server in debug mode
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
