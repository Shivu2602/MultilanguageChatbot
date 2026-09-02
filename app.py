from flask import Flask, render_template, request, jsonify, session
import json
import random
import re
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Secret key required for Flask sessions
app.secret_key = "multilanguage_chatbot_secret_key"


# =========================================
# LOAD RESPONSES FROM JSON
# =========================================

with open("data/responses.json", "r", encoding="utf-8") as file:
    responses = json.load(file)


# =========================================
# ENGLISH INTENT PATTERNS
# =========================================

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
        r"\bgood evening\b",
        r"\bhow are you\b",
        r"\bhow are you doing\b",
        r"\bhow is it going\b"
    ],

    "thanks": [
        r"\bthank you\b",
        r"\bthanks\b",
        r"\bthank\b",
        r"\bthanks a lot\b",
        r"\bthank you so much\b",
        r"\bmany thanks\b",
        r"\bthanks for helping\b",
        r"\bthank you for helping\b"
    ],

    "goodbye": [
        r"\bbye\b",
        r"\bgoodbye\b",
        r"\bsee you\b",
        r"\bsee you later\b",
        r"\btalk to you later\b",
        r"\bsee you again\b",
        r"\bcatch you later\b",
        r"\bi have to go\b"
    ],

    "help": [
        r"\bhelp\b",
        r"\bcan you help me\b",
        r"\bi need help\b",
        r"\bwhat can you do\b",
        r"\bhow can you help me\b",
        r"\bhow do you help\b",
        r"\bwhat do you know\b",
        r"\bhow can i use you\b",
        r"\bwhat can i ask you\b",
        r"\bwhat questions can i ask\b"
    ],

    "college_location": [
        r"\bwhere is the college\b",
        r"\bwhere is rymec\b",
        r"\bwhere is rym engineering college\b",
        r"\bwhere is rymec located\b",
        r"\bcollege location\b",
        r"\bcollege address\b",
        r"\bwhat is the college address\b",
        r"\bwhere can i find the college\b",
        r"\bwhere is the college located\b",
        r"\bwhere can i find rymec\b",
        r"\bwhat is the location of the college\b",
        r"\bwhat is the location of rymec\b",
        r"\bcollege is located where\b",
        r"\bwhere can i visit the college\b"
    ],

    "courses": [
        r"\bwhat courses\b",
        r"\bwhich courses\b",
        r"\bwhat branches\b",
        r"\bwhich branches\b",
        r"\bavailable courses\b",
        r"\bavailable branches\b",
        r"\bcollege courses\b",
        r"\bengineering branches\b",
        r"\bwhat can i study\b",
        r"\bwhat can i study here\b",
        r"\bwhat programs are available\b",
        r"\bwhat programs does the college offer\b",
        r"\bwhat programs does rymec offer\b",
        r"\bwhat engineering courses are available\b",
        r"\bwhich engineering courses are offered\b",
        r"\bwhat are the courses offered\b",
        r"\bwhat are the available courses\b",
        r"\bwhat branches are offered\b",
        r"\bwhich branches are offered\b",
        r"\bwhat can i study in rymec\b",
        r"\bi want to know about the courses\b",
        r"\btell me about the courses\b",
        r"\btell me about available courses\b",
        r"\btell me the branches\b",
        r"\blist the courses\b",
        r"\blist the branches\b",
        r"\bwhat can i choose\b",
        r"\bwhich course can i choose\b"
    ],

    "timings": [
        r"\bcollege timing\b",
        r"\bcollege timings\b",
        r"\bcollege time\b",
        r"\bcollege working hours\b",
        r"\bwhat are the college timings\b",
        r"\bwhen does college start\b",
        r"\bwhen does college end\b",
        r"\bwhat time does college start\b",
        r"\bwhat time does college end\b",
        r"\bwhen does the college open\b",
        r"\bwhen does the college close\b",
        r"\bwhat time does college open\b",
        r"\bwhat time does college close\b",
        r"\bwhat are the working hours\b",
        r"\bwhen is the college open\b",
        r"\bwhen is the college closed\b",
        r"\bcollege opens at what time\b",
        r"\bcollege closes at what time\b",
        r"\bcollege starts at what time\b",
        r"\bcollege ends at what time\b",
        r"\bhow many hours is the college open\b"
    ],

    "admission": [
        r"\badmission\b",
        r"\badmissions\b",
        r"\bhow to get admission\b",
        r"\bhow can i get admission\b",
        r"\bcollege admission\b",
        r"\bcet admission\b",
        r"\bmanagement admission\b",
        r"\badmission process\b",
        r"\bhow to join the college\b",
        r"\bhow can i join the college\b",
        r"\bhow do i get admission\b",
        r"\bhow can i take admission\b",
        r"\bhow to take admission\b",
        r"\bhow do i join rymec\b",
        r"\bhow can i join rymec\b",
        r"\bwhat is the admission process\b",
        r"\bwhat is the admission procedure\b",
        r"\bhow can i apply for admission\b",
        r"\bhow do i apply for admission\b",
        r"\bwhat are the admission options\b",
        r"\bcan i get admission through cet\b",
        r"\bdoes rymec accept cet\b",
        r"\bis management admission available\b"
    ],

    "departments": [
        r"\bdepartments\b",
        r"\bcollege departments\b",
        r"\bwhat departments\b",
        r"\bwhich departments\b",
        r"\bdepartment list\b",
        r"\bwhat departments are there\b",
        r"\bwhat departments does the college have\b",
        r"\blist the departments\b",
        r"\bwhat are the college departments\b",
        r"\bwhich departments are available\b",
        r"\bwhat departments are available\b",
        r"\btell me about the departments\b",
        r"\bshow me the departments\b",
        r"\bhow many departments\b"
    ],

    "facilities": [
        r"\bfacilities\b",
        r"\bcollege facilities\b",
        r"\bwhat facilities\b",
        r"\bwhat facilities are available\b",
        r"\bcollege infrastructure\b",
        r"\bwhat infrastructure does the college have\b",
        r"\bhostel\b",
        r"\bdoes the college have a hostel\b",
        r"\bis there a hostel\b",
        r"\bis hostel available\b",
        r"\bdoes rymec have hostel\b",
        r"\blibrary\b",
        r"\bdoes the college have a library\b",
        r"\bis there a library\b",
        r"\bis library available\b",
        r"\bdoes rymec have a library\b",
        r"\blaborator(y|ies)\b",
        r"\blabs\b",
        r"\bdoes the college have labs\b",
        r"\bsports\b",
        r"\bdoes the college have sports\b",
        r"\bsports facilities\b",
        r"\bcomputer center\b",
        r"\bcomputer facilities\b",
        r"\bwhat facilities does rymec have\b",
        r"\btell me about the facilities\b",
        r"\bwhat facilities does the college provide\b",
        r"\bwhat amenities are available\b"
    ],

    "contact": [
        r"\bcontact\b",
        r"\bcontact details\b",
        r"\bcontact number\b",
        r"\bphone number\b",
        r"\btelephone\b",
        r"\bemail\b",
        r"\bcollege phone\b",
        r"\bcollege email\b",
        r"\bhow can i contact the college\b",
        r"\bhow can i contact rymec\b",
        r"\bwhat is the contact number\b",
        r"\bwhat is the phone number\b",
        r"\bwhat is the college phone number\b",
        r"\bwhat is the college email\b",
        r"\bhow do i contact the college\b",
        r"\bhow do i contact rymec\b",
        r"\bwhere can i contact the college\b",
        r"\bcan you give me the contact details\b",
        r"\bgive me the college contact\b"
    ],

    "college": [
        r"\btell me about the college\b",
        r"\babout the college\b",
        r"\babout rymec\b",
        r"\bcollege information\b",
        r"\bcollege info\b",
        r"\bwhat is rymec\b",
        r"\bwhat is rym engineering college\b",
        r"\btell me about rymec\b",
        r"\bi want to know about the college\b",
        r"\bi want information about the college\b",
        r"\bgive me information about the college\b",
        r"\bgive me college information\b",
        r"\bcan you tell me about the college\b",
        r"\bcan you tell me about rymec\b",
        r"\bwhat do you know about rymec\b",
        r"\bwhat do you know about the college\b",
        r"\bmore information about rymec\b",
        r"\bmore information about the college\b"
    ]
}


