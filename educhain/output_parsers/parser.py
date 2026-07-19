"""
parser.py

Contains OutputParser classes.

Responsibility:
Convert the AIMessage
into the format the user wants.
"""

from abc import ABC, abstractmethod
from langchain_core.messages import AIMessage
from educhain.core.runnable import Runnable

class OutputParser(Runnable, ABC):
    """
    Base OutputParser class.

    Every parser just needs to implement invoke(),
    which takes an AIMessage and returns whatever
    format makes sense for that parser.
    """

    @abstractmethod
    def invoke(self, input_data):
        pass

class StringOutputParser(OutputParser):
    """
    Converts AIMessage -> string

    Simplest parser, just pulls out the .content
    """

    def invoke(self, input_data):

        if not isinstance(input_data, AIMessage):
            raise TypeError(
                f"StringOutputParser expects an AIMessage, but got {type(input_data).__name__}. "
                "This parser should be placed right after a ChatModel in the chain."
            )

        return input_data.content


class JsonOutputParser(OutputParser):
    """
    Converts JSON string (from AIMessage.content)
    into a Python dictionary.

    Useful when the prompt asks the LLM to
    respond strictly in JSON format.
    """

    import json

    def invoke(self, input_data):

        if not isinstance(input_data, AIMessage):
            raise TypeError(
                f"JsonOutputParser expects an AIMessage, but got {type(input_data).__name__}. "
                "This parser should be placed right after a ChatModel in the chain."
            )

        try:

            return self.json.loads(
                input_data.content
            )

        except Exception:

            raise ValueError(
                "LLM did not return valid JSON. "
                "Tip: make your prompt explicitly ask for JSON output, "
                "e.g. 'Respond only in valid JSON format.'"
            )