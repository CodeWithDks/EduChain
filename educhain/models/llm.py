"""
llm.py

This file contains the ChatModel class.

Responsibility:
---------------
Receive a formatted prompt (string),
send it to the LLM,
and return the generated response.
"""

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from educhain.core.runnable import Runnable

load_dotenv()


class ChatModel(Runnable):
    """
    Wrapper around a LangChain chat model.

    Any chat model that supports .invoke()
    can be passed here.
    
    I am using ChatOpenAI() as the default model.
    Just for testing purpose.
    """

    def __init__(self, model=None):

        if model is None:
            model = ChatOpenAI()

        self.model = model

    def invoke(self, input_data):

        # Validation

        if not isinstance(input_data, str):
            raise TypeError(
                "ChatModel expects a string prompt."
            )

        if input_data.strip() == "":
            raise ValueError(
                "Prompt cannot be empty."
            )
        # Send prompt to model

        response = self.model.invoke(input_data)

        # AIMessage object
        return response