# =========================================
# KANNADA INTENT PATTERNS
# =========================================

kannada_patterns = {

    "greeting": [
        "ನಮಸ್ಕಾರ",
        "ನಮಸ್ತೆ",
        "ಹಾಯ್",
        "ಹಲೋ",
        "ಹೇ",
        "ಹೇಗಿದ್ದೀರಾ",
        "ಎಲ್ಲಾ ಹೇಗಿದೆ"
    ],

    "thanks": [
        "ಧನ್ಯವಾದ",
        "ಧನ್ಯವಾದಗಳು",
        "ತುಂಬಾ ಧನ್ಯವಾದಗಳು",
        "ಸಹಾಯ ಮಾಡಿದ್ದಕ್ಕೆ ಧನ್ಯವಾದ",
        "ಸಹಾಯಕ್ಕೆ ಧನ್ಯವಾದ"
    ],

    "goodbye": [
        "ವಿದಾಯ",
        "ಬೈ",
        "ಮತ್ತೆ ಸಿಗೋಣ",
        "ಮತ್ತೆ ಭೇಟಿಯಾಗೋಣ",
        "ನಂತರ ಸಿಗೋಣ",
        "ಹೋಗುತ್ತೇನೆ"
    ],

    "help": [
        "ಸಹಾಯ",
        "ಸಹಾಯ ಮಾಡಿ",
        "ನನಗೆ ಸಹಾಯ ಬೇಕು",
        "ನೀವು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು",
        "ನೀವು ಏನು ಮಾಡಬಹುದು",
        "ನನಗೆ ಸಹಾಯ ಬೇಕಾಗಿದೆ",
        "ನಾನು ಏನು ಕೇಳಬಹುದು",
        "ನೀವು ಯಾವ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಬಹುದು",
        "ನಿಮ್ಮಿಂದ ಏನು ಸಹಾಯ ಪಡೆಯಬಹುದು"
    ],

    "college_location": [
        "ಕಾಲೇಜು ಎಲ್ಲಿದೆ",
        "ಕಾಲೇಜಿನ ಸ್ಥಳ",
        "ಕಾಲೇಜಿನ ವಿಳಾಸ",
        "ಕಾಲೇಜು ಯಾವ ಸ್ಥಳದಲ್ಲಿದೆ",
        "RYMEC ಎಲ್ಲಿದೆ",
        "ಆರ್‌ವೈಎಂಇಸಿ ಎಲ್ಲಿದೆ",
        "ಕಾಲೇಜಿನ ವಿಳಾಸ ಏನು",
        "ಕಾಲೇಜು ಎಲ್ಲಿದೆ ಎಂದು ಹೇಳಿ",
        "ಕಾಲೇಜು ಯಾವ ಕಡೆ ಇದೆ",
        "RYMEC ಯಾವ ಸ್ಥಳದಲ್ಲಿದೆ",
        "ಕಾಲೇಜಿನ ಸ್ಥಳ ಯಾವುದು",
        "ಕಾಲೇಜಿನ ವಿಳಾಸ ತಿಳಿಸಿ",
        "ಕಾಲೇಜನ್ನು ಎಲ್ಲಿ ಕಾಣಬಹುದು"
    ],

    "courses": [
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳು ಇವೆ",
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳಿವೆ",
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳು ಲಭ್ಯವಿವೆ",
        "ಯಾವ ಬ್ರಾಂಚ್‌ಗಳಿವೆ",
        "ಯಾವ ವಿಭಾಗಗಳಿವೆ",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ಕೋರ್ಸ್‌ಗಳಿವೆ",
        "ಎಂಜಿನಿಯರಿಂಗ್ ಕೋರ್ಸ್‌ಗಳು ಯಾವುವು",
        "ನಾನು ಏನು ಓದಬಹುದು",
        "ಇಲ್ಲಿ ಏನು ಓದಬಹುದು",
        "ಯಾವ ಕಾರ್ಯಕ್ರಮಗಳು ಲಭ್ಯವಿವೆ",
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳನ್ನು ನೀಡಲಾಗುತ್ತದೆ",
        "ಯಾವ ಕೋರ್ಸ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಬಹುದು",
        "ಲಭ್ಯವಿರುವ ಕೋರ್ಸ್‌ಗಳ ಬಗ್ಗೆ ತಿಳಿಸಿ",
        "ಕೋರ್ಸ್‌ಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕು",
        "ಕೋರ್ಸ್‌ಗಳ ಬಗ್ಗೆ ಹೇಳಿ",
        "ಯಾವ ಬ್ರಾಂಚ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಬಹುದು",
        "ಯಾವ ವಿಭಾಗಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಬಹುದು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಏನು ಓದಬಹುದು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ಬ್ರಾಂಚ್‌ಗಳಿವೆ",
        "ಕೋರ್ಸ್‌ಗಳ ಪಟ್ಟಿ ನೀಡಿ"
    ],

    "timings": [
        "ಕಾಲೇಜಿನ ಸಮಯ",
        "ಕಾಲೇಜಿನ ಸಮಯ ಏನು",
        "ಕಾಲೇಜು ಸಮಯ",
        "ಕಾಲೇಜಿನ ಕಾರ್ಯನಿರ್ವಹಣಾ ಸಮಯ",
        "ಕಾಲೇಜು ಯಾವ ಸಮಯಕ್ಕೆ ಪ್ರಾರಂಭವಾಗುತ್ತದೆ",
        "ಕಾಲೇಜು ಯಾವ ಸಮಯಕ್ಕೆ ಮುಗಿಯುತ್ತದೆ",
        "ಕಾಲೇಜು ಯಾವಾಗ ಪ್ರಾರಂಭವಾಗುತ್ತದೆ",
        "ಕಾಲೇಜು ಯಾವಾಗ ಮುಗಿಯುತ್ತದೆ",
        "ಕಾಲೇಜು ಬೆಳಿಗ್ಗೆ ಯಾವ ಸಮಯಕ್ಕೆ ತೆರೆಯುತ್ತದೆ",
        "ಕಾಲೇಜು ಸಂಜೆ ಯಾವ ಸಮಯಕ್ಕೆ ಮುಚ್ಚುತ್ತದೆ",
        "ಕಾಲೇಜು ಯಾವ ಸಮಯಕ್ಕೆ ತೆರೆಯುತ್ತದೆ",
        "ಕಾಲೇಜು ಯಾವ ಸಮಯಕ್ಕೆ ಮುಚ್ಚುತ್ತದೆ",
        "ಕಾಲೇಜಿನ ಕೆಲಸದ ಸಮಯ ಎಷ್ಟು",
        "ಕಾಲೇಜಿನ ಕಾರ್ಯ ಸಮಯ ತಿಳಿಸಿ",
        "ಕಾಲೇಜು ಎಷ್ಟು ಗಂಟೆ ತೆರೆದಿರುತ್ತದೆ"
    ],

    "admission": [
        "ಪ್ರವೇಶ",
        "ಪ್ರವೇಶದ ಬಗ್ಗೆ",
        "ಪ್ರವೇಶದ ಬಗ್ಗೆ ಹೇಳಿ",
        "ಕಾಲೇಜು ಪ್ರವೇಶ",
        "CET ಪ್ರವೇಶ",
        "ಮ್ಯಾನೇಜ್‌ಮೆಂಟ್ ಪ್ರವೇಶ",
        "ಪ್ರವೇಶ ಪ್ರಕ್ರಿಯೆ",
        "ಕಾಲೇಜಿಗೆ ಹೇಗೆ ಪ್ರವೇಶ ಪಡೆಯುವುದು",
        "ಕಾಲೇಜಿಗೆ ಹೇಗೆ ಸೇರಬಹುದು",
        "ಪ್ರವೇಶ ಹೇಗೆ ಪಡೆಯಬಹುದು",
        "ಪ್ರವೇಶ ಪಡೆಯುವುದು ಹೇಗೆ",
        "ಕಾಲೇಜಿಗೆ ಸೇರಲು ಹೇಗೆ",
        "ಕಾಲೇಜಿಗೆ ಪ್ರವೇಶ ಪಡೆಯಲು ಹೇಗೆ",
        "CET ಮೂಲಕ ಪ್ರವೇಶ ಪಡೆಯಬಹುದೇ",
        "ಮ್ಯಾನೇಜ್‌ಮೆಂಟ್ ಮೂಲಕ ಪ್ರವೇಶ ಇದೆಯೇ",
        "ಪ್ರವೇಶದ ವಿಧಾನ ಏನು",
        "ಪ್ರವೇಶದ ಪ್ರಕ್ರಿಯೆ ಏನು"
    ],

    "departments": [
        "ವಿಭಾಗಗಳು",
        "ಕಾಲೇಜಿನ ವಿಭಾಗಗಳು",
        "ಯಾವ ವಿಭಾಗಗಳಿವೆ",
        "ಯಾವ ವಿಭಾಗಗಳು ಇವೆ",
        "ವಿಭಾಗಗಳ ಪಟ್ಟಿ",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ವಿಭಾಗಗಳಿವೆ",
        "ಯಾವ ವಿಭಾಗಗಳು ಲಭ್ಯವಿವೆ",
        "ಕಾಲೇಜಿನ ಯಾವ ವಿಭಾಗಗಳಿವೆ",
        "ವಿಭಾಗಗಳ ಬಗ್ಗೆ ತಿಳಿಸಿ",
        "ವಿಭಾಗಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕು",
        "ವಿಭಾಗಗಳ ಪಟ್ಟಿಯನ್ನು ನೀಡಿ"
    ],

    "facilities": [
        "ಸೌಲಭ್ಯಗಳು",
        "ಕಾಲೇಜಿನ ಸೌಲಭ್ಯಗಳು",
        "ಯಾವ ಸೌಲಭ್ಯಗಳಿವೆ",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ಸೌಲಭ್ಯಗಳಿವೆ",
        "ಕಾಲೇಜಿನ ಮೂಲಸೌಕರ್ಯ",
        "ಹಾಸ್ಟೆಲ್",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಹಾಸ್ಟೆಲ್ ಇದೆಯೇ",
        "ಹಾಸ್ಟೆಲ್ ಸೌಲಭ್ಯ ಇದೆಯೇ",
        "ಹಾಸ್ಟೆಲ್ ಇದೆಯಾ",
        "ಗ್ರಂಥಾಲಯ",
        "ಲೈಬ್ರರಿ",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಲೈಬ್ರರಿ ಇದೆಯೇ",
        "ಲ್ಯಾಬ್",
        "ಲ್ಯಾಬ್‌ಗಳು",
        "ಪ್ರಯೋಗಾಲಯ",
        "ಕ್ರೀಡೆ",
        "ಕ್ರೀಡಾ ಸೌಲಭ್ಯಗಳು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಕ್ರೀಡಾ ಸೌಲಭ್ಯಗಳಿವೆಯೇ",
        "ಕಂಪ್ಯೂಟರ್ ಸೆಂಟರ್",
        "ಕಂಪ್ಯೂಟರ್ ಸೌಲಭ್ಯಗಳು",
        "ಕಾಲೇಜಿನಲ್ಲಿ ಯಾವ ಸೌಲಭ್ಯಗಳು ಲಭ್ಯವಿವೆ",
        "ಸೌಲಭ್ಯಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕು",
        "ಕಾಲೇಜಿನ ಸೌಲಭ್ಯಗಳ ಬಗ್ಗೆ ಹೇಳಿ"
    ],

    "contact": [
        "ಸಂಪರ್ಕ",
        "ಸಂಪರ್ಕ ವಿವರಗಳು",
        "ಸಂಪರ್ಕ ಸಂಖ್ಯೆ",
        "ಫೋನ್ ಸಂಖ್ಯೆ",
        "ದೂರವಾಣಿ ಸಂಖ್ಯೆ",
        "ಇಮೇಲ್",
        "ಕಾಲೇಜಿನ ಫೋನ್",
        "ಕಾಲೇಜಿನ ಇಮೇಲ್",
        "ಕಾಲೇಜನ್ನು ಹೇಗೆ ಸಂಪರ್ಕಿಸುವುದು",
        "RYMEC ಅನ್ನು ಹೇಗೆ ಸಂಪರ್ಕಿಸುವುದು",
        "ಕಾಲೇಜಿನ ಸಂಪರ್ಕ ಸಂಖ್ಯೆ ಏನು",
        "ಕಾಲೇಜಿನ ಫೋನ್ ಸಂಖ್ಯೆ ಏನು",
        "ಕಾಲೇಜಿನ ಇಮೇಲ್ ಏನು",
        "ಕಾಲೇಜಿನ ಸಂಪರ್ಕ ವಿವರಗಳನ್ನು ನೀಡಿ",
        "ಕಾಲೇಜನ್ನು ಸಂಪರ್ಕಿಸುವುದು ಹೇಗೆ"
    ],

    "college": [
        "ಕಾಲೇಜಿನ ಬಗ್ಗೆ",
        "ಕಾಲೇಜಿನ ಬಗ್ಗೆ ಹೇಳಿ",
        "ಕಾಲೇಜಿನ ಮಾಹಿತಿ",
        "RYMEC ಬಗ್ಗೆ",
        "ಆರ್‌ವೈಎಂಇಸಿ ಬಗ್ಗೆ",
        "RYMEC ಬಗ್ಗೆ ಹೇಳಿ",
        "ಕಾಲೇಜಿನ ಬಗ್ಗೆ ಮಾಹಿತಿ ನೀಡಿ",
        "ನನಗೆ ಕಾಲೇಜಿನ ಬಗ್ಗೆ ತಿಳಿಯಬೇಕು",
        "ಕಾಲೇಜಿನ ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕು",
        "ಕಾಲೇಜಿನ ಕುರಿತು ಹೇಳಿ",
        "ಕಾಲೇಜಿನ ಕುರಿತು ಮಾಹಿತಿ ನೀಡಿ",
        "RYMEC ಬಗ್ಗೆ ಮಾಹಿತಿ ಬೇಕು",
        "ಕಾಲೇಜಿನ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ತಿಳಿಸಿ"
    ]
}


