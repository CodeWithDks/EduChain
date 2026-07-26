# Memory

Lets a chain remember what was said in earlier turns of a conversation.

---

## What it is

By default, every `.invoke()` call in EduChain is stateless — a chain has
no idea what you asked it a moment ago. Memory solves this with two
classes working together:

- **`MessageHistory`** (`core/history.py`) — a plain store of conversation
  turns (a list of `HumanMessage`/`AIMessage` objects)
- **`ChatMessageHistory`** (`memory/chat_history.py`) — wraps an existing
  chain, automatically injecting past turns into the prompt and saving new
  ones after each call

```python
chain = prompt | model | parser
chat = ChatMessageHistory(chain, history_key="history")

chat.invoke({"question": "My name is Deepak"})
chat.invoke({"question": "What's my name?"})
# -> correctly remembers "Deepak"
```

---

## Why it exists

Without memory, a chatbot forgets everything between messages — every
question is answered in total isolation from the last one. Real
conversation requires context: the model needs to see what was said
before to answer follow-up questions correctly. `ChatMessageHistory`
handles this automatically so you don't have to manually track and
re-inject history into every single call yourself.

### Why two separate classes, not one

`MessageHistory` and `ChatMessageHistory` do genuinely different jobs and
are kept separate on purpose:

- `MessageHistory` is a plain data structure — it doesn't know what a
  chain is, doesn't call `.invoke()` on anything, just stores messages.
- `ChatMessageHistory` is a `Runnable` that *uses* a `MessageHistory`
  internally, and adds the actual behavior: formatting history as text,
  injecting it into the prompt, deciding what counts as the "user
  message" to save.

This is the same "layered building blocks" pattern used everywhere else in
EduChain — a low-level primitive, and a higher-level component built on
top of it.

---

## Basic usage

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser
from educhain.memory.chat_history import ChatMessageHistory

prompt = PromptTemplate(
    template="Conversation so far:\n{history}\n\nUser: {question}\nAssistant:",
    input_variables=["history", "question"],
)

chain = prompt | ChatModel() | StringOutputParser()
chat = ChatMessageHistory(chain, history_key="history")

print(chat.invoke({"question": "My favorite language is Python."}))
print(chat.invoke({"question": "What did I just say my favorite language was?"}))
# -> correctly answers "Python"
```

The template **must** include a placeholder matching `history_key`
(`{history}` by default) — that's where past turns get inserted.

---

## API Reference

### `MessageHistory()`

| Method | Description |
|---|---|
| `.add_user_message(content: str)` | Appends a `HumanMessage` |
| `.add_ai_message(content: str)` | Appends an `AIMessage` |
| `.clear()` | Empties the history |

**Raises:** `TypeError` if `content` isn't a string, on either add method.

### `ChatMessageHistory(chain, history_key="history")`

| Parameter | Type | Description |
|---|---|---|
| `chain` | `Runnable` | The chain to wrap — its prompt must have a variable matching `history_key` |
| `history_key` | `str` | The prompt variable name where history text gets injected |

**Raises at construction:** `TypeError` — if `chain` isn't a `Runnable`

### `.invoke(input_data)`

| Parameter | Type | Description |
|---|---|---|
| `input_data` | `dict` | Must NOT include the `history_key` — that's injected automatically |

**Behavior:** builds a plain-text version of stored history, injects it
into the input under `history_key`, runs the wrapped chain, then
automatically saves the new turn (both the user's message and the AI's
response) back into history.

**Raises:** `TypeError` — if `input_data` isn't a dict

---

## Full example

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser
from educhain.memory.chat_history import ChatMessageHistory

prompt = PromptTemplate(
    template="Conversation so far:\n{history}\n\nUser: {question}\nAssistant:",
    input_variables=["history", "question"],
)

chain = prompt | ChatModel() | StringOutputParser()
chat = ChatMessageHistory(chain, history_key="history")

turns = [
    "I'm planning a trip to Japan.",
    "What country did I just mention?",
]

for turn in turns:
    response = chat.invoke({"question": turn})
    print(f"You: {turn}")
    print(f"Bot: {response}\n")

print(chat.history)   # ChatMessageHistory(4 messages)
```

---

## Common pitfalls

**Forgetting the `{history}` placeholder in the prompt.**
If your `PromptTemplate` doesn't include a variable matching
`history_key`, you'll get a `PromptTemplate` validation error about
missing variables the moment `ChatMessageHistory` tries to inject it. The
prompt and the wrapper's `history_key` have to agree.

**Passing `history` yourself in `input_data`.**
Don't manually include `history` in the dict you pass to
`.invoke()` — it's injected automatically. If you include it yourself,
you'll get an "unexpected variable" error from `PromptTemplate` once the
wrapper tries to inject its own copy on top of yours.

**Memory is in-memory only.**
`MessageHistory` doesn't persist anywhere — once your program exits, the
conversation is gone. This is intentional for a learning project; a real
application would swap this for a database-backed store, but the
`ChatMessageHistory` interface wouldn't need to change to support that.

**The "which value is the user's message" guess.**
`ChatMessageHistory` picks whichever key in your input dict *isn't*
`history_key` and saves it as the user's message. This works cleanly when
your prompt only has two variables (`history` and one question-like
field). If your prompt has three or more input variables, this guess
becomes ambiguous — worth being aware of if you build a more complex
prompt on top of memory.

---

## Where this is used next

Memory is the first "execution model" layer, on top of the core
primitives. The next doc, `10_streaming.md`, covers a different kind of
execution model — getting a response back token by token, instead of
waiting for the whole thing to finish.