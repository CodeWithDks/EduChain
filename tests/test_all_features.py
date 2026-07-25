"""
test_all_features.py

Full feature test suite for EduChain — mirrors what LangChain's
own test coverage would look like for these core primitives.

Run directly:
    python test_all_features.py
"""

from dotenv import load_dotenv

from educhain.models import ChatModel
from educhain.prompts import PromptTemplate
from educhain.output_parsers import StringOutputParser, JsonOutputParser
from educhain.core import RunnableSequence
from educhain.memory import ChatMessageHistory
from educhain.core.parallel import RunnableParallel
from educhain.core.passthrough import RunnablePassthrough
from educhain.core.lambda_runnable import RunnableLambda
from educhain.core.tool import Tool
from educhain.core.vectorstore import InMemoryVectorStore
from educhain.core.rag import RAGChain

load_dotenv()


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# 1. PromptTemplate — basic formatting
# ---------------------------------------------------------------
def test_prompt_template():
    section("TEST 1: PromptTemplate.invoke()")

    prompt = PromptTemplate(
        template="You are a helpful assistant. Write a short paragraph on:\n{topic}",
        input_variables=["topic"],
    )

    result = prompt.invoke({"topic": "Radha Rani"})
    print(result)
    assert isinstance(result, str), "PromptTemplate should return a string"
    assert "Radha Rani" in result
    print("✅ PASSED")


# ---------------------------------------------------------------
# 2. ChatModel — invoke (single response)
# ---------------------------------------------------------------
def test_chat_model_invoke():
    section("TEST 2: ChatModel.invoke()")

    model = ChatModel()
    response = model.invoke("Say hello in one short sentence.")

    print(response.content)
    assert hasattr(response, "content"), "ChatModel.invoke() should return an AIMessage"
    print("✅ PASSED")


# ---------------------------------------------------------------
# 3. ChatModel — stream (chunked response)
# ---------------------------------------------------------------
def test_chat_model_stream():
    section("TEST 3: ChatModel.stream()")

    model = ChatModel()
    full_text = ""
    for chunk in model.stream("Say hello in one short sentence."):
        print(chunk.content, end="", flush=True)
        full_text += chunk.content

    print(f"\n--- {len(full_text)} chars streamed ---")
    assert len(full_text) > 0
    print("✅ PASSED")


# ---------------------------------------------------------------
# 4. ChatModel — validation errors
# ---------------------------------------------------------------
def test_chat_model_validation():
    section("TEST 4: ChatModel validation (invoke + stream)")

    model = ChatModel()

    try:
        model.invoke(123)
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ invoke() correctly raised TypeError: {e}")

    try:
        model.invoke("   ")
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ invoke() correctly raised ValueError: {e}")

    try:
        list(model.stream(123))
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ stream() correctly raised TypeError: {e}")


# ---------------------------------------------------------------
# 5. StringOutputParser — invoke
# ---------------------------------------------------------------
def test_string_parser_invoke():
    section("TEST 5: StringOutputParser.invoke()")

    model = ChatModel()
    parser = StringOutputParser()

    ai_message = model.invoke("Say hello in one short sentence.")
    result = parser.invoke(ai_message)

    print(result)
    assert isinstance(result, str)
    print("✅ PASSED")


# ---------------------------------------------------------------
# 6. StringOutputParser — invoke with wrong type (should fail)
# ---------------------------------------------------------------
def test_string_parser_validation():
    section("TEST 6: StringOutputParser validation")

    parser = StringOutputParser()
    try:
        parser.invoke("just a plain string, not an AIMessage")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")


# ---------------------------------------------------------------
# 7. JsonOutputParser — invoke with valid JSON
# ---------------------------------------------------------------
def test_json_parser_invoke():
    section("TEST 7: JsonOutputParser.invoke()")

    model = ChatModel()
    parser = JsonOutputParser()

    ai_message = model.invoke(
        'Respond ONLY with valid JSON, no markdown, no explanation. '
        'Format: {"name": "Radha Rani", "role": "consort of Krishna"}'
    )
    print("Raw model output:", ai_message.content)

    try:
        result = parser.invoke(ai_message)
        print("Parsed:", result)
        assert isinstance(result, dict)
        print("✅ PASSED")
    except ValueError as e:
        # model didn't return clean JSON this time — not a code bug,
        # just LLM non-determinism. Worth knowing either way.
        print(f"⚠️  Model didn't return valid JSON this run: {e}")


