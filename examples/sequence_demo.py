from educhain.models import ChatModel
from educhain.output_parsers import StringOutputParser
from educhain.prompt import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
model = ChatModel(max_tokens=200)
parser = StringOutputParser()

prompt = PromptTemplate(
    template='You generate a  questions with 4 option and correct answers given following topic: {topic}',
    input_variables=['topic']
)


chain = prompt | model | parser

response = chain.invoke({'topic': 'Ai'})
print('='*30)
print(response)
print('='*30)

