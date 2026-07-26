# Agents

An LLM that can take multiple steps — deciding which tools to call,
running them, looking at the results, and deciding what to do next —
until it reaches a final answer. The capstone of EduChain.

---

## What it is

`Agent` wraps a tool-bound `ChatModel` in a reasoning loop:

```python
from educhain.core.tool import Tool
from educhain.models.llm import ChatModel
from educhain.core.agent import Agent

def get_weather(city: str) -> str:
    """Get the current weather for a specific named city.
    Only use this if the user is asking about weather conditions."""
    return f"Sunny in {city}"

model = ChatModel(tools=[Tool(get_weather)])
agent = Agent(model=model)

answer = agent.invoke("What's the weather like in Delhi right now?")
print(answer)
# "The current weather in Delhi is 32°C and sunny."
```

Unlike a plain `ChatModel.invoke()` call, which is a single request and a
single response, `Agent.invoke()` can involve several round trips: ask →
tool call requested → tool runs → result fed back → ask again → repeat as
many times as needed → final answer.

---

## Why it exists — and why it had to come last

Every other layer in EduChain exists specifically to make this one
possible:

```
Agent needs:
   ChatModel with tools bound          (13_tool_calling.md)
   + has_tool_calls() / run_tool_calls()
   + a way to hold a growing conversation, not just one prompt
   + visibility into each step while debugging               (12_callbacks.md)
```

That third requirement — a growing conversation — is what actually forced
a real architectural change. Every earlier chain in EduChain sent
`ChatModel` a single formatted string. An agent loop needs to send a
**list of messages** that grows with each round: the original question,
the AI's tool request, the tool's result, the AI's next move, and so on.

This gap was identified early, during the Tool Calling phase, and
deliberately **deferred** rather than solved speculatively — it only
became a concrete requirement once Agent needed it. `ChatModel.invoke()`
was extended to accept either a plain string (unchanged, existing
behavior) or a list of message objects (new), specifically to support this:

```python
def invoke(self, input_data):
    is_string = isinstance(input_data, str)
    is_message_list = isinstance(input_data, list) and len(input_data) > 0
    ...
```

### The loop, precisely

```
conversation = [HumanMessage(question)]

for step in range(max_iterations):
    response = model.invoke(conversation)
    conversation.append(response)

    if not model.has_tool_calls(response):
        return response.content          # final answer — stop

    results = model.run_tool_calls(response)
    for call, result in zip(response.tool_calls, results):
        conversation.append(ToolMessage(result, tool_call_id=call["id"]))
    # loop again with the updated conversation

raise RuntimeError("Exceeded max_iterations")   # safety net
```

Nothing here is a new mechanism — it's `ChatModel`'s tool detection and
execution, called repeatedly, with the conversation growing each time.

---

## Basic usage

```python
from educhain.core.tool import Tool
from educhain.models.llm import ChatModel
from educhain.core.agent import Agent

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together. Only use this for addition."""
    return a + b

def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together. Only use this for multiplication."""
    return a * b

model = ChatModel(tools=[Tool(add_numbers), Tool(multiply_numbers)])
agent = Agent(model=model)

print(agent.invoke("What is 12 multiplied by 7?"))
# "12 multiplied by 7 is 84."

print(agent.invoke("What is the capital of Japan?"))
# "The capital of Japan is Tokyo." — no tool needed, answered directly
```

An agent doesn't call a tool just because one exists — it only reaches
for one when the question actually calls for it, same discipline
established in `13_tool_calling.md`.

---

## API Reference

### `Agent(model, max_iterations=5, callbacks=None)`

| Parameter | Type | Description |
|---|---|---|
| `model` | `ChatModel` with `tools` bound | Required — an agent with no tools can only talk, not act |
| `max_iterations` | `int` | Hard safety cap on reasoning loops (default 5) |
| `callbacks` | `list[CallbackHandler]`, optional | Fires around each iteration — see `12_callbacks.md` |

**Raises at construction:**
- `TypeError` — if `model` isn't a `ChatModel` with tool-calling support
- `ValueError` — if `model` has zero tools bound

### `.invoke(question)`

| Parameter | Type | Description |
|---|---|---|
| `question` | `str` | The task or question to reason about |

**Returns:** `str` — the final answer, once the LLM stops requesting tools

**Raises:**
- `TypeError` — if `question` isn't a string
- `ValueError` — if `question` is empty
- `RuntimeError` — if `max_iterations` is exceeded without reaching a
  final answer

---

## Full example — RAG as a tool

This is the pattern that ties every layer of EduChain together: wrapping
a `RAGChain` (see `15_rag.md`) as a `Tool`, so the agent can search its
own knowledge base as one of its available actions.

