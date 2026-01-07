from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import logging

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.weather_client import get_weather

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Routes ----------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/weather/current", methods=["GET"])
@limiter.limit("10 per minute")
def current_weather():
    city = request.args.get("city", "").strip()
    state = request.args.get("state", "").strip().upper() or None
    country = request.args.get("country", "US").strip().upper()
    unit = request.args.get("unit", "metric").strip()

    # Basic validation
    if not city:
        return jsonify({"error": "city is required"}), 400

    if country != "US":
        return jsonify({"error": "Only US locations are supported right now"}), 400

    if state and len(state) != 2:
        return jsonify({"error": "state must be a 2-letter code like 'VA'"}), 400

    logger.info(
        "Weather request: city=%s state=%s country=%s unit=%s",
        city, state, country, unit,
    )

    try:
        result = get_weather(
            city=city,
            state=state,
            country=country,
            unit_group=unit,
            use_cache=True,
        )

        raw = result["data"]
        current = raw.get("currentConditions", {})

        response = {
            "city": raw.get("resolvedAddress", city),
            "temperature": current.get("temp"),
            "conditions": current.get("conditions"),
            "humidity": current.get("humidity"),
            "windSpeed": current.get("windspeed"),
            "source": result["source"],  # "api" or "cache"
        }
        return jsonify(response), 200

    except ValueError as ve:
        logger.warning("Bad request error: %s", ve)
        return jsonify({"error": str(ve)}), 400
    except RuntimeError as re:
        logger.error("Upstream service error: %s", re)
        return jsonify({"error": str(re)}), 503
    except Exception as ex:
        logger.exception("Unexpected error while handling request")
        return jsonify({"error": "Unexpected error", "details": str(ex)}), 500


# Optional: raw data endpoint
@app.route("/weather/raw", methods=["GET"])
def raw_weather():
    city = request.args.get("city", "").strip()
    state = request.args.get("state", "").strip().upper() or None
    country = request.args.get("country", "US").strip().upper()
    unit = request.args.get("unit", "metric").strip()

    if not city:
        return jsonify({"error": "city is required"}), 400

    try:
        result = get_weather(
            city=city,
            state=state,
            country=country,
            unit_group=unit,
            use_cache=True,
        )
        return jsonify(result), 200
    except Exception as ex:
        logger.exception("Error in /weather/raw")
        return jsonify({"error": "Unexpected error", "details": str(ex)}), 500


# ---------- Error handler ----------

@app.errorhandler(HTTPException)
def handle_http_exception(e: HTTPException):
    logger.warning("HTTPException: %s %s", e.code, e.description)
    return jsonify({"error": e.description}), e.code


# ---------- Entry point ----------

if __name__ == "__main__":
    app.run(debug=True)
