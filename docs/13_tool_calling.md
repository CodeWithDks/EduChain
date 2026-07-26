# Tool Calling

Lets an LLM decide, on its own, to call a Python function — turning a
chatbot that only talks into one that can actually *act*.

---

## What it is

Two pieces work together here:

- **`Tool`** (`core/tool.py`) — wraps a plain Python function so an LLM
  can understand what it does and how to call it
- **`ChatModel`** — accepts a list of tools, binds their schemas to the
  underlying model, and exposes methods to detect and execute tool calls
  the LLM chooses to make

```python
def get_weather(city: str) -> str:
    """Get the current weather for a specific named city."""
    return f"Sunny in {city}"

weather_tool = Tool(get_weather)
model = ChatModel(tools=[weather_tool])

response = model.invoke("What's the weather in Delhi?")

if model.has_tool_calls(response):
    results = model.run_tool_calls(response)
    print(results)
    # [{'name': 'get_weather', 'args': {'city': 'Delhi'}, 'result': 'Sunny in Delhi'}]
```

The LLM chose to call `get_weather` and figured out the right argument
(`city="Delhi"`) — nothing in the code told it to do that explicitly.

---

## Why it exists

An LLM on its own can only generate text based on what it already knows.
It can't check today's weather, do exact arithmetic reliably, query a
database, or take any real action. Tool calling gives the LLM a menu of
functions it's allowed to use, and lets it *reason* about whether calling
one would help answer the question — then your code actually executes
whatever it chose.

### Why `Tool` doesn't inherit from `Runnable`

Every other component in EduChain takes one input and returns one output
— that's the `Runnable` contract. `Tool` genuinely doesn't fit this shape:
the LLM calls it with **named arguments** (`get_weather(city="Delhi")`),
not one piped value. Forcing `Tool` to be a `Runnable` just to look
consistent would break the actual abstraction. Instead, `Tool` has its
own method, `.run(**kwargs)`, that matches its real shape.

### Auto-generated schemas

Rather than requiring you to hand-write a JSON schema for every function,
`Tool` inspects your function's type hints and docstring automatically:

```python
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

tool = Tool(add_numbers)
print(tool.schema)
# {'type': 'function', 'function': {'name': 'add_numbers',
#   'description': 'Add two numbers together.',
#   'parameters': {'type': 'object',
#     'properties': {'a': {'type': 'integer'}, 'b': {'type': 'integer'}},
#     'required': ['a', 'b']}}}
```

---

## Basic usage

```python
from educhain.core.tool import Tool
from educhain.models.llm import ChatModel

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together. Only use this for addition."""
    return a + b

model = ChatModel(tools=[Tool(add_numbers)])

response = model.invoke("What is 47 plus 89?")

if model.has_tool_calls(response):
    results = model.run_tool_calls(response)
    print(results[0]["result"])   # 136
```

---

## API Reference

### `Tool(func, name=None, description=None)`

| Parameter | Type | Description |
|---|---|---|
| `func` | callable | The Python function to wrap |
| `name` | `str`, optional | Defaults to `func.__name__` |
| `description` | `str`, optional | Defaults to `func`'s docstring — **required one way or another**, since the LLM needs it to know when to use the tool |

**Raises at construction:**
- `TypeError` — if `func` isn't callable
- `ValueError` — if there's no description available (no docstring, none passed explicitly)

### `.run(**kwargs)`

Executes the wrapped function with the given keyword arguments.

**Raises:** `RuntimeError` — if the function fails internally (wraps and
re-raises the original error with context)

### `ChatModel(tools=[...])`

Binds tool schemas to the model via `.bind_tools(schemas, tool_choice="auto")`.

### `.has_tool_calls(response)`

**Returns:** `bool` — `True` if the response is requesting a tool call
instead of answering directly.

### `.run_tool_calls(response)`

Executes every tool the LLM requested.

**Returns:** `list[dict]` — each with `name`, `args`, and `result` keys.

**Raises:** `ValueError` — if the LLM asks for a tool name that isn't
bound to this `ChatModel`.

---

## Full example — multiple tools, LLM picks the right one

```python
from educhain.core.tool import Tool
from educhain.models.llm import ChatModel

def get_weather(city: str) -> str:
    """Get the current weather for a specific named city.
    Only use this if the user is asking about weather conditions."""
    return f"Sunny in {city}"

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together. Only use this for addition."""
    return a + b

model = ChatModel(tools=[Tool(get_weather), Tool(add_numbers)])

# The LLM correctly ignores both tools for an unrelated question
response = model.invoke("What is the capital of France?")
print(model.has_tool_calls(response))   # False
print(response.content)                 # "The capital of France is Paris."

# The LLM correctly picks add_numbers, not get_weather
response = model.invoke("What is 12 plus 30?")
results = model.run_tool_calls(response)
print(results[0]["name"])    # "add_numbers"
print(results[0]["result"])  # 42
```

---

## Common pitfalls

**No description, no `ValueError` warning — until you hit it.**
```python
def mystery_func(x: str) -> str:
    return x

Tool(mystery_func)
# ValueError: Tool 'mystery_func' has no description. Either add a
# docstring to your function, or pass description='...' explicitly.
```
This fails loudly on purpose. A tool with no description isn't a minor
gap — the LLM has no way to judge when to use it, so it's effectively
broken. Failing at construction time is far better than the tool being
silently ignored (or misused) later.

**A single vague tool gets called for everything.**
This is a real behavior pattern hit while building EduChain: with only
*one* tool bound, some models get overeager and call it even for
completely unrelated questions — because the training data skews toward
"if a tool exists, consider using it." Two things fix this:
1. `tool_choice="auto"` explicitly set when binding (rather than leaving
   it to the model's default).
2. Sharper, scoped docstrings — `"Only use this if the user is asking
   about weather conditions"` gives the model something concrete to rule
   the tool *out* with, not just what it does.

**Forgetting that Tool Calling alone doesn't loop.**
`has_tool_calls()` and `run_tool_calls()` give you detection and
execution for a *single* round — you still have to manually feed the
tool's result back into a new message and call `invoke()` again to get a
final natural-language answer. Automating that entire loop is exactly
what `Agent` does — see `16_agents.md`.

---

## Where this is used next

Tool Calling gives an LLM the ability to *act*. The next doc,
`14_vector_store.md`, covers a different kind of capability — giving the
LLM access to real, specific information it wasn't trained on, through
semantic search.