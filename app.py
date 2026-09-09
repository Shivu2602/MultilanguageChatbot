from flask import Flask, render_template, request, jsonify, session
import json
import random
import re
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "multilanguage_chatbot_secret_key"


# =========================================================
# LOAD RESPONSES
# =========================================================

with open("data/responses.json", "r", encoding="utf-8") as file:
    responses = json.load(file)

with open("data/college_data.json", "r", encoding="utf-8") as file:
    college_data = json.load(file)

# =========================================================
# ENGLISH PATTERNS
# =========================================================

patterns = {

    "greeting": [
        "hi",
        "hii",
        "hiii",
        "hello",
        "hey",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "how are you doing",
        "what's up",
        "whats up",
        "nice to meet you"
    ],

    "thanks": [
        "thanks",
        "thank you",
        "thankyou",
        "thank u",
        "thanks a lot",
        "thank you so much",
        "many thanks"
    ],

    "goodbye": [
        "bye",
        "goodbye",
        "good bye",
        "see you",
        "see you later",
        "talk to you later",
        "take care"
    ],

    "help": [
        "help",
        "help me",
        "what can you do",
        "what do you know",
        "how can you help me",
        "what can i ask",
        "what questions can i ask"
    ],

    "college_location": [
        "where is the college",
        "where is your college",
        "college location",
        "college address",
        "where is rymec",
        "where is rym engineering college",
        "where is rym engineering college located",
        "where is rymec located",
        "location of rymec",
        "location of the college",
        "address of the college",
        "college situated",
        "where college is located"
    ],

    "courses": [
        "courses",
        "course",
        "what courses are available",
        "what courses are offered",
        "which courses are available",
        "which branches are available",
        "branches available",
        "engineering branches",
        "what branches does the college have",
        "what are the branches",
        "programs offered",
        "degree courses"
    ],

    "timings": [
        "timings",
        "timing",
        "college timing",
        "college timings",
        "college working hours",
        "working hours",
        "when does college start",
        "when does college end",
        "college starts at",
        "college ends at",
        "what time does college start",
        "what time does college close"
    ],

    "admission": [
        "admission",
        "admissions",
        "admission process",
        "how to get admission",
        "how can i get admission",
        "how do i get admission",
        "admission procedure",
        "admission details",
        "how to join college",
        "how can i join college",
        "ways to get admission",
        "cet admission",
        "management admission"
    ],

    "departments": [
        "departments",
        "department",
        "which departments are there",
        "what departments are there",
        "college departments",
        "engineering departments",
        "list of departments",
        "available departments",
        "what are the departments"
    ],

    "facilities": [
        "facilities",
        "facility",
        "college facilities",
        "what facilities are available",
        "what facilities does the college have",
        "college infrastructure",
        "infrastructure",
        "hostel",
        "library",
        "labs",
        "laboratories",
        "sports",
        "campus facilities"
    ],

    "contact": [
        "contact",
        "contact details",
        "contact number",
        "phone number",
        "college phone number",
        "college contact number",
        "how can i contact the college",
        "college telephone",
        "telephone number",
        "email",
        "college email"
    ],

    "college": [
        "college",
        "about college",
        "about the college",
        "tell me about the college",
        "tell me about rymec",
        "tell me about rym engineering college",
        "information about college",
        "college information",
        "rymec",
        "rym engineering college",
        "ry mec"
    ]
}
# =========================================================
# KANNADA PATTERNS
# =========================================================

