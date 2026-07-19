"""
passthrough.py

Contains the RunnablePassthrough class.

Responsibility:
---------------
Returns the input as-is, unchanged.

Sounds pointless on its own, but it's actually useful
inside a RunnableParallel — it lets you keep the original
input available alongside other processed branches.

Example:

RunnableParallel(
    original=RunnablePassthrough(),
    summary=summary_chain
)

# result -> {"original": <input>, "summary": <processed>}
"""

from educhain.core.runnable import Runnable


class RunnablePassthrough(Runnable):
    """
    Simply returns whatever input it receives.
    No transformation, no validation — just a pass-through.
    """

    def invoke(self, input_data):
        return input_data