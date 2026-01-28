from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)

# ================== ENV VARIABLES ==================
PAYHERO_AUTH = os.getenv("PAYHERO_AUTH_TOKEN")  # FULL: "Basic xxxxxx"
ACCOUNT_ID = os.getenv("PAYHERO_ACCOUNT_ID")
CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL")

# ✅ CORRECT PayHero v2 endpoint
PAYHERO_URL = "https://backend.payhero.co.ke/api/v2/payments"

# ===================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "service": "PayHero STK Backend"}), 200


@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    try:
        data = request.get_json(force=True)

        phone = data.get("phone")
        amount = data.get("amount")
        reference = data.get("reference", f"OKOA_{int(time.time())}")

        if not phone or not amount:
            return jsonify({"error": "phone and amount are required"}), 400

        payload = {
            "amount": int(amount),
            "phone_number": phone,
            "channel_id": int(CHANNEL_ID),
            "external_reference": reference,
            "callback_url": CALLBACK_URL
        }

        headers = {
            "Authorization": PAYHERO_AUTH,   # already "Basic xxx"
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(
            PAYHERO_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        # 🔍 Safe debug logs
        print("STK PUSH SENT")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print("SERVER ERROR:", str(e))
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    data = request.get_json(silent=True)
    print("PAYHERO CALLBACK RECEIVED:", data)

    # Always acknowledge PayHero
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
