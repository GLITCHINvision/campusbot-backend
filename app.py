"""Flask backend API to serve chatbot responses."""

from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import process_query

app = Flask(__name__)
CORS(app)  


@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint to process user queries."""
    try:
        user_query = request.json.get("query")
        print(" Received query from frontend:", user_query)

        if not user_query:
            return jsonify({"reply": " No query received."}), 400

        response = process_query(user_query)
        return jsonify({"reply": response})

    except (KeyError, TypeError, ValueError) as e:
        print(" Known error:", str(e))
        return jsonify({"reply": " Invalid input received."}), 400

    except Exception as unexpected:  
        print(" Unknown error:", str(unexpected))
        return jsonify({"reply": " Internal server error occurred."}), 500


if __name__ == "__main__":
    print(" CampusBot Flask backend is running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
