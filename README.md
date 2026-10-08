# SmartLearn.AI

SmartLearn.AI is an adaptive, curriculum-aware learning platform designed for school students. It delivers personalized learning pathways, structured board syllabi, multi-modal topic study with verified resources, and a curriculum-aware AI Tutor with text, image doubt-solving, and live voice conversation.

---

## 📋 System Prerequisites

Ensure you have the following installed on your host system:

- **Node.js**: v18.0.0 or higher (`node -v`)
- **Python**: v3.10 or higher (`python --version`)
- **PostgreSQL**: v14 or higher running locally on port `5432` with a database named `smartlearn`
- **Modern Web Browser**: Google Chrome, Brave, or Microsoft Edge (recommended for Web Speech API speech-to-text recognition)

---

## ⚙️ Environment Setup

### 1. Backend Configuration

Navigate to the `backend/` directory and configure the environment:

```bash
cd backend
cp .env.example .env
```

Ensure your `backend/.env` file contains valid database and application settings:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smartlearn
SECRET_KEY=your_generated_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://localhost:5173

# Optional: Required for real AI-generated tutoring answers
# Leave blank to use graceful fallback mode (clear in-app configuration warnings)
GEMINI_API_KEY=
```

Install backend dependencies:
```bash
pip install -r requirements.txt
```

### 2. Frontend Configuration

Navigate to the `frontend/` directory and install dependencies:

```bash
cd frontend
npm install
```

---

## 🗄️ Database Migrations & Seed Data

SmartLearn.AI includes idempotent seeding scripts for official board syllabi and a verified demo student.

Run the following commands from the `backend/` directory:

```bash
cd backend

# Run database migrations
alembic upgrade head

# Seed official CISCE ISC Class 11 History curriculum (2027 Examination Year)
python -m app.db.seed_curriculum

# Seed verified demo student with complete onboarding profile
python -m app.db.seed_demo_user
```

---

## 🚀 Running the Product Locally

### Terminal 1 — Start Backend Server:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

### Terminal 2 — Start Frontend Server:
```bash
cd frontend
npm run dev
```
- **Frontend Web Application**: `http://localhost:5173`

---

## 🎯 Demo Student Journey & Interactive Verification

Follow these steps to experience the complete student flow:

1. **Open the Application**:
   Navigate to [http://localhost:5173](http://localhost:5173) in your browser (redirects to `/login`).

2. **Login with Demo Credentials**:
   - **Email**: `demo.student@smartlearn.ai`
   - **Password**: `Password@123`
   - Click **Sign In**.

3. **Explore the Dashboard**:
   - Verify personalized greeting: *"Welcome back, Demo Student!"*.
   - View enrolled subjects (*ISC Class 11 History*), weekly target tracking, and recommended study sessions.

4. **Navigate to Subject Syllabus**:
   - Click on the **History** card or open `/learning/subjects/43`.
   - Inspect chapters and topics (Section A: Indian History, Section B: World History).

5. **Study a Topic**:
   - Click on **Chapter 1, Topic 1**: *"Development of Transport & Communication: Railways, Roads, and Telegraphs"* (`/learning/topics/44`).
   - Switch between **Video Lesson**, **Study Notes**, and **Reading Material**.
   - Note the embedded verified YouTube lesson with an external fallback link ("Watch directly on YouTube") preserving copyright and CISCE attribution.

6. **Engage the AI Tutor (Text & Image)**:
   - Click the floating **Ask AI Tutor 🤖** button in the bottom right corner.
   - Click any starter prompt (e.g., *"Explain this concept in simple terms 💡"*) or attach an image diagram for doubt solving.
   - If `GEMINI_API_KEY` is configured, real-time curriculum-grounded explanations are returned. If missing, a clear, friendly configuration banner informs the user without crashing.

7. **Test Live Voice Tutor**:
   - In the tutor drawer, switch to the **Live Voice** tab.
   - Click **Start Voice Tutoring**.
   - Grant microphone permissions when prompted by your browser.
   - Speak naturally to the tutor: observe the real-time audio visualizer frequency orb and live interim/final transcriptions.
   - Test **Mute/Unmute**, **Stop Voice**, and **End Call**.

---

## 🔑 AI Provider Configuration (Google Gemini)

To enable live AI generation for text and voice tutoring:

1. **Obtain an API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/).
   - Click **Get API key** and generate a new key on the free tier.
2. **Configure the Key**:
   - Open your local `backend/.env` file.
   - Set `GEMINI_API_KEY=your_actual_gemini_api_key_here`.
   - **Never commit `.env` or your API key to Git.** (`.env` is strictly in `.gitignore`).
3. **Restart the Backend**:
   - Restart Uvicorn to load the new environment variable.
4. **Behavior**:
   - With key configured: The tutor uses `gemini-1.5-flash` with curriculum grounding (board, grade, subject, chapter, topic, learning style).
   - Without key: Returns HTTP 503 with user-facing guidance in the drawer.

---

## 🎙️ Voice Architecture & Technical Assessment

SmartLearn.AI implements a dual-layer voice tutoring architecture:

| Capability | Current Status | Underlying Technology | Notes |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text (STT)** | Working | Web Speech API (`webkitSpeechRecognition`) | Zero-cost, client-side, browser-native. Requires Chromium/Brave/Edge/Safari. |
| **Audio Visualization** | Working | Web Audio API (`AudioContext` + `AnalyserNode`) | Real-time 60 FPS canvas spectrum orb showing mic activity. |
| **Session Handshake** | Working | WebSocket (`/ws/tutor/voice`) | JWT token authentication with reconnect resilience and keepalive. |
| **Text-to-Speech (TTS)** | Working | Web Speech API (`SpeechSynthesis`) | Browser-native vocal response with support for interruption/barge-in (`speechSynthesis.cancel()`). |
| **Curriculum Grounding** | Working | FastAPI Tutor Service | Injects CISCE syllabus context, chapter topics, and student learning style into prompt. |
| **Streaming Raw Audio** | Planned | WebRTC / Gemini 2.0 Live WebSocket | True full-duplex PCM audio streaming requires server-side STT/TTS models or Gemini Live protocol. |

### Known Limitations:
- **Firefox Speech Recognition**: Firefox does not support the Web Speech API recognition interface by default without experimental flags. Use Chromium-based browsers or Safari for voice input.
- **Audio Interruption**: Voice cancellation stops local speech playback instantly when the student speaks or clicks "Stop", but does not abort in-flight backend LLM text completion.

---

## 🧪 Automated Testing

SmartLearn.AI maintains strict test suites for both frontend and backend:

```bash
# Run Backend Pytest Suite (41 tests)
cd backend
python -m pytest -v

# Run Frontend Vitest Suite (111 tests)
cd frontend
npm test

# Run TypeScript Typecheck & Production Build
cd frontend
npm run build
```
