from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)  # allow frontend to call this API

# Load environment variables
PAYHERO_AUTH = os.getenv("PAYHERO_AUTH_TOKEN")  # Should include 'Basic ...'
ACCOUNT_ID = os.getenv("PAYHERO_ACCOUNT_ID")
CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL")  # Must be publicly accessible (HTTPS)

PAYHERO_URL = "https://api.payhero.co.ke/v1/mpesa/stk-push"

# Check environment variables at startup
missing_vars = [name for name, value in [
    ("PAYHERO_AUTH_TOKEN", PAYHERO_AUTH),
    ("PAYHERO_ACCOUNT_ID", ACCOUNT_ID),
    ("PAYHERO_CHANNEL_ID", CHANNEL_ID),
    ("CALLBACK_URL", CALLBACK_URL)
] if not value]

if missing_vars:
    print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")

@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount")
    reference = data.get("reference", f"PROC_{int(time.time())}")  # fallback unique reference

    # Validate input
    if not phone or not amount:
        return jsonify({"error": "phone and amount are required"}), 400

    # Payload for PayHero
    payload = {
        "account_id": ACCOUNT_ID,
        "channel_id": CHANNEL_ID,
        "amount": amount,
        "phone_number": phone,
        "reference": reference,
        "callback_url": CALLBACK_URL
    }

    headers = {
        "Authorization": PAYHERO_AUTH.strip(),  # Must include 'Basic ...'
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(PAYHERO_URL, json=payload, headers=headers, timeout=20)
        print("PAYHERO STATUS:", response.status_code)
        print("PAYHERO RESPONSE:", response.text)

        try:
            resp_json = response.json()
        except Exception:
            resp_json = {"error": "Invalid JSON response from PayHero", "raw": response.text}

        if not response.ok:
            # Return full details for debugging
            return jsonify({
                "error": "PayHero rejected request",
                "status_code": response.status_code,
                "details": resp_json
            }), response.status_code

        return jsonify(resp_json), response.status_code

    except requests.exceptions.RequestException as e:
        print("HTTP REQUEST ERROR:", str(e))
        return jsonify({"error": "Failed to reach PayHero", "details": str(e)}), 500


@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    # Log callback from PayHero
    print("PAYHERO CALLBACK RECEIVED:", request.json)
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    # For Render: use host 0.0.0.0 and port 5000 or the environment PORT
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
