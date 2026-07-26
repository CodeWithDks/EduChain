# PromptTemplate

Turns a dictionary of values into a formatted prompt string.

---

## What it is

`PromptTemplate` takes a template string with `{placeholders}` and a list
of expected variable names, and produces a finished prompt when you call
`.invoke()` with a dictionary of values.

```python
prompt = PromptTemplate(
    template="Explain {topic} in simple words.",
    input_variables=["topic"]
)

prompt.invoke({"topic": "gravity"})
# -> "Explain gravity in simple words."
```

It's a `Runnable`, like everything else — it just happens to take a
`dict` as input and return a `str` as output.

---

## Why it exists

You could format prompts with plain f-strings, but that has two problems
once prompts get reused across a real application:

1. **No validation.** A typo in a variable name, or a missing value,
   silently produces a broken prompt — the LLM just gets confusing text
   instead of a clear error.
2. **No composability.** An f-string can't be chained with `|` into a
   `RunnableSequence` — it's just a string, not a `Runnable`.

`PromptTemplate` solves both: it validates every input before formatting,
and because it's a `Runnable`, it slots directly into `prompt | model |
parser` chains.

---

## Basic usage

```python
from educhain.prompts.prompt import PromptTemplate

prompt = PromptTemplate(
    template="Write a short paragraph about {topic}.",
    input_variables=["topic"]
)

result = prompt.invoke({"topic": "the ocean"})
print(result)
# "Write a short paragraph about the ocean."
```

Multiple variables work the same way:

```python
prompt = PromptTemplate(
    template="Translate '{text}' into {language}.",
    input_variables=["text", "language"]
)

prompt.invoke({"text": "Good morning", "language": "Hindi"})
# "Translate 'Good morning' into Hindi."
```

---

## API Reference

### `PromptTemplate(template, input_variables)`

| Parameter | Type | Description |
|---|---|---|
| `template` | `str` | A string with `{variable}` placeholders |
| `input_variables` | `list[str]` | Names of every variable the template expects — must match the placeholders in `template` |

**Raises at construction:**
- `TypeError` — if `template` isn't a string
- `TypeError` — if `input_variables` isn't a list
- `ValueError` — if `input_variables` is empty

### `.invoke(input_data)`

| Parameter | Type | Description |
|---|---|---|
| `input_data` | `dict` | Must contain exactly the keys listed in `input_variables` — no more, no less |

**Returns:** `str` — the formatted prompt

**Raises:**
- `TypeError` — if `input_data` isn't a dict
- `ValueError` — if any expected variable is missing
- `ValueError` — if `input_data` contains keys not in `input_variables`

---

## Full example

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(
    template=(
        "You are a helpful assistant. "
        "Answer the following question in one sentence: {question}"
    ),
    input_variables=["question"],
)

model = ChatModel()
parser = StringOutputParser()

chain = prompt | model | parser

answer = chain.invoke({"question": "What is the capital of Japan?"})
print(answer)
# "The capital of Japan is Tokyo."
```

`PromptTemplate` doesn't know anything about `ChatModel` or
`StringOutputParser` — it just formats a string and hands it off. The `|`
operator (inherited from `Runnable`) is what wires the three together.

---

## Common pitfalls

**Missing variables.**
```python
prompt = PromptTemplate(
    template="Hello {name}, welcome to {place}.",
    input_variables=["name", "place"]
)

prompt.invoke({"name": "Deepak"})
# ValueError: Missing variables: ['place']. This template needs: ['name', 'place']
```
The error tells you exactly what's missing and what the template actually
expects — no guessing.

**Extra, unexpected variables.**
```python
prompt.invoke({"name": "Deepak", "place": "Delhi", "extra": "oops"})
# ValueError: Unexpected variables: {'extra'}. This template only accepts: ['name', 'place']
```
This might seem strict, but it catches real bugs — usually a leftover key
from copy-pasted code, or a typo where you meant to overwrite an existing
key but added a new one instead.

**Placeholder in `template` not listed in `input_variables` (or vice versa).**
`PromptTemplate` doesn't automatically detect placeholders inside the
template string — you have to list them explicitly in `input_variables`.
If they don't match, you'll get a `KeyError` from Python's own
`str.format()` call, which is less friendly than the validation errors
above. Always double check the two lists agree.

---

## Where this is used next

Every chain in EduChain starts with a `PromptTemplate` (or skips straight
to a `ChatModel` for pre-formatted input). The next doc, `03_chat_model.md`,
covers what actually receives this formatted string — `ChatModel`, the
wrapper around the LLM itself.