from flask import Flask, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


@app.route("/")
def home():
    return "Dial *544# to purchase bundles"


@app.route("/send-request", methods=["GET"])
def USSD_request():

    user_code = request.args.get("code", "") + "#"
    if user_code == "*544#":
        first_screen = {
            0: "My Data Deals",
            1: "No Expiry Bundles"
        }
        if request.args.get("text") == "0":
            bundle_0 = {
                "1": "Sh 10=750MB for 1hr",
                "2": "sh 5=500MB for 1hr",
                "0.": "Back",
                "00.": "Home"
            }
            if request.args.get("text") == "2":
                accept_decline = {
                    "Accept": "None",
                    "Decline": "N",
                }
                return jsonify(accept_decline)

            return jsonify(bundle_0)

        return first_screen

    else:
        invalid_message = {
            "Error": "Invalid MMI code"
        }
        return jsonify(invalid_message)


if __name__ == "__main__":
    app.run(debug=True)
