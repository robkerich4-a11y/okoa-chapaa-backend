from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
import base64

app = Flask(__name__)
CORS(app)

# ================== ENV VARIABLES ==================
PAYHERO_AUTH = os.getenv("PAYHERO_AUTH_TOKEN")  # Must start with "Basic "
ACCOUNT_ID = os.getenv("PAYHERO_ACCOUNT_ID")
CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL")

# ✅ CORRECT PAYHERO ENDPOINT
PAYHERO_URL = "https://api.payhero.co.ke/v2/stk-push"

# ===================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK"}), 200


@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    data = request.get_json(force=True)

    phone = data.get("phone")
    amount = data.get("amount")
    reference = data.get("reference", f"PROC_{int(time.time())}")

    if not phone or not amount:
        return jsonify({"error": "phone and amount are required"}), 400

    payload = {
        "account_id": int(ACCOUNT_ID),
        "channel_id": int(CHANNEL_ID),
        "amount": int(amount),
        "phone_number": phone,
        "reference": reference,
        "callback_url": CALLBACK_URL
    }

    # PayHero requires Basic Auth with service token
    token = f"{PAYHERO_API_USERNAME}:{PAYHERO_SERVICE_TOKEN}"
    auth_header = "Basic " + base64.b64encode(token.encode()).decode()

    headers = {
        "Authorization": auth_header,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            PAYHERO_URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        print("PAYHERO STATUS:", response.status_code)
        print("PAYHERO RESPONSE:", response.text)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    print("CALLBACK RECEIVED:", request.json)
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
