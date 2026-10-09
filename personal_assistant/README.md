# Task 1: Personal AI Assistant

A general-purpose assistant built with Google ADK with three capabilities:
1. **Google Search**: Built-in `GoogleSearchTool` (with `bypass_multi_tools_limit=True`) for current events and factual search.
2. **Calculator**: Safe mathematical AST parser evaluating expressions, percentages, GST, and compound interest without `eval`.
3. **Text Analyzer**: Analyzes exact character, word, and sentence counts.

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
   *(On Windows if you encounter `_make_subprocess_transport NotImplementedError`, use `adk web --no-reload`)*
3. Select `personal_assistant` from the top-left dropdown in http://localhost:8000.
