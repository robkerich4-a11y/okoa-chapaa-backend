from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # allow your frontend to call the API

# Load environment variables
PAYHERO_AUTH = os.getenv("PAYHERO_AUTH_TOKEN")
ACCOUNT_ID = os.getenv("PAYHERO_ACCOUNT_ID")
CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL")

PAYHERO_URL = "https://api.payhero.co.ke/v1/mpesa/stk-push"

@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount")
    reference = data.get("reference", "TEST")  # optional reference

    if not phone or not amount:
        return jsonify({"error": "phone and amount are required"}), 400

    payload = {
        "account_id": ACCOUNT_ID,
        "channel_id": CHANNEL_ID,
        "amount": amount,
        "phone_number": phone,
        "reference": reference,
        "callback_url": CALLBACK_URL
    }

    headers = {
        "Authorization": PAYHERO_AUTH,
        "Content-Type": "application/json"
    }

    response = requests.post(PAYHERO_URL, json=payload, headers=headers)
    return jsonify(response.json()), response.status_code


@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    # Just acknowledge receipt
    print("PAYHERO CALLBACK:", request.json)
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
