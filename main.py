# main.py
from flask import Flask, request, jsonify
import hmac
import hashlib
import requests
import os

app = Flask(__name__)

# Bybit APIキー（環境変数から取得）
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

# USDT無期限（Perpetual）用エンドポイント
BYBIT_ENDPOINT = "https://api.bybit.com"

def create_signature(params, secret):
    sorted_params = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(
        bytes(secret, "utf-8"),
        bytes(sorted_params, "utf-8"),
        hashlib.sha256
    ).hexdigest()

@app.route("/", methods=["POST"])
def webhook():
    data = request.json

    symbol = data.get("symbol", "BTCUSDT")
    side = data.get("side", "Buy")  # Buy or Sell
    qty = float(data.get("qty", 0.01))
    order_type = "Market"

    params = {
        "api_key": API_KEY,
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "qty": qty,
        "timestamp": int(requests.get("https://api.bybit.com/v2/public/time").json()["time_now"].split(".")[0] + "000")
    }

    sign = create_signature(params, API_SECRET)
    params["sign"] = sign

    r = requests.post(f"{BYBIT_ENDPOINT}/v2/private/order/create", data=params)

    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