kannada_patterns = {

    "greeting": [
        "ನಮಸ್ಕಾರ",
        "ನಮಸ್ತೆ",
        "ಹಾಯ್",
        "ಹಲೋ",
        "ಹೇ",
        "ಶುಭೋದಯ",
        "ಶುಭ ಮಧ್ಯಾಹ್ನ",
        "ಶುಭ ಸಂಜೆ"
    ],

    "thanks": [
        "ಧನ್ಯವಾದ",
        "ಧನ್ಯವಾದಗಳು",
        "ತುಂಬಾ ಧನ್ಯವಾದ",
        "ತುಂಬಾ ಧನ್ಯವಾದಗಳು"
    ],

    "goodbye": [
        "ಬೈ",
        "ವಿದಾಯ",
        "ಮತ್ತೆ ಸಿಗೋಣ",
        "ನಂತರ ಸಿಗೋಣ"
    ],

    "help": [
        "ಸಹಾಯ",
        "ಸಹಾಯ ಮಾಡಿ",
        "ನೀವು ಏನು ಮಾಡಬಹುದು",
        "ನೀವು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು",
        "ನಾನು ಏನು ಕೇಳಬಹುದು"
    ],

    "college_location": [
        "ಕಾಲೇಜು ಎಲ್ಲಿದೆ",
        "ಕಾಲೇಜ್ ಎಲ್ಲಿದೆ",
        "ಕಾಲೇಜಿನ ಸ್ಥಳ ಎಲ್ಲಿದೆ",
        "ಕಾಲೇಜಿನ ವಿಳಾಸ ಏನು",
        "ಆರ್ ವೈ ಎಂ ಇ ಸಿ ಎಲ್ಲಿದೆ",
        "ಆರ್ ವೈ ಎಂ ಇಂಜಿನಿಯರಿಂಗ್ ಕಾಲೇಜು ಎಲ್ಲಿದೆ",
        "ಕಾಲೇಜು ಯಾವ ಸ್ಥಳದಲ್ಲಿದೆ"
    ],

    "courses": [
        "ಕೋರ್ಸ್‌ಗಳು ಯಾವುವು",
        "ಕೋರ್ಸ್‌ಗಳು",
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳಿವೆ",
        "ಯಾವ ಶಾಖೆಗಳಿವೆ",
        "ಶಾಖೆಗಳು ಯಾವುವು",
        "ಎಂಜಿನಿಯರಿಂಗ್ ಶಾಖೆಗಳು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ಕೋರ್ಸ್‌ಗಳಿವೆ"
    ],

    "timings": [
        "ಕಾಲೇಜಿನ ಸಮಯ ಏನು",
        "ಕಾಲೇಜಿನ ಸಮಯಗಳು",
        "ಕಾಲೇಜು ಸಮಯ",
        "ಕಾಲೇಜು ಯಾವಾಗ ಪ್ರಾರಂಭವಾಗುತ್ತದೆ",
        "ಕಾಲೇಜು ಯಾವಾಗ ಮುಗಿಯುತ್ತದೆ",
        "ಕಾಲೇಜಿನ ಕೆಲಸದ ಸಮಯ"
    ],

    "admission": [
        "ಪ್ರವೇಶ ಹೇಗೆ ಪಡೆಯುವುದು",
        "ಕಾಲೇಜಿಗೆ ಪ್ರವೇಶ ಹೇಗೆ",
        "ಪ್ರವೇಶ ಪ್ರಕ್ರಿಯೆ ಏನು",
        "ಅಡ್ಮಿಷನ್ ಹೇಗೆ",
        "ಅಡ್ಮಿಷನ್ ಪ್ರಕ್ರಿಯೆ",
        "ಸಿಇಟಿ ಮೂಲಕ ಪ್ರವೇಶ",
        "ಮ್ಯಾನೇಜ್ಮೆಂಟ್ ಪ್ರವೇಶ"
    ],

    "departments": [
        "ವಿಭಾಗಗಳು ಯಾವುವು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ವಿಭಾಗಗಳಿವೆ",
        "ಯಾವ ವಿಭಾಗಗಳಿವೆ",
        "ಎಂಜಿನಿಯರಿಂಗ್ ವಿಭಾಗಗಳು",
        "ವಿಭಾಗಗಳ ಪಟ್ಟಿ"
    ],

    "facilities": [
        "ಸೌಲಭ್ಯಗಳು ಯಾವುವು",
        "ಕಾಲೇಜಿನ ಸೌಲಭ್ಯಗಳು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ಸೌಲಭ್ಯಗಳಿವೆ",
        "ಹಾಸ್ಟೆಲ್ ಇದೆಯೇ",
        "ಗ್ರಂಥಾಲಯ ಇದೆಯೇ",
        "ಲ್ಯಾಬ್‌ಗಳು ಇವೆಯೇ",
        "ಕ್ರೀಡಾ ಸೌಲಭ್ಯಗಳಿವೆಯೇ"
    ],

    "contact": [
        "ಸಂಪರ್ಕ ಸಂಖ್ಯೆ ಏನು",
        "ಕಾಲೇಜಿನ ಸಂಪರ್ಕ ಸಂಖ್ಯೆ",
        "ಫೋನ್ ನಂಬರ್ ಏನು",
        "ಕಾಲೇಜಿನ ಫೋನ್ ನಂಬರ್",
        "ಕಾಲೇಜನ್ನು ಹೇಗೆ ಸಂಪರ್ಕಿಸುವುದು",
        "ಸಂಪರ್ಕ ವಿವರಗಳು",
        "ಕಾಲೇಜಿನ ಇಮೇಲ್"
    ],

    "college": [
        "ಕಾಲೇಜಿನ ಬಗ್ಗೆ ಹೇಳಿ",
        "ಕಾಲೇಜಿನ ಮಾಹಿತಿ",
        "ಆರ್ ವೈ ಎಂ ಇ ಸಿ ಬಗ್ಗೆ ಹೇಳಿ",
        "ಕಾಲೇಜು ಬಗ್ಗೆ ಮಾಹಿತಿ",
        "ಈ ಕಾಲೇಜಿನ ಬಗ್ಗೆ ಹೇಳಿ"
    ]
}


