# 🚀 EduChain
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

> **An educational Python framework inspired by LangChain for learning how modern LLM frameworks work internally.**

EduChain is a lightweight framework that recreates the core building blocks of LangChain from scratch. Instead of treating LLM frameworks as a black box, EduChain focuses on understanding the design patterns, abstractions, and architecture behind them.

> **Note:** EduChain is an educational project. It is **not** intended to replace LangChain or be feature-compatible with it.

---

## ✨ Features

- ✅ Runnable Abstraction
- ✅ Prompt Templates
- ✅ Chat Model Wrapper
- ✅ Output Parsers
- ✅ RunnableSequence
- ✅ RunnableParallel
- ✅ RunnablePassthrough
- ✅ Chat History
- ✅ Memory Module
- ✅ Operator Overloading (`|`)
- ✅ Input Validation
- ✅ Modular Package Design
- 🚧 More components coming soon
---

# 📂 Project Structure

```
EduChain/
│
├── educhain/
│   ├── core/
│   ├── prompts/
│   ├── models/
│   ├── output_parsers/
│   └── __init__.py
│
├── examples/
│
├── tests/
│
├── docs/
│
├── README.md
├── requirements.txt
└── LICENSE
```

---

# 🏛 Architecture

                              Runnable
                                  │
        ┌───────────────┬─────────┴───────────┬───────────────┐
        ▼               ▼                     ▼               ▼
 PromptTemplate     ChatModel         OutputParser     RunnablePassthrough
        │
        ▼
 RunnableSequence
        │
        ▼
 RunnableParallel
        │
        ▼
 Memory & Chat History

Every component in EduChain follows a single interface:

```python
invoke(input)
```

Because every component behaves consistently, they can be composed into flexible execution pipelines.

---

# ⚡ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/EduChain.git
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

```python
from educhain import (
    PromptTemplate,
    ChatModel,
    StringOutputParser,
)

prompt = PromptTemplate(
    template="Explain {topic} in simple words.",
    input_variables=["topic"]
)

model = ChatModel()

parser = StringOutputParser()

chain = prompt | model | parser

response = chain.invoke({
    "topic": "Artificial Intelligence"
})

print(response)
```

---

# 🔄 Execution Flow

```
Dictionary
      │
      ▼
PromptTemplate
      │
      ▼
Formatted Prompt
      │
      ▼
ChatModel
      │
      ▼
AIMessage
      │
      ▼
OutputParser
      │
      ▼
Final Response
```

---

# 🧩 Core Components

## Runnable

The base abstraction of EduChain.

Every component inherits from `Runnable` and implements a common `invoke()` interface.

---

## PromptTemplate

Formats prompts by replacing template variables with user input.

Example:

```python
PromptTemplate(
    template="Explain {topic}.",
    input_variables=["topic"]
)
```

---

## ChatModel

A lightweight wrapper around an LLM that receives a prompt and returns an AI response.

---

## OutputParser

Transforms raw model outputs into clean Python objects.

Current implementation:

- StringOutputParser

---

## RunnableSequence

Executes multiple runnables sequentially.

```python
chain = prompt | model | parser
```

instead of

```python
response = parser.invoke(
    model.invoke(
        prompt.invoke(data)
    )
)
```

---

## RunnableParallel

Executes multiple independent chains concurrently using Python's `ThreadPoolExecutor`.

Example output:

```python
{
    "summary": "...",
    "joke": "...",
    "interview": "..."
}
```

---

# 📚 Examples

Example scripts are available inside the `examples/` directory.

```
examples/
│
├── chatbot.py
├── sequence_demo.py
└── parallel_demo.py
```

Run an example:

```bash
python -m examples.sequence_demo
```

---

# 🧪 Tests

Run all tests

```bash
python -m pytest
```

---

# 🎯 Learning Objectives

EduChain was built to understand the engineering principles behind modern LLM frameworks.

Topics covered include:

- Object-Oriented Programming
- Abstract Base Classes
- Operator Overloading
- Method Chaining
- Software Architecture
- Dependency Injection
- ThreadPoolExecutor
- Prompt Engineering
- Sequential Pipelines
- Parallel Pipelines

---

## 🛣 Roadmap

### Completed

- [x] Runnable
- [x] PromptTemplate
- [x] ChatModel
- [x] OutputParser
- [x] RunnableSequence
- [x] RunnableParallel
- [x] RunnablePassthrough
- [x] Chat History
- [x] Memory

### Planned

- [ ] Streaming
- [ ] Callback Manager
- [ ] Batch Processing
- [ ] Async Support
- [ ] Tool Calling
- [ ] Agents
- [ ] Retriever
- [ ] Vector Store
- [ ] RAG Pipeline

# 📖 Documentation

Additional documentation is available in the `docs/` directory.

- Development Notes
- Design Decisions
- Architecture

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

If you find a bug or have an idea for improving EduChain, feel free to open an issue or submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 🙏 Acknowledgements

EduChain is inspired by the architecture and design principles of LangChain.

This project is an educational reimplementation created to better understand how modern LLM frameworks are designed. It is not affiliated with or endorsed by the LangChain project.

---

# 👨‍💻 Author

**Deepak Kumar Singh**

If you found this project helpful, consider giving it a ⭐ on GitHub.