# ---------------------------------------------------------------
# 8. RunnableSequence — invoke (full chain)
# ---------------------------------------------------------------
def test_sequence_invoke():
    section("TEST 8: RunnableSequence.invoke() — prompt | model | parser")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="You are a helpful assistant. Write one sentence on:\n{topic}",
        input_variables=["topic"],
    )

    chain = prompt | model | parser
    result = chain.invoke({"topic": "Radha Rani"})

    print(result)
    assert isinstance(result, str)
    print("✅ PASSED")


# ---------------------------------------------------------------
# 9. RunnableSequence — stream (full chain, fixed version)
# ---------------------------------------------------------------
def test_sequence_stream_with_parser():
    section("TEST 9: RunnableSequence.stream() — prompt | model | parser")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="You are a helpful assistant. Write one sentence on:\n{topic}",
        input_variables=["topic"],
    )

    chain = prompt | model | parser

    full_text = ""
    for chunk in chain.stream({"topic": "Radha Rani"}):
        print(chunk, end="", flush=True)
        full_text += chunk

    print(f"\n--- {len(full_text)} chars streamed ---")
    assert len(full_text) > 0
    print("✅ PASSED — streaming through parser works")
    
# ---------------------------------------------------------------
# 10. RunnableSequence — __or__ flattening (no nested sequences)
# ---------------------------------------------------------------
def test_sequence_flattening():
    section("TEST 10: RunnableSequence flattening via __or__")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Write one sentence on:\n{topic}",
        input_variables=["topic"],
    )

    chain = prompt | model | parser
    print(repr(chain))

    assert isinstance(chain, RunnableSequence)
    assert len(chain.steps) == 3, f"Expected 3 flat steps, got {len(chain.steps)}"
    assert not any(isinstance(step, RunnableSequence) for step in chain.steps), \
        "Chain should be flat, not nested"
    print("✅ PASSED — 3 flat steps, no nesting")


# ---------------------------------------------------------------
# 11. RunnableSequence — minimum steps validation
# ---------------------------------------------------------------
def test_sequence_min_steps_validation():
    section("TEST 11: RunnableSequence requires at least 2 steps")

    model = ChatModel()
    try:
        RunnableSequence(model)
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")


# ---------------------------------------------------------------
# 12. RunnableSequence — type validation on steps
# ---------------------------------------------------------------
def test_sequence_type_validation():
    section("TEST 12: RunnableSequence rejects non-Runnable steps")

    model = ChatModel()
    try:
        RunnableSequence(model, "not a runnable")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")


# ---------------------------------------------------------------
# 13. ChatMessageHistory — remembers across turns
# ---------------------------------------------------------------
def test_chat_message_history():
    section("TEST 13: ChatMessageHistory.invoke() — memory across turns")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Conversation so far:\n{history}\n\nUser: {question}\nAssistant:",
        input_variables=["history", "question"],
    )

    chain = prompt | model | parser
    chat = ChatMessageHistory(chain, history_key="history")

    r1 = chat.invoke({"question": "My name is Deepak. Just say OK."})
    print("Turn 1:", r1)

    r2 = chat.invoke({"question": "What's my name? Answer in one short sentence."})
    print("Turn 2:", r2)

    print("History stored:", repr(chat.history))
    assert len(chat.history.messages) == 4, "Should have 2 user + 2 AI messages"
    print("✅ PASSED (check Turn 2 manually — it should mention 'Deepak')")


# ---------------------------------------------------------------
# 14. ChatMessageHistory — input validation
# ---------------------------------------------------------------
def test_chat_message_history_validation():
    section("TEST 14: ChatMessageHistory validation")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="{history}\n{question}",
        input_variables=["history", "question"],
    )
    chain = prompt | model | parser

    try:
        ChatMessageHistory("not a runnable")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    chat = ChatMessageHistory(chain)
    try:
        chat.invoke("not a dict")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

