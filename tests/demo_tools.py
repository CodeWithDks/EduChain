"""
demo_tools.py

Author: Deepak Singh (github.com/CodeWithDks)
Project: EduChain — a mini LangChain clone, built for learning

Demonstrates Tool Calling — the LLM decides on its own whether
to call a function, based on the user's question.

Run directly:
    python demo_tools.py
"""

from dotenv import load_dotenv

from educhain.models.llm import ChatModel
from educhain.core.tool import Tool

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# Define plain Python functions — EduChain builds the schema
# automatically from the type hints + docstring
# ---------------------------------------------------------------
def get_weather(city: str) -> str:
    """Get the current weather for a specific named city. 
    Only use this if the user is asking about weather conditions."""
    # fake data on purpose — this is a demo, not a real weather API
    fake_weather = {
        "delhi": "32°C, sunny",
        "mumbai": "29°C, humid",
        "london": "15°C, rainy",
    }
    return fake_weather.get(city.lower(), f"No weather data for {city}")


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


# ---------------------------------------------------------------
# 1. LLM correctly chooses NOT to call a tool for a normal question
# ---------------------------------------------------------------
def demo_no_tool_needed():
    section("1. Normal question — LLM should answer directly, no tool call")

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])

    response = model.invoke("What is the capital of France?")

    if model.has_tool_calls(response):
        print("⚠️  Unexpected: LLM tried to call a tool for this question")
    else:
        print(f"Answer (no tool used): {response.content}")


# ---------------------------------------------------------------
# 2. LLM correctly chooses to call the weather tool
# ---------------------------------------------------------------
def demo_weather_tool():
    section("2. Weather question — LLM should call get_weather()")

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])

    response = model.invoke("What's the weather like in Delhi right now?")

    if model.has_tool_calls(response):
        print("LLM wants to call a tool ✔")

        results = model.run_tool_calls(response)

        for r in results:
            print(f"  Tool called : {r['name']}")
            print(f"  Arguments   : {r['args']}")
            print(f"  Result      : {r['result']}")
    else:
        print(f"⚠️  Unexpected: LLM answered directly: {response.content}")


# ---------------------------------------------------------------
# 3. LLM picks the correct tool out of multiple available ones
# ---------------------------------------------------------------
def demo_multiple_tools():
    section("3. Multiple tools bound — LLM picks the right one")

    weather_tool = Tool(get_weather)
    add_tool = Tool(add_numbers)
    model = ChatModel(tools=[weather_tool, add_tool])

    response = model.invoke("What is 47 plus 89?")

    if model.has_tool_calls(response):
        results = model.run_tool_calls(response)
        for r in results:
            print(f"  Tool called : {r['name']}")
            print(f"  Arguments   : {r['args']}")
            print(f"  Result      : {r['result']}")
    else:
        print(f"⚠️  Unexpected: LLM answered directly: {response.content}")


# ---------------------------------------------------------------
# 4. Full round trip — call tool, feed result back, get final answer
# ---------------------------------------------------------------
def demo_full_round_trip():
    section("4. Full round trip — tool result fed back for a final answer")

    from langchain_core.messages import HumanMessage, ToolMessage

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])

    question = "What's the weather in Mumbai? Answer in one friendly sentence."

    # step 1: ask the question
    first_response = model.model.invoke([HumanMessage(content=question)])

    if not model.has_tool_calls(first_response):
        print(f"⚠️  No tool call happened: {first_response.content}")
        return

    results = model.run_tool_calls(first_response)
    print(f"Tool called: {results[0]['name']}({results[0]['args']}) → {results[0]['result']}")

    # step 2: feed the tool's result back as a ToolMessage,
    # so the LLM can give a final natural-language answer
    tool_call_id = first_response.tool_calls[0]["id"]

    conversation = [
        HumanMessage(content=question),
        first_response,
        ToolMessage(content=str(results[0]["result"]), tool_call_id=tool_call_id),
    ]

    final_response = model.model.invoke(conversation)
    print(f"\nFinal answer: {final_response.content}")


# ---------------------------------------------------------------
# 5. Tool validation errors
# ---------------------------------------------------------------
def demo_tool_validation():
    section("5. Tool validation")

    try:
        Tool("not a function")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    def no_docstring_func(x: str) -> str:
        return x

    try:
        Tool(no_docstring_func)
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")


# ---------------------------------------------------------------
# Run all tool demos
# ---------------------------------------------------------------
if __name__ == "__main__":

    demos = [
        demo_no_tool_needed,
        demo_weather_tool,
        demo_multiple_tools,
        demo_full_round_trip,
        demo_tool_validation,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  {demo.__name__} failed: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("✨ EduChain — tool calling demoed")
    print("=" * 60)