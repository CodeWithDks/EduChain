# 🚀 EduChain
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-v1.0-success.svg)
![Tests](https://img.shields.io/badge/Tests-36%2F36%20passing-brightgreen.svg)

> **An educational Python framework inspired by LangChain — built from scratch to understand how modern LLM frameworks work internally.**

EduChain recreates the core building blocks of LangChain by hand — including the parts most frameworks hide behind an import statement, like cosine similarity search, streaming source detection, and the agent reasoning loop. Instead of treating LLM frameworks as a black box, EduChain is about understanding the design patterns, abstractions, and architecture behind them well enough to build them yourself.

> **Note:** EduChain is an educational project. It is **not** intended to replace LangChain or be feature-compatible with it.

---

## ✨ Features

**Core Primitives**
- ✅ Runnable Abstraction (`invoke()` / `stream()` / `ainvoke()`)
- ✅ Prompt Templates
- ✅ Chat Model Wrapper
- ✅ Output Parsers (String, JSON)
- ✅ RunnableSequence (with `|` operator, auto-flattening)
- ✅ RunnableParallel
- ✅ RunnablePassthrough
- ✅ RunnableLambda

**Memory**
- ✅ Chat History / Memory Module

**Execution Models**
- ✅ Streaming (token-by-token, smart source/transformer detection)
- ✅ Async Execution (`ainvoke`, true concurrency via `asyncio.gather`)
- ✅ Callback System (pluggable hooks — no hardcoded logging)

**Agentic Capabilities**
- ✅ Tool Calling (auto-generated schemas from Python type hints)
- ✅ Vector Stores (in-memory, hand-written cosine similarity)
- ✅ RAG (Retrieval-Augmented Generation)
- ✅ Agents (multi-step tool-calling reasoning loop)

**Engineering Fundamentals**
- ✅ Input Validation across every component
- ✅ Modular Package Design
- ✅ 36/36 tests passing (happy paths + validation + full-stack integration)

---

# 📂 Project Structure

EduChain/
│
├── educhain/
│ ├── core/
│ │ ├── runnable.py → Runnable (base class)
│ │ ├── sequence.py → RunnableSequence
│ │ ├── parallel.py → RunnableParallel
│ │ ├── passthrough.py → RunnablePassthrough
│ │ ├── lambda_runnable.py → RunnableLambda
│ │ ├── history.py → MessageHistory (raw store)
│ │ ├── callbacks.py → CallbackHandler, PrintCallbackHandler
│ │ ├── tool.py → Tool
│ │ ├── vectorstore.py → InMemoryVectorStore
│ │ ├── rag.py → RAGChain
│ │ └── agent.py → Agent
│ ├── prompts/
│ │ └── prompt.py → PromptTemplate
│ ├── models/
│ │ └── llm.py → ChatModel
│ ├── output_parsers/
│ │ └── parser.py → StringOutputParser, JsonOutputParser
│ └── memory/
│ └── chat_history.py → ChatMessageHistory (chain wrapper)
│
├── test_all_features.py → 36 tests, full coverage
├── demo_all_features.py → core primitives, real usage
├── demo_async.py → async execution + speed comparison
├── demo_callbacks.py → callback system
├── demo_tools.py → tool calling
├── demo_vectorstore.py → semantic search
├── demo_rag.py → retrieval-augmented generation
├── demo_agent.py → full agentic reasoning loop
│
├── ROADMAP.md
├── README.md
├── requirements.txt
└── LICENSE


---

# 🏛 Architecture
                              Runnable
                                 │
    ┌───────────┬───────────┬───┴───────┬───────────┬──────────┐
    ▼           ▼           ▼           ▼           ▼          ▼

PromptTemplate ChatModel OutputParser Passthrough Lambda Agent
│ │
▼ ▼
(tools bound) ChatModel + Tools
│ + Callbacks
▼ │
RunnableSequence ◄──── RAGChain ◄──── InMemoryVectorStore
│
▼
RunnableParallel
│
▼
Memory & Chat History


Every component follows the same core interface:

```python
invoke(input)      # synchronous
stream(input)       # chunked/streaming
ainvoke(input)       # async
```

Because every component behaves consistently, they compose into flexible pipelines — from a simple 3-step chain to a full agent that searches its own knowledge base.

---

# ⚡ Installation

Clone the repository

```bash
git clone https://github.com/CodeWithDks/EduChain.git
```

Move into the project

```bash
cd EduChain
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
OPENAI_API_KEY=your_api_key_here
```

---

# 🚀 Quick Start

### Basic Chain

```python
from educhain.prompts.prompt import PromptTemplate
from educhain.models.llm import ChatModel
from educhain.output_parsers.parser import StringOutputParser

prompt = PromptTemplate(
    template="Explain {topic} in simple words.",
    input_variables=["topic"]
)

model = ChatModel()
parser = StringOutputParser()

chain = prompt | model | parser

response = chain.invoke({"topic": "Artificial Intelligence"})
print(response)
```

### Agent with Tools + RAG

```python
from educhain.models.llm import ChatModel
from educhain.core.tool import Tool
from educhain.core.agent import Agent

def get_weather(city: str) -> str:
    """Get the current weather for a specific named city."""
    return f"It's sunny in {city}"

weather_tool = Tool(get_weather)
model = ChatModel(tools=[weather_tool])
agent = Agent(model=model)

answer = agent.invoke("What's the weather like in Delhi?")
print(answer)
```

See `demo_agent.py` for a full example combining Tool Calling, RAG, and Callbacks together.

---

# 🔄 Execution Flow

**Basic chain:**

Dictionary → PromptTemplate → Formatted Prompt → ChatModel → AIMessage → OutputParser → Final Response


**Agent loop:**

Question → ChatModel (with tools) → tool call requested?
│
yes ────────┴──────── no
│ │
run the tool final answer
│
feed result back, repeat
(up to max_iterations)


---

# 🧩 Core Components

## Runnable
The base abstraction of EduChain. Every component inherits from `Runnable` and implements `invoke()`, with optional `stream()` and `ainvoke()` overrides.

## PromptTemplate
Formats prompts by replacing template variables with user input.

## ChatModel
Wraps any LangChain-compatible chat model. Supports plain string prompts *and* full message-list conversations (needed for multi-turn tool calling). Optionally accepts `tools=[...]` to enable tool calling.

## OutputParser
Transforms raw model outputs into clean Python objects — `StringOutputParser` and `JsonOutputParser`.

## RunnableSequence
Executes multiple runnables sequentially via the `|` operator, with smart streaming support that correctly detects which step is the actual streaming source vs. a downstream transformer.

## RunnableParallel
Executes multiple independent chains — concurrently via threads (`invoke`) or `asyncio.gather` (`ainvoke`).

## Tool
Wraps a plain Python function as something an LLM can call — auto-generates the JSON schema from type hints and docstrings, no hand-written schema required.

## InMemoryVectorStore
Stores text + embeddings, retrieves the most relevant chunks for a query using hand-written cosine similarity search.

## RAGChain
Combines a vector store with an existing chain — retrieves relevant context, injects it into the prompt, generates a grounded answer.

## Agent
Wraps a tool-bound `ChatModel` in a reasoning loop — decides which tool to call, executes it, feeds the result back, and repeats until it reaches a final answer (bounded by `max_iterations` as a safety limit).

## CallbackHandler
Pluggable observability hooks (`on_step_start`, `on_step_end`, `on_error`, etc.) — swap in custom logging, timing, or monitoring logic without touching core chain code.

---

# 📚 Examples & Demos

demo_all_features.py → core primitives working together
demo_async.py → async chains + speed comparison
demo_callbacks.py → built-in + custom callback handlers
demo_tools.py → tool detection, execution, full round trip
demo_vectorstore.py → semantic search across mixed topics
demo_rag.py → retrieval-augmented generation, grounded answers
demo_agent.py → full agentic loop, including RAG-as-a-tool


Run any demo directly:

```bash
python demo_agent.py
```

---

# 🧪 Tests

Run the full test suite (36 tests — happy paths, validation, and full-stack integration):

```bash
python test_all_features.py
```

---

# 🎯 Learning Objectives

EduChain was built to understand the engineering principles behind modern LLM frameworks — not just use them.

Topics covered include:

- Object-Oriented Programming & Abstract Base Classes
- Operator Overloading & Method Chaining
- Software Architecture & Dependency Injection
- Sequential and Parallel Pipelines (threads + asyncio)
- Streaming (source vs. transformer detection)
- Observer Pattern (Callback System)
- Function Calling / Tool Use (JSON schema generation from type hints)
- Vector Embeddings & Cosine Similarity (implemented by hand)
- Retrieval-Augmented Generation
- Agentic Reasoning Loops & Safety Limits (`max_iterations`)

---

## 🛣 Roadmap

### ✅ v1.0 — Complete

- [x] Runnable, PromptTemplate, ChatModel, OutputParser
- [x] RunnableSequence, RunnableParallel, RunnablePassthrough, RunnableLambda
- [x] Chat History / Memory
- [x] Streaming
- [x] Async Support
- [x] Callback System
- [x] Tool Calling
- [x] Vector Store
- [x] RAG Pipeline
- [x] Agents

### 💡 Future Directions (not committed)

- [ ] Persistent storage for memory & vector store (swap in-memory for a real DB)
- [ ] Pluggable vector store backends (FAISS/Chroma) behind the same interface
- [ ] Multi-agent coordination
- [ ] Streaming support inside the Agent loop
- [ ] Batch processing (`.batch()`)

See `ROADMAP.md` for full build history and design decisions.

---

# 📖 Documentation

Additional documentation is available in the `docs/` directory and `ROADMAP.md`.

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome. If you find a bug or have an idea for improving EduChain, feel free to open an issue or submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

EduChain is inspired by the architecture and design principles of LangChain. This project is an educational reimplementation created to better understand how modern LLM frameworks are designed. It is not affiliated with or endorsed by the LangChain project.

---

# 👨‍💻 Author

**Deepak Kumar Singh**
[GitHub](https://github.com/CodeWithDks)

If you found this project helpful, consider giving it a ⭐ on GitHub.