from educhain.models import ChatModel
from educhain.prompts import PromptTemplate
from educhain.output_parsers import StringOutputParser
from dotenv import load_dotenv
import os


load_dotenv()
model = ChatModel()
parser = StringOutputParser()

prompt = PromptTemplate(
    template='you are helpfull assistant. write content on the given topic:\n {topic}',
    input_variables=['topic']
)

chain = prompt | model | parser

print(chain.stream({'topic':'Radha Rani'}))