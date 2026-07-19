"""
runnable.py

This file contains the base Runnable class.

Every component in EduChain
(PromptTemplate, ChatModel, OutputParser, etc.)
inherits from this class.

Why?

Because every component should expose the same
public interface:

    invoke(input)

This is the core idea behind LangChain's Runnable architecture,
and it's what lets us chain totally different components together
using the same syntax.
"""

from abc import ABC, abstractmethod


class Runnable(ABC):
    """
    Base abstract class for all runnable components.

    Anything that inherits from this MUST implement invoke().
    That's the one rule that makes the whole chaining system work.
    """

    @abstractmethod
    def invoke(self, input_data):
        """
        Execute the runnable.

        Every child class defines its own version of this —
        PromptTemplate formats a dict into a string,
        ChatModel sends a string to the LLM,
        OutputParser converts the AIMessage into something usable.
        """
        pass

    def __or__(self, other):
        """
        Enables the pipe syntax:

            runnable1 | runnable2

        Under the hood this just wraps both runnables
        into a RunnableSequence, so calling .invoke() on
        the result runs them one after another, passing
        the output of one as the input to the next.
        """

        # imported here (not at the top) to avoid a circular import,
        # since sequence.py also imports from this file
        from educhain.core.sequence import RunnableSequence

        return RunnableSequence(self, other)