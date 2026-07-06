# Spotter

**An AI gym coach that watches your form in real time, coaches you like a real trainer, and pauses before you get hurt.**

Real-time pose detection with proactive AI safety spotting — built with a multi-agent architecture (ADK), Google Gemini, and MCP.

**[Live App](https://spotter-pqqswzbavkfppesnuxvvuk.streamlit.app/)** · **[Demo Video](#)** ·

---

## The Problem

People training alone have no one watching their form. Bad reps go uncorrected, injuries build up silently, and most fitness apps just log your workout — they don't actually watch *how* you're doing it. In a real gym, a spotter catches you before you get hurt. Spotter brings that role to anyone with a camera.

## Why Agents

- **Real-time reasoning** — form evaluation needs live interpretation of spatial pose data, not a fixed script
- **Tool use** — wraps computer vision (MediaPipe) so raw movement feeds directly into an AI decision layer
- **Safety gates** — a system that flags danger needs the authority to pause and wait for a human, not just continue

## Architecture

```
+------------------+     +-------------------+     +---------------------+
|   CAMERA FRAME   | --> | Vision Tool Agent | --> | Safety Agent (HITL) |
| (Live via WebRTC)|     | (7 Skills, Det.)  |     | (Danger Thresholds) |
+------------------+     +-------------------+     +---------------------+
                                                              |
+------------------+     +-------------------+                v
|    MCP SERVER    | <-- |   Program Agent   |            [ PAUSED ]
| (Weekly Reports) |     |  (Deterministic)  |        (Await User OK)
+------------------+     +-------------------+                |
         ^                         ^                          v
         |                         |               +---------------------+
         +---- [ Database ] -------+ <------------ |  Coordinator Agent  |
               (Reps, Sets, Hist)                  |  (Sequential ADK)   |
                                                              |
                                                              v
                                                   +---------------------+
                                                   |   Coaching Agent    |
                                                   |  (Gemini Voice/Text)|
                                                   +---------------------+
```

*See `docs/architecture.png` for the full illustrated diagram.*

### Agents

| Agent | Type | Role |
|---|---|---|
| **Vision Tool Agent** | Deterministic | Wraps 7 exercise skills (Squats, Push-ups, Biceps Curls, Shoulder Press, Lunges, Plank, Jumping Jacks); extracts joint angles and form status from live pose landmarks |
| **Safety Agent (HITL)** | Guardrail | Checks every rep against danger thresholds; pauses the workflow and waits for human confirmation on critical form violations |
| **Coordinator Agent** | Orchestrator | Sequential ADK pipeline: `Vision → Safety → Coaching → Persistence` — nothing is coached or saved before it's confirmed safe |
| **Coaching Agent** | Generative (Gemini) | Real-time text and matching voice feedback, tied to the exact detected issue |
| **Program Agent** | Deterministic | Rule-based weekly summary — no LLM, chosen for reliability after hitting rate limits |
| **MCP Server** | Tool delivery | Pushes the weekly report to a local file, outside the main app loop |

## Core Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Multi-Agent System (ADK) | Vision, Safety, Coordinator, Coaching, Program agents |
| MCP Server | Weekly report delivery |
| Security | HITL safety gate; zero hardcoded API keys |
| Agent Skills | 7 modular, swappable exercise detectors |
| Deployability | Live on Streamlit Community Cloud |

## Tech Stack

- **Language:** Python
- **UI:** Streamlit
- **Video:** streamlit-webrtc
- **Pose Detection:** MediaPipe
- **CV:** OpenCV
- **Database:** SQLite
- **LLM:** Google Gemini (`google-generativeai`)
- **Voice:** gTTS
- **Agent Orchestration:** Google ADK patterns

## Getting Started

### Prerequisites
- Python 3.11+
- A [Gemini API key](https://aistudio.google.com)

### Installation

```bash
git clone https://github.com/PrakratiArya/Spotter.git
cd Spotter/MainApp
pip install -r requirements.txt
```

### Environment Setup

Set your Gemini API key as an environment variable:

```bash
# Windows
set GEMINI_API_KEY=your_key_here

# macOS/Linux
export GEMINI_API_KEY=your_key_here
```

### Run Locally

```bash
streamlit run main.py
```

Open `http://localhost:8501` in your browser, allow camera access, and click **Start Workout**.

## Project Structure

```
Spotter/
├── MainApp/
│   ├── main.py                      # Streamlit entry point
│   ├── agents/
│   │   ├── coordinator.py           # Sequential orchestration
│   │   ├── safety_agent.py          # HITL safety gate
│   │   ├── vision_tool_agent.py     # Deterministic vision wrapper
│   │   └── program_agent.py         # Rule-based weekly report
│   ├── skills/                      # 7 exercise detectors
│   │   ├── squat.py
│   │   ├── pushup.py
│   │   ├── biceps_curl.py
│   │   ├── shoulder_press.py
│   │   ├── lunges.py
│   │   ├── plank.py
│   │   └── jumping_jacks.py
│   ├── services/
│   │   ├── coaching/                # LLM + TTS voice pipeline
│   │   ├── vision/                  # Video processor
│   │   ├── tracking/                # Metrics + session state
│   │   └── persistence/             # SQLite storage
│   ├── mcp_server/
│   │   └── server.py                # Weekly report MCP tool
│   ├── packages.txt                 # System-level deps (Streamlit Cloud)
│   └── requirements.txt
├── LandingPage/                     # Static marketing page
└── README.md
```

## Deployment

Deployed on **Streamlit Community Cloud**:
- Repository: `PrakratiArya/Spotter`
- Main file path: `MainApp/main.py`
- Secrets: `GEMINI_API_KEY` set under app settings

## Evaluation

Manually verified across live test sessions:
- ✅ Clean rep → correct praise, matching text and voice
- ✅ Bad-form rep → specific correction matching the detected issue
- ✅ Dangerous angle crossed → Safety Agent pauses, waits for confirmation
- ✅ Weekly report generates correctly, zero external API dependency
- ✅ Full pipeline runs identically on Streamlit Cloud and locally

## Engineering Journey

- **State-clearing bug:** A rep's form-issue data was cleared before the Coaching Agent could read it — fixed by tracking the *worst* issue seen during the rep, not after.
- **LLM pivot:** Switched from Groq to Gemini mid-build for tighter course alignment.
- **Rate-limit resilience:** Hit Gemini free-tier limits on weekly reports — solved by making the Program Agent fully rule-based.
- **Cloud dependency fix:** Pose-detection model file failed to resolve on Streamlit Cloud — solved with an auto-download fallback at startup.

## Security

- No API keys or secrets committed to the repository
- All credentials read from environment variables / Streamlit Secrets
- `.gitignore` excludes `.env`, `*.db`, and local secrets files

## License

Educational project — built for the Kaggle AI Agents Intensive Vibe Coding Capstone.

## Author

**Prakrati Arya** — [GitHub](https://github.com/PrakratiArya)