# =========================================
# ENGLISH KEYWORDS
# =========================================

english_keywords = {

    "greeting": [
        "hello",
        "hi",
        "hey",
        "morning",
        "afternoon",
        "evening"
    ],

    "thanks": [
        "thank",
        "thanks",
        "grateful",
        "appreciate"
    ],

    "goodbye": [
        "bye",
        "goodbye",
        "later",
        "see you"
    ],

    "help": [
        "help",
        "assist",
        "support",
        "what can you do"
    ],

    "college_location": [
        "where",
        "location",
        "located",
        "address",
        "place",
        "find"
    ],

    "courses": [
        "course",
        "courses",
        "branch",
        "branches",
        "program",
        "programs",
        "study",
        "engineering"
    ],

    "timings": [
        "time",
        "timing",
        "timings",
        "hours",
        "start",
        "end",
        "open",
        "close"
    ],

    "admission": [
        "admission",
        "admissions",
        "join",
        "apply",
        "cet",
        "management",
        "enroll"
    ],

    "departments": [
        "department",
        "departments",
        "section",
        "sections"
    ],

    "facilities": [
        "facility",
        "facilities",
        "hostel",
        "library",
        "lab",
        "labs",
        "laboratory",
        "sports",
        "computer",
        "infrastructure",
        "workshop",
        "internet"
    ],

    "contact": [
        "contact",
        "phone",
        "number",
        "telephone",
        "email",
        "call"
    ],

    "college": [
        "college",
        "rymec"
    ]
}


