"""
parallel.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Runs multiple Runnable objects in parallel.

Example:

Input
  │
  ├────────► Summary Chain
  │
  ├────────► Joke Chain
  │
  └────────► Interview Chain

Returns:

{
    "summary": "...",
    "joke": "...",
    "interview": "..."
}
"""

from concurrent.futures import ThreadPoolExecutor

from educhain.core.runnable import Runnable


class RunnableParallel(Runnable):

    def __init__(self, **runnables):
        """
        Example:

        RunnableParallel(
            summary=summary_chain,
            joke=joke_chain
        )

        Pass verbose=True on invoke() if you want to see
        each branch's progress while it runs.
        """

        if len(runnables) == 0:
            raise ValueError(
                "At least one runnable is required."
            )

        for name, runnable in runnables.items():

            if not isinstance(runnable, Runnable):
                raise TypeError(
                    f"'{name}' is not a Runnable. "
                    "Every branch passed to RunnableParallel must implement invoke()."
                )

        self.runnables = runnables

    def invoke(self, input_data, verbose=False):

        if verbose:
            print("=" * 60)
            print("🚀 EduChain — Running branches in parallel")
            print("=" * 60)

        results = {}

        with ThreadPoolExecutor() as executor:

            futures = {}

            for name, runnable in self.runnables.items():

                if verbose:
                    print(f"→ Submitting '{name}'...")

                futures[name] = executor.submit(
                    runnable.invoke,
                    input_data
                )

            for name, future in futures.items():

                results[name] = future.result()

                if verbose:
                    print(f"✅ '{name}' completed")

        if verbose:
            print("=" * 60)
            print("All branches finished\n")

            for name, output in results.items():
                print(f"{name.upper()}")
                print("-" * 40)
                print(output)
                print()

        return results