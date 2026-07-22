"""
sequence.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

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

    def __init__(self, *steps, verbose=False, callbacks=None):

        if len(steps) < 2:
            raise ValueError(
                "RunnableSequence requires at least two runnables."
            )

        for step in steps:
            if not isinstance(step, Runnable):
                raise TypeError(
                    f"{step} is not a Runnable. "
                    "Every step in the chain must implement invoke()."
                )

        self.steps = steps
        self.verbose = verbose

        # if verbose=True and no callbacks given, fall back to
        # PrintCallbackHandler so old verbose=True code keeps working
        if callbacks is None and verbose:
            from educhain.core.callbacks import PrintCallbackHandler
            callbacks = [PrintCallbackHandler()]

        self.callbacks = callbacks or []

    def invoke(self, input_data):

        self._fire("on_chain_start", "RunnableSequence", input_data)

        result = input_data

        for step in self.steps:
            step_name = step.__class__.__name__

            self._fire("on_step_start", step_name, result)

            try:
                result = step.invoke(result)
            except Exception as e:
                self._fire("on_error", step_name, e)
                raise

            self._fire("on_step_end", step_name, result)

        self._fire("on_chain_end", "RunnableSequence", result)

        return result
    
    async def ainvoke(self, input_data):
        """
        Async version of invoke() — awaits each step in order.
        Doesn't use the base class fallback because that would
        silently call sync invoke() on every step, defeating
        the whole point of going async.
        """

        self._print_banner("EduChain — built by Deepak Singh (async)")

        result = input_data

        for i, step in enumerate(self.steps, start=1):
            if self.verbose:
                print(f"[Step {i}] Running {step.__class__.__name__} (async)...")

            result = await step.ainvoke(result)

            if self.verbose:
                print(f"[Step {i}] Done ✔\n")

        return result

    def stream(self, input_data):
        """
        Runs steps normally (invoke) up until the streaming SOURCE step
        (usually ChatModel) — then starts a generator there and pipes it
        through every remaining step's stream(), however many there are.

        A step is treated as a "transformer" (consumes a generator instead
        of starting one) if it sets IS_STREAM_TRANSFORMER = True. This lets
        us walk backwards from the end and find the real source step,
        instead of blindly assuming the last step is always the one
        that streams.
        """

        if self.verbose:
            print("=" * 60)
            print("✨ EduChain — streaming response")
            print("=" * 60)

        steps = self.steps

        # walk backwards from the end, skipping any trailing steps that
        # are transformers (they consume a generator, they don't start one)
        split_index = len(steps) - 1
        while split_index > 0 and getattr(steps[split_index], "IS_STREAM_TRANSFORMER", False):
            split_index -= 1

        # run everything before the streaming source normally
        result = input_data
        for step in steps[:split_index]:
            result = step.invoke(result)

        # start the stream at the source step (e.g. ChatModel)
        source_step = steps[split_index]
        chunks = source_step.stream(result)

        # pipe the generator through every remaining transformer step
        for step in steps[split_index + 1:]:
            chunks = step.stream(chunks)

        yield from chunks

    def __or__(self, other):

        if not isinstance(other, Runnable):
            raise TypeError(
                f"{other} is not a Runnable. "
                "Every step in the chain must implement invoke()."
            )

        # if we're chaining another sequence, just merge the steps
        # instead of nesting sequences inside sequences
        if isinstance(other, RunnableSequence):
            return RunnableSequence(*self.steps, *other.steps)

        return RunnableSequence(*self.steps, other)

    def __repr__(self):
        chain = " | ".join(step.__class__.__name__ for step in self.steps)
        return f"RunnableSequence({chain})"