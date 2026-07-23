"""
llm.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

This file contains the ChatModel class.

Responsibility:
---------------
Receive a formatted prompt (string),
send it to the LLM,
and return the generated response.

Also supports Tool Calling — if tools are bound, the LLM can
choose to call one instead of answering directly.
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

    def __init__(self, model=None, max_tokens=None, tools=None):

        # if user didn't pass a model, fall back to default ChatOpenAI
        if model is None:
            model = ChatOpenAI(max_tokens=max_tokens)

        self.max_tokens = max_tokens

        # store tools by name, so we can look them up later when
        # the LLM asks to call one by name
        self.tools = {tool.name: tool for tool in (tools or [])}

        # if tools were given, bind their schemas to the model so
        # the LLM actually knows they exist and can choose to use them
        if self.tools:
            schemas = [tool.schema for tool in self.tools.values()]
            model = model.bind_tools(schemas, tool_choice="auto")
        self.model = model

    def invoke(self, input_data):

        # ---- Validation ----
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

        # returns an AIMessage object (has .content, .response_metadata,
        # and — if tools are bound — .tool_calls when the LLM wants to act)
        return response

    def has_tool_calls(self, response):
        """
        Checks whether a model response is asking to call a tool,
        instead of just answering with text. Use this after invoke()
        when tools are bound, to decide what to do next.
        """
        return bool(getattr(response, "tool_calls", None))

    def run_tool_calls(self, response):
        """
        Executes every tool call requested in the response, using
        the actual Tool objects bound to this ChatModel.

        Returns a list of dicts: [{"name": ..., "args": ..., "result": ...}]
        so you can see exactly what ran and what came back.
        """

        if not self.has_tool_calls(response):
            return []

        results = []

        for call in response.tool_calls:

            tool_name = call["name"]
            tool_args = call["args"]

            tool = self.tools.get(tool_name)

            if tool is None:
                raise ValueError(
                    f"LLM tried to call '{tool_name}', but no tool with "
                    f"that name is bound to this ChatModel. "
                    f"Available tools: {list(self.tools.keys())}"
                )

            output = tool.run(**tool_args)

            results.append({
                "name": tool_name,
                "args": tool_args,
                "result": output,
            })

        return results

    def stream(self, input_data):

        # ---- Validation (same rules as invoke) ----
        if not isinstance(input_data, str):
            raise TypeError(
                f"ChatModel expects a string prompt, but got {type(input_data).__name__}. "
                "Did you forget to call .format() on your PromptTemplate?"
            )

        if input_data.strip() == "":
            raise ValueError(
                "Prompt cannot be empty. Please pass some text before calling invoke()."
            )

        # ---- Stream chunks from the model as they arrive ----
        for chunk in self.model.stream(input_data):
            yield chunk

    async def ainvoke(self, input_data):

        # ---- Validation (same rules as invoke) ----
        if not isinstance(input_data, str):
            raise TypeError(
                f"ChatModel expects a string prompt, but got {type(input_data).__name__}. "
                "Did you forget to call .format() on your PromptTemplate?"
            )

        if input_data.strip() == "":
            raise ValueError(
                "Prompt cannot be empty. Please pass some text before calling invoke()."
            )

        # ---- Send prompt to model asynchronously ----
        response = await self.model.ainvoke(input_data)
        return response