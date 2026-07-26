"""
educhain/__init__.py

Top-level convenience imports. Every class below is also available
via its full module path (e.g. educhain.core.agent.Agent) — this file
just lets you skip the deep path for common use, same as LangChain's
own top-level __init__.py does.
"""

from educhain.core.runnable import Runnable
from educhain.core.sequence import RunnableSequence
from educhain.core.parallel import RunnableParallel
from educhain.core.passthrough import RunnablePassthrough
from educhain.core.lambda_runnable import RunnableLambda
from educhain.core.callbacks import CallbackHandler, PrintCallbackHandler
from educhain.core.tool import Tool
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain
from educhain.core.agent import Agent
from educhain.core.history import MessageHistory

from educhain.models.llm import ChatModel
from educhain.prompts.prompt import PromptTemplate
from educhain.output_parsers.parser import StringOutputParser, JsonOutputParser
from educhain.memory.chat_history import ChatMessageHistory

__version__ = "1.0.0"

__all__ = [
    "Runnable", "RunnableSequence", "RunnableParallel", "RunnablePassthrough",
    "RunnableLambda", "CallbackHandler", "PrintCallbackHandler", "Tool",
    "InMemoryVectorStore", "RAGChain", "Agent", "MessageHistory",
    "ChatModel", "PromptTemplate", "StringOutputParser", "JsonOutputParser",
    "ChatMessageHistory",
]