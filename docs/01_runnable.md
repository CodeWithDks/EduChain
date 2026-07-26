# Runnable

The base abstraction every component in EduChain is built on.

---

## What it is

`Runnable` is an abstract base class. It defines the one interface every
component in EduChain must implement:

```python
class Runnable(ABC):
    @abstractmethod
    def invoke(self, input_data):
        pass
```

`PromptTemplate`, `ChatModel`, `StringOutputParser`, `RunnableSequence`,
`Agent` — every single one of them is a `Runnable`. None of them know or
care what kind of `Runnable` they're talking to. They just call `.invoke()`
and trust it returns something usable.

---

## Why it exists

Without a shared interface, composing components together would mean
writing custom glue code every time two pieces need to talk to each other —
"if this is a prompt template, call `.format()`; if it's a model, call
`.generate()`; if it's a parser, call `.parse()`." That's brittle, and it
means every new component type breaks existing code that composes them.

`Runnable` solves this with one rule: **everything takes an input and
returns an output through `.invoke()`.** A `RunnableSequence` doesn't need
special-case logic for each step type — it just does:

```python
result = step.invoke(result)
```

...in a loop, for every step, regardless of what that step actually is.
This is what makes chains, parallel branches, agents, and RAG pipelines
all composable with each other using the exact same mechanism.

---

## The three methods

`Runnable` defines one required method and two optional ones with sensible
defaults:

```python
def invoke(self, input_data):
    ...  # REQUIRED — every subclass must implement this

def stream(self, input_data):
    yield self.invoke(input_data)  # default: just run invoke() and yield once

async def ainvoke(self, input_data):
    return self.invoke(input_data)  # default: just run invoke() synchronously
```

Components that can do something smarter — like `ChatModel`, which can
genuinely stream tokens from the LLM as they arrive, or run asynchronously
over the network — override `stream()` and `ainvoke()` with real
implementations. Components that can't (like `PromptTemplate`, which is
just instant string formatting) simply inherit the defaults and it works
correctly with zero extra code.

---

## The `|` operator

`Runnable` also defines how components chain together:

```python
def __or__(self, other):
    from educhain.core.sequence import RunnableSequence
    return RunnableSequence(self, other)
```

This is what makes `prompt | model | parser` work. It's not special syntax
— it's Python's operator overloading, wired to build a `RunnableSequence`
behind the scenes.

---

## Basic usage

You won't use `Runnable` directly very often — it's abstract, so it can't
be instantiated on its own. Instead, you'll build your own components by
subclassing it:

```python
from educhain.core.runnable import Runnable

class UppercaseStep(Runnable):
    def invoke(self, input_data):
        if not isinstance(input_data, str):
            raise TypeError("Expected a string.")
        return input_data.upper()

step = UppercaseStep()
print(step.invoke("hello"))  # "HELLO"
```

This is exactly the pattern `RunnableLambda` is built on (see
`08_runnable_lambda.md`) — except `RunnableLambda` lets you skip writing a
whole class for something this simple.

---

## API Reference

### `Runnable` (abstract base class)

| Method | Required to override? | Description |
|---|---|---|
| `invoke(input_data)` | **Yes** | Runs the component, returns a result |
| `stream(input_data)` | No | Defaults to yielding `invoke()`'s result once |
| `ainvoke(input_data)` | No | Defaults to running `invoke()` synchronously |
| `__or__(other)` | No | Enables `self | other` → builds a `RunnableSequence` |

---

## Full example

```python
from educhain.core.runnable import Runnable

class WordCounter(Runnable):
    """A custom Runnable that counts words in a string."""

    def invoke(self, input_data):
        if not isinstance(input_data, str):
            raise TypeError(
                f"WordCounter expects a string, but got {type(input_data).__name__}."
            )
        return len(input_data.split())


class Doubler(Runnable):
    """A custom Runnable that doubles a number."""

    def invoke(self, input_data):
        if not isinstance(input_data, int):
            raise TypeError(
                f"Doubler expects an int, but got {type(input_data).__name__}."
            )
        return input_data * 2


# Because both inherit from Runnable, they chain with | automatically —
# even though they were written completely independently
pipeline = WordCounter() | Doubler()

result = pipeline.invoke("the quick brown fox jumps")
print(result)  # 5 words -> doubled -> 10
```

This is the entire point of `Runnable`: two classes that know nothing
about each other still compose correctly, because they both honor the
same contract.

---

## Common pitfalls

**Forgetting to implement `invoke()`.**
Since `Runnable` is an `ABC` with `invoke()` marked `@abstractmethod`,
Python will refuse to instantiate any subclass that doesn't implement it —
you'll get a `TypeError` at the moment you try to create the object, not
somewhere confusing later. This is a feature, not an annoyance: it catches
incomplete components immediately.

**Assuming `stream()` always streams.**
Not every component can genuinely stream — `PromptTemplate` formatting a
string is instant, there's nothing to chunk. The default `stream()`
behavior (yield the full `invoke()` result once) is correct for these
cases. Only override `stream()` when there's real incremental output to
produce — see `10_streaming.md` for how `ChatModel` and `RunnableSequence`
do this properly.

**The local import inside `__or__`.**
You'll notice `__or__` imports `RunnableSequence` *inside* the method
body, not at the top of the file:

```python
def __or__(self, other):
    from educhain.core.sequence import RunnableSequence
    return RunnableSequence(self, other)
```

This is intentional — `sequence.py` also imports from `runnable.py`, so
importing `RunnableSequence` at the top of `runnable.py` would create a
circular import. Delaying the import until the method actually runs avoids
the problem entirely.

---

## Where this is used next

Every other doc in this set builds on `Runnable`. The next one,
`02_prompt_template.md`, covers the first real subclass — `PromptTemplate`
— which turns a dictionary into a formatted prompt string.