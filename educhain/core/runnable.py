"""
runnable.py

This file contains the base Runnable class.

Every component in our MiniLangChain framework
(PromptTemplate, ChatModel, OutputParser, etc.)
will inherit from this class.

Why?

Because every component should expose the same
public interface:

    invoke(input)

This is the core idea behind LangChain's Runnable architecture.
"""

from abc import ABC, abstractmethod


class Runnable(ABC):
    """
    Base abstract class for all runnable components.
    """

    @abstractmethod
    def invoke(self, input_data):
        """
        Execute the runnable.

        Every child class should have this.
        """
        pass

    def __or__(self, other):
        """
        Enables:

        runnable1 | runnable2

        implement RunnableSequence.
        """

        from educhain.core.sequence import RunnableSequence

        return RunnableSequence(self, other)