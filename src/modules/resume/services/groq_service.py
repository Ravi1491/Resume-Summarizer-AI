from groq import Groq
from flask import current_app

class GroqService():
  
  def get_response(self, prompt):
    client = Groq(api_key=current_app.config['GROQ_API_KEY'])
    chat_completion = client.chat.completions.create(
      messages=[
        {
            "role": "user",
            "content": prompt,
        }
      ],
      model="llama3-70b-8192",
    )
    
    return chat_completion.choices[0].message.content