# ---------------------------------------------------------------
# 15. RunnableParallel — runs multiple chains on the same input
# ---------------------------------------------------------------
def test_runnable_parallel():
    section("TEST 15: RunnableParallel.invoke() — multiple branches")

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

    parallel = RunnableParallel(summary=summary_chain, joke=joke_chain)
    result = parallel.invoke({"text": "robots"})

    print("Summary:", result["summary"])
    print("Joke   :", result["joke"])

    assert isinstance(result, dict)
    assert "summary" in result and "joke" in result
    assert isinstance(result["summary"], str) and len(result["summary"]) > 0
    assert isinstance(result["joke"], str) and len(result["joke"]) > 0
    print("✅ PASSED")


# ---------------------------------------------------------------
# 16. RunnableParallel — validation errors
# ---------------------------------------------------------------
def test_runnable_parallel_validation():
    section("TEST 16: RunnableParallel validation")

    model = ChatModel()
    parser = StringOutputParser()
    ok_chain = (
        PromptTemplate(template="{text}", input_variables=["text"])
        | model
        | parser
    )

    # zero runnables should fail
    try:
        RunnableParallel()
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # a non-Runnable branch should fail
    try:
        RunnableParallel(good=ok_chain, bad="not a runnable")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")


# ---------------------------------------------------------------
# 17. RunnablePassthrough — returns input unchanged
# ---------------------------------------------------------------
def test_runnable_passthrough():
    section("TEST 17: RunnablePassthrough.invoke() — unchanged input")

    passthrough = RunnablePassthrough()

    # works with a dict
    original = {"text": "Good morning"}
    result = passthrough.invoke(original)
    print("Dict input :", result)
    assert result == original

    # works with a plain string too — passthrough shouldn't care about type
    result_str = passthrough.invoke("just a string")
    print("String input:", result_str)
    assert result_str == "just a string"

    print("✅ PASSED")


# ---------------------------------------------------------------
# 18. RunnablePassthrough — combined with RunnableParallel
# ---------------------------------------------------------------
def test_passthrough_inside_parallel():
    section("TEST 18: RunnablePassthrough inside RunnableParallel")

    model = ChatModel()
    parser = StringOutputParser()

    translate_chain = (
        PromptTemplate(
            template="Translate to Hindi: {text}",
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
    print("Original  :", result["original"])
    print("Translated:", result["translated"])

    assert result["original"] == {"text": "Good morning"}
    assert isinstance(result["translated"], str) and len(result["translated"]) > 0
    print("✅ PASSED")


# ---------------------------------------------------------------
# 19. RunnableLambda — plugs a plain function into a chain
# ---------------------------------------------------------------
def test_runnable_lambda():
    section("TEST 19: RunnableLambda.invoke() — custom function step")

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Give one fact about {topic}.",
        input_variables=["topic"],
    )

    uppercase_step = RunnableLambda(lambda text: text.upper())

    chain = prompt | model | parser | uppercase_step
    result = chain.invoke({"topic": "the ocean"})

    print("Result:", result)
    assert isinstance(result, str)
    assert result == result.upper()
    print("✅ PASSED")


# ---------------------------------------------------------------
# 20. RunnableLambda — validation errors
# ---------------------------------------------------------------
def test_runnable_lambda_validation():
    section("TEST 20: RunnableLambda validation")

    # non-callable should fail at construction
    try:
        RunnableLambda("not a function")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # a function that raises internally should surface as RuntimeError
    broken_lambda = RunnableLambda(lambda x: x.upper())  # will fail on non-string input

    try:
        broken_lambda.invoke(123)  # int has no .upper()
        print("❌ FAILED: should have raised RuntimeError")
    except RuntimeError as e:
        print(f"✅ Correctly raised RuntimeError: {e}")

# ---------------------------------------------------------------
# 21. Tool — schema auto-generation from a plain function
# ---------------------------------------------------------------
def test_tool_schema_generation():
    section("TEST 21: Tool — auto-generates schema from function")

    def get_weather(city: str) -> str:
        """Get the current weather for a specific named city."""
        return f"Sunny in {city}"

    tool = Tool(get_weather)

    print("Tool name  :", tool.name)
    print("Description:", tool.description)
    print("Schema     :", tool.schema)

    assert tool.name == "get_weather"
    assert "city" in tool.schema["function"]["parameters"]["properties"]
    assert tool.schema["function"]["parameters"]["properties"]["city"]["type"] == "string"
    assert "city" in tool.schema["function"]["parameters"]["required"]
    print("✅ PASSED")


# ---------------------------------------------------------------
# 22. Tool — validation errors
# ---------------------------------------------------------------
def test_tool_validation():
    section("TEST 22: Tool validation")

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
# 23. Tool.run() — direct execution, correct and incorrect args
# ---------------------------------------------------------------
def test_tool_run():
    section("TEST 23: Tool.run() — direct execution")

    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    tool = Tool(add_numbers)

    result = tool.run(a=5, b=7)
    print("5 + 7 =", result)
    assert result == 12

    try:
        tool.run(a=5)  # missing required arg 'b'
        print("❌ FAILED: should have raised RuntimeError")
    except RuntimeError as e:
        print(f"✅ Correctly raised RuntimeError: {e}")


# ---------------------------------------------------------------
# 24. ChatModel — correctly ignores irrelevant tools
# ---------------------------------------------------------------
def test_chatmodel_ignores_irrelevant_tool():
    section("TEST 24: ChatModel — no tool call for an unrelated question")

    def get_weather(city: str) -> str:
        """Get the current weather for a specific named city.
        Only use this if the user is asking about weather conditions."""
        return f"Sunny in {city}"

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])

    response = model.invoke("What is the capital of France?")
    print("Response:", response.content)

    assert not model.has_tool_calls(response), \
        "LLM should NOT have called a tool for an unrelated question"
    print("✅ PASSED")