# =========================================
# TYPO / FUZZY MATCH KEYWORDS
# =========================================

fuzzy_keywords = {

    "greeting": [
        "hello",
        "hi",
        "hey",
        "hii",
        "hiii",
        "helo",
        "helloo",
        "heyy",
        "hiiiii"
    ],

    "thanks": [
        "thanks",
        "thank",
        "thankyou",
        "thnks",
        "thx",
        "thanksss"
    ],

    "goodbye": [
        "bye",
        "byee",
        "goodbye",
        "goodby",
        "seeyou"
    ],

    "help": [
        "help",
        "helpp",
        "hepl",
        "halp",
        "assist"
    ],

    "college_location": [
        "location",
        "located",
        "address",
        "adress",
        "loction",
        "where"
    ],

    "courses": [
        "course",
        "courses",
        "coursee",
        "cours",
        "cousres",
        "corses",
        "branch",
        "branches",
        "program",
        "study"
    ],

    "timings": [
        "time",
        "timing",
        "timings",
        "tim",
        "hours",
        "opening",
        "closing"
    ],

    "admission": [
        "admission",
        "admisn",
        "admisson",
        "admissionn",
        "admit",
        "apply",
        "join"
    ],

    "departments": [
        "department",
        "departments",
        "deparment",
        "departmnt",
        "dept"
    ],

    "facilities": [
        "facility",
        "facilities",
        "facilty",
        "facilites",
        "hostel",
        "library",
        "libary",
        "librery",
        "lab",
        "labs",
        "sports",
        "computer"
    ],

    "contact": [
        "contact",
        "contct",
        "conatct",
        "phone",
        "phne",
        "number",
        "email",
        "emal"
    ],

    "college": [
        "college",
        "collage",
        "colleg",
        "rymec"
    ]
}


