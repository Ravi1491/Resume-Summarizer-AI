from langchain_groq	import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from flask import current_app

class GroqService():
    
	def get_response(self, prompt):
		llm = ChatGroq(model_name="llama3-70b-8192", temperature=0.7)

		chat_prompt = ChatPromptTemplate.from_messages([
			("human", "{input}")
		])
		
		chain = chat_prompt | llm
		response = chain.invoke({"input": prompt})
  
		return response.content
