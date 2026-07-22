"""
parallel.py
Runs multiple Runnable objects in parallel.

Example:

Input
  │
  ├──────── Summary Chain
  │
  ├──────── Joke Chain
  │
  └──────── Interview Chain

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

    def __init__(self, verbose=False, **runnables):
        if len(runnables) == 0:
            raise ValueError("At least one runnable is required.")

        for name, runnable in runnables.items():
            if not isinstance(runnable, Runnable):
                raise TypeError(
                    f"'{name}' is not a Runnable. "
                    "Every branch passed to RunnableParallel must implement invoke()."
                )

        self.runnables = runnables
        self.verbose = verbose

    def invoke(self, input_data):
        if self.verbose:
            print("=" * 60)
            print("EduChain — Running branches in parallel")
            print("=" * 60)

        results = {}

        with ThreadPoolExecutor() as executor:
            futures = {}

            for name, runnable in self.runnables.items():
                if self.verbose:
                    print(f"→ Submitting '{name}'...")
                futures[name] = executor.submit(runnable.invoke, input_data)

            for name, future in futures.items():
                results[name] = future.result()
                if self.verbose:
                    print(f"'{name}' completed")

        if self.verbose:
            print("=" * 60)
            print("All branches finished\n")
            for name, output in results.items():
                print(f"{name.upper()}")
                print("-" * 40)
                print(output)
                print()

        return results

    
    async def ainvoke(self, input_data):
        """
        Runs every branch concurrently using asyncio.gather(),
        instead of the thread-based approach in invoke().
        This is genuinely faster for I/O-bound work like LLM calls,
        since branches don't block each other while waiting on the network.
        """

        import asyncio

        names = list(self.runnables.keys())
        coros = [self.runnables[name].ainvoke(input_data) for name in names]

        results_list = await asyncio.gather(*coros)

        return dict(zip(names, results_list))

    

    def stream(self, input_data):
        yield self.invoke(input_data)