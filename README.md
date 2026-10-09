# Beyond Chatbots: Building AI Agents with Google ADK

This repository contains the complete implementation of the certification tasks for the **Google Agent Development Kit (ADK) Workshop**, showcasing single-agent tool integration and complex multi-agent orchestration architectures.

---

## 📋 Overview of Tasks

### Task 1: Personal AI Assistant (`personal_assistant`)
A general-purpose assistant equipped with three integrated tools:
1. **Google Search (`GoogleSearchTool`)**: Built-in ADK search tool configured with `bypass_multi_tools_limit=True` allowing coexistence with custom tools.
2. **Calculator (`calculator`)**: Custom, secure mathematical evaluator built using Python's `ast` (Abstract Syntax Trees) without `eval`. Accurately handles arithmetic, percentages, GST calculations, and compound interest.
3. **Text Analyzer (`text_analyzer`)**: Custom Python tool computing exact character, word, and sentence counts.

### Task 2: SmartStudy Multi-Agent Study Planner (`smartstudy`)
A multi-agent personalized study planner combining **Sequential**, **Parallel**, and **Loop** workflows coordinated via ADK session state:

```text
smartstudy_pipeline (SequentialAgent)
  ├── 1. coordinator_agent (Agent)               -> saves 'student_profile'
  ├── 2. planning_workflow (SequentialAgent)
  │        ├── a. planning_agent (Agent)         -> saves 'planning_brief'
  │        └── b. parallel_analysis (ParallelAgent)
  │                 ├── topic_agent (Agent)      -> saves 'topic_analysis'
  │                 ├── practice_agent (Agent)   -> saves 'practice_plan'
  │                 └── schedule_agent (Agent)   -> saves 'schedule_plan'
  ├── 3. review_loop (LoopAgent, max_iterations=2)
  │        ├── a. study_plan_writer (Agent)      -> saves 'current_plan'
  │        └── b. review_agent (Agent)           -> evaluates & calls exit_loop tool
  └── 4. final_plan_presenter (BaseAgent)        -> formats & emits final 10-day plan
```

---

## 🗂️ Project Structure

```text
adk_workshop/
├── .gitignore                    # Ignores .venv, .env, __pycache__, .adk, submission
├── README.md                     # Root project documentation
├── personal_assistant/           # Task 1 Implementation
│   ├── __init__.py               # Exports agent
│   ├── agent.py                  # root_agent definition with 3 tools
│   ├── .env.example              # Safe template for submission
│   └── README.md
└── smartstudy/                   # Task 2 Implementation
    ├── __init__.py               # Exports agent
    ├── agent.py                  # root_agent definition with 7-agent pipeline
    ├── .env.example              # Safe template for submission
    └── README.md
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Environment Setup
Create and activate a virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip & install ADK
pip install --upgrade pip
pip install google-adk python-dotenv
```

### 3. Configure API Keys
Copy `.env.example` to `.env` in both agent directories:

```powershell
cp personal_assistant/.env.example personal_assistant/.env
cp smartstudy/.env.example smartstudy/.env
```

Add your Gemini API key inside `personal_assistant/.env` and `smartstudy/.env`:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

> **Note:** `.env` files are ignored by git to prevent secret leakage. Only `.env.example` with placeholder values is committed.

---

## 🖥️ Running Locally

Launch the ADK Web UI from the root `adk_workshop` directory:

```powershell
adk web --no-reload
```

Open **`http://localhost:8000`** in your browser.

---

## 🧪 Test Prompts

### Task 1: Personal Assistant
Select `personal_assistant` from the dropdown:
- **Calculator**: `Calculate 18% GST on ₹25,000.` *(Result: 4,500)*
- **Compound Interest**: `Calculate the compound interest on ₹10,000 at 8% for 3 years, compounded annually.` *(Result: 2,597.12)*
- **Text Analyzer**: `Analyze this paragraph and tell me its word and sentence count: Google ADK helps developers build AI agents. It supports tools and workflows!` *(Result: 77 characters, 12 words, 2 sentences)*
- **Google Search**: `Search for the latest developments in AI agents.`

### Task 2: SmartStudy Planner
Select `smartstudy` from the dropdown and submit:
```text
I have a Data Structures exam in 10 days.
My current level is Intermediate.
Topics:
Arrays
Linked Lists
Trees
Graphs
Dynamic Programming
I can study for 3 hours per day.
Create a preparation plan for me.
```

---

