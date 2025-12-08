import boto3
import re
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
        line_stripped = line.strip()
        if line_stripped.startswith("===") and line_stripped.endswith("==="):
            # Hit a section header
            if in_section:
                # We were in the right section and hit the next one -> stop
                break
            if line_stripped == header:
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
    return response.get("Users", [])

def get_user_permissions(username: str) -> str:
    """
    Returns a summary of a user's IAM permissions:
    - Attached user policies
    - Inline user policies
    - Groups
    - Attached group policies
    - Inline group policies
    """
    # Attached user policies
    attached_user_policies = iam.list_attached_user_policies(
        UserName=username
    ).get("AttachedPolicies", [])

    # Inline user policies
    inline_user_policies = iam.list_user_policies(
        UserName=username
    ).get("PolicyNames", [])

    # Groups
    groups = iam.list_groups_for_user(UserName=username).get("Groups", [])

    attached_group_policies = []
    inline_group_policies = []

    for g in groups:
        gname = g["GroupName"]

        # Attached policies on the group
        gap = iam.list_attached_group_policies(
            GroupName=gname
        ).get("AttachedPolicies", [])
        for p in gap:
            attached_group_policies.append((gname, p.get("PolicyName", "(no name)")))

        # Inline policies on the group
        gip = iam.list_group_policies(GroupName=gname).get("PolicyNames", [])
        for pname in gip:
            inline_group_policies.append((gname, pname))

    lines = []
    lines.append(f"Here are the IAM permissions for user '{username}':\n")

    # Attached user policies
    lines.append("Attached user policies:")
    if attached_user_policies:
        for p in attached_user_policies:
            lines.append(f" - {p.get('PolicyName', '(no name)')}")
    else:
        lines.append(" - (none)")

    # Inline user policies
    lines.append("\nInline user policies:")
    if inline_user_policies:
        for pname in inline_user_policies:
            lines.append(f" - {pname}")
    else:
        lines.append(" - (none)")

    # Groups
    lines.append("\nGroups:")
    if groups:
        for g in groups:
            lines.append(f" - {g.get('GroupName', '(no name)')}")
    else:
        lines.append(" - (none)")

    # Attached group policies
    lines.append("\nAttached group policies:")
    if attached_group_policies:
        for gname, pname in attached_group_policies:
            lines.append(f" - {pname} (via group: {gname})")
    else:
        lines.append(" - (none)")

    # Inline group policies
    lines.append("\nInline group policies:")
    if inline_group_policies:
        for gname, pname in inline_group_policies:
            lines.append(f" - {pname} (via group: {gname})")
    else:
        lines.append(" - (none)")

    return "\n".join(lines)

def get_mfa_status(username: str) -> str:
    devices = iam.list_mfa_devices(UserName=username).get("MFADevices", [])
    if not devices:
        return f"User '{username}' does NOT have MFA enabled ❌"
    lines = [f"User '{username}' HAS MFA enabled ✔️", ""]
    for d in devices:
        serial = d.get("SerialNumber", "(no serial)")
        enable_date = d.get("EnableDate")
        lines.append(f"- Device: {serial}, Enabled: {enable_date}")
    return "\n".join(lines)

def get_access_key_status(username: str) -> str:
    keys = iam.list_access_keys(UserName=username).get("AccessKeyMetadata", [])
    if not keys:
        return f"User '{username}' has no access keys."
    lines = [f"Access keys for user '{username}':", ""]
    for k in keys:
        key_id = k.get("AccessKeyId")
        status = k.get("Status")
        created = k.get("CreateDate")
        lines.append(f"- KeyId: {key_id}, Status: {status}, Created: {created}")
    return "\n".join(lines)

def get_policy_document(identifier: str) -> str:
    """
    Try to show an IAM policy by ARN or by name.
    This is a simple helper; in a real system you'd want stricter resolution.
    """
    policy_arn = identifier.strip()

    # If the identifier doesn't look like an ARN, try to find by name.
    if not policy_arn.startswith("arn:aws:iam::"):
        # Try listing customer-managed policies and matching by PolicyName
        paginator = iam.get_paginator("list_policies")
        for page in paginator.paginate(Scope="All"):
            for p in page.get("Policies", []):
                if p.get("PolicyName") == identifier:
                    policy_arn = p.get("Arn")
                    break
            if policy_arn.startswith("arn:aws:iam::"):
                break

    if not policy_arn.startswith("arn:aws:iam::"):
        return f"I could not find a policy matching '{identifier}'."

    policy = iam.get_policy(PolicyArn=policy_arn)["Policy"]
    version_id = policy["DefaultVersionId"]
    version = iam.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=version_id
    )["PolicyVersion"]

    return f"Policy '{policy.get('PolicyName', '(no name)')}' (ARN: {policy_arn})\n\nDocument:\n{version['Document']}"

