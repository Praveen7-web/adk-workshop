# Task 2: SmartStudy Multi-Agent Planner

A multi-agent personalized study preparation planner built with Google ADK combining Sequential, Parallel, and Loop workflows:

- **coordinator_agent** (`Agent`): Extracts student profile (subject, days remaining, topics, level, study hours).
- **planning_workflow** (`SequentialAgent`):
  - **planning_agent**: Prepares requirements brief.
  - **parallel_analysis** (`ParallelAgent`):
    - **topic_agent**: Analyzes topic priorities and difficulty.
    - **practice_agent**: Determines problem counts and practice types.
    - **schedule_agent**: Constructs day-wise timetable.
- **review_loop** (`LoopAgent`, max 2 iterations):
  - **study_plan_writer**: Synthesizes the analyses into a comprehensive study plan.
  - **review_agent**: Evaluates against 5 quality checks and calls `exit_loop` upon approval.
- **final_plan_presenter** (`BaseAgent`): Emits the final approved study plan.

## How to Run

1. Add your Gemini API key to `.env`:
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
   ```
2. From the project root (`adk_workshop`), run:
   ```bash
   adk web
   ```
3. Select `smartstudy` from the top-left dropdown in http://localhost:8000.
