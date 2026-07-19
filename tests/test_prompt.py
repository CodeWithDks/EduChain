from educhain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="You are a helpful assistant. answer only from then text:\n {text}",
    input_variables=['text']
)

final_prompt = prompt.invoke({'text': 'Radha rani is my everything.'})

print(final_prompt)