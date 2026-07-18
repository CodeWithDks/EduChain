# 🚀 MiniLangChain

> **Learn LangChain by Building It Yourself**

MiniLangChain is a lightweight educational framework inspired by LangChain. The goal of this project is **not to replace LangChain**, but to understand **how LangChain works internally** by implementing its core building blocks from scratch.

Instead of treating LangChain as a black box, this project recreates the most important abstractions such as **Runnable**, **PromptTemplate**, **ChatModel**, **OutputParser**, **RunnableSequence**, and **RunnableParallel** using clean and beginner-friendly Python code.

---

# 📖 Why This Project?

Many developers start using LangChain like this:

```python
prompt | model | parser
```

Everything works.

But have you ever wondered...

* How does `PromptTemplate` replace variables?
* How does the `|` operator work?
* Why does every component have an `invoke()` method?
* How are multiple chains executed in parallel?
* Why does LangChain use Runnables?

Instead of reading thousands of lines of framework code, I decided to rebuild the core concepts myself.

This repository is the result.

---

# 🎯 Goals

The primary goals of MiniLangChain are:

* Learn object-oriented design
* Understand framework architecture
* Understand abstraction using Abstract Base Classes (ABC)
* Learn operator overloading (`|`)
* Understand prompt formatting
* Build a simple LLM wrapper
* Learn sequential execution
* Learn parallel execution
* Understand how LangChain pipelines work internally

---

# ✨ Features

* ✅ Custom Runnable abstraction
* ✅ Prompt Template implementation
* ✅ Chat Model wrapper
* ✅ Output Parser
* ✅ RunnableSequence
* ✅ RunnableParallel
* ✅ Input validation
* ✅ Type checking
* ✅ Modular architecture
* ✅ Beginner-friendly implementation

---

# 📂 Project Structure

```
mini_langchain/

│
├── runnable.py
│
├── prompt.py
│
├── llm.py
│
├── parser.py
│
├── sequence.py
│
├── parallel.py
│
└── main.py
```

---

# 🏗 Architecture

```
                  Runnable (Abstract Base Class)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 PromptTemplate      ChatModel         OutputParser
        │
        │
        ▼
 RunnableSequence
        │
        ▼
 RunnableParallel
```

Everything in MiniLangChain is a **Runnable**.

Every Runnable exposes one common interface:

```python
invoke(input)
```

Because every component behaves the same way, they can easily be combined together.

---

# 🧩 Core Components

## 1. Runnable

`Runnable` is the foundation of the entire framework.

It is an Abstract Base Class (ABC).

Every component inherits from it.

Responsibilities:

* Define the common interface
* Force child classes to implement `invoke()`
* Support chaining using the `|` operator

Example:

```python
class Runnable(ABC):

    @abstractmethod
    def invoke(self, input):
        pass
```

---

## 2. PromptTemplate

Responsibility:

Convert

```python
{
    "topic": "Artificial Intelligence"
}
```

into

```text
Explain Artificial Intelligence.
```

Flow:

```
Dictionary
      │
      ▼
PromptTemplate
      │
      ▼
Formatted Prompt
```

---

## 3. ChatModel

The ChatModel is a thin wrapper around an LLM.

Responsibilities:

* Validate prompt
* Call the language model
* Return AIMessage

Flow:

```
Prompt
   │
   ▼
ChatModel
   │
   ▼
AIMessage
```

---

## 4. OutputParser

Large Language Models usually return structured objects.

For example:

```
AIMessage
├── content
├── metadata
├── usage
└── id
```

Most applications only need

```
content
```

The OutputParser extracts the useful information.

Flow:

```
AIMessage
     │
     ▼
OutputParser
     │
     ▼
String
```

---

## 5. RunnableSequence

RunnableSequence executes multiple Runnables one after another.

Example:

```
Dictionary
     │
     ▼
PromptTemplate
     │
     ▼
ChatModel
     │
     ▼
OutputParser
     │
     ▼
Final Response
```

Instead of manually calling every component:

```python
formatted = prompt.invoke(data)
response = model.invoke(formatted)
answer = parser.invoke(response)
```

you simply write:

```python
chain = prompt | model | parser

response = chain.invoke(data)
```

---

## 6. RunnableParallel

RunnableParallel executes multiple Runnables simultaneously.

Example:

```
                 Input
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 Summary       Joke       Interview
   Chain        Chain        Chain
      │            │            │
      └────────────┼────────────┘
                   ▼
            Combined Results
```

Output:

```python
{
    "summary": "...",
    "joke": "...",
    "interview": "..."
}
```

---

# 🔥 Execution Flow

```
User Input
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

# 🚀 Example

```python
from prompt import PromptTemplate
from llm import ChatModel
from parser import StringOutputParser

prompt = PromptTemplate(
    template="Explain {topic} in {language}.",
    input_variables=["topic", "language"]
)

llm = ChatModel()

parser = StringOutputParser()

chain = prompt | llm | parser

response = chain.invoke({
    "topic": "Artificial Intelligence",
    "language": "English"
})

print(response)
```

Output

```
Artificial Intelligence (AI) is a branch of computer science that focuses on building systems capable of performing tasks that normally require human intelligence.
```

---

# 🛡 Input Validation

MiniLangChain performs validation before execution.

Examples:

Missing Variables

```python
prompt.invoke({})
```

Raises

```
ValueError
```

Wrong Input Type

```python
prompt.invoke([])
```

Raises

```
TypeError
```

Unexpected Variables

```python
{
    "topic":"AI",
    "age":20
}
```

Raises

```
ValueError
```

---

# 📚 What I Learned

While building this project I learned:

* Abstract Base Classes
* Object-Oriented Design
* Framework Design
* Dependency Injection
* Operator Overloading
* Method Chaining
* ThreadPoolExecutor
* Sequential Pipelines
* Parallel Pipelines
* Prompt Engineering
* LLM Wrappers
* Software Architecture

---

# 🚧 Roadmap

Future improvements:

* [ ] Chat History
* [ ] Memory
* [ ] Streaming Responses
* [ ] Batch Processing
* [ ] Retry Logic
* [ ] Callback Manager
* [ ] Logging System
* [ ] Tool Calling
* [ ] Agents
* [ ] Retrieval
* [ ] Vector Database Integration
* [ ] RAG Pipeline

---

# 🤝 Contributing

Contributions, improvements, bug reports, and suggestions are always welcome.

If you'd like to improve MiniLangChain, feel free to fork the repository and submit a Pull Request.

---

# 📜 License

This project is released under the MIT License.

---

# ⭐ Acknowledgements

This project is inspired by the design principles of the LangChain framework.

It is an educational reimplementation created to understand the internal architecture and concepts behind LangChain. It is **not affiliated with or a replacement for LangChain**.

---

# 👨‍💻 Author

**Deepak Singh**

If you found this project helpful, consider giving it a ⭐ on GitHub.

Happy Learning! 🚀