```python
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain
from educhain.core.tool import Tool
from educhain.core.agent import Agent
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

# 1. Build the knowledge base (14_vector_store.md)
store = InMemoryVectorStore()
store.add_texts([
    "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
    "NimbusTech's headquarters moved from Pune to Bangalore in 2023.",
])

# 2. Build the RAG chain (15_rag.md)
prompt = PromptTemplate(
    template=(
        "Answer using ONLY the context below. "
        "If the answer isn't in the context, say you don't know.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    ),
    input_variables=["context", "question"],
)
chain = prompt | ChatModel() | StringOutputParser()
rag = RAGChain(vectorstore=store, chain=chain, k=3)

# 3. Wrap RAG's .invoke() as a plain function, then as a Tool (13_tool_calling.md)
def search_company_knowledge(question: str) -> str:
    """Search internal company knowledge about NimbusTech.
    Use this for any question about NimbusTech — its founder,
    history, products, or headquarters."""
    return rag.invoke(question)

knowledge_tool = Tool(search_company_knowledge)

# 4. Give the agent this tool
model = ChatModel(tools=[knowledge_tool])
agent = Agent(model=model)

answer = agent.invoke("Where is NimbusTech headquartered now, and who founded it?")
print(answer)
# "NimbusTech is headquartered in Bangalore, India, and it was founded by Ariana Kessler."
```

Every layer of EduChain participates in producing that one answer:
`Agent` decides a tool is needed → `Tool` executes `search_company_knowledge`
→ that function calls `RAGChain.invoke()` → which calls
`InMemoryVectorStore.similarity_search()` → hand-written cosine similarity
finds the right facts → injected into a `PromptTemplate` → run through
`ChatModel` → result returned to the agent as a `ToolMessage` → fed back
into the conversation → final answer generated.

---

## Full example — with callbacks for full visibility

```python
from educhain.core.callbacks import PrintCallbackHandler

model = ChatModel(tools=[Tool(add_numbers)])
agent = Agent(model=model, callbacks=[PrintCallbackHandler()])

agent.invoke("What is 12 plus 30?")
```

```
============================================================
✨ EduChain — starting Agent
============================================================
[Running] Agent iteration 1...
[Done] Agent iteration 1 ✔
[Running] Agent iteration 2...
[Done] Agent iteration 2 ✔
============================================================
Your answer is ready ❤️  — Agent finished
============================================================
```

Two iterations: the first requests the tool call, the second returns the
final answer after seeing the tool's result. This is the callback system
(`12_callbacks.md`) proving its value on something more complex than a
simple chain — you can see exactly how many reasoning steps a question
actually took.

---

## Common pitfalls

**Building an agent with no tools.**
```python
Agent(model=ChatModel())
# ValueError: Agent's model has no tools bound. An agent with zero tools
# can't take any actions — pass tools=[...] when creating the ChatModel.
```
This fails at construction on purpose — an agent that can't act isn't
really an agent, it's just a `ChatModel` with extra steps.

**Not setting `max_iterations` thoughtfully.**
The default of 5 is generous for simple tasks but genuinely necessary as
a safety net — an LLM can get stuck repeatedly calling the same tool, or
ping-ponging between two tools, without ever producing a final answer.
Without a hard cap, this would hang indefinitely, burning API calls the
whole time.
```python
agent = Agent(model=model, max_iterations=2)
agent.invoke("...")
# RuntimeError: Agent did not reach a final answer within 2 iterations.
# The LLM may be stuck in a tool-calling loop. Consider raising
# max_iterations, or check if your tool is returning something the
# LLM can't use to finish.
```
A `RuntimeError` here is intentional — a silent, incomplete answer would
be far more dangerous than an honest failure.

**Assuming the message-list conversation is something you build by hand
elsewhere.**
Outside of `Agent`, you'll almost never construct a message list yourself
— every other chain in EduChain uses `PromptTemplate`, which always
produces a plain string. Message-list support in `ChatModel.invoke()`
exists specifically to power `Agent`'s internal loop; you don't need to
think about it unless you're extending `Agent` itself or building
something similarly multi-turn.

**Streaming isn't supported inside the agent loop (yet).**
`Agent.invoke()` returns the final answer as a complete string, not a
stream — each internal `model.invoke()` call in the loop runs to
completion before the agent decides its next move. Streaming the *final*
answer once the loop finishes is a reasonable future addition, but the
intermediate reasoning steps aren't naturally streamable the way a single
`ChatModel.stream()` call is (see `10_streaming.md`).

---

## Closing the loop

This is the last doc in the set, but it's also where every earlier one
comes back together. `Agent` doesn't introduce a new mechanism — it's
`Runnable` (`01`), `ChatModel` with tools (`03`, `13`), a conversation held
in a growing list, and `CallbackHandler` (`12`) for visibility, all
composed into a loop with one safety limit.

If you're new to EduChain and read these docs start to finish, you've now
seen the same idea — one interface, everywhere, composed in layers — show
up at every scale: from formatting a single string, to a multi-step agent
searching its own knowledge base and deciding what to do next on its own.
```

