"""
parallel.py

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
        """

        if len(runnables) == 0:
            raise ValueError(
                "At least one runnable is required."
            )

        for name, runnable in runnables.items():

            if not isinstance(runnable, Runnable):
                raise TypeError(
                    f"{name} is not a Runnable."
                )

        self.runnables = runnables

    def invoke(self, input_data):

        print("=" * 60)
        print("🚀 Runnable Parallel Started")
        print("=" * 60)

        results = {}

        with ThreadPoolExecutor() as executor:

            futures = {}

            for name, runnable in self.runnables.items():

                print(f"Submitting '{name}'...")

                futures[name] = executor.submit(
                    runnable.invoke,
                    input_data
                )

            print()

            for name, future in futures.items():

                results[name] = future.result()

                print(f"✅ {name} completed")

        print("\n" + "=" * 60)
        print("Runnable Parallel Finished")
        print("=" * 60)

        print()

        for name, output in results.items():

            print(f"\n{name.upper()}")

            print("-" * 40)

            print(output)

        return results