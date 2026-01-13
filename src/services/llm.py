from langchain_groq	import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

class LLMService():
    
	def get_groq_response(self, prompt):
		llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature=0.7)

		chat_prompt = ChatPromptTemplate.from_messages([
			("human", "{input}")
		])
		
		chain = chat_prompt | llm
		response = chain.invoke({"input": prompt})
  
		print("response ====== ", response.content)
  
		return response.content

	def get_response_anthropic(self, prompt):
		llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

		chat_prompt = ChatPromptTemplate.from_messages([
			("human", "{input}")
		])
		
		chain = chat_prompt | llm
		response = chain.invoke({"input": prompt})
		return response.content
