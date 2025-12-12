import boto3
import re
from datetime import datetime
import os

# =========================
# Files
# =========================
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
        return "Grace: I can’t find my IT support instructions right now, but I’m here to help however I can."

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
        return "Grace: I haven’t learned the detailed steps for that yet, but I’m still growing every day."

    return "".join(content).strip()


# =========================
# Intent Detection
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

    return None


# =========================
# AWS IAM AUTOMATION
# =========================
iam = boto3.client("iam")


def list_iam_users():
    return iam.list_users().get("Users", [])


def check_iam_mfa(username: str) -> str:
    devices = iam.list_mfa_devices(UserName=username).get("MFADevices", [])
    if not devices:
        return f"Here’s what I found: '{username}' does *not* have MFA enabled. Enabling MFA adds an important layer of security."

    lines = [
        f"Great news — '{username}' has MFA enabled. Their account is protected.",
        ""
    ]
    for d in devices:
        lines.append(f"- Device ARN: {d.get('SerialNumber')}")
        lines.append(f"  Enabled: {d.get('EnableDate')}")
    return "\n".join(lines)


def get_access_key_status(username: str) -> str:
    keys = iam.list_access_keys(UserName=username).get("AccessKeyMetadata", [])
    if not keys:
        return f"'{username}' doesn’t have any access keys assigned."

    lines = [f"Here are the access keys for '{username}':", ""]
    for k in keys:
        lines.append(f"- KeyId: {k.get('AccessKeyId')}")
        lines.append(f"  Status: {k.get('Status')}")
        lines.append(f"  Created: {k.get('CreateDate')}")
    return "\n".join(lines)


# === Your existing permission helper, unchanged ===
def get_iam_permissions(username: str) -> str:
    """
    Summarize IAM permissions for a user by listing:
    - Groups they belong to
    - Inline policies on groups
    - Inline policies on the user
    - Attached managed policies on the user
    """
    lines = []

    # Groups the user belongs to
    groups_resp = iam.list_groups_for_user(UserName=username)
    groups = groups_resp.get("Groups", [])
    if groups:
        lines.append("Groups:")
        for g in groups:
            group_name = g["GroupName"]
            lines.append(f"  - {group_name}")

            # Inline policies on the group
            inline_group = iam.list_group_policies(GroupName=group_name)["PolicyNames"]
            if inline_group:
                lines.append(f"    Inline policies: {', '.join(inline_group)}")

    # Inline policies directly on the user
    inline_user = iam.list_user_policies(UserName=username)["PolicyNames"]
    if inline_user:
        lines.append("User inline policies:")
        lines.append("  " + ", ".join(inline_user))

    # Attached managed policies on the user
    attached_user = iam.list_attached_user_policies(UserName=username)["AttachedPolicies"]
    if attached_user:
        lines.append("Attached user managed policies:")
        for p in attached_user:
            lines.append(f"  - {p['PolicyName']}")

    if not lines:
        return "I didn’t find any groups or policies assigned to this user."

    return "\n".join(lines)


# =========================
# Grace Introduction (new)
# =========================
print("""
Hi there, I’m Grace — your IT & Cloud Security assistant.
My goal is to guide you through technical issues with clarity, patience, and care.

I can help you with things like:
• Password resets
• Wi-Fi & connectivity issues
• Permission or access problems
• Camera & microphone troubleshooting
• Software or hardware questions
• AWS IAM tasks (listing users, checking MFA, reviewing permissions, and access key status)

Just let me know what you need, and I’ll do my best to support you.
If you’d like to end our session, you can type 'exit' or 'quit' anytime.

""")


# =========================
# Fallback Messages
# =========================
fallback_messages = [
    "I’m not trained on that yet, but I’m learning more every day.",
    "I may not have that information, but I can help with IT issues like login or Wi-Fi.",
    "That’s outside my knowledge right now — could you describe a technology issue you’re having?",
]


# =========================
# Chat Loop
# =========================
while True:
    user_input = input("You: ").strip()

    # Exit if the *word* 'exit' or 'quit' appears anywhere
    if re.search(r"\b(exit|quit)\b", user_input, re.IGNORECASE):
        goodbye = "Thank you for chatting with me. I hope the rest of your day goes smoothly."
        print("Grace:", goodbye)
        log_message("grace", goodbye)
        break

    # Log what the user said
    log_message("user", user_input)
    text = user_input.lower()

    # =========================
    # AWS IAM Commands FIRST
    # =========================

    # 1) List IAM users
    # Works with: "list iam users", "list the iam users",
    #             "Hi Grace, can you list the IAM users?"
    if re.search(r"\blist\b.*\biam users\b", text):
        try:
            users = list_iam_users()
            if users:
                names = [u.get("UserName", "(no name)") for u in users]
                reply = "Here are the IAM users I found:\n\n- " + "\n- ".join(names)
            else:
                reply = "I didn’t find any IAM users in this account."
        except Exception as e:
            reply = f"I tried to list IAM users, but something went wrong: {e}"

        print("Grace:", reply)
        log_message("grace", reply)
        continue

    # 2) Check IAM MFA
    # Works with: "check iam mfa for maya.developer",
    #             "can you check mfa for maya.developer"
    if re.search(r"\b(check|show|verify)\b.*\bmfa\b.*\bfor\b", text):
        username = user_input.split("for", 1)[-1].strip().rstrip(".!,?")
        try:
            reply = check_iam_mfa(username)
        except Exception as e:
            reply = f"I tried to check MFA for '{username}', but something went wrong: {e}"

        print("Grace:", reply)
        log_message("grace", reply)
        continue

    # 3) Check IAM access keys
    # Works with: "check iam access keys for alex.support",
    #             "can you check access keys for alex.support"
    if re.search(r"\b(check|show|list)\b.*\b(access keys?|keys?)\b.*\bfor\b", text):
        username = user_input.split("for", 1)[-1].strip().rstrip(".!,?")
        try:
            reply = get_access_key_status(username)
        except Exception as e:
            reply = f"I tried to check access keys for '{username}', but I ran into an issue: {e}"

        print("Grace:", reply)
        log_message("grace", reply)
        continue


    # =========================
    # IT SUPPORT INTENT HANDLING (KB)
    # =========================
    intent = detect_intent(user_input)

    if intent:
        header = KB_SECTIONS[intent]
        kb_resp = load_kb_section(header)
        print("Grace:", kb_resp)
        log_message("grace", kb_resp)
        continue

    # =========================
    # Fallback
    # =========================
    fallback = fallback_messages[0]
    fallback_messages.append(fallback_messages.pop(0))

    print("Grace:", fallback)
    log_message("grace", fallback)
