"""
demo_async.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Demonstrates async execution across EduChain — ainvoke() on a
basic chain, plus a direct speed comparison between
RunnableParallel's threaded invoke() and its concurrent ainvoke().

Run directly:
    python demo_async.py
"""

import asyncio
import time

from dotenv import load_dotenv

from educhain.models.llm import ChatModel
from educhain.prompts.prompt import PromptTemplate
from educhain.output_parsers.parser import StringOutputParser
from educhain.core.parallel import RunnableParallel

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# 1. Basic async chain — prompt | model | parser, using ainvoke()
# ---------------------------------------------------------------
async def demo_basic_async_chain():
    section("1. Basic Async Chain — chain.ainvoke()")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Answer in one short sentence: {question}",
        input_variables=["question"],
    )

    chain = prompt | model | parser
    answer = await chain.ainvoke({"question": "What is the capital of Japan?"})

    print(f"Q: What is the capital of Japan?\nA: {answer}")


# ---------------------------------------------------------------
# 2. Speed comparison — RunnableParallel: invoke() vs ainvoke()
# ---------------------------------------------------------------
async def demo_parallel_speed_comparison():
    section("2. Speed Test — RunnableParallel.invoke() (threads) vs ainvoke() (asyncio)")

    model = ChatModel()
    parser = StringOutputParser()

    summary_chain = (
        PromptTemplate(
            template="Summarize in one sentence: {text}",
            input_variables=["text"],
        )
        | model
        | parser
    )

    joke_chain = (
        PromptTemplate(
            template="Tell a one-line joke about: {text}",
            input_variables=["text"],
        )
        | model
        | parser
    )

    fact_chain = (
        PromptTemplate(
            template="Give one interesting fact about: {text}",
            input_variables=["text"],
        )
        | model
        | parser
    )

    parallel = RunnableParallel(
        summary=summary_chain,
        joke=joke_chain,
        fact=fact_chain,
    )

    topic = {"text": "the ocean"}

    # ---- Threaded invoke() ----
    start = time.perf_counter()
    result_sync = parallel.invoke(topic)
    sync_time = time.perf_counter() - start

    # ---- Concurrent ainvoke() ----
    start = time.perf_counter()
    result_async = await parallel.ainvoke(topic)
    async_time = time.perf_counter() - start

    print(f"invoke()  (threads)  took: {sync_time:.2f}s")
    print(f"ainvoke() (asyncio)  took: {async_time:.2f}s")
    print(f"\nBoth returned {len(result_sync)} results — confirming ainvoke() didn't break anything:")
    print(f"  summary: {result_async['summary'][:60]}...")
    print(f"  joke   : {result_async['joke'][:60]}...")
    print(f"  fact   : {result_async['fact'][:60]}...")


# ---------------------------------------------------------------
# 3. Multiple independent chains running truly concurrently
# ---------------------------------------------------------------
async def demo_concurrent_chains():
    section("3. Running 3 separate chains concurrently with asyncio.gather()")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Name one famous landmark in {city}.",
        input_variables=["city"],
    )

    chain = prompt | model | parser
    cities = ["Paris", "Tokyo", "Cairo"]

    start = time.perf_counter()

    results = await asyncio.gather(
        *[chain.ainvoke({"city": city}) for city in cities]
    )

    elapsed = time.perf_counter() - start

    for city, result in zip(cities, results):
        print(f"{city}: {result}")

    print(f"\nAll 3 completed concurrently in {elapsed:.2f}s")


# ---------------------------------------------------------------
# Run all async demos in sequence
# ---------------------------------------------------------------
async def main():

    demos = [
        demo_basic_async_chain,
        demo_parallel_speed_comparison,
        demo_concurrent_chains,
    ]

    for demo in demos:
        try:
            await demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — async execution demoed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())