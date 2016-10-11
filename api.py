from __future__ import print_function
from flask import Flask, request, jsonify

# Load the model
import joblib
model = joblib.load('model/model.pkl')

app = Flask("api")

@app.route('/predict', methods=['POST'])
def predict_api():
    """Endpoint for predicting truthfulness of a review."""
    text = request.get_json()['text']
    prediction = model.predict_proba([text]).tolist()[0]
    return jsonify(prediction=prediction)

@app.route('/')
def healthcheck():
    return jsonify({"status": "success"})
