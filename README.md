🤖 AI Personal Chat Assistant with Analytics Dashboard

A fully interactive AI-powered personal assistant built using OpenAI GPT-4o, Gradio, and Python.
The chatbot acts as a professional persona that can hold context-aware conversations, analyze user sentiment, record interests, and generate activity analytics — all in one system.

🚀 Project Overview

This project creates a personalized chat assistant capable of:

Representing an individual (e.g., Revanth) in natural, engaging conversations.

Tracking and analyzing user sentiment and engagement patterns.

Maintaining persistent user profiles, chat history, and analytics logs.

Sending real-time notifications through the Pushover API.

Providing an analytics dashboard to visualize usage patterns and emotional trends.

Deployed on Hugging Face Spaces with GitHub auto-integration for continuous updates.

🧠 Key Features
Category	Description
💬 AI Chat Engine	Powered by OpenAI GPT-4o (via OpenAI API) with Gradio interface.
🧾 Persistent Memory	Saves user sessions, chat history, and interests across visits.
❤️ Sentiment & Emotion Tracking	Uses Hugging Face Transformers to detect and log sentiment for every message.
📊 Analytics Dashboard	Tracks user activity, most common topics, and engagement duration.
🔔 Pushover Notifications	Sends real-time push alerts for new users or unknown queries.
☁️ Deployment Ready	Hosted on Hugging Face Spaces with automatic GitHub redeployment.
🏗️ Tech Stack

Python 3.10+

OpenAI GPT-4o API

Gradio – Chat UI and app framework

Transformers (Hugging Face) – Sentiment analysis

Pandas + Matplotlib – Data logging and analytics visualization

Pushover API – Notifications

Hugging Face Spaces + GitHub – Deployment and version control

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Add Environment Variables

Create a .env file in the root directory:

OPENAI_API_KEY=your_openai_api_key
PUSHOVER_TOKEN=your_pushover_app_token
PUSHOVER_USER=your_pushover_user_key

4️⃣ Run the App Locally
python app.py


Gradio will show a local and a shareable public link (if share=True).

📦 Folder Structure
AI-Chat-Assistant/
├── app.py                   # Main application file
├── requirements.txt         # Project dependencies
├── me/
│   ├── profile.pdf          # Your profile (used as context)
│   └── summary.txt          # Summary for system prompt
├── chats/                   # Stores user chat histories
├── logs/
│   └── analytics.csv        # Conversation analytics data
├── users.json               # User profiles and sentiment data
└── README.md                # Project documentation

📊 Analytics Example

The app automatically tracks:

Total sessions

Most active users

Common words/topics

Average session duration

Sentiment trends

Example analytics.csv:

timestamp,session_id,user_name,message,sentiment,duration_sec
2025-10-29T21:15:20,12ab-43de,Revanth,"I'm learning AI agents","POSITIVE",23

☁️ Deployment on Hugging Face Spaces

Push your code to GitHub.

Create a new Hugging Face Space → choose Gradio SDK.

Link it to your GitHub repo under Settings → Integrations → GitHub.

Add your environment variables in the Space Settings → Variables.

Hugging Face auto-deploys every time you push to GitHub.

Public URL example:

https://huggingface.co/spaces/revanth-ai-assistant

🧩 Future Enhancements

Add voice input and TTS response capability.

Integrate external storage (e.g., Google Drive or SQLite) for permanent logs.

Build interactive analytics dashboard tabs inside Gradio.

Multi-user identity support with secure authentication.

👨‍💻 Author

Revanth Kanubaddi
Bridgewater State University
📧 rkanubaddi@student.bridgew.edu
