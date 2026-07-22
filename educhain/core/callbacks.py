"""
callbacks.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the CallbackHandler system.

Responsibility:
---------------
Give users visibility into what's happening inside a chain
without hardcoding print statements everywhere. Subclass
CallbackHandler and override only the hooks you care about —
log to a file, send to a dashboard, count tokens, whatever.

Example:

class MyLogger(CallbackHandler):
    def on_step_start(self, step_name, input_data):
        print(f"Starting {step_name}")

chain = RunnableSequence(prompt, model, parser, callbacks=[MyLogger()])
"""


class CallbackHandler:
    """
    Base class for all callback handlers.

    Every hook does nothing by default — subclass this and
    override only what you actually need. This is intentional:
    a handler that only cares about errors shouldn't be forced
    to implement on_step_start/on_step_end too.
    """

    def on_step_start(self, step_name, input_data):
        """Called right before a step runs."""
        pass

    def on_step_end(self, step_name, output_data):
        """Called right after a step finishes successfully."""
        pass

    def on_error(self, step_name, error):
        """Called if a step raises an exception."""
        pass

    def on_chain_start(self, chain_name, input_data):
        """Called once, before the very first step in the chain."""
        pass

    def on_chain_end(self, chain_name, output_data):
        """Called once, after the very last step in the chain."""
        pass


class PrintCallbackHandler(CallbackHandler):
    """
    A ready-to-use handler that prints progress to the console.

    This is basically your old verbose=True logic, but now it's
    reusable and swappable instead of hardcoded inside
    RunnableSequence/RunnableParallel.
    """

    def on_chain_start(self, chain_name, input_data):
        print("=" * 60)
        print(f"✨ EduChain — starting {chain_name}")
        print("=" * 60)

    def on_step_start(self, step_name, input_data):
        print(f"[Running] {step_name}...")

    def on_step_end(self, step_name, output_data):
        print(f"[Done] {step_name} ✔")

    def on_error(self, step_name, error):
        print(f"[Error] {step_name} failed: {error}")

    def on_chain_end(self, chain_name, output_data):
        print("=" * 60)
        print(f"Your answer is ready ❤️  — {chain_name} finished")
        print("=" * 60)