from openai import OpenAI
from dotenv import load_dotenv
import os
import random

# --- Load environment variables securely ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    print("Grace: I’m offline right now — please check my connection or API settings 💜")
    client = None  # Grace won’t run without this key, but stays friendly


# --- Grace’s fallback responses by category ---
fallback_categories = {
    "network": [
        "Grace: I don’t have that specific network fix yet, but I can walk you through checking your Wi-Fi connection.",
        "Grace: That might be a connectivity issue. Try restarting your router or verifying your network adapter settings."
    ],
    "password": [
        "Grace: I can’t reset passwords directly, but I can guide you through the password reset process.",
        "Grace: Make sure your password meets your company’s security policy — length, symbols, and numbers all matter!"
    ],
    "hardware": [
        "Grace: I’m not sure about that hardware issue, but I can help you check drivers or connection ports.",
        "Grace: It might be a hardware fault — try unplugging and reconnecting your device before escalating."
    ],
    "permissions": [
        "Grace: It sounds like a permissions issue. You might not have access rights for that action — try contacting your admin.",
        "Grace: Let’s verify your account permissions before proceeding — that often resolves access issues."
    ],
    "webcam": [
        "Grace: Let’s make sure your webcam is enabled in your system settings and not blocked by another app.",
        "Grace: Try unplugging and reconnecting your webcam — and check if your browser or app has permission to access it."
    ],
    "default": [
        "Grace: Hmm, I don’t have that information yet — but I can log it for review or help you troubleshoot another issue!",
        "Grace: I’m not sure about that one, but I can assist with other IT topics like passwords or Wi-Fi."
    ]
}


# --- Grace’s introduction ---
if client:
    print("Hello! I’m Grace, your IT Support Assistant.")
    print("I can help with password resets, Wi-Fi issues, and other common IT problems you may run into.\n")
    print("Type 'exit' anytime to end the conversation.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Grace: Goodbye! Stay productive 💜")
            break

        # --- Chatbot response ---
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Grace, a friendly IT Support Assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        print("Grace:", response.choices[0].message.content)