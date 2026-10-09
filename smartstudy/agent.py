from typing import AsyncGenerator
from google.adk.agents import Agent, BaseAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools.tool_context import ToolContext
from google.genai import types

MODEL = 'gemini-3.7-flash'
MODEL_LITE = 'gemini-flash-lite-latest'  # Used across parallel analysts to avoid free-tier 5 RPM limit

# 1. Coordinator ---------------------------------------------------------
coordinator_agent = Agent(
    name='coordinator_agent',
    model=MODEL,
    description='Receives the student request and extracts the requirements.',
    instruction='''You are the Coordinator of SmartStudy. Read the student's message and extract:
- Subject
- Exam date / days remaining
- Topics (list)
- Current level
- Available study time per day
If anything is missing, assume a sensible default and mark it (assumed).
Output ONLY a clean student profile with those five fields.''',
    output_key='student_profile',
)

# 2. Planning agent ------------------------------------------------------
planning_agent = Agent(
    name='planning_agent',
    model=MODEL,
    description='Prepares requirements and briefs the three parallel analysts.',
    instruction='''Student profile:
{student_profile}
Prepare a short planning brief: total days, hours per day, total study hours, and one clear task
each for the Topic Agent (priority, difficulty, focus), the Practice Agent (problem counts and
practice type) and the Schedule Agent (day-wise timetable with revision). Keep it under 150 words.''',
    output_key='planning_brief',
)

# 3-5. Parallel analysts -------------------------------------------------
topic_agent = Agent(
    name='topic_agent',
    model=MODEL,
    description='Analyzes each topic.',
    instruction='''Profile: {student_profile}
Brief: {planning_brief}
For EACH topic give: Priority (High / Medium / Low), Difficulty, and Recommended study focus.
Adjust for the student's current level. Output a compact table.''',
    output_key='topic_analysis',
)

practice_agent = Agent(
    name='practice_agent',
    model=MODEL_LITE,
    description='Decides practice volume and type per topic.',
    instruction='''Profile: {student_profile}
Brief: {planning_brief}
For EACH topic decide how many problems to solve (for example Arrays 5, Linked Lists 5, Trees 8,
Graphs 8, Dynamic Programming 10, adjusted to the level) and the practice type:
Concept Questions, Coding Problems, Mixed Practice, or Mock Test. Output a compact table.''',
    output_key='practice_plan',
)

schedule_agent = Agent(
    name='schedule_agent',
    model=MODEL_LITE,
    description='Turns available time into a realistic day-wise schedule.',
    instruction='''Profile: {student_profile}
Brief: {planning_brief}
Produce a day-wise schedule for every day until the exam. Never exceed the daily study hours.
Include revision and practice, not only new topics. Keep the last day light and focused on
final preparation / a mock test. Output Day 1 ... Day N with hours per activity.''',
    output_key='schedule_plan',
)

parallel_analysis = ParallelAgent(
    name='parallel_analysis',
    description='Runs the Topic, Practice and Schedule agents independently in parallel.',
    sub_agents=[topic_agent, practice_agent, schedule_agent],
)

planning_workflow = SequentialAgent(
    name='planning_workflow',
    description='Planning agent first, then the three parallel analysts.',
    sub_agents=[planning_agent, parallel_analysis],
)

# 6. Study Plan Writer + 7. Review Agent (loop) ---------------------------
writer_agent = Agent(
    name='study_plan_writer',
    model=MODEL,
    description='Combines the analyses into one complete study plan.',
    instruction='''Combine the following into ONE complete personalized study plan.
Topic analysis:
{topic_analysis}
Practice plan:
{practice_plan}
Schedule:
{schedule_plan}
Reviewer feedback (empty on the first pass):
{review_feedback?}
If the feedback says NEEDS IMPROVEMENT, fix every point it lists. The plan MUST include: a
day-wise schedule for all days, topics to study each day, practice to complete, revision slots,
and mock test / final preparation. Stay within the daily study hours. Output only the plan.''',
    output_key='current_plan',
)

def exit_loop(tool_context: ToolContext) -> dict:
    '''Call this ONLY when the study plan passes all five review checks.'''
    tool_context.actions.escalate = True
    return {'status': 'approved'}

review_agent = Agent(
    name='review_agent',
    model=MODEL,
    description='Checks the draft plan and approves it or asks for improvements.',
    instruction='''You review a draft study plan.
Student profile:
{student_profile}
Draft plan:
{current_plan}
Check:
1. Are all topics covered?
2. Does the plan fit within the available study time every day?
3. Is sufficient practice included?
4. Is revision included?
5. Is the final day suitable for exam preparation?
If ALL five pass: call the exit_loop tool, then reply with APPROVED and one line of reasoning.
If ANY fail: reply with NEEDS IMPROVEMENT followed by a numbered list of specific fixes.
Do not rewrite the plan yourself.''',
    tools=[exit_loop],
    output_key='review_feedback',
)

review_loop = LoopAgent(
    name='review_loop',
    description='Writer then Reviewer, at most 2 iterations.',
    sub_agents=[writer_agent, review_agent],
    max_iterations=2,
)

# Final presenter (no LLM call) ------------------------------------------
class FinalPlanPresenter(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        plan = ctx.session.state.get('current_plan', 'No plan was generated.')
        text = '## FINAL 10-DAY STUDY PLAN' + chr(10) * 2 + plan
        yield Event(
            author=self.name,
            content=types.Content(role='model', parts=[types.Part(text=text)]),
        )

# Root: Sequential workflow ----------------------------------------------
root_agent = SequentialAgent(
    name='smartstudy_pipeline',
    description='SmartStudy: coordinator, planning (parallel analysis), reviewed writing loop, final plan.',
    sub_agents=[
        coordinator_agent,
        planning_workflow,
        review_loop,
        FinalPlanPresenter(name='final_plan_presenter', description='Prints the approved plan.'),
    ],
)
