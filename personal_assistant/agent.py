import ast
import math
import operator
import re
from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool

MODEL = 'gemini-3.7-flash'

# ---------- Tool 2: Calculator (safe, no eval) ----------
_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {'sqrt': math.sqrt, 'abs': abs, 'round': round, 'log': math.log, 'log10': math.log10}
_CONSTS = {'pi': math.pi, 'e': math.e}

def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError('exponent too large')
        return _BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCS and not node.keywords):
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError('unsupported expression')

def calculator(expression: str) -> dict:
    '''Evaluates a mathematical expression and returns the exact result.

    Args:
        expression: A plain math expression using numbers and + - * / // % ** ( ).
            Convert percentages first, e.g. 18% of 50000 becomes 50000 * 18 / 100.

    Returns:
        dict with status and result, or status and error_message.
    '''
    try:
        cleaned = re.sub(r'(?<=[0-9]),(?=[0-9]{3})', '', expression)  # 25,000 -> 25000
        for old, new in (('₹', ''), ('$', ''), ('×', '*'), ('÷', '/'), ('^', '**')):
            cleaned = cleaned.replace(old, new)
        value = _eval(ast.parse(cleaned.strip(), mode='eval'))
        if isinstance(value, float):
            value = int(value) if value.is_integer() else round(value, 6)
        return {'status': 'success', 'expression': expression, 'result': value}
    except ZeroDivisionError:
        return {'status': 'error', 'error_message': 'Division by zero.'}
    except Exception as exc:
        return {'status': 'error', 'error_message': f'Could not evaluate: {exc}'}

# ---------- Tool 3: Text Analyzer ----------
def text_analyzer(text: str) -> dict:
    '''Analyzes a piece of text and returns its character, word and sentence counts.

    Args:
        text: The exact text to analyze.

    Returns:
        dict with status, characters, words, sentences and a summary string.
    '''
    characters = len(text)
    words = len([w for w in text.split() if any(c.isalnum() for c in w)])
    sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
    return {
        'status': 'success',
        'characters': characters,
        'words': words,
        'sentences': sentences,
        'summary': f'Characters: {characters} | Words: {words} | Sentences: {sentences}',
    }

INSTRUCTION = '''You are a helpful general-purpose personal assistant with three tools.
- google_search: use for current events, news, or any external fact you are not sure about.
- calculator: ALWAYS use for arithmetic, percentages, GST, interest and similar maths. Never calculate in your head.
  First turn the request into ONE plain expression, e.g. 18% of 50000 -> 50000 * 18 / 100.
  Compound interest: P * (1 + r/100) ** n, and subtract P to get the interest.
- text_analyzer: use when the user wants character, word or sentence counts. Pass their text exactly as given.
If a request needs more than one tool (for example search AND calculate), call each tool you need and then
combine the results into one clear answer. If no tool is needed, answer directly.
Briefly mention which tool(s) you used.'''

root_agent = Agent(
    name='personal_assistant',
    model=MODEL,
    description='A general-purpose assistant that can search the web, calculate, and analyze text.',
    instruction=INSTRUCTION,
    tools=[
        GoogleSearchTool(bypass_multi_tools_limit=True),  # Tool 1 (built-in Google Search)
        calculator,                                        # Tool 2
        text_analyzer,                                     # Tool 3
    ],
)
