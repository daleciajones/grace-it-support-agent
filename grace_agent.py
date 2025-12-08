import boto3
from datetime import datetime
import os

CHAT_LOG_FILE = "grace_chat.log"
KB_FILE = "knowledgebase.txt"

# =========================
# Knowledge Base Section Headers
# =========================
KB_SECTIONS = {
    "password": "=== PASSWORD RESET INSTRUCTIONS ===",
    "permissions": "=== PERMISSIONS / ACCESS REQUEST INSTRUCTIONS ===",
    "av": "=== WEBCAM & MICROPHONE TROUBLESHOOTING ===",
    "hw_sw": "=== HARDWARE / SOFTWARE REQUEST INSTRUCTIONS ===",
    "wifi": "=== WIFI CONNECTION TROUBLESHOOTING ===",
}

# =========================
# Logging
# =========================
def log_message(role: str, message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {role.upper()}: {message}\n")

# =========================
# Load Knowledge Base Sections
# =========================
def load_kb_section(header: str) -> str:
    if not os.path.exists(KB_FILE):
        return "Grace: I cannot locate my internal IT support instructions. Please try again later."

    with open(KB_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    content = []
    in_section = False
    for line in lines:
        if line.strip().startswith("===") and line.strip().endswith("==="):
            if in_section:
                break
            if line.strip() == header:
                in_section = True
                content.append(line)
        else:
            if in_section:
                content.append(line)

    if not content:
        return "Grace: I have not been trained on detailed steps for that yet."

    return "".join(content).strip()

# =========================
# AWS IAM AUTOMATION
# =========================
iam = boto3.client("iam")

def list_users():
    response = iam.list_users()
    return response["Users"]

# =========================
# Intent Detection Rules
# =========================
def detect_intent(text: str):
    t = text.lower()

    if any(x in t for x in ["password", "log in", "login", "sign in", "locked", "expired"]):
        return "password"
    if any(x in t for x in ["permission", "access denied", "request access", "file access"]):
        return "permissions"
    if any(x in t for x in ["webcam", "camera", "microphone", "mic", "zoom", "teams"]):
        return "av"
    if any(x in t for x in ["hardware", "software", "install", "new laptop", "monitor", "order"]):
        return "hw_sw"
    if any(x in t for x in ["wifi", "internet", "wi-fi", "network"]):
        return "wifi"

    # NEW: IAM users intent
    if "iam" in t and "user" in t:
        return "iam_users"

    return None

# =========================
# Introduction
# =========================
print("Hello, I’m Grace, your IT Support Assistant.")
print("I can help with password resets, Wi-Fi issues, permissions, webcam/mic problems,")
print("hardware/software requests, and I can also list IAM users from AWS.")
print("Type 'exit' anytime to close our chat.\n")

# =========================
# Fallback Responses
# =========================
fallback_messages = [
    "I’m not trained on that yet, but I’m learning more every day.",
    "I may not have the information for that topic, but I can assist with technology issues such as login or Wi-Fi.",
    "That is outside my knowledge right now. Could you describe a technology-related issue?"
]

# =========================
# Chat Loop
# =========================
while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ("exit", "quit"):
        goodbye = "Thank you for contacting IT. I hope the rest of your day goes smoothly."
        print("Grace:", goodbye)
        log_message("grace", goodbye)
        break

    log_message("user", user_input)

    intent = detect_intent(user_input)

    # First: handle IAM intent
    if intent == "iam_users":
        try:
            users = list_users()
            if not users:
                resp = "I did not find any IAM users in this account."
            else:
                lines = ["Here are the IAM users I found:"]
                for u in users:
                    lines.append(f" - {u.get('UserName', '(no name)')}")
                resp = "\n".join(lines)
        except Exception as e:
            resp = f"I tried to list IAM users, but I ran into an error: {e}"
        print("Grace:", resp)
        log_message("grace", resp)
        continue

    # Next: handle knowledge base intents
    if intent in KB_SECTIONS:
        header = KB_SECTIONS[intent]
        kb_resp = load_kb_section(header)
        print("Grace:", kb_resp)
        log_message("grace", kb_resp)
    else:
        # Rotate fallback messages
        fallback = fallback_messages[0]
        fallback_messages.append(fallback_messages.pop(0))
        print("Grace:", fallback)
        log_message("grace", fallback)