# =========================================================
# ENGLISH KEYWORDS
# =========================================================

english_keywords = {

    "greeting": [
        "hi",
        "hii",
        "hello",
        "hey",
        "morning",
        "afternoon",
        "evening"
    ],

    "thanks": [
        "thanks",
        "thank"
    ],

    "goodbye": [
        "bye",
        "goodbye",
        "later"
    ],

    "help": [
        "help",
        "assist",
        "questions",
        "ask"
    ],

    "college_location": [
        "where",
        "location",
        "address",
        "situated",
        "located"
    ],

    "courses": [
        "course",
        "courses",
        "branch",
        "branches",
        "program",
        "programs"
    ],

    "timings": [
        "time",
        "timing",
        "timings",
        "hours",
        "start",
        "close",
        "end"
    ],

    "admission": [
        "admission",
        "admissions",
        "join",
        "joining",
        "cet",
        "management"
    ],

    "departments": [
        "department",
        "departments"
    ],

    "facilities": [
        "facility",
        "facilities",
        "hostel",
        "library",
        "lab",
        "labs",
        "sports",
        "infrastructure"
    ],

    "contact": [
        "contact",
        "phone",
        "number",
        "email",
        "telephone"
    ],

    "college": [
        "college",
        "rymec",
        "engineering"
    ]
}


#=========================================================
# FUZZY TYPO KEYWORDS
# =========================================================