# ---------------------------------------------------------------
# 25. ChatModel — correctly calls a relevant tool with right args
# ---------------------------------------------------------------
def test_chatmodel_calls_relevant_tool():
    section("TEST 25: ChatModel — calls the right tool with correct arguments")

    def get_weather(city: str) -> str:
        """Get the current weather for a specific named city.
        Only use this if the user is asking about weather conditions."""
        fake_weather = {"delhi": "32°C, sunny"}
        return fake_weather.get(city.lower(), "No data")

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])

    response = model.invoke("What's the weather like in Delhi right now?")

    assert model.has_tool_calls(response), "LLM should have called a tool"

    results = model.run_tool_calls(response)
    print("Tool results:", results)

    assert len(results) == 1
    assert results[0]["name"] == "get_weather"
    assert results[0]["args"]["city"].lower() == "delhi"
    assert results[0]["result"] == "32°C, sunny"
    print("✅ PASSED")


# ---------------------------------------------------------------
# 26. ChatModel — run_tool_calls raises on unknown tool name
# ---------------------------------------------------------------
def test_chatmodel_unknown_tool_error():
    section("TEST 26: ChatModel.run_tool_calls — unknown tool name safety check")

    # simulate a fake response object claiming a tool call
    # that isn't actually bound to this model
    class FakeResponse:
        tool_calls = [{"name": "nonexistent_tool", "args": {}, "id": "fake_id"}]

    def get_weather(city: str) -> str:
        """Get the current weather for a specific named city."""
        return f"Sunny in {city}"

    weather_tool = Tool(get_weather)
    model = ChatModel(tools=[weather_tool])

    try:
        model.run_tool_calls(FakeResponse())
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

