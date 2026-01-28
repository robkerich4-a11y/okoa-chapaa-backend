from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)  # allow frontend (Vercel) to call this API

# =========================
# Environment Variables
# =========================
PAYHERO_AUTH = os.getenv("PAYHERO_AUTH_TOKEN")  # Must start with 'Basic '
ACCOUNT_ID = os.getenv("PAYHERO_ACCOUNT_ID")
CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL")  # Public HTTPS callback

# ✅ CORRECT PayHero STK Push endpoint
PAYHERO_URL = "https://api.payhero.co.ke/v1/payments/mpesa/stk-push"

# =========================
# Startup validation
# =========================
missing_vars = []
if not PAYHERO_AUTH:
    missing_vars.append("PAYHERO_AUTH_TOKEN")
if not ACCOUNT_ID:
    missing_vars.append("PAYHERO_ACCOUNT_ID")
if not CHANNEL_ID:
    missing_vars.append("PAYHERO_CHANNEL_ID")
if not CALLBACK_URL:
    missing_vars.append("CALLBACK_URL")

if missing_vars:
    print("❌ ERROR: Missing environment variables:", ", ".join(missing_vars))
else:
    print("✅ All PayHero environment variables loaded")

# =========================
# STK Push Endpoint
# =========================
@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    data = request.get_json(force=True)

    phone = data.get("phone")
    amount = data.get("amount")
    reference = data.get("reference", f"OKOA_{int(time.time())}")

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
        "Authorization": PAYHERO_AUTH.strip(),  # MUST include 'Basic '
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            PAYHERO_URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        print("🔵 PAYHERO STATUS:", response.status_code)
        print("🔵 PAYHERO RESPONSE:", response.text)

        try:
            response_data = response.json()
        except Exception:
            response_data = {
                "error": "Invalid JSON from PayHero",
                "raw": response.text
            }

        if not response.ok:
            return jsonify({
                "error": "PayHero rejected request",
                "status_code": response.status_code,
                "details": response_data
            }), response.status_code

        return jsonify(response_data), 200

    except requests.exceptions.RequestException as e:
        print("❌ REQUEST ERROR:", str(e))
        return jsonify({
            "error": "Failed to reach PayHero",
            "details": str(e)
        }), 500

# =========================
# PayHero Callback Endpoint
# =========================
@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    data = request.get_json(force=True)
    print("✅ PAYHERO CALLBACK RECEIVED:", data)
    return jsonify({"status": "received"}), 200

# =========================
# Health Check (optional)
# =========================
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "OKOA CHAPAA BACKEND RUNNING"}), 200

# =========================
# App Runner (Render)
# =========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