fuzzy_keywords = {

    "greeting": [
        "hi",
        "hello",
        "hey"
    ],

    "thanks": [
        "thanks",
        "thankyou"
    ],

    "goodbye": [
        "bye",
        "goodbye"
    ],

    "help": [
        "help"
    ],

    "college_location": [
        "location",
        "address",
        "where"
    ],

    "courses": [
        "course",
        "courses",
        "branch",
        "branches"
    ],

    "timings": [
        "timing",
        "timings",
        "hours"
    ],

    "admission": [
        "admission",
        "admissions"
    ],

    "departments": [
        "department",
        "departments"
    ],

    "facilities": [
        "facility",
        "facilities",
        "library",
        "hostel",
        "labs"
    ],

    "contact": [
        "contact",
        "phone",
        "email"
    ],

    "college": [
        "college",
        "rymec"
    ]
}


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def is_kannada(message):
    """
    Detect Kannada using Unicode range.
    Kannada Unicode range: U+0C80 - U+0CFF
    """

    return bool(re.search(r"[\u0C80-\u0CFF]", message))


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):

    text = text.lower().strip()

    # Remove unnecessary punctuation
    text = re.sub(r"[?!.,;:'\"`]+", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# KANNADA INTENT RECOGNITION
# =========================================================

def recognize_kannada_intent(message):

    normalized_message = normalize_text(message)

    for intent, examples in kannada_patterns.items():

        for example in examples:

            if normalize_text(example) == normalized_message:
                return intent

    # Partial matching
    for intent, examples in kannada_patterns.items():

        for example in examples:

            normalized_example = normalize_text(example)

            if normalized_example in normalized_message:
                return intent

    return None


# =========================================================
# EXACT ENGLISH INTENT RECOGNITION
# =========================================================

def recognize_intent(message):

    normalized_message = normalize_text(message)

    # Exact pattern matching
    for intent, examples in patterns.items():

        for example in examples:

            if normalize_text(example) == normalized_message:
                return intent

    return None


# =========================================================
# KEYWORD-BASED INTENT RECOGNITION
# =========================================================

def recognize_intent_by_keywords(message):

    normalized_message = normalize_text(message)

    words = normalized_message.split()

    scores = {}

    for intent, keywords in english_keywords.items():

        score = 0

        for keyword in keywords:

            keyword = normalize_text(keyword)

            # Exact word match
            if keyword in words:
                score += 2

            # Phrase match
            if keyword in normalized_message:
                score += 1

        scores[intent] = score

    if not scores:
        return None

    best_intent = max(scores, key=scores.get)

    if scores[best_intent] > 0:
        return best_intent

    return None


# =========================================================
# SIMILARITY CALCULATION
# =========================================================

def similarity(text1, text2):

    return SequenceMatcher(
        None,
        normalize_text(text1),
        normalize_text(text2)
    ).ratio()


# =========================================================
# TYPO / FUZZY INTENT RECOGNITION
# =========================================================

def recognize_typo_intent(message):

    normalized_message = normalize_text(message)

    words = normalized_message.split()

    best_intent = None
    best_score = 0

    for intent, keywords in fuzzy_keywords.items():

        for word in words:

            for keyword in keywords:

                score = similarity(word, keyword)

                if score > best_score:
                    best_score = score
                    best_intent = intent

    # Only accept reasonably close words
    if best_score >= 0.72:
        return best_intent

    return None


# =========================================================
# SMART ENGLISH INTENT RECOGNITION
# =========================================================

def smart_english_intent(message):

    normalized_message = normalize_text(message)

    # -----------------------------------------------------
    # Exact match
    # -----------------------------------------------------

    intent = recognize_intent(normalized_message)

    if intent:
        return intent

    # -----------------------------------------------------
    # Important phrase rules
    # -----------------------------------------------------

    location_phrases = [
        "where is",
        "where are",
        "where can i find",
        "located",
        "location",
        "address"
    ]

    if any(phrase in normalized_message for phrase in location_phrases):

        if "college" in normalized_message or \
           "rymec" in normalized_message or \
           "engineering" in normalized_message:

            return "college_location"

    # Admission
    if any(word in normalized_message for word in [
        "admission",
        "admissions",
        "admisson",
        "admissons"
    ]):
        return "admission"

    # Courses / branches
    if any(word in normalized_message for word in [
        "course",
        "courses",
        "branch",
        "branches",
        "program",
        "programs"
    ]):
        return "courses"

    # Timings
    if any(word in normalized_message for word in [
        "timing",
        "timings",
        "time",
        "hours"
    ]) and "college" in normalized_message:

        return "timings"

    # Departments
    if "department" in normalized_message or \
       "departments" in normalized_message:

        return "departments"

    # Facilities
    if any(word in normalized_message for word in [
        "facility",
        "facilities",
        "hostel",
        "library",
        "lab",
        "labs",
        "sports",
        "infrastructure"
    ]):

        return "facilities"

    # Contact
    if any(word in normalized_message for word in [
        "contact",
        "phone",
        "telephone",
        "email"
    ]):

        return "contact"
    # -----------------------------------------------------
    # Keyword matching
    # -----------------------------------------------------

    intent = recognize_intent_by_keywords(normalized_message)

    if intent:
        return intent

    # -----------------------------------------------------
    # Fuzzy typo matching
    # -----------------------------------------------------

    intent = recognize_typo_intent(normalized_message)

    if intent:
        return intent

    return "default"


# =========================================================
# TRANSLATE KANNADA TO ENGLISH
# =========================================================

def translate_to_english(message):

    try:

        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(message)

        return translated

    except Exception as error:

        print("Kannada translation error:", error)

        return message


# =========================================================
# GENERATE RESPONSE
# =========================================================

def generate_response(language, intent):

    # Make sure language exists
    if language not in responses:
        language = "en"

    # Make sure intent exists
    if intent not in responses[language]:
        intent = "default"

    response_list = responses[language][intent]

    # Safety check
    if not response_list:
        return "Please try asking your question again."

    # -----------------------------------------------------
    # Avoid immediately repeating the same response
    # -----------------------------------------------------

    previous_response = session.get("previous_response")

    available_responses = [
        response
        for response in response_list
        if response != previous_response
    ]

    if not available_responses:
        available_responses = response_list

    response = random.choice(available_responses)

    session["previous_response"] = response

    return response


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin/data", methods=["GET"])
def get_college_data():
    return jsonify(college_data)


@app.route("/admin/data", methods=["POST"])
def update_college_data():
    global college_data

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid data."
        }), 400

    college_data = data

    try:
        with open(
            "data/college_data.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                college_data,
                file,
                ensure_ascii=False,
                indent=4
            )

        return jsonify({
            "success": True,
            "message": "College information updated successfully."
        })

    except Exception as error:

        print("Error saving college data:", error)

        return jsonify({
            "success": False,
            "message": "Unable to save college information."
        }), 500