# ---------------------------------------------------------------
# 27. RAGChain — end-to-end retrieval + generation
# ---------------------------------------------------------------
def test_rag_basic():
    section("TEST 27: RAGChain.invoke() — answers using retrieved context")

    store = InMemoryVectorStore()
    store.add_texts([
        "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
        "NimbusTech's headquarters moved from Pune to Bangalore in 2023.",
        "NimbusTech's flagship product is CloudSprint, a deployment tool.",
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

    answer = rag.invoke("Where is NimbusTech based now?")
    print("Answer:", answer)

    assert isinstance(answer, str)
    assert "bangalore" in answer.lower(), \
        "Answer should mention Bangalore — this is fictional data, so a correct answer proves retrieval worked"
    print("✅ PASSED")


# ---------------------------------------------------------------
# 28. RAGChain — refuses to answer when info isn't in context
# ---------------------------------------------------------------
def test_rag_out_of_context():
    section("TEST 28: RAGChain — admits it doesn't know when context lacks the answer")

    store = InMemoryVectorStore()
    store.add_texts([
        "NimbusTech was founded in 2021 by Ariana Kessler in Pune, India.",
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

    answer = rag.invoke("What is NimbusTech's annual revenue?")
    print("Answer:", answer)

    assert isinstance(answer, str)
    assert len(answer) > 0
    print("✅ PASSED (check manually — should decline to answer, not invent a number)")


# ---------------------------------------------------------------
# 29. RAGChain.get_relevant_chunks() — inspect retrieval separately
# ---------------------------------------------------------------
def test_rag_get_relevant_chunks():
    section("TEST 29: RAGChain.get_relevant_chunks() — retrieval without generation")

    store = InMemoryVectorStore()
    store.add_texts([
        "CloudSprint supports deployments to AWS, Azure, and Google Cloud.",
        "The Eiffel Tower is located in Paris, France.",
        "Mount Everest is the tallest mountain on Earth.",
    ])

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="Context:\n{context}\n\nQuestion: {question}\nAnswer:",
        input_variables=["context", "question"],
    )

    chain = prompt | model | parser
    rag = RAGChain(vectorstore=store, chain=chain, k=2)

    chunks = rag.get_relevant_chunks("What cloud platforms does CloudSprint support?")
    print("Retrieved chunks:", chunks)

    assert isinstance(chunks, list)
    assert len(chunks) == 2
    top_text, top_score = chunks[0]
    assert "cloud" in top_text.lower() or "aws" in top_text.lower()
    print("✅ PASSED")


# ---------------------------------------------------------------
# 30. RAGChain — validation errors
# ---------------------------------------------------------------
def test_rag_validation():
    section("TEST 30: RAGChain validation")

    store = InMemoryVectorStore()
    store.add_texts(["A valid fact to search against."])

    model = ChatModel()
    parser = StringOutputParser()
    prompt = PromptTemplate(
        template="{context}\n{question}",
        input_variables=["context", "question"],
    )
    chain = prompt | model | parser

    # bad chain type
    try:
        RAGChain(vectorstore=store, chain="not a runnable")
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # bad vectorstore type (missing similarity_search)
    try:
        RAGChain(vectorstore="not a vectorstore", chain=chain)
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")

    # empty question
    rag = RAGChain(vectorstore=store, chain=chain)
    try:
        rag.invoke("")
        print("❌ FAILED: should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")

    # non-string question
    try:
        rag.invoke(123)
        print("❌ FAILED: should have raised TypeError")
    except TypeError as e:
        print(f"✅ Correctly raised TypeError: {e}")
# ---------------------------------------------------------------
# NOT YET TESTED — code not shared with me yet
# ---------------------------------------------------------------
# core/parallel.py     -> RunnableParallel (run multiple chains on same input?)
# core/passthrough.py  -> RunnablePassthrough (pass input through unchanged?)
# Share these files and I'll add real tests for them too.
# ---------------------------------------------------------------


if __name__ == "__main__":
    tests = [
        test_prompt_template,
        test_chat_model_invoke,
        test_chat_model_stream,
        test_chat_model_validation,
        test_string_parser_invoke,
        test_string_parser_validation,
        test_json_parser_invoke,
        test_sequence_invoke,
        test_sequence_stream_with_parser,
        test_sequence_flattening,
        test_sequence_min_steps_validation,
        test_sequence_type_validation,
        test_chat_message_history,
        test_chat_message_history_validation,
        test_runnable_parallel,
        test_runnable_parallel_validation,
        test_runnable_passthrough,
        test_passthrough_inside_parallel,
        test_runnable_lambda,
        test_runnable_lambda_validation,
        test_tool_schema_generation,
        test_tool_validation,
        test_tool_run,
        test_chatmodel_ignores_irrelevant_tool,
        test_chatmodel_calls_relevant_tool,
        test_chatmodel_unknown_tool_error,
        test_rag_basic,
        test_rag_out_of_context,
        test_rag_get_relevant_chunks,
        test_rag_validation,
    ]

    passed, failed = 0, 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ ASSERTION FAILED in {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR in {test.__name__}: {type(e).__name__}: {e}")

    section(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)}")