# =========================================
# KANNADA SCRIPT DETECTION
# =========================================

def is_kannada(message):

    return bool(
        re.search(r"[\u0C80-\u0CFF]", message)
    )


# =========================================
# KANNADA INTENT RECOGNITION
# =========================================

def recognize_kannada_intent(message):

    message = message.strip().lower()

    for intent, phrases in kannada_patterns.items():

        for phrase in phrases:

            if phrase.lower() in message:
                return intent

    return None


# =========================================
# ENGLISH INTENT RECOGNITION
# =========================================

def recognize_intent(message):

    message = message.lower().strip()

    for intent, intent_patterns in patterns.items():

        for pattern in intent_patterns:

            if re.search(pattern, message):

                return intent

    return "default"


# =========================================
# KEYWORD INTENT SCORING
# =========================================

def recognize_intent_by_keywords(message):

    message = message.lower().strip()

    scores = {}

    for intent, keywords in english_keywords.items():

        score = 0

        for keyword in keywords:

            if keyword in message:

                if " " in keyword:
                    score += 3
                else:
                    score += 1

        if score > 0:

            scores[intent] = score

    if not scores:

        return "default"

    best_intent = max(
        scores,
        key=scores.get
    )

    print("Keyword scores:", scores)

    return best_intent


# =========================================
# FUZZY TYPO RECOGNITION
# =========================================

