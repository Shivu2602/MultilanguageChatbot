from flask import Flask, render_template, request, jsonify
import json
import random
import re

app = Flask(__name__)


# Load chatbot responses
with open("data/responses.json", "r", encoding="utf-8") as file:
    responses = json.load(file)


# Patterns used to identify user intent
patterns = {
    "greeting": [
        r"\bhello\b",
        r"\bhi\b",
        r"\bhey\b",
        r"\bhello chatbot\b",
        r"\bhi chatbot\b",
        r"\bhey there\b",
        r"\bgood morning\b",
        r"\bgood afternoon\b",
        r"\bgood evening\b"
    ],

    "thanks": [
        r"\bthank you\b",
        r"\bthanks\b",
        r"\bthank\b",
        r"\bthanks a lot\b",
        r"\bthank you so much\b"
    ],

    "goodbye": [
        r"\bbye\b",
        r"\bgoodbye\b",
        r"\bsee you\b",
        r"\bsee you later\b",
        r"\btalk to you later\b"
    ],

    "help": [
        r"\bhelp\b",
        r"\bcan you help me\b",
        r"\bi need help\b",
        r"\bwhat can you do\b",
        r"\bhow can you help me\b"
    ]
}

def recognize_intent(message):
    """Identify the user's intent using pattern matching."""

    message = message.lower().strip()

    for intent, intent_patterns in patterns.items():

        for pattern in intent_patterns:

            if re.search(pattern, message):
                return intent

    return "default"


def generate_response(intent):
    """Select a response for the detected intent."""

    return random.choice(responses[intent])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "response": "Please enter a message."
        })

    # Identify intent
    intent = recognize_intent(user_message)

    # Generate response
    response = generate_response(intent)

    return jsonify({
        "response": response
    })


if __name__ == "__main__":
    app.run(debug=True)