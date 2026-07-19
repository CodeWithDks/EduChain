"""
history_runnable.py

Contains the MessageHistory class.

Responsibility:
---------------
Wraps an existing chain (PromptTemplate | ChatModel | ...)
and automatically remembers past turns, so you don't have
to manually pass conversation history yourself every time.

Example:

chain = prompt | model | parser

chat = ChatMessageHistory(chain, history_key="history")

chat.invoke({"question": "My name is Deepak"})
chat.invoke({"question": "What's my name?"})   # remembers!

Note: your PromptTemplate needs a variable (default "history")
where past messages get inserted as text.
"""

from educhain.core.runnable import Runnable
from educhain.core import MessageHistory


class ChatMessageHistory(Runnable):
    """
    Adds memory on top of any Runnable chain.

    Keeps track of the conversation and injects it into
    the input dict before passing it down to the wrapped chain.
    """

    def __init__(self, chain, history_key="history"):

        if not isinstance(chain, Runnable):
            raise TypeError(
                f"MessageHistory expects a Runnable chain, "
                f"but got {type(chain).__name__}."
            )

        self.chain = chain
        self.history_key = history_key
        self.history = MessageHistory()

    def invoke(self, input_data):

        if not isinstance(input_data, dict):
            raise TypeError(
                f"MessageHistory expects a dict input, "
                f"but got {type(input_data).__name__}."
            )

        # build a plain-text version of the conversation so far
        history_text = "\n".join(
            f"{msg.type}: {msg.content}" for msg in self.history.messages
        )

        # inject history into the input before it reaches the chain
        enriched_input = {
            **input_data,
            self.history_key: history_text
        }

        result = self.chain.invoke(enriched_input)

        # try to figure out what the user asked and what the model said,
        # so we can save both sides of the conversation automatically
        user_message = next(
            (v for k, v in input_data.items() if k != self.history_key),
            ""
        )

        ai_message = result.content if hasattr(result, "content") else str(result)

        self.history.add_user_message(str(user_message))
        self.history.add_ai_message(ai_message)

        return result