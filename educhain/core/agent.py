"""
agent.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the Agent class.

Responsibility:
---------------
Let an LLM take multiple steps to answer a question — deciding
on its own which tools to call, running them, looking at the
results, and deciding what to do next — until it has a final
answer.

This is NOT a new mechanism. It's a loop built entirely from
things you've already built:

    ChatModel (with tools bound)
    + has_tool_calls() / run_tool_calls()
    + message-list support (just added)
    + CallbackHandler (for visibility into each step)

Flow:

question
   |
   v
[LOOP, up to max_iterations]
   |
   ask the LLM (with full conversation so far)
   |
   did it ask for a tool?
   |         \
   no          yes
   |            |
   done      run the tool(s), add results to conversation
                |
                loop again
   |
final answer (string)
"""

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from educhain.core.runnable import Runnable


class Agent(Runnable):
    """
    Wraps a tool-bound ChatModel in a decision loop, so it can
    take multiple steps — not just one shot — to answer a question.
    """

    def __init__(self, model, max_iterations=5, callbacks=None):

        if not hasattr(model, "has_tool_calls") or not hasattr(model, "run_tool_calls"):
            raise TypeError(
                "Agent expects a ChatModel with tools bound. "
                "Example: Agent(model=ChatModel(tools=[my_tool]))"
            )

        if not model.tools:
            raise ValueError(
                "Agent's model has no tools bound. An agent with zero tools "
                "can't take any actions — pass tools=[...] when creating the ChatModel."
            )

        self.model = model
        self.max_iterations = max_iterations
        self.callbacks = callbacks or []

    def invoke(self, question):

        if not isinstance(question, str):
            raise TypeError(
                f"Agent expects a string question, but got {type(question).__name__}."
            )

        if question.strip() == "":
            raise ValueError(
                "Question cannot be empty."
            )

        self._fire("on_chain_start", "Agent", question)

        conversation = [HumanMessage(content=question)]

        for step in range(1, self.max_iterations + 1):

            self._fire("on_step_start", f"Agent iteration {step}", conversation)

            response = self.model.invoke(conversation)
            conversation.append(response)

            # ---- No tool call — the LLM has a final answer, stop here ----
            if not self.model.has_tool_calls(response):
                self._fire("on_step_end", f"Agent iteration {step}", response.content)
                self._fire("on_chain_end", "Agent", response.content)
                return response.content

            # ---- Tool call requested — run it, add result, loop again ----
            tool_results = self.model.run_tool_calls(response)

            for call, result in zip(response.tool_calls, tool_results):
                conversation.append(
                    ToolMessage(
                        content=str(result["result"]),
                        tool_call_id=call["id"],
                    )
                )

            self._fire("on_step_end", f"Agent iteration {step}", tool_results)

        # ---- Safety net — ran out of iterations without a final answer ----
        self._fire("on_error", "Agent", f"Exceeded max_iterations ({self.max_iterations})")
        raise RuntimeError(
            f"Agent did not reach a final answer within {self.max_iterations} iterations. "
            "The LLM may be stuck in a tool-calling loop. Consider raising max_iterations, "
            "or check if your tool is returning something the LLM can't use to finish."
        )

    def __repr__(self):
        return f"Agent(tools={list(self.model.tools.keys())}, max_iterations={self.max_iterations})"