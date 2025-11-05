# 💜 Grace IT Support Chatbot
*A Python-based chatbot that simulates IT helpdesk support using keyword logic and an API fallback for unknown issues.*

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 🧠 Overview
Grace is a semi-static chatbot built in Python to simulate real-world IT support conversations.  
She uses a small local knowledge base for common technical issues (like Wi-Fi, password resets, or login errors),  
and an optional API fallback for questions she doesn’t recognize.  

## 🎥 [Watch Demo Video](Grace%20Demo.mov)

*(Grace walks through Wi-Fi troubleshooting, password resets, and fallback handling.)*

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 💜 How to Use Grace (No Coding Needed)
**Download Grace**  
- Click the green **Code** button → **Download ZIP**

**Unzip the Folder**  
- Double-click the ZIP file (Mac) or right-click → **Extract All** (Windows)

**Run Grace**  
- Open the folder and double-click `grace_agent.py`  
- If it doesn’t open, right-click → **Open With → Python**

**Start Chatting**  
- Type your IT question (e.g., *“How do I reset my password?”*) and press **Enter**  
- Grace will respond instantly  

💡 *If she doesn’t know the answer, she’ll use her API connection to find one.*

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 💻 Developer Setup
Follow these steps to set up and run Grace locally.

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

### - Clone the Repository
```bash
git clone https://github.com/daleciajones/grace-it-support-chatbot.git
cd grace-it-support-chatbot
```
## Create and Activate a Virtual Environment
macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
# Windows
```bash
python -m venv venv
venv\Scripts\activate
```
# Install Dependencies
-Grace only requires the requests library, but you can install everything from the requirements.txt file for convenience:
```bash
pip install -r requirements.txt
```
- Set Up Your API Key

Grace can use a fallback API when she doesn’t recognize a question.

# macOS / Linux
```bash
export OPENAI_API_KEY="your_api_key_here"
```
# Windows PowerShell
```bash
setx OPENAI_API_KEY "your_api_key_here"
```

## 💡 Restart your terminal after setting the key to apply changes.

-Run Grace
```bash
python3 grace_agent.py
```


Grace will start in interactive mode — ready to handle basic IT support queries through her local knowledge base, and API fallback when connected online.

## ⚙️ Additional Notes

Built with Python 3.8+

Designed for command-line execution

Stores logs and responses locally for easy debugging

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

✨ Project Vision

Grace represents my early steps in Python development and automation.She blends logic, structure, and human-like interaction.

Her purpose is simple: to make IT support feel seamless and human. 
