"""
history.py

Contains the MessageHistory class.

Responsibility:
---------------
Store the back-and-forth of a conversation so a chain
can "remember" what was said earlier.

Without this, every invoke() call is stateless —
the model has no idea what you asked it two messages ago.

This class just keeps a running list of HumanMessage /
AIMessage objects and knows how to add to it.
"""

from langchain_core.messages import HumanMessage, AIMessage


class MessageHistory:
    """
    A simple in-memory store for conversation turns.

    Not persisted anywhere — once the program ends,
    the history is gone. Good enough for learning/testing.
    A real app would swap this for a DB-backed version later.
    """

    def __init__(self):
        self.messages = []

    def add_user_message(self, content):

        if not isinstance(content, str):
            raise TypeError(
                f"add_user_message expects a string, but got {type(content).__name__}."
            )

        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content):

        if not isinstance(content, str):
            raise TypeError(
                f"add_ai_message expects a string, but got {type(content).__name__}."
            )

        self.messages.append(AIMessage(content=content))

    def clear(self):
        self.messages = []

    def __repr__(self):
        return f"MessageHistory({len(self.messages)} messages)"