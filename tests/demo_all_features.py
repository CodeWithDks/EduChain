"""
demo_all_features.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

A real-world style usage demo — this is how an actual user
would use EduChain, not a test suite. Shows every major
feature working together with clean, controlled output.

Run directly:
    python demo_all_features.py
"""

from dotenv import load_dotenv

from educhain.models import ChatModel
from educhain.prompts import PromptTemplate
from educhain.output_parsers import StringOutputParser, JsonOutputParser
from educhain.core.parallel import RunnableParallel
from educhain.core.lambda_runnable import RunnableLambda
from educhain.core.passthrough import RunnablePassthrough
from educhain.memory import ChatMessageHistory

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# 1. Basic chain — prompt | model | parser
# ---------------------------------------------------------------
def demo_basic_chain():
    section("1. Basic Chain — Ask a question, get a clean string back")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Answer in one short sentence: {question}",
        input_variables=["question"],
    )

    chain = prompt | model | parser
    answer = chain.invoke({"question": "What is the capital of India?"})

    print(f"Q: What is the capital of India?\nA: {answer}")


# ---------------------------------------------------------------
# 2. Streaming — see the response arrive chunk by chunk
# ---------------------------------------------------------------
def demo_streaming():
    section("2. Streaming — response prints as it's generated")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Write a two-line poem about: {topic}",
        input_variables=["topic"],
    )

    chain = prompt | model | parser

    print("Q: Write a two-line poem about the moon")
    print("A: ", end="", flush=True)

    for chunk in chain.stream({"topic": "the moon"}):
        print(chunk, end="", flush=True)

    print()  # newline after streaming finishes


# ---------------------------------------------------------------
# 3. JsonOutputParser — structured output from the LLM
# ---------------------------------------------------------------
def demo_json_parser():
    section("3. JsonOutputParser — get structured data instead of text")

    model = ChatModel()
    parser = JsonOutputParser()
    prompt = PromptTemplate(
        template=(
            "Respond ONLY with valid JSON, no markdown, no explanation. "
            "Give info about {city} in this format: "
            '{{"city": "...", "country": "...", "famous_for": "..."}}'
        ),
        input_variables=["city"],
    )

    chain = prompt | model | parser
    result = chain.invoke({"city": "Jaipur"})

    print(f"City   : {result.get('city')}")
    print(f"Country: {result.get('country')}")
    print(f"Famous : {result.get('famous_for')}")


# ---------------------------------------------------------------
# 4. RunnableParallel — run multiple chains on the same input
# ---------------------------------------------------------------
def demo_parallel():
    section("4. RunnableParallel — summary + joke, generated together")

    model = ChatModel()
    parser = StringOutputParser()

    summary_chain = (
        PromptTemplate(
            template="Summarize this in one sentence: {text}",
            input_variables=["text"],
        )
        | model
        | parser
    )

    joke_chain = (
        PromptTemplate(
            template="Tell a short one-line joke related to: {text}",
            input_variables=["text"],
        )
        | model
        | parser
    )

    parallel = RunnableParallel(
        summary=summary_chain,
        joke=joke_chain,
    )

    topic = "Artificial Intelligence is changing the world"
    results = parallel.invoke({"text": topic})

    print(f"Input  : {topic}")
    print(f"Summary: {results['summary']}")
    print(f"Joke   : {results['joke']}")


# ---------------------------------------------------------------
# 5. RunnablePassthrough — keep original input alongside output
# ---------------------------------------------------------------
def demo_passthrough():
    section("5. RunnablePassthrough — keep original input + processed output")

    model = ChatModel()
    parser = StringOutputParser()

    translate_chain = (
        PromptTemplate(
            template="Translate this to Hindi: {text}",
            input_variables=["text"],
        )
        | model
        | parser
    )

    parallel = RunnableParallel(
        original=RunnablePassthrough(),
        translated=translate_chain,
    )

    result = parallel.invoke({"text": "Good morning"})

    print(f"Original  : {result['original']}")
    print(f"Translated: {result['translated']}")


# ---------------------------------------------------------------
# 6. RunnableLambda — plug a plain function into a chain
# ---------------------------------------------------------------
def demo_lambda():
    section("6. RunnableLambda — post-process model output with plain Python")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Give me one interesting fact about {topic}.",
        input_variables=["topic"],
    )

    make_uppercase = RunnableLambda(lambda text: text.upper())

    chain = prompt | model | parser | make_uppercase
    result = chain.invoke({"topic": "the Taj Mahal"})

    print(f"Fact (uppercased): {result}")


# ---------------------------------------------------------------
# 7. ChatMessageHistory — a chatbot that remembers the conversation
# ---------------------------------------------------------------
def demo_memory():
    section("7. Memory — a short conversation across multiple turns")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Conversation so far:\n{history}\n\nUser: {question}\nAssistant:",
        input_variables=["history", "question"],
    )

    chain = prompt | model | parser
    chat = ChatMessageHistory(chain, history_key="history")

    turns = [
        "My favorite programming language is Python.",
        "What did I just say my favorite language was?",
    ]

    for turn in turns:
        response = chat.invoke({"question": turn})
        print(f"You : {turn}")
        print(f"Bot : {response}\n")


# ---------------------------------------------------------------
# Run all demos, one after another, with clean separation
# ---------------------------------------------------------------
if __name__ == "__main__":

    demos = [
        demo_basic_chain,
        demo_streaming,
        demo_json_parser,
        demo_parallel,
        demo_passthrough,
        demo_lambda,
        demo_memory,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — all features demoed")
    print("=" * 60)