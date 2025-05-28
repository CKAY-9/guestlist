from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from better_profanity import profanity
import os
import json

messages_file_path = "./messages.json"
messages = []

if not os.path.exists(messages_file_path):
    with open(messages_file_path, "w") as file:
        file.write("[]")
else:
    with open(messages_file_path, "r") as file:
        try:
            messages = json.loads(file.read())
        except:
            print("Failed to load messages file")

app = Flask(__name__)
CORS(app=app)
limiter = Limiter(get_remote_address, app=app)

@app.post("/message")
@limiter.limit("3/hour")
def new_message():
    if not request.is_json:
        return "Invalid message", 400
    
    data: dict = request.json
    if not data.get("message") or len(data.get("message")) < 5:
        return "Invalid message", 400
    
    message = profanity.censor(data.get("message"))
    name = profanity.censor(data.get("name") or "")
    offset = data.get("timezone")

    messages.append({"name": name, "message": message, "offset": offset, "id": len(messages) + 1})
    with open(messages_file_path, "w") as file:
        file.write(json.dumps(messages))

    return "Created message", 200

@app.get("/message")
def get_messages():
    return messages

@app.get("/")
def home_page():
    return """
        <head>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">
        </head>
        <body 
            style="background: rgb(10, 10, 18); margin: 0; padding: 0;"
        >
            <div style="color: white; display: grid; place-content: center; width: 100vw; height: 100vh">
                <h1 style="font-family: 'Inter', sans-serif;">
                    Guest List Message API. <a style="color: white" href="https://github.com/CKAY-9/guestlist">GitHub</a>
                </h1>
            </div>
        </body>
    """, 200