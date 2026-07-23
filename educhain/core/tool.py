"""
tool.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the Tool class.

Responsibility:
---------------
Wrap a plain Python function so an LLM can understand what
it does and call it — automatically, based on the conversation.

Example:

def get_weather(city: str) -> str:
    "Get the current weather for a given city."
    return f"It's sunny in {city}"

weather_tool = Tool(get_weather)

The LLM sees the function name, its docstring, and its
parameter names/types — and decides on its own whether and
when to call it. We just build the schema, LangChain's
bind_tools() handles the actual LLM communication.
"""

import inspect
from typing import get_type_hints


# maps Python types to JSON schema types, since that's the
# format LLM tool-calling APIs expect
PYTHON_TO_JSON_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class Tool:
    """
    Wraps a plain Python function as an LLM-callable tool.

    Auto-generates the JSON schema from the function's type hints,
    so you don't have to hand-write one every time.
    """

    def __init__(self, func, name=None, description=None):

        if not callable(func):
            raise TypeError(
                f"Tool expects a function, but got {type(func).__name__}."
            )

        self.func = func
        self.name = name or func.__name__

        # fall back to the docstring if no explicit description given —
        # the LLM NEEDS a description to know when to use this tool,
        # so we fail loudly if there's genuinely nothing to use
        self.description = description or inspect.getdoc(func)

        if not self.description:
            raise ValueError(
                f"Tool '{self.name}' has no description. "
                "Either add a docstring to your function, or pass "
                "description='...' explicitly. The LLM needs this "
                "to know when to use the tool."
            )

        self.schema = self._build_schema()

    def _build_schema(self):
        """
        Builds a JSON-schema-style function definition from the
        wrapped function's signature and type hints. This is the
        format most LLM tool-calling APIs (OpenAI, Anthropic, Groq)
        expect under the hood.
        """

        signature = inspect.signature(self.func)
        hints = get_type_hints(self.func)

        properties = {}
        required = []

        for param_name, param in signature.parameters.items():

            param_type = hints.get(param_name, str)  # default to string if unhinted
            json_type = PYTHON_TO_JSON_TYPE.get(param_type, "string")

            properties[param_name] = {"type": json_type}

            # if the parameter has no default value, it's required
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def run(self, **kwargs):
        """
        Actually executes the wrapped function with the arguments
        the LLM decided to pass. Separate from invoke() on purpose —
        Tool isn't a Runnable, it doesn't fit the single-input
        pipeline model, since it takes named arguments, not one
        piped value.
        """

        try:
            return self.func(**kwargs)

        except Exception as e:
            raise RuntimeError(
                f"Tool '{self.name}' failed while running: {e}"
            )

    def __repr__(self):
        return f"Tool(name='{self.name}')"