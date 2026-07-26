# RunnableLambda

Wraps any plain Python function so it can be used as a step inside a
chain — no need to write a full `Runnable` subclass for simple logic.

---

## What it is

`RunnableLambda` takes a function and makes it behave like every other
component in EduChain, so it can sit inside a `|` chain right alongside
`PromptTemplate`, `ChatModel`, and everything else:

```python
from educhain.core.lambda_runnable import RunnableLambda

uppercase_step = RunnableLambda(lambda text: text.upper())

chain = prompt | model | parser | uppercase_step
```

---

## Why it exists

Writing a whole class every time you need a small transformation —
uppercasing text, stripping whitespace, reformatting a value — is a lot
of ceremony for something this simple:

```python
# Without RunnableLambda — full class just to uppercase a string
class UppercaseStep(Runnable):
    def invoke(self, input_data):
        return input_data.upper()
```

```python
# With RunnableLambda — one line
uppercase_step = RunnableLambda(lambda text: text.upper())
```

`RunnableLambda` is the escape hatch for quick, ad-hoc logic — you get the
full benefit of composability (`|`, working inside `RunnableSequence`)
without the boilerplate of a dedicated class every time.

---

## Basic usage

```python
from educhain.core.lambda_runnable import RunnableLambda

double_it = RunnableLambda(lambda x: x * 2)
print(double_it.invoke(21))   # 42
```

Works with named functions too, not just lambdas:

```python
def clean_text(text):
    return text.strip().lower()

cleaner = RunnableLambda(clean_text)
print(cleaner.invoke("  Hello World  "))   # "hello world"
```

---

## API Reference

### `RunnableLambda(func)`

| Parameter | Type | Description |
|---|---|---|
| `func` | any callable | The function to wrap — a `lambda`, a named function, anything callable |

**Raises at construction:** `TypeError` — if `func` isn't callable

### `.invoke(input_data)`

Calls `func(input_data)` and returns the result.

**Raises:** `RuntimeError` — if the wrapped function raises any exception
internally. The original error message is included, so you can see
exactly what went wrong inside your function.

---

## Full example

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser
from educhain.core.lambda_runnable import RunnableLambda

prompt = PromptTemplate(
    template="Give me one interesting fact about {topic}.",
    input_variables=["topic"],
)

make_uppercase = RunnableLambda(lambda text: text.upper())

chain = prompt | ChatModel() | StringOutputParser() | make_uppercase

result = chain.invoke({"topic": "the Taj Mahal"})
print(result)
# "THE TAJ MAHAL CHANGES COLOR DEPENDING ON THE TIME OF DAY..."
```

`RunnableLambda` doesn't care that it's positioned after a full
prompt-model-parser chain — from its perspective, it just received a
string and returned a transformed string, same as it would from any other
input.

---

## Common pitfalls

**Passing something non-callable.**
```python
RunnableLambda("not a function")
# TypeError: RunnableLambda expects a function, but got str.
# Example: RunnableLambda(lambda x: x.strip())
```

**A function that fails on unexpected input.**
```python
step = RunnableLambda(lambda x: x.upper())
step.invoke(123)
# RuntimeError: RunnableLambda failed while running your function:
# 'int' object has no attribute 'upper'
```
This is deliberately wrapped and re-raised as a `RuntimeError` rather than
letting the original exception bubble up bare. In a long chain, an
unwrapped error from deep inside a lambda can be genuinely confusing to
trace — this makes it explicit that the failure happened *inside your
function*, not somewhere else in the chain.

**Using it for anything beyond simple, stateless transformations.**
`RunnableLambda` is meant for quick, self-contained logic. If your
transformation needs to hold state, do validation with custom error
messages, or reuse logic across multiple chains, a proper `Runnable`
subclass (see `01_runnable.md`) is the better tool — it's not much more
code, and it's clearer about what it's doing.

---

## Where this is used next

This closes out the core primitives — `Runnable` through
`RunnableLambda`. The next doc, `09_memory.md`, moves into the execution
model layer, covering how EduChain gives a chain the ability to remember
past turns in a conversation.