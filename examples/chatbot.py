import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from educhain.prompts import PromptTemplate
from educhain.models import ChatModel
from educhain.output_parsers import StringOutputParser
from educhain.memory import ChatMessageHistory

load_dotenv()


def build_chatbot():

    # ---- Groq model setup ----
    # get a free key from https://console.groq.com
    groq_model = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=300,
    )

    model = ChatModel(model=groq_model)

    # ---- Prompt with memory placeholder ----
    prompt = PromptTemplate(
        template=(
            "You are a friendly, helpful assistant built with EduChain.\n"
            "Conversation so far:\n{history}\n\n"
            "User: {question}\n"
            "Assistant:"
        ),
        input_variables=["history", "question"],
    )

    parser = StringOutputParser()

    # ---- Build the chain ----
    chain = prompt | model | parser

    # ---- Wrap with memory so it remembers past turns ----
    chatbot = ChatMessageHistory(chain, history_key="history")

    return chatbot


def main():

    print("=" * 60)
    print("🤖 EduChain Chatbot — powered by Groq")
    print("Type 'exit' or 'quit' to stop")
    print("=" * 60)

    chatbot = build_chatbot()

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("\nBye! 👋")
            break

        if user_input == "":
            print("Please type something.")
            continue

        try:
            response = chatbot.invoke({"question": user_input})
            print(f"\nBot: {response}")

        except Exception as e:
            print(f"\n⚠️ Something went wrong: {e}")


if __name__ == "__main__":
    main()