"""
demo_callbacks.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Demonstrates the callback system — swapping observability
behavior in and out of a chain without touching RunnableSequence
itself.

Run directly:
    python demo_callbacks.py
"""

from dotenv import load_dotenv

from educhain.models.llm import ChatModel
from educhain.prompts.prompt import PromptTemplate
from educhain.output_parsers.parser import StringOutputParser
from educhain.core.sequence import RunnableSequence
from educhain.core.callbacks import CallbackHandler, PrintCallbackHandler

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# 1. Built-in PrintCallbackHandler — same as old verbose=True,
#    but now it's a swappable handler instead of hardcoded prints
# ---------------------------------------------------------------
def demo_print_handler():
    section("1. PrintCallbackHandler — built-in step-by-step logging")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Answer in one short sentence: {question}",
        input_variables=["question"],
    )

    chain = RunnableSequence(
        prompt, model, parser,
        callbacks=[PrintCallbackHandler()],
    )

    result = chain.invoke({"question": "What is the tallest mountain on Earth?"})
    print(f"\nFinal result: {result}")


# ---------------------------------------------------------------
# 2. Custom handler — counts steps and tracks timing.
#    RunnableSequence knows NOTHING about this logic — that's
#    the actual value of the callback system.
# ---------------------------------------------------------------
class StepCounterHandler(CallbackHandler):
    """
    A custom handler someone writes themselves — counts how many
    steps ran and how long each one took, without ever touching
    RunnableSequence's own code.
    """

    def __init__(self):
        self.step_count = 0
        self.step_times = {}
        self._start_time = None

    def on_chain_start(self, chain_name, input_data):
        print(f"📊 Starting to track '{chain_name}'...")

    def on_step_start(self, step_name, input_data):
        import time
        self._start_time = time.perf_counter()

    def on_step_end(self, step_name, output_data):
        import time
        elapsed = time.perf_counter() - self._start_time
        self.step_count += 1
        self.step_times[step_name] = elapsed

    def on_chain_end(self, chain_name, output_data):
        print(f"📊 Tracked {self.step_count} steps:")
        for name, seconds in self.step_times.items():
            print(f"   {name}: {seconds:.3f}s")


def demo_custom_handler():
    section("2. Custom StepCounterHandler — user-written, zero changes to RunnableSequence")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Give one fact about {topic}.",
        input_variables=["topic"],
    )

    tracker = StepCounterHandler()

    chain = RunnableSequence(
        prompt, model, parser,
        callbacks=[tracker],
    )

    result = chain.invoke({"topic": "black holes"})
    print(f"\nFinal result: {result}")


# ---------------------------------------------------------------
# 3. Multiple handlers at once — Print + Counter together
# ---------------------------------------------------------------
def demo_multiple_handlers():
    section("3. Multiple handlers together — Print + StepCounter")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Answer in one short sentence: {question}",
        input_variables=["question"],
    )

    tracker = StepCounterHandler()

    chain = RunnableSequence(
        prompt, model, parser,
        callbacks=[PrintCallbackHandler(), tracker],
    )

    result = chain.invoke({"question": "What is the boiling point of water?"})
    print(f"\nFinal result: {result}")


# ---------------------------------------------------------------
# 4. on_error — a handler reacting to a failure
# ---------------------------------------------------------------
class ErrorLoggerHandler(CallbackHandler):
    def on_error(self, step_name, error):
        print(f"🚨 ALERT: {step_name} crashed with: {error}")


def demo_error_handler():
    section("4. ErrorLoggerHandler — reacts when a step fails")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="{question}",
        input_variables=["question"],
    )

    chain = RunnableSequence(
        prompt, model, parser,
        callbacks=[ErrorLoggerHandler()],
    )

    try:
        # passing an int where a dict is expected — triggers a real error
        chain.invoke("not a dict")
    except Exception as e:
        print(f"(chain correctly raised: {type(e).__name__}: {e})")


# ---------------------------------------------------------------
# Run all callback demos
# ---------------------------------------------------------------
if __name__ == "__main__":

    demos = [
        demo_print_handler,
        demo_custom_handler,
        demo_multiple_handlers,
        demo_error_handler,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — callback system demoed")
    print("=" * 60)