# =========================
# Intent Detection Rules
# =========================
def detect_intent(text: str):
    t = text.lower()

    # Regular IT intents
    if any(x in t for x in ["password", "log in", "login", "sign in", "locked", "expired"]):
        return "password"
    if any(x in t for x in ["permission", "access denied", "request access", "file access"]) and "iam" not in t:
        return "permissions"
    if any(x in t for x in ["webcam", "camera", "microphone", "mic", "zoom", "teams"]):
        return "av"
    if any(x in t for x in ["hardware", "software", "install", "new laptop", "monitor", "order"]):
        return "hw_sw"
    if any(x in t for x in ["wifi", "internet", "wi-fi", "network"]):
        return "wifi"

    # IAM-specific intents
    if "iam" in t and "user" in t and "permission" not in t and "mfa" not in t and "key" not in t and "policy" not in t:
        return "iam_users"

    if "iam" in t and "permission" in t:
        return "iam_permissions"

    if "iam" in t and "mfa" in t:
        return "iam_mfa"

    if "iam" in t and ("access key" in t or "access keys" in t or "keys" in t):
        return "iam_keys"

    if "iam" in t and "policy" in t:
        return "iam_policy"

    return None

# =========================
# Simple helpers to parse usernames / policy names from text
# =========================
def extract_after_keyword(text: str, keyword: str) -> str | None:
    """
    Naive helper: return the first word after a given keyword.
    E.g. "check iam permissions for admin user" with keyword "for" -> "admin"
    """
    lower = text.lower()
    if keyword not in lower:
        return None
    before, after = lower.split(keyword, 1)
    # Get same slice from original text to preserve case
    original_after = text[len(before) + len(keyword):].strip()
    if not original_after:
        return None
    first = original_after.split()[0]
    return first.replace("?", "").strip()

# =========================
# Introduction
# =========================
print("Hello, I’m Grace, your IT & Cloud Security Assistant.")
print("I can help with password resets, Wi-Fi issues, permissions, webcam/mic problems,")
print("hardware/software requests, and AWS IAM tasks like listing users and checking permissions, MFA, keys, and policies.")
print("Include the word 'exit' or 'quit' in a sentence any time to close our chat.\n")

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

    # Exit if 'exit' or 'quit' appears anywhere in the sentence
    lower_text = user_input.lower()
    if "exit" in lower_text or "quit" in lower_text:
        goodbye = "Thank you for contacting IT. I hope the rest of your day goes smoothly."
        print("Grace:", goodbye)
        log_message("grace", goodbye)
        break

    log_message("user", user_input)
    intent = detect_intent(user_input)

    # ----- IAM: list users -----
    if intent == "iam_users":
        try:
            users = list_users()
            if not users:
                resp = "I did not find any IAM users in this account."
            else:
                lines = ["Here are the IAM users I found:", ""]
                for u in users:
                    lines.append(f" - {u.get('UserName', '(no name)')}")
                resp = "\n".join(lines)
        except Exception as e:
            resp = f"I tried to list IAM users, but I ran into an error: {e}"
        print("Grace:", resp)
        log_message("grace", resp)
        continue

    # ----- IAM: permissions for a user -----
    if intent == "iam_permissions":
        username = extract_after_keyword(user_input, "for")
        if not username:
            resp = "Please specify a username, e.g. 'check IAM permissions for admin'."
        else:
            try:
                resp = get_user_permissions(username)
            except Exception as e:
                resp = f"I tried to check IAM permissions for '{username}', but I ran into an error: {e}"
        print("Grace:", resp)
        log_message("grace", resp)
        continue

    # ----- IAM: MFA status -----
    if intent == "iam_mfa":
        username = extract_after_keyword(user_input, "for")
        if not username:
            resp = "Please specify a username, e.g. 'check IAM MFA for admin'."
        else:
            try:
                resp = get_mfa_status(username)
            except Exception as e:
                resp = f"I tried to check MFA for '{username}', but I ran into an error: {e}"
        print("Grace:", resp)
        log_message("grace", resp)
        continue

    # ----- IAM: access key status -----
    if intent == "iam_keys":
        username = extract_after_keyword(user_input, "for")
        if not username:
            resp = "Please specify a username, e.g. 'check IAM access keys for admin'."
        else:
            try:
                resp = get_access_key_status(username)
            except Exception as e:
                resp = f"I tried to check access keys for '{username}', but I ran into an error: {e}"
        print("Grace:", resp)
        log_message("grace", resp)
        continue

    # ----- IAM: show policy -----
    if intent == "iam_policy":
        # Try to extract after 'policy'
        policy_identifier = extract_after_keyword(user_input, "policy")
        if not policy_identifier:
            resp = "Please specify a policy name or ARN, e.g. 'show IAM policy AdministratorAccess'."
        else:
            try:
                resp = get_policy_document(policy_identifier)
            except Exception as e:
                resp = f"I tried to show the IAM policy '{policy_identifier}', but I ran into an error: {e}"
        print("Grace:", resp)
        log_message("grace", resp)
        continue

    # ----- Knowledge base intents -----
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
