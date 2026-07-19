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

    I am using ChatOpenAI() as the default model,
    just for testing purpose. You can swap it with
    any other chat model later.
    """

    def __init__(self, model=None, max_tokens=None):

        # if user didn't pass a model, fall back to default ChatOpenAI
        # max_tokens only applies here — if a custom model is passed in,
        # it's assumed to already be configured the way the user wants
        if model is None:
            model = ChatOpenAI(max_tokens=max_tokens)

        self.model = model
        self.max_tokens = max_tokens

    def invoke(self, input_data):

        # ---- Validation ----
        # ChatModel only accepts plain string prompts.
        # This usually comes from PromptTemplate.format()

        if not isinstance(input_data, str):
            raise TypeError(
                f"ChatModel expects a string prompt, but got {type(input_data).__name__}. "
                "Did you forget to call .format() on your PromptTemplate?"
            )

        if input_data.strip() == "":
            raise ValueError(
                "Prompt cannot be empty. Please pass some text before calling invoke()."
            )

        # ---- Send prompt to model ----
        response = self.model.invoke(input_data)

        # returns an AIMessage object (has .content, .response_metadata etc.)
        return response