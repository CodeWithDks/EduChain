"""
parser.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

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

    # tells RunnableSequence.stream() that this step consumes a
    # generator of chunks rather than being a streaming source itself —
    # without this flag, RunnableSequence assumes THIS parser is the
    # source and tries to call model logic on it, which breaks
    IS_STREAM_TRANSFORMER = True

    def invoke(self, input_data):

        if not isinstance(input_data, AIMessage):
            raise TypeError(
                f"StringOutputParser expects an AIMessage, but got {type(input_data).__name__}. "
                "This parser should be placed right after a ChatModel in the chain."
            )

        return input_data.content

    def stream(self, input_data):
        """
        input_data here is a generator of AIMessageChunks coming from
        ChatModel.stream() (or another transformer before this one).
        Yields just the text content of each chunk.
        """

        for chunk in input_data:

            if not hasattr(chunk, "content"):
                raise TypeError(
                    "StringOutputParser.stream() expected chunks with a "
                    "'.content' attribute. Are you streaming from a ChatModel?"
                )

            yield chunk.content


class JsonOutputParser(OutputParser):
    """
    Converts JSON string
    into Python dictionary.

    Note: intentionally does NOT support streaming (no IS_STREAM_TRANSFORMER
    flag, no stream() override). Partial JSON can't be reliably parsed
    chunk-by-chunk, so this parser stays invoke-only. Use StringOutputParser
    if you need streaming.
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