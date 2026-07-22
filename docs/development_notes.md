# 📒 EduChain Development Notes

> A personal engineering journal documenting the process of building EduChain from scratch to understand how LangChain works internally.

---

# 📅 Day 1

**Date:** July 4, 2026

---

# 🎯 Objective

Instead of learning LangChain by simply using its APIs, I decided to rebuild its core architecture from scratch.

The objective of this project is **not** to replace LangChain, but to understand the design principles behind modern LLM frameworks.

I want to understand:

- How PromptTemplate works
- How Chat Models communicate with LLMs
- How Output Parsers transform responses
- How RunnableSequence executes components
- How RunnableParallel executes multiple chains
- Why everything inherits from Runnable

---

# 💡 Core Idea

Every component in EduChain is a **Runnable**.

Every Runnable:

- accepts one input
- performs one task
- returns one output

Because every component follows the same interface, they become composable.

Instead of remembering

```python
prompt.format()
model.predict()
parser.parse()
```

everything becomes

```python
.invoke(input)
```

This single abstraction makes the framework simple and extensible.

---

# 🏛 Architecture

```
                    Runnable
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
 PromptTemplate     ChatModel     OutputParser
        │
        ▼
 RunnableSequence
        │
        ▼
 RunnableParallel
```

---

# 📂 Components Built

## 1. Runnable

Purpose:

Provide a common interface for every component.

Responsibilities:

- Define invoke()
- Force subclasses to implement invoke()
- Support chaining using |

Concepts Learned:

- Abstract Base Classes
- @abstractmethod
- Interface Design

---

## 2. PromptTemplate

Purpose:

Convert

```python
{
    "topic": "Artificial Intelligence"
}
```

into

```
Explain Artificial Intelligence.
```

Responsibilities:

- Store prompt template
- Validate variables
- Format prompt

Validation:

- Missing variables
- Extra variables
- Wrong datatype

Output:

```
Dictionary
      │
      ▼
Formatted Prompt (String)
```

---

## 3. ChatModel

Purpose:

Wrapper around ChatOpenAI.

Responsibilities:

- Validate prompt
- Send prompt to LLM
- Return AIMessage

Initially:

I returned

```python
response.content
```

Later I realized returning the entire AIMessage object is more aligned with LangChain.

The OutputParser should decide what information to extract.

---

## 4. OutputParser

Purpose:

Convert

```
AIMessage
```

into

```
String
```

or

```
Dictionary
```

Implemented:

- StringOutputParser
- JsonOutputParser

Important Lesson:

The parser controls the final output type.

---

## 5. RunnableSequence

Purpose:

Execute multiple Runnable objects sequentially.

Flow:

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

Implemented:

```python
chain = prompt | llm | parser
```

instead of

```python
RunnableSequence(
    prompt,
    llm,
    parser
)
```

Concepts Learned:

- Method Chaining
- Operator Overloading
- __or__()

---

## 6. RunnableParallel

Purpose:

Execute multiple RunnableSequences simultaneously.

Flow:

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

Implemented using

```
ThreadPoolExecutor
```

Output:

```python
{
    "summary": "...",
    "joke": "...",
    "interview": "..."
}
```

Concepts Learned:

- Concurrency
- Futures
- ThreadPoolExecutor

---

# 🐞 Problems Faced

## Problem 1

Creating PromptTemplate.

Initially it only formatted prompts.

Later added proper validation.

---

## Problem 2

Understanding AIMessage.

I initially assumed

```python
model.invoke()
```

returns a string.

Actually it returns

```
AIMessage
```

which contains

- content
- metadata
- usage
- id
- finish reason

OutputParser extracts the useful information.

---

## Problem 3

RunnableSequence

Error:

```
RunnableSequence requires at least two runnables.
```

Cause:

I accidentally created

```
RunnableSequence(
    RunnableSequence(...)
)
```

instead of

```python
prompt | llm | parser
```

Understanding operator evaluation solved the problem.

---

## Problem 4

RunnableParallel Logging

Every thread printed to the console simultaneously.

Result:

Unreadable logs.

Lesson:

Execution and logging should be separated.

---

## Problem 5

Console Output

Initially

AIMessage

printed like

```
content='...'
metadata={...}
usage={...}
id='...'
```

Too noisy.

Solution:

Display only

```
response.content
```

for readability.

---

# 📚 Python Concepts Learned

- Abstract Base Classes
- Object-Oriented Programming
- Method Overriding
- Operator Overloading
- Dependency Injection
- ThreadPoolExecutor
- Polymorphism
- Method Chaining
- Software Architecture

---

# 🏗 Design Principles Learned

## Single Responsibility Principle

PromptTemplate

↓

Create prompts only.

---

ChatModel

↓

Call LLM only.

---

OutputParser

↓

Parse output only.

---

RunnableSequence

↓

Coordinate execution only.

---

# ❌ Mistakes Made

- Created ChatOpenAI inside invoke()
- Returned string too early
- Printed entire AIMessage
- Mixed logging with execution
- Used "Dummy" naming
- Misspelled __init__()
- Executed testing code during imports

---

# 💭 Biggest Realization

LangChain is not "magic."

It is a collection of small reusable components connected through one common interface:

```
Runnable
```

Every component performs one responsibility.

Because every component follows the same interface, they can be composed into larger pipelines.

---

# 🚀 Roadmap

## Core

- [x] Runnable
- [x] PromptTemplate
- [x] ChatModel
- [x] OutputParser
- [x] RunnableSequence
- [x] RunnableParallel
- [x] Chat History
- [x] Memory

---

## Next Components

- [ ] Console Logger
- [ ] Streaming
- [ ] Batch Processing
- [ ] Callback Manager
- [ ] Tools
- [ ] Agents
- [ ] Retriever
- [ ] Vector Store
- [ ] RAG
- [ ] Async Support

---

# 🎯 Final Takeaway

The biggest lesson from Day 1 is that powerful frameworks are built from small, well-defined abstractions.

Instead of building one large class, each component has a single responsibility.

The Runnable abstraction is the foundation that makes the entire framework composable.

Understanding this architecture makes learning LangChain significantly easier.

---

# 📌 Personal Reflection

Before this project, I knew how to *use* LangChain.

After rebuilding its core components, I understand *why* LangChain is designed the way it is.

This project has strengthened my understanding of:

- Object-Oriented Programming
- Framework Design
- Software Architecture
- Python Internals
- LLM Application Development

The goal is no longer just to learn LangChain APIs.

The goal is to think like a framework engineer.