def similarity(word1, word2):

    return SequenceMatcher(
        None,
        word1,
        word2
    ).ratio()


def recognize_typo_intent(message):

    words = re.findall(
        r"[a-zA-Z]+",
        message.lower()
    )

    best_intent = "default"
    best_score = 0

    for word in words:

        # Ignore very short words
        if len(word) < 2:
            continue

        for intent, keywords in fuzzy_keywords.items():

            for keyword in keywords:

                score = similarity(
                    word,
                    keyword
                )

                if score > best_score:

                    best_score = score
                    best_intent = intent

    print(
        "Fuzzy match:",
        best_intent,
        "Score:",
        round(best_score, 2)
    )

    # Require a reasonable similarity
    if best_score >= 0.72:

        return best_intent

    return "default"


# =========================================
# SMART ENGLISH INTENT RECOGNITION
# =========================================

def smart_english_intent(message):

    # 1. Exact pattern recognition
    intent = recognize_intent(message)

    if intent != "default":

        return intent

    # 2. Keyword scoring
    intent = recognize_intent_by_keywords(message)

    if intent != "default":

        return intent

    # 3. Typo / fuzzy recognition
    intent = recognize_typo_intent(message)

    return intent


# =========================================
# TRANSLATE KANNADA TO ENGLISH
# =========================================

