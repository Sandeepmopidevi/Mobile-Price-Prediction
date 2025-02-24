from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import os

# Load trained model (Pipeline includes preprocessing)
model_path = os.path.join(os.path.dirname(__file__), "../models/model.pkl")
model = pickle.load(open(model_path, "rb"))

app = Flask(__name__, template_folder="../templates", static_folder="../static")  # Ensure static folder is accessible

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # Serve HTML page

@app.route("/predict", methods=["POST"])  # Only allow POST
def predict():
    data = request.json
    try:
        # Reject Apple devices
        if "company" in data and data["company"].strip().lower() == "apple":
            return jsonify({"error": "Apple devices are not supported for prediction."}), 400

        # Convert input into a DataFrame (matching the model's trained format)
        features = pd.DataFrame([data])

        # Predict price using the saved pipeline
        prediction = model.predict(features)
        return jsonify({"predicted_price": round(prediction[0], 2)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
