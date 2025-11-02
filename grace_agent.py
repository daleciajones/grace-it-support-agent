from datetime import datetime
import os

# ==============================
# Grace's Configuration
# ==============================
KB_FILE = os.path.join(os.path.dirname(__file__), "knowledgebase.txt")
CHAT_LOG_FILE = "grace_chat.log"
# ==============================
# Knowledge Base Section Headers
# ==============================
KB_SECTIONS = {
    "password": "=== PASSWORD RESET INSTRUCTIONS ===",
    "permissions": "=== PERMISSIONS / ACCESS REQUEST INSTRUCTIONS ===",
    "av": "=== WEBCAM & MICROPHONE TROUBLESHOOTING ===",
    "hw_sw": "=== HARDWARE & SOFTWARE REQUEST INSTRUCTIONS ===",
    "wifi": "=== WIFI CONNECTION TROUBLESHOOTING ==="
}

# ==============================
# Fallback Responses
# ==============================
FALLBACK_RESPONSES = [
    "Grace: I’m unable to locate my internal IT support instructions at the moment. Please check back later.",
    "Grace: I can’t seem to find the right section in my knowledge base. Let’s double-check the topic together.",
    "Grace: I don’t have that information stored yet, but I can help you with Wi-Fi, password resets, or access requests.",
    "Grace: I’m missing the documentation for that issue right now. You might want to contact the IT Helpdesk for further assistance."
]

# ==============================
# Logging
# ==============================
def log_message(role: str, message: str):
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] {role}: {message}\n")

# ==============================
# Load Knowledge Base Section
# ==============================
def load_kb_section(header):
    if not os.path.exists(KB_FILE):
        return "Grace: My knowledge base file is missing. Please make sure 'knowledgebase.txt' is in the same folder."

    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return f"Grace: Error reading my internal documentation: {e}"

    content = []
    in_section = False

    for line in lines:
        # Start reading when header is found
        if line.strip() == header:
            in_section = True
            continue

        # Stop reading when a new header begins
        if in_section and line.strip().startswith("===") and line.strip() != header:
            break

        if in_section:
            content.append(line)

    if not content:
        import random
        return random.choice(FALLBACK_RESPONSES)

    return "".join(content).strip()

# ==============================
# Grace Introduction
# ==============================
print("Hello, I’m Grace, your IT Support Assistant.")
print("I can help with password resets, Wi-Fi issues, permissions, and other common IT problems.")
print("Type 'exit' anytime to close our chat.\n")

# ==============================
# Chat Loop
# ==============================
while True:
    user_input = input("You: ").lower().strip()

    if user_input in ["exit", "quit"]:
        print("Grace: Goodbye! Remember to reboot if something isn’t working — it fixes more than you’d think.")
        break

    # Detect intent
    if "password" in user_input:
        header = KB_SECTIONS["password"]
    elif "permission" in user_input or "access" in user_input:
        header = KB_SECTIONS["permissions"]
    elif "camera" in user_input or "microphone" in user_input:
        header = KB_SECTIONS["av"]
    elif "hardware" in user_input or "software" in user_input:
        header = KB_SECTIONS["hw_sw"]
    elif "wifi" in user_input or "wi-fi" in user_input:
        header = KB_SECTIONS["wifi"]
    else:
        print("Grace: I’m not sure which issue this relates to. Could you clarify if it’s about Wi-Fi, passwords, permissions, or something else?")
        continue

    # Load and respond
    response = load_kb_section(header)
    print(response)

    # Log interaction
    log_message("user", user_input)
    log_message("grace", response)
