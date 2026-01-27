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

# Check that all required env variables are set
if not PAYHERO_AUTH or not ACCOUNT_ID or not CHANNEL_ID or not CALLBACK_URL:
    print("ERROR: Missing one or more PayHero environment variables!")
    print(f"PAYHERO_AUTH: {PAYHERO_AUTH}")
    print(f"ACCOUNT_ID: {ACCOUNT_ID}")
    print(f"CHANNEL_ID: {CHANNEL_ID}")
    print(f"CALLBACK_URL: {CALLBACK_URL}")

@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount")
    reference = data.get("reference", f"TEST_{int(os.times()[4])}")  # fallback reference

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
        "Authorization": PAYHERO_AUTH.strip(),  # must include 'Basic ...'
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(PAYHERO_URL, json=payload, headers=headers, timeout=20)
        print("PAYHERO STATUS:", response.status_code)
        print("PAYHERO RESPONSE:", response.text)

        try:
            resp_json = response.json()
        except Exception:
            resp_json = {"error": "Invalid response from PayHero", "raw": response.text}

        # If PayHero returned non-2xx, wrap as error
        if not response.ok:
            return jsonify({"error": "PayHero rejected request", "details": resp_json}), response.status_code

        return jsonify(resp_json), response.status_code

    except requests.exceptions.RequestException as e:
        print("HTTP REQUEST ERROR:", str(e))
        return jsonify({"error": "Failed to reach PayHero", "details": str(e)}), 500


@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    # Just acknowledge receipt
    print("PAYHERO CALLBACK RECEIVED:", request.json)
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
