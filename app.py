"""Run with python app.py, then open http://127.0.0.1:5000."""
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from prediction import predict_price

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=str(ROOT / 'site/dist'), static_url_path='')

@app.get('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.post('/api/predict')
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='Send a JSON object with the property features.'), 400
    try:
        return jsonify(prediction_aud=predict_price(data))
    except ValueError as error:
        return jsonify(error=str(error)), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
