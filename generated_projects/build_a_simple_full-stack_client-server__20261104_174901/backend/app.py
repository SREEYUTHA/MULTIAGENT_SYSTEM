import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS to allow only the specified frontend origins
CORS(app, origins=["http://localhost:8081", "http://127.0.0.1:8081"])

# Regex to validate HH:mm format (24-hour)
TIME_REGEX = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def get_greeting(hour: int) -> str:
    """
    Determine the greeting based on the hour.
    
    05:00-11:59: Good Morning
    12:00-16:59: Good Afternoon
    17:00-20:59: Good Evening
    21:00-04:59: Good Night
    """
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"


@app.route("/api/hello", methods=["GET"])
def hello():
    name = request.args.get("name")
    time_str = request.args.get("time")

    # Validate name
    if name is None or name.strip() == "":
        return jsonify({"error": "Missing or empty 'name' parameter."}), 400

    # Validate time
    if time_str is None or time_str.strip() == "":
        return jsonify({"error": "Missing or empty 'time' parameter."}), 400

    if not TIME_REGEX.match(time_str):
        return jsonify({"error": "Invalid 'time' format. Expected HH:mm (24-hour)."}), 400

    # Parse time
    hour = int(time_str.split(":")[0])
    # minute = int(time_str.split(":")[1])  # Not needed for greeting logic

    greeting = get_greeting(hour)
    message = f"{greeting}, {name.strip()}!"

    return jsonify({"message": message}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)