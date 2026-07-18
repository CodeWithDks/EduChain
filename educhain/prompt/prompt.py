"""
prompt.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Contains the PromptTemplate class.
Its responsibility is simple:

Dictionary
      ↓
Formatted Prompt (string)
"""

from educhain.core.runnable import Runnable

class PromptTemplate(Runnable):

    def __init__(self, template, input_variables):

        if not isinstance(template, str):
            raise TypeError(
                "template must be a string. "
                "Example: PromptTemplate('Hello {name}', ['name'])"
            )

        if not isinstance(input_variables, list):
            raise TypeError(
                "input_variables must be a list of variable names, e.g. ['name', 'topic']."
            )

        if len(input_variables) == 0:
            raise ValueError(
                "input_variables cannot be empty. "
                "Add at least one variable that appears in your template."
            )

        self.template = template
        self.input_variables = input_variables

    def invoke(self, input_data):

        if not isinstance(input_data, dict):
            raise TypeError(
                f"PromptTemplate expects a dict, but got {type(input_data).__name__}. "
                "Pass values like {'name': 'Deepak'}."
            )

        # ---- Check for missing variables ----
        missing = []

        for variable in self.input_variables:

            if variable not in input_data:
                missing.append(variable)

        if missing:
            raise ValueError(
                f"Missing variables: {missing}. "
                f"This template needs: {self.input_variables}"
            )

        # ---- Check for extra/unexpected variables ----
        extra = set(input_data.keys()) - set(self.input_variables)

        if extra:
            raise ValueError(
                f"Unexpected variables: {extra}. "
                f"This template only accepts: {self.input_variables}"
            )

        # ---- Format and return the final prompt string ----
        return self.template.format(**input_data)