markdown# ☕ CafeEye AI — The Restaurant That Sees, Thinks & Speaks

> Real-time multimodal AI restaurant intelligence powered by Gemini Live API and Google Cloud

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.5-red)
![YOLO](https://img.shields.io/badge/YOLO-v11-green)

---

## 🎯 What is CafeEye AI?

CafeEye AI is a real-time multimodal AI system that gives 
restaurants a brain. It uses a live camera to detect people 
at tables, tracks occupancy and timing, listens to staff 
questions by voice, and responds with natural spoken answers 
— all powered by Google's Gemini Live API.

**Built for the Gemini Live Agent Challenge Hackathon**

---

## ✨ Features

| Feature | Description |
|---|---|
| 👁️ Live Detection | YOLO v11 detects people at tables in real time |
| ⏱️ Time Tracking | Tracks how long each table has been occupied |
| 🎤 Voice Questions | Staff ask questions — AI answers by voice |
| 🗣️ Spoken Responses | Gemini Live API responds with natural voice |
| 🍽️ Food Ordering | AI recommends dishes and confirms orders by voice |
| 📊 Live Dashboard | Real-time web dashboard with analytics |
| 🚨 Smart Alerts | Alerts when tables need attention (30+ mins) |
| 📈 Peak Hours | Tracks and visualizes busiest hours |

---

## 🏗️ Architecture
```
Camera + Mic → YOLO + SoundDevice → Gemini Live API → Voice + Dashboard
```

**Layers:**
- **Input**: Camera (OpenCV), Microphone (SoundDevice)
- **Processing**: YOLO v11 (people detection), TableTracker (occupancy)
- **AI Brain**: Gemini 2.5 Flash Native Audio (Google GenAI SDK)
- **Output**: Voice responses, Streamlit dashboard, Order log
- **Deployment**: Google Cloud Run + Streamlit Cloud

---

## 🛠️ Tech Stack

- **AI**: Gemini 2.5 Flash Native Audio, Gemini Live API
- **Vision**: YOLO v11 (Ultralytics), OpenCV
- **Audio**: SoundDevice, NumPy
- **Frontend**: Streamlit
- **Cloud**: Google Cloud Run, Google Cloud Build
- **Language**: Python 3.12, asyncio, threading

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Webcam
- Gemini API key ([get free key](https://aistudio.google.com/apikey))

### Installation
```bash
# Clone the repo
git clone https://github.com/anshuu08/cafeeye-ai.git
cd cafeeye-ai

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Setup Environment

Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Run the App
```bash
streamlit run dashboard.py
```

Open **http://localhost:8501** in your browser.

---

## 📱 How to Use

### Dashboard
1. Click **▶ Start Camera** — live feed begins
2. YOLO detects people at tables automatically
3. Table status updates in real time

### Ask AI (Voice)
1. Click **🎤 Ask AI** in navigation
2. Click **Click & Speak** button
3. Ask naturally: *"Which table has been waiting longest?"*
4. Hear the AI respond by voice

### Place an Order
1. Click **🛎️ Place Order** in navigation
2. Choose Vegetarian or Non-Vegetarian
3. Hear AI recommendations by voice
4. Type your order or click a recommendation
5. Hear AI confirm: *"Thank you! Your order is placed!"*

---

## ☁️ Google Cloud Deployment

### Automated Deployment
```bash
# Make script executable
chmod +x gcp_deploy.sh

# Deploy to Google Cloud Run
./gcp_deploy.sh
```

### Manual Deployment
```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable services
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy
gcloud run deploy cafeeye-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2
```

---

## 📁 Project Structure
```
cafeeye-ai/
├── dashboard.py        # Main Streamlit dashboard
├── live_agent.py       # Gemini Live API voice agent
├── detector.py         # YOLO detection + table tracking
├── menu.py             # Restaurant menu data
├── gcp_deploy.sh       # Automated GCP deployment
├── Dockerfile          # Google Cloud Run container
├── requirements.txt    # Python dependencies
├── packages.txt        # System dependencies
└── .env                # API keys (not in repo)
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |

---

## 🎥 Demo

Watch the full demo: [YouTube Link]

---

## 👨‍💻 Author

Built with ❤️ for the **Gemini Live Agent Challenge Hackathon**

---

## 📄 License

MIT License — feel free to use and modify!

Create the file:
bashNew-Item README.md -type file
Paste the content, save, then push:
bashgit add README.md
git commit -m "Add README"
git push
