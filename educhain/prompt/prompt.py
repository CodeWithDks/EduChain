"""
prompt.py
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
                "template must be a string."
            )

        if not isinstance(input_variables, list):
            raise TypeError(
                "input_variables must be a list."
            )

        if len(input_variables) == 0:
            raise ValueError(
                "input_variables cannot be empty."
            )

        self.template = template
        self.input_variables = input_variables

    def invoke(self, input_data):

        if not isinstance(input_data, dict):
            raise TypeError(
   
                "Input must be a dictionary."
            )

        # Missing Variables 
        missing = []

        for variable in self.input_variables:

            if variable not in input_data:
                missing.append(variable)

        if missing:
            raise ValueError(
                f"Missing variables: {missing}"
            )

        # Extra Variables 

        extra = set(input_data.keys()) - set(self.input_variables)

        if extra:
            raise ValueError(
                f"Unexpected variables: {extra}"
            )

        # Format Prompt

        return self.template.format(**input_data)