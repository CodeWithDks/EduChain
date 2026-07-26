# Streaming

Get a model's response token by token, as it's generated, instead of
waiting for the whole thing to finish.

---

## What it is

Streaming changes *how* a chain runs, not what it does. Instead of
`.invoke()`, you call `.stream()`, and instead of getting back one final
result, you get a generator that yields pieces of the answer as they
arrive:

```python
for chunk in chain.stream({"topic": "the moon"}):
    print(chunk, end="", flush=True)
```

This is what makes a chatbot feel "live" — text appearing as it's
generated, instead of a pause followed by the whole answer at once.

---

## Why it exists

Waiting for a full LLM response before showing anything can feel slow,
especially for longer answers. Streaming lets your program (and the
person using it) start seeing output immediately, even though the model
is still generating the rest.

### The real design problem: who actually streams?

In a chain like `prompt | model | parser`, only **one** step genuinely
produces a stream — `ChatModel`, since it's the only one making a network
call to an LLM that returns tokens incrementally. `PromptTemplate` just
formats a string instantly; there's nothing to "chunk" about that.

So `RunnableSequence.stream()` has to figure out: which step is the real
streaming *source*, and which steps just need to *transform* whatever
comes out of that source (like `StringOutputParser`, which needs to turn
each `AIMessageChunk` into plain text)?

This is solved with a class attribute:

```python
class StringOutputParser(OutputParser):
    IS_STREAM_TRANSFORMER = True
    ...
```

`RunnableSequence.stream()` walks backward from the last step, skipping
any step flagged as a transformer, until it finds the real source (the
model). Everything before the source runs normally with `.invoke()`;
everything from the source onward streams.

---

## Basic usage

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(
    template="Write a two-line poem about {topic}.",
    input_variables=["topic"],
)

chain = prompt | ChatModel() | StringOutputParser()

for chunk in chain.stream({"topic": "the ocean"}):
    print(chunk, end="", flush=True)
```

Each `chunk` here is already a plain string — `StringOutputParser`
converts the raw `AIMessageChunk` objects into text as they pass through.

---

## API Reference

### `ChatModel.stream(input_data)`

Same validation as `.invoke()`. Returns a generator yielding
`AIMessageChunk` objects directly from the underlying model.

### `RunnableSequence.stream(input_data)`

Runs steps before the streaming source with `.invoke()`, then streams
from the source step through any remaining transformer steps.

### `StringOutputParser.stream(input_data)`

`IS_STREAM_TRANSFORMER = True`. Expects a generator of chunks (each with
a `.content` attribute) and yields plain text per chunk.

### `JsonOutputParser`

**Does not support streaming** — no `stream()` override, no
`IS_STREAM_TRANSFORMER` flag. See pitfalls below for why.

---

## Full example

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(
    template="Explain {topic} like I'm five.",
    input_variables=["topic"],
)

chain = prompt | ChatModel() | StringOutputParser()

print("Answer: ", end="", flush=True)

full_text = ""
for chunk in chain.stream({"topic": "black holes"}):
    print(chunk, end="", flush=True)
    full_text += chunk

print(f"\n\n({len(full_text)} characters streamed)")
```

---

## Common pitfalls

**A step that should support streaming, but doesn't set the flag.**
This was a real bug hit while building EduChain: `StringOutputParser`
initially had a working `stream()` method, but no
`IS_STREAM_TRANSFORMER = True` flag. Without the flag,
`RunnableSequence.stream()` couldn't tell the parser wasn't the source —
it treated the *parser* as the streaming source, called `.stream()` on it
with a single `AIMessage` (not a generator), and the parser's `for chunk
in input_data` loop iterated over the message's internal attributes
instead of real chunks — producing a confusing error about missing
`.content`. The fix was one line (adding the flag), but it's a good
reminder that streaming support needs both the mechanism (`stream()`
method) *and* the signal (`IS_STREAM_TRANSFORMER`) to actually work
inside a sequence.

**Expecting `JsonOutputParser` to stream.**
It can't, on principle — partial JSON like `{"name": "Rad` isn't valid
JSON, so there's no safe way to parse it chunk by chunk. If you need
streaming with structured output, stream as plain text with
`StringOutputParser` and parse the complete result once streaming
finishes.

**Forgetting `flush=True` when printing chunks.**
```python
print(chunk, end="")   # may buffer, defeating the point of streaming
print(chunk, end="", flush=True)   # prints immediately
```
Without `flush=True`, Python may buffer output and print in bursts rather
than smoothly — which undermines the whole visual effect streaming is
meant to provide.

---

## Where this is used next

Streaming is one way to change *how* a chain runs. The next doc,
`11_async_execution.md`, covers another — running chains asynchronously,
which matters most once you're serving multiple requests concurrently
(e.g. inside a web server).