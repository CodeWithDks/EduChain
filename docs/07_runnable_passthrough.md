# RunnablePassthrough

Returns whatever input it receives, completely unchanged.

---

## What it is

`RunnablePassthrough` is the simplest `Runnable` in EduChain — it does
nothing to its input except hand it straight back out:

```python
from educhain.core.passthrough import RunnablePassthrough

passthrough = RunnablePassthrough()
passthrough.invoke({"text": "Good morning"})
# -> {"text": "Good morning"}   (unchanged)
```

On its own, that sounds pointless. Its real value shows up inside
`RunnableParallel`.

---

## Why it exists

`RunnableParallel` runs every branch on the *same* input and collects the
results into a dict. Once you're inside a parallel block, though, the
original input isn't automatically available in the output — only what
each branch produces is. If you want the original input preserved
alongside the processed results, you need a branch that does nothing but
return it as-is. That's exactly what `RunnablePassthrough` is for.

```python
RunnableParallel(
    original=RunnablePassthrough(),   # keeps the input as one of the outputs
    summary=summary_chain,             # processes the input
)
```

---

## Basic usage

```python
from educhain.core.passthrough import RunnablePassthrough

passthrough = RunnablePassthrough()

print(passthrough.invoke({"text": "Good morning"}))
# {"text": "Good morning"}

print(passthrough.invoke("just a plain string"))
# "just a plain string"
```

Notice it accepts *anything* — a dict, a string, a number — and returns
exactly that, unchanged. There's no validation here on purpose; there's
nothing to validate.

---

## API Reference

### `RunnablePassthrough()`

No constructor parameters.

### `.invoke(input_data)`

**Returns:** `input_data`, exactly as received — no type checking, no
transformation.

---

## Full example

```python
from educhain.core.parallel import RunnableParallel
from educhain.core.passthrough import RunnablePassthrough
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

translate_chain = (
    PromptTemplate(template="Translate to Hindi: {text}", input_variables=["text"])
    | ChatModel() | StringOutputParser()
)

parallel = RunnableParallel(
    original=RunnablePassthrough(),
    translated=translate_chain,
)

result = parallel.invoke({"text": "Good morning"})

print(result["original"])     # {'text': 'Good morning'} — untouched
print(result["translated"])   # "सुप्रभात" — processed
```

Without `RunnablePassthrough`, you'd have no clean way to see both the
original input and the translated output in one result — you'd have to
track the original input separately, outside the chain.

---

## Common pitfalls

**Expecting it to validate or transform anything.**
It deliberately does neither. If you need light processing (e.g.
`.strip()` on a string) alongside keeping the original, that's not what
`RunnablePassthrough` is for — use `RunnableLambda` instead (see
`08_runnable_lambda.md`), which lets you define exactly what
transformation happens.

**Using it outside of `RunnableParallel`.**
It works fine standalone (`passthrough.invoke(x)` just returns `x`), but
that's rarely useful on its own — its entire purpose is solving a specific
problem inside parallel branches. If you're using it outside that context,
you probably just want to keep a reference to your original input in a
regular variable instead.

---

## Where this is used next

`RunnablePassthrough` rounds out the composition tools that work *around*
existing chains. The next doc, `08_runnable_lambda.md`, covers the last
core primitive — a way to drop any plain Python function into a chain
without writing a full `Runnable` subclass for it.