def translate_to_english(message):

    try:

        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(message)

        print(
            "Translated to English:",
            translated
        )

        return translated

    except Exception as error:

        print(
            "Translation error:",
            error
        )

        return None


# =========================================
# GET RESPONSE FROM JSON
# =========================================

def generate_response(language, intent):

    if language not in responses:

        language = "en"

    if intent not in responses[language]:

        intent = "default"

    response_list = responses[language][intent]

    previous_response = session.get(
        "previous_response"
    )

    available_responses = [
        response
        for response in response_list
        if response != previous_response
    ]

    if not available_responses:

        available_responses = response_list

    response = random.choice(
        available_responses
    )

    session["previous_response"] = response

    return response


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================
# CHAT API
# =========================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get(
        "message",
        ""
    ).strip()


    if not user_message:

        return jsonify({

            "response":
            "Please enter a message.",

            "intent":
            "default",

            "language":
            "en"
        })


    # =====================================
    # AUTOMATIC LANGUAGE DETECTION
    # =====================================

    if is_kannada(user_message):

        language = "kn"

    else:

        language = "en"


    print("\n================================")
    print(
        "User message:",
        user_message
    )

    print(
        "Detected language:",
        language
    )


    # =====================================
    # KANNADA PROCESSING
    # =====================================

    if language == "kn":

        # First try direct Kannada recognition
        intent = recognize_kannada_intent(
            user_message
        )

        # If Kannada recognition fails,
        # translate it to English
        if intent is None:

            english_message = translate_to_english(
                user_message
            )

            if english_message:

                intent = smart_english_intent(
                    english_message
                )

            else:

                intent = "default"


    # =====================================
    # ENGLISH PROCESSING
    # =====================================

    else:

        intent = smart_english_intent(
            user_message
        )


    # =====================================
    # CONVERSATION CONTEXT
    # =====================================

    follow_up_phrases_en = [

        "tell me more",
        "more information",
        "give me more",
        "more details",
        "what about it",
        "and what about it",
        "tell me more about it",
        "can you explain more"
    ]


    follow_up_phrases_kn = [

        "ಇನ್ನಷ್ಟು ಹೇಳಿ",
        "ಇನ್ನಷ್ಟು ಮಾಹಿತಿ",
        "ಹೆಚ್ಚಿನ ಮಾಹಿತಿ",
        "ಇನ್ನಷ್ಟು ವಿವರ",
        "ಇದರ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ಹೇಳಿ",
        "ಇನ್ನಷ್ಟು ತಿಳಿಸಿ",
        "ಮತ್ತಷ್ಟು ಮಾಹಿತಿ ನೀಡಿ"
    ]


    normalized_message = (
        user_message.lower().strip()
    )


    if language == "en":

        is_follow_up = any(

            phrase in normalized_message

            for phrase in follow_up_phrases_en
        )

    else:

        is_follow_up = any(

            phrase in user_message

            for phrase in follow_up_phrases_kn
        )


    if is_follow_up:

        previous_intent = session.get(
            "previous_intent"
        )

        if previous_intent:

            intent = previous_intent


    # =====================================
    # SAVE CURRENT INTENT
    # =====================================

    if intent != "default":

        session["previous_intent"] = intent


    print(
        "Detected intent:",
        intent
    )


    # =====================================
    # GET RESPONSE
    # =====================================

    response = generate_response(
        language,
        intent
    )


    print(
        "Response:",
        response
    )

    print("================================")


    return jsonify({

        "response":
        response,

        "intent":
        intent,

        "language":
        language
    })


# =========================================
# START APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(debug=True)