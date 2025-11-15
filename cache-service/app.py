from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# In-memory cache: key → (value, expiry_timestamp)
cache = {}

DEFAULT_TTL = 60  # seconds (you can change)

def is_expired(expiry):
    return expiry is not None and expiry < time.time()

@app.route("/health", methods=["GET"])
def health():
    return jsonify(service="cache-service", status="ok", time=time.time()), 200


@app.route("/set", methods=["POST"])
def set_value():
    data = request.get_json() or {}

    if "key" not in data or "value" not in data:
        return jsonify(error="key and value required"), 400

    key = data["key"]
    value = data["value"]
    ttl = data.get("ttl", DEFAULT_TTL)

    expiry = time.time() + ttl if ttl else None

    cache[key] = (value, expiry)

    return jsonify(message="stored", key=key, ttl=ttl), 200


@app.route("/get", methods=["GET"])
def get_value():
    key = request.args.get("key")
    if not key:
        return jsonify(error="key required"), 400

    if key not in cache:
        return jsonify(hit=False, value=None), 404

    value, expiry = cache[key]

    if is_expired(expiry):
        del cache[key]
        return jsonify(hit=False, value=None, expired=True), 404

    return jsonify(hit=True, value=value), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
