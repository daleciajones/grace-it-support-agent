import os
import openai
from dotenv import load_dotenv
import glob

# Load environment variables 
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load all text files in the knowledgebase
knowledge_text = ""
for file in glob.glob("knowledgebase/*.txt"):
    with open(file, "r") as f:
        content = f.read()
        knowledge_text += f"\n\n{content}"

# Grace's introduction
print("Hello! I'm Grace, your IT Support Assistant.")
print("I can help you with common technical issues like password resets, Wi-Fi problems, and more.")
print("Just ask your question below, and I'll do my best to guide you!\n")

# Ask the user a question
user_question = input("Ask Grace your IT Supprt question: ")

#Define Grace's personality and instructions
prompt = f""" 
You are Grace, a friendly and knowledgeable IT Support Assistant. 
You help users troubleshoot techinical issues and guide through solutions
based on the instructions below.
Respond clearly, with a calm and professional tone, as if assisting a real employee.

Knowledge Base:
{knowledge_text}

User: {user_question}
Grace:
"""

# Send the question to OpenAI and get a response 
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo" ,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Print Grace's response 
print("\n...Grace says:\n")
print(response["choices"][0]["message"]["content"])

# Grace's goodbye message 
print("\nThank you for chatting with me! If you need more help, just let me know.")
print("-Grace, your IT Support Assistant")