# =========================================================
# TRANSLATOR API
# =========================================================

@app.route("/translate", methods=["POST"])
def translate_text():

    data = request.get_json()

    if not data:
        return jsonify({
            "translation": "",
            "error": "Invalid request."
        }), 400

    text = data.get("text", "").strip()

    target_language = data.get("target", "kn")

    # -----------------------------------------------------
    # Empty text
    # -----------------------------------------------------

    if not text:

        return jsonify({
            "translation": "",
            "error": "Please enter text to translate."
        }), 400

    # -----------------------------------------------------
    # Allow only English and Kannada
    # -----------------------------------------------------

    if target_language not in ["en", "kn"]:
        target_language = "kn"

    try:

        translator = GoogleTranslator(
            source="auto",
            target=target_language
        )

        translated = translator.translate(text)

        if not translated:
            raise Exception("Empty translation received")

        print("--------------------------------")
        print("Translation request")
        print("Original:", text)
        print("Target:", target_language)
        print("Translation:", translated)
        print("--------------------------------")

        return jsonify({
            "translation": translated,
            "error": ""
        })

    except Exception as error:

        print("TRANSLATION ERROR:", error)

        return jsonify({
            "translation": "",
            "error": "Translation service is temporarily unavailable."
        }), 500


# =========================================================
# CHAT API
# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:

        return jsonify({
            "response": "Please enter a message.",
            "intent": "default",
            "language": "en"
        })

    user_message = data.get(
        "message",
        ""
    ).strip()

    # -----------------------------------------------------
    # Empty message
    # -----------------------------------------------------

    if not user_message:

        return jsonify({
            "response": "Please enter a message.",
            "intent": "default",
            "language": "en"
        })

    print()
    print("========================================")
    print("User message:", user_message)

    # =====================================================
    # AUTOMATIC LANGUAGE DETECTION
    # =====================================================

    if is_kannada(user_message):

        language = "kn"

        # First try direct Kannada intent recognition
        intent = recognize_kannada_intent(user_message)

        # If not recognized, translate Kannada to English
        # and use English intent recognition
        if intent is None:

            english_message = translate_to_english(
                user_message
            )

            print(
                "Translated Kannada:",
                english_message
            )

            intent = smart_english_intent(
                english_message
            )

    else:

        language = "en"

        intent = smart_english_intent(
            user_message
        )

    # =====================================================
    # FOLLOW-UP QUESTIONS
    # =====================================================

    normalized_message = normalize_text(user_message)

    follow_up_phrases = [
        "tell me more",
        "more details",
        "more information",
        "what else",
        "anything else",
        "and",
        "also",
        "more",
        "ಇನ್ನಷ್ಟು",
        "ಹೆಚ್ಚಿನ ಮಾಹಿತಿ",
        "ಇನ್ನೇನು",
        "ಮತ್ತಷ್ಟು"
    ]

    is_follow_up = any(
        phrase == normalized_message
        for phrase in follow_up_phrases
    )

    if is_follow_up:

        previous_intent = session.get(
            "previous_intent"
        )

        if previous_intent:

            intent = previous_intent

    # =====================================================
    # SAVE CONVERSATION CONTEXT
    # =====================================================

    session["previous_intent"] = intent

    # =====================================================
    # GENERATE RESPONSE
    # =====================================================

    response = generate_response(
        language,
        intent
    )

    # =====================================================
    # TERMINAL DEBUG INFORMATION
    # =====================================================

    print("Detected language:", language)
    print("Detected intent:", intent)
    print("Response:", response)
    print("========================================")
    print()

    return jsonify({
        "response": response,
        "intent": intent,
        "language": language
    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )