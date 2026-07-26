# ChatModel

A wrapper around any LangChain-compatible chat model — the component that
actually talks to the LLM.

---

## What it is

`ChatModel` takes a prompt (a string, or a list of conversation messages)
and sends it to an underlying LLM, returning an `AIMessage` object. By
default it wraps `ChatOpenAI()`, but any chat model that supports
`.invoke()` can be passed in instead.

```python
model = ChatModel()
response = model.invoke("Say hello in one sentence.")
print(response.content)
```

It's the only component in EduChain's core primitives that does real
network I/O — everything before it (like `PromptTemplate`) is just string
manipulation. That distinction matters a lot once you get to streaming and
async, both of which only make sense here.

---

## Why it exists

You could call `ChatOpenAI()` directly, but wrapping it gives EduChain
three things a raw LangChain model doesn't have out of the box:

1. **Consistent validation** — the same clear error messages every other
   EduChain component uses, instead of whatever error the underlying
   provider's SDK happens to throw.
2. **A single interface** (`Runnable`) — so `ChatModel` composes with `|`
   into chains, just like `PromptTemplate` and every parser.
3. **Extra capabilities layered on top** — tool binding, callback hooks on
   failure, and support for both simple string prompts *and* full
   multi-turn conversations (needed for Agents — see `16_agents.md`).

---

## Basic usage

```python
from educhain.models.llm import ChatModel

model = ChatModel()
response = model.invoke("What is the capital of France?")

print(response.content)
# "The capital of France is Paris."
```

Note that `.invoke()` returns an `AIMessage` object, not a plain string —
`response.content` is where the actual text lives. This is intentional:
the full object also carries metadata (`response.response_metadata`) and,
if tools are bound, `response.tool_calls`. If you just want a clean
string, pair `ChatModel` with `StringOutputParser` (see
`04_output_parsers.md`).

---

## API Reference

### `ChatModel(model=None, max_tokens=None, tools=None, callbacks=None)`

| Parameter | Type | Description |
|---|---|---|
| `model` | any LangChain chat model, optional | Defaults to `ChatOpenAI()` if not provided. Pass a different model (e.g. `ChatGroq`) to swap providers. |
| `max_tokens` | `int`, optional | Caps response length. Only applies when using the default model — if you pass your own `model`, configure it directly. |
| `tools` | `list[Tool]`, optional | Enables tool calling. See `13_tool_calling.md`. |
| `callbacks` | `list[CallbackHandler]`, optional | Hooks fired on error. See `12_callbacks.md`. |

### `.invoke(input_data)`

| Parameter | Type | Description |
|---|---|---|
| `input_data` | `str` or `list[Message]` | A plain prompt string, OR a list of message objects (`HumanMessage`, `AIMessage`, `ToolMessage`) for multi-turn conversations |

**Returns:** `AIMessage`

**Raises:**
- `TypeError` — if `input_data` is neither a string nor a non-empty list
- `ValueError` — if a string prompt is empty, or a message list is empty

### `.stream(input_data)`

Same validation as `.invoke()`. Returns a generator yielding
`AIMessageChunk` objects as they arrive from the model. See
`10_streaming.md`.

### `.ainvoke(input_data)`

Async version of `.invoke()`, same validation, same return type. See
`11_async_execution.md`.

### `.has_tool_calls(response)`

Returns `True` if a response is asking to call a tool instead of
answering directly. See `13_tool_calling.md`.

### `.run_tool_calls(response)`

Executes every tool the LLM requested in a response, returns structured
results. See `13_tool_calling.md`.

---

## Full example — swapping the default model

```python
from educhain.models.llm import ChatModel
from educhain.prompts.prompt import PromptTemplate
from educhain.output_parsers.parser import StringOutputParser
from langchain_groq import ChatGroq
import os

groq_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)

model = ChatModel(model=groq_model, max_tokens=200)

prompt = PromptTemplate(
    template="Answer briefly: {question}",
    input_variables=["question"],
)
parser = StringOutputParser()

chain = prompt | model | parser
print(chain.invoke({"question": "What is photosynthesis?"}))
```

`ChatModel` doesn't care which provider it's wrapping — anything with an
`.invoke()` method (and `.stream()`/`.ainvoke()` if you want those
features too) works the same way.

---

## Common pitfalls

**Passing a dict instead of a string.**
```python
model.invoke({"topic": "AI"})
# TypeError: ChatModel expects a string prompt or a list of messages, but got dict.
# Did you forget to call .format() on your PromptTemplate?
```
This is the single most common mistake when wiring a chain by hand instead
of using `|` — `ChatModel` needs a *formatted* string, not the raw
dictionary you'd pass to `PromptTemplate`.

**Empty prompts.**
```python
model.invoke("   ")
# ValueError: Prompt cannot be empty. Please pass some text before calling invoke().
```
Caught before it reaches the API — saves you a wasted network call and a
confusing provider-side error.

**Assuming `.invoke()` always returns text you can print directly.**
```python
print(model.invoke("Hello"))
# <AIMessage content='Hello! How can I help you?' ...>
```
Always use `.content`, or better, put a `StringOutputParser` after it in
a chain so this is handled for you automatically.

**Message-list support exists, but only matters for advanced use.**
`ChatModel.invoke()` accepting a list of messages (not just a string) was
added specifically to support `Agent` (see `16_agents.md`) — a normal
`prompt | model | parser` chain will never need this, since
`PromptTemplate` always produces a plain string. You'll only build message
lists by hand if you're working with multi-turn tool conversations
directly.

---

## Where this is used next

`ChatModel` sits at the center of almost every chain in EduChain. The next
doc, `04_output_parsers.md`, covers what typically comes right after it —
turning the raw `AIMessage` into something clean and usable.