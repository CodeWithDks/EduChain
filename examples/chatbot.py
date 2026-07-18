from educhain.models import ChatModel
from dotenv import load_dotenv


load_dotenv()
model = ChatModel()

result = model.invoke('what is ai?')
print(result.content)