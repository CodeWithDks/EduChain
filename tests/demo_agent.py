"""
demo_agent.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Demonstrates the Agent — an LLM that decides, on its own, which
tools to call (possibly multiple, possibly none) to answer a
question, looping until it reaches a final answer.

This is the capstone demo: Tool Calling + Callbacks + RAG all
working together inside a single reasoning loop.

Run directly:
    python demo_agent.py
"""

from dotenv import load_dotenv

from educhain.models import ChatModel
from educhain.prompts import PromptTemplate
from educhain.output_parsers import StringOutputParser
from educhain.core.tool import Tool
from educhain.core.agent import Agent
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain
from educhain.core.callbacks import PrintCallbackHandler

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# Tools the agent can choose from
# ---------------------------------------------------------------
def get_weather(city: str) -> str:
    """Get the current weather for a specific named city.
    Only use this if the user is asking about weather conditions."""
    fake_weather = {
        "delhi": "32°C, sunny",
        "mumbai": "29°C, humid",
        "london": "15°C, rainy",
    }
    return fake_weather.get(city.lower(), f"No weather data for {city}")


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together. Only use this for addition."""
    return a + b


def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together. Only use this for multiplication."""
    return a * b


# ---------------------------------------------------------------
# Build a RAG-backed knowledge base tool — reuses everything
# from the RAG phase, wrapped so the Agent can call it like
# any other tool
# ---------------------------------------------------------------
def build_knowledge_search_tool():

    store = InMemoryVectorStore()
    store.add_texts([
        "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
        "NimbusTech's headquarters moved from Pune to Bangalore in 2023.",
        "NimbusTech's flagship product is CloudSprint, a deployment tool.",
        "NimbusTech has 42 employees as of 2025.",
    ])

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template=(
            "Answer using ONLY the context below. "
            "If the answer isn't in the context, say you don't know.\n\n"
            "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        ),
        input_variables=["context", "question"],
    )
    chain = prompt | model | parser
    rag = RAGChain(vectorstore=store, chain=chain, k=3)

    # wrap RAGChain.invoke() as a plain function so Tool can use it —
    # this is the moment RAG becomes an Agent capability, not just
    # something you call directly
    def search_company_knowledge(question: str) -> str:
        """Search internal company knowledge about NimbusTech.
        Use this for any question about NimbusTech — its founder,
        history, products, employees, or headquarters."""
        return rag.invoke(question)

    return Tool(search_company_knowledge)


# ---------------------------------------------------------------
# 1. Agent uses a single tool to answer a direct question
# ---------------------------------------------------------------
def demo_single_tool():
    section("1. Agent — single tool call")

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])
    agent = Agent(model=model)

    answer = agent.invoke("What's the weather like in Delhi right now?")
    print(f"\nFinal answer: {answer}")


# ---------------------------------------------------------------
# 2. Agent picks the correct tool from several options
# ---------------------------------------------------------------
def demo_tool_selection():
    section("2. Agent — picks the right tool among several")

    tools = [Tool(get_weather), Tool(add_numbers), Tool(multiply_numbers)]
    model = ChatModel(tools=tools)
    agent = Agent(model=model)

    answer = agent.invoke("What is 12 multiplied by 7?")
    print(f"\nFinal answer: {answer}")


# ---------------------------------------------------------------
# 3. Agent uses RAG as a tool — the real payoff
# ---------------------------------------------------------------
def demo_rag_as_tool():
    section("3. Agent — searching its own knowledge base via RAG")

    knowledge_tool = build_knowledge_search_tool()
    model = ChatModel(tools=[knowledge_tool])
    agent = Agent(model=model)

    answer = agent.invoke("Where is NimbusTech headquartered now, and who founded it?")
    print(f"\nFinal answer: {answer}")


# ---------------------------------------------------------------
# 4. Full visibility — watch the agent's reasoning with callbacks
# ---------------------------------------------------------------
def demo_agent_with_callbacks():
    section("4. Agent with PrintCallbackHandler — see every step")

    tools = [Tool(get_weather), Tool(add_numbers)]
    model = ChatModel(tools=tools)
    agent = Agent(model=model, callbacks=[PrintCallbackHandler()])

    answer = agent.invoke("What's the weather in Mumbai?")
    print(f"\nFinal answer: {answer}")


# ---------------------------------------------------------------
# 5. No tool needed — agent should answer directly, zero iterations wasted
# ---------------------------------------------------------------
def demo_no_tool_needed():
    section("5. Agent — question needs no tool at all")

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])
    agent = Agent(model=model)

    answer = agent.invoke("What is the capital of Japan?")
    print(f"\nFinal answer: {answer}")


# ---------------------------------------------------------------
# 6. Validation errors
# ---------------------------------------------------------------
def demo_agent_validation():
    section("6. Agent validation")

    # model with no tools bound
    try:
        Agent(model=ChatModel())
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # not a ChatModel at all
    try:
        Agent(model="not a model")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # empty question
    model = ChatModel(tools=[Tool(get_weather)])
    agent = Agent(model=model)
    try:
        agent.invoke("")
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")


# ---------------------------------------------------------------
# Run all agent demos
# ---------------------------------------------------------------
if __name__ == "__main__":

    demos = [
        demo_single_tool,
        demo_tool_selection,
        demo_rag_as_tool,
        demo_agent_with_callbacks,
        demo_no_tool_needed,
        demo_agent_validation,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — Agent demoed (the full roadmap is now built)")
    print("=" * 60)