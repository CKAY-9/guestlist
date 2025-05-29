from flask import Flask, request, render_template
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
@limiter.limit("3/day")
def new_message():
    if not request.is_json:
        return "Invalid message", 400
    
    data: dict = request.json
    if not data.get("message") or len(data.get("message")) < 5 or len(data.get("message")) >= 255 or len(data.get("name")) >= 50:
        return "Invalid message", 400
    
    message = profanity.censor(data.get("message"))
    name = profanity.censor(data.get("name") or "")
    offset = data.get("timezone")

    messages.append({"name": name, "message": message, "offset": offset, "id": len(messages) + 1})
    with open(messages_file_path, "w") as file:
        file.write(json.dumps(messages))

    return "Created message", 200

@app.get("/message")
@limiter.limit("15/minute")
def get_messages():
    start = request.args.get("start", default=0, type=int)
    reversed_messages = messages[::-1]
    sliced_messages = reversed_messages[start:start + 25]
    return sliced_messages

@app.get("/message/<int:message_id>")
@limiter.limit("15/minute")
def get_message_from_id(message_id: int):
    for entry in messages:
        if entry["id"] == message_id:
            return entry
        
    return "Invalid ID", 404

@app.get("/")
def home_page():
    return render_template("index.html"), 200