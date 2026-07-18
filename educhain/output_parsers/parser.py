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
    """

    @abstractmethod
    def invoke(self, input_data):
        pass

class StringOutputParser(OutputParser):
    """
    Converts AIMessage -> string
    """

    def invoke(self, input_data):

        if not isinstance(input_data, AIMessage):
            raise TypeError(
                "Expected AIMessage."
            )

        return input_data.content


class JsonOutputParser(OutputParser):
    """
    Converts JSON string
    into Python dictionary.
    """

    import json

    def invoke(self, input_data):

        if not isinstance(input_data, AIMessage):
            raise TypeError(
                "Expected AIMessage."
            )

        try:

            return self.json.loads(
                input_data.content
            )

        except Exception:

            raise ValueError(
                "LLM did not return valid JSON."
            )