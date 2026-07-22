"""
lambda_runnable.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the RunnableLambda class.

Responsibility:
---------------
Lets users drop any plain Python function into a chain
without writing a whole new Runnable subclass for it.

Example:

chain = prompt | RunnableLambda(lambda x: x.upper()) | model

Basically a thin wrapper that makes a function behave
like every other component in EduChain (i.e. it has invoke()).
"""

from educhain.core.runnable import Runnable


class RunnableLambda(Runnable):
    """
    Wraps a plain Python function so it can be used
    inside a chain, just like PromptTemplate or ChatModel.
    """

    def __init__(self, func):

        if not callable(func):
            raise TypeError(
                f"RunnableLambda expects a function, but got {type(func).__name__}. "
                "Example: RunnableLambda(lambda x: x.strip())"
            )

        self.func = func

    def invoke(self, input_data):

        try:
            return self.func(input_data)

        except Exception as e:
            raise RuntimeError(
                f"RunnableLambda failed while running your function: {e}"
            )