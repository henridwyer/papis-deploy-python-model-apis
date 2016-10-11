from __future__ import print_function
from flask import Flask, request, jsonify
import gevent

app = Flask("api")

# Load celery
from predict_celery import predict_text

@app.route('/predict', methods=['POST'])
def predict_api():
    """Endpoint for predicting truthfulness of a review."""
    print("API REQUEST")
    text = request.get_json()['text']
    prediction = predict_text.delay(text)
    while not prediction.ready():
        gevent.sleep(0.001)
    return jsonify(prediction=prediction.wait())

@app.route('/')
def healthcheck():
    return jsonify({"status": "success"})
