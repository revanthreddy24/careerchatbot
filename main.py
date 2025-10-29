# --- Standard Library Imports ---
import os
import json
import uuid
import csv
import time
from datetime import datetime
from collections import Counter

# --- Third-Party Packages ---
from dotenv import load_dotenv
from openai import OpenAI
import requests
from pypdf import PdfReader
import gradio as gr
from transformers import pipeline

# --- Load Environment Variables ---
load_dotenv(override=True)


# --- Pushover functions ---
def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional info about the conversation"},
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {"question": {"type": "string", "description": "The question that couldn't be answered"}},
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
         {"type": "function", "function": record_unknown_question_json}]


# --- Session management ---
class SessionManager:
    def __init__(self, chat_dir="chats"):
        self.chat_dir = chat_dir
        os.makedirs(chat_dir, exist_ok=True)
        self.sessions = {}  # maps session_id to username

    def get_username(self, session_id):
        return self.sessions.get(session_id)

    def set_username(self, session_id, username):
        self.sessions[session_id] = username

    def get_history_path(self, username):
        return os.path.join(self.chat_dir, f"chat_history_{username}.json")

    def save_history(self, username, history):
        path = self.get_history_path(username)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_history(self, username):
        path = self.get_history_path(username)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

class UserProfileManager:
    def __init__(self, file_path="users.json"):
        self.file_path = file_path
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load_profiles(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_profiles(self, data):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update_user(self, name, email=None, new_interest=None, message=None):
        users = self.load_profiles()
        user = users.get(name, {
            "email": email or "unknown",
            "joined": datetime.now().isoformat(),
            "interests": [],
            "sentiments": []
        })

        # update timestamp
        user["last_chat"] = datetime.now().isoformat()

        # analyze sentiment
        if message:
            sentiment = self.sentiment_analyzer(message[:500])[0]["label"]
            user["sentiments"].append(sentiment)

        # add interest if provided
        if new_interest and new_interest not in user["interests"]:
            user["interests"].append(new_interest)

        users[name] = user
        self.save_profiles(users)

    def get_user_summary(self, name):
        users = self.load_profiles()
        if name not in users:
            return None
        u = users[name]
        avg_mood = "NEUTRAL"
        if u["sentiments"]:
            mood_score = sum(1 if s == "POSITIVE" else -1 if s == "NEGATIVE" else 0 for s in u["sentiments"])
            avg_mood = "POSITIVE" if mood_score > 0 else "NEGATIVE" if mood_score < 0 else "NEUTRAL"
        return f"{name} last chatted on {u['last_chat']}, main interests: {', '.join(u['interests']) or 'none'}, average mood: {avg_mood}"
import csv, time
from collections import Counter

class AnalyticsLogger:
    def __init__(self, log_file="logs/analytics.csv"):
        os.makedirs("logs", exist_ok=True)
        self.log_file = log_file
        if not os.path.exists(log_file):
            with open(log_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "session_id", "user_name", "message", "sentiment", "duration_sec"])

        self.start_times = {}  # track session start times

    def start_session(self, session_id):
        self.start_times[session_id] = time.time()

    def log_message(self, session_id, user_name, message, sentiment):
        duration = time.time() - self.start_times.get(session_id, time.time())
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), session_id, user_name, message, sentiment, int(duration)])

    def generate_summary(self):
        import pandas as pd
        df = pd.read_csv(self.log_file)
        summary = {}

        summary["total_sessions"] = df["session_id"].nunique()
        summary["total_messages"] = len(df)
        summary["most_active_users"] = df["user_name"].value_counts().head(5).to_dict()

        # Common words
        all_words = " ".join(df["message"].astype(str)).lower().split()
        common_words = Counter([w for w in all_words if len(w) > 3]).most_common(10)
        summary["common_words"] = common_words

        avg_session_time = df.groupby("session_id")["duration_sec"].max().mean()
        summary["avg_session_length"] = round(avg_session_time, 2)

        return summary

# --- Main Me class ---
class Me:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Revanth"
        reader = PdfReader("me/profile.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()
        self.sessions = SessionManager()
        self.user_profiles = UserProfileManager()
        self.analytics = AnalyticsLogger()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results

    def system_prompt(self, user_name=None):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
If you don't know the answer, use the record_unknown_question tool. \
If the user shares an email, record it using record_user_details. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        if user_name:
            system_prompt += f"The user you are chatting with is named {user_name}.\n"
        system_prompt += f"Always stay professional and engaging as {self.name}."
        return system_prompt

    def chat(self, message, history, request: gr.Request):
        # Each Gradio session gets its own unique ID stored in cookies
        if not hasattr(request, "session_hash") or not request.session_hash:
            session_id = str(uuid.uuid4())
        else:
            session_id = request.session_hash  # Unique per tab/session

        #  Initialize analytics tracking
        self.analytics.start_session(session_id)

        user_name = self.sessions.get_username(session_id)

        # Step 1: Ask user's name if not known yet
        if not user_name:
            if not history:  # first message ever
                self.sessions.set_username(session_id, None)
                return "Hi there! 👋 What's your name?"
            else:
                # Take user's name from their reply
                user_name = message.strip().split(" ")[-1].capitalize()
                self.sessions.set_username(session_id, user_name)
                push(f"New user joined: {user_name}")

                # Log first interaction
                self.analytics.log_message(
                    session_id=session_id,
                    user_name=user_name,
                    message=message,
                    sentiment=self.user_profiles.sentiment_analyzer(message[:500])[0]["label"]
                )

                return f"Nice to meet you, {user_name}! How can I help you today?"

        # Step 2: Load or create chat history for that user
        user_history = self.sessions.load_history(user_name)

        # Step 3: Prepare messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt(user_name)}]
        for h in user_history:
            messages.append({"role": "user", "content": h[0]})
            messages.append({"role": "assistant", "content": h[1]})
        messages.append({"role": "user", "content": message})

        # Step 4: Detect possible user interests (simple keyword tagging)
        detected_interest = None
        lower_msg = message.lower()
        if "ai" in lower_msg or "agent" in lower_msg:
            detected_interest = "AI/Agents"
        elif "resume" in lower_msg:
            detected_interest = "Resume"
        elif "career" in lower_msg:
            detected_interest = "Career"
        elif "job" in lower_msg:
            detected_interest = "Job Opportunities"
        elif "learning" in lower_msg or "study" in lower_msg:
            detected_interest = "Learning"

        # Step 5: OpenAI API call
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini", messages=messages, tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message_obj)
                messages.extend(results)
            else:
                done = True

        reply = response.choices[0].message.content

        # Step 6: Update user profile with sentiment and interests
        self.user_profiles.update_user(
            name=user_name,
            message=message,
            new_interest=detected_interest
        )
        print(f"✅ Profile updated for {user_name} (interest: {detected_interest})", flush=True)

        # Step 7: Log analytics for this message
        self.analytics.log_message(
            session_id=session_id,
            user_name=user_name,
            message=message,
            sentiment=self.user_profiles.sentiment_analyzer(message[:500])[0]["label"]
        )
        print(f"📊 Logged message for analytics: {user_name}", flush=True)

        # Step 8: Save chat history
        user_history.append((message, reply))
        self.sessions.save_history(user_name, user_history)

        return reply



# --- Gradio interface ---
if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(
        fn=me.chat,
        type="messages",
        title="Chat with Revanth",
        description="A personal AI assistant representing Revanth.",
        theme="soft"
    ).launch()

