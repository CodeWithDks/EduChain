from educhain.models import ChatModel
from educhain.output_parsers import StringOutputParser
from educhain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
model = ChatModel()
parser = StringOutputParser()

prompt = PromptTemplate(
    template='You generate a detailed outlier given following topic: {topic}',
    input_variables=['topic']
)

chain = prompt | model | parser

response = chain.invoke({'topic': 'Agentic Ai'})

print(response)


