"""
sequence.py


Contains the RunnableSequence class.

A RunnableSequence executes multiple Runnable objects
one after another.

Example:

dict
 |
PromptTemplate
 |
string
 |
ChatModel
 |
AIMessage
 |
OutputParser
 |
string
"""

from educhain.core.runnable import Runnable


class RunnableSequence(Runnable):
    """
    Runs multiple Runnable objects sequentially.

    The output of one step becomes the input of the next —
    that's the whole idea. Use verbose=True if you want to
    see what's happening at each step while debugging.
    """

    def __init__(self, *steps, verbose=False):

        if len(steps) < 2:
            raise ValueError(
                "RunnableSequence requires at least two runnables."
            )

        # Validate every step
        for step in steps:

            if not isinstance(step, Runnable):
                raise TypeError(
                    f"{step} is not a Runnable. "
                    "Every step in the chain must implement invoke()."
                )

        self.steps = steps
        self.verbose = verbose

    def invoke(self, input_data):

        if self.verbose:
            print("=" * 60)
            print("EduChain — built by Deepak Singh")
            print("=" * 60)

        result = input_data

        for i, step in enumerate(self.steps, start=1):

            if self.verbose:
                print(f"[Step {i}] Running {step.__class__.__name__}...")

            result = step.invoke(result)

            if self.verbose:
                print(f"[Step {i}] Done ✔\n")

        if self.verbose:
            print("=" * 60)
            print("Your answer is ready ❤️\n")

        return result

    def __or__(self, other):

        # if we're chaining another sequence, just merge the steps
        # instead of nesting sequences inside sequences
        if isinstance(other, RunnableSequence):
            return RunnableSequence(
                *self.steps,
                *other.steps
            )

        return RunnableSequence(
            *self.steps,
            other
        )