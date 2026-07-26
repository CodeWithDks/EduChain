# Output Parsers

Convert a raw `AIMessage` into the format you actually want to work with.

---

## What they are

Output parsers are the last step in a typical chain. `ChatModel` returns
an `AIMessage` object — useful, but not always what you want to pass
along to the rest of your program. EduChain ships two:

- **`StringOutputParser`** — pulls out the plain text (`.content`)
- **`JsonOutputParser`** — parses that text as JSON into a Python `dict`

Both are `Runnable`s, so they slot directly onto the end of a chain:

```python
chain = prompt | model | parser
```

---

## Why they exist

Without a parser, every piece of code downstream of a chain would need to
know it's dealing with an `AIMessage` and manually pull `.content` off it.
That's a leaky abstraction — the "shape" of LangChain's message object
would bleed into code that shouldn't care about it. A parser draws a clean
line: everything *before* it deals with `AIMessage`; everything *after* it
deals with plain strings or dicts.

---

## Basic usage

### StringOutputParser

```python
from educhain.output_parsers.parser import StringOutputParser
from educhain.models.llm import ChatModel

model = ChatModel()
parser = StringOutputParser()

ai_message = model.invoke("Say hello.")
text = parser.invoke(ai_message)

print(text)          # "Hello! How can I help you today?"
print(type(text))    # <class 'str'>
```

### JsonOutputParser

```python
from educhain.output_parsers.parser import JsonOutputParser

model = ChatModel()
parser = JsonOutputParser()

ai_message = model.invoke(
    'Respond ONLY with JSON: {"name": "Radha Rani", "role": "consort of Krishna"}'
)
data = parser.invoke(ai_message)

print(data)           # {'name': 'Radha Rani', 'role': 'consort of Krishna'}
print(type(data))     # <class 'dict'>
```

---

## API Reference

### `StringOutputParser`

`.invoke(input_data)`

| Parameter | Type | Description |
|---|---|---|
| `input_data` | `AIMessage` | Must be an `AIMessage` — typically straight from `ChatModel.invoke()` |

**Returns:** `str` — the message's `.content`

**Raises:** `TypeError` — if `input_data` isn't an `AIMessage`

`.stream(input_data)` — accepts a generator of `AIMessageChunk` objects
(from `ChatModel.stream()`) and yields plain text chunks. See
`10_streaming.md` for why this parser supports streaming and
`JsonOutputParser` deliberately does not.

### `JsonOutputParser`

`.invoke(input_data)`

| Parameter | Type | Description |
|---|---|---|
| `input_data` | `AIMessage` | Must be an `AIMessage` whose `.content` is valid JSON text |

**Returns:** `dict`

**Raises:**
- `TypeError` — if `input_data` isn't an `AIMessage`
- `ValueError` — if `.content` isn't valid JSON

---

## Full example

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import JsonOutputParser

prompt = PromptTemplate(
    template=(
        "Respond ONLY with valid JSON, no explanation. "
        "Give info about {city} in this format: "
        '{{"city": "...", "country": "...", "famous_for": "..."}}'
    ),
    input_variables=["city"],
)

chain = prompt | ChatModel() | JsonOutputParser()

result = chain.invoke({"city": "Jaipur"})
print(result["country"])   # "India"
```

---

## Common pitfalls

**Passing a plain string instead of an `AIMessage`.**
```python
parser.invoke("just a string")
# TypeError: StringOutputParser expects an AIMessage, but got str.
# This parser should be placed right after a ChatModel in the chain.
```
This is almost always a sign the parser is in the wrong position in a
chain — it must come directly after a `ChatModel`, not after another
parser or a `PromptTemplate`.

**`JsonOutputParser` failing on non-JSON output.**
LLMs don't *always* follow formatting instructions perfectly — if the
model adds explanation text around the JSON, or uses markdown code
fences, parsing will fail:
```python
# ValueError: LLM did not return valid JSON. Tip: make your prompt
# explicitly ask for JSON output, e.g. 'Respond only in valid JSON format.'
```
This isn't a bug in the parser — it's a reminder that structured output
from an LLM is only as reliable as your prompt's instructions. Being
explicit ("Respond ONLY with JSON, no markdown, no explanation") reduces
this significantly but can't eliminate it entirely.

**Why `JsonOutputParser` has no `stream()` method.**
Streaming means receiving a response piece by piece, but you can't call
`json.loads()` on half a JSON object — `{"name": "Rad` isn't valid JSON on
its own. Rather than build something fragile that pretends to stream and
breaks constantly, `JsonOutputParser` intentionally stays invoke-only. If
you need streaming, use `StringOutputParser` and parse the final complete
text yourself once streaming finishes.

---

## Where this is used next

Parsers are almost always the last link in a chain. The next doc,
`05_runnable_sequence.md`, covers the mechanism that actually chains
`PromptTemplate → ChatModel → OutputParser` together — `RunnableSequence`,
the class behind the `|` operator.