"""
sequence.py

Contains the RunnableSequence class.

A RunnableSequence executes multiple Runnable objects
one after another.

Example:

dict
 ↓
PromptTemplate
 ↓
string
 ↓
ChatModel
 ↓
AIMessage
 ↓
OutputParser
 ↓
string
"""

from educhain.core.runnable import Runnable


class RunnableSequence(Runnable):
    """
    Runs multiple Runnable objects sequentially.
    """

    def __init__(self, *steps,verbose=False):

        if len(steps) < 2:
            raise ValueError(
                "RunnableSequence requires at least two runnables."
            )

        # Validate every step
        for step in steps:

            if not isinstance(step, Runnable):
                raise TypeError(
                    f"{step} is not a Runnable."
                )

        self.steps = steps
        self.verbose = verbose

    def invoke(self, input_data):
        print("=" * 60)
        print("Your answer is here ❤️  with Deepak Singh\n")

        result = input_data

        for step in self.steps:
            result = step.invoke(result)

        return result


    def __or__(self, other):

        if isinstance(other, RunnableSequence):
            return RunnableSequence(
                *self.steps,
                *other.steps
            )

        return RunnableSequence(
            *self.steps,
            other
        )

    
    