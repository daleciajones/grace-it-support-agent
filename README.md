# 💜 Grace IT Support Agent
*A Python chatbot for IT helpdesk support and AWS IAM identiy checks.*

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 🧠 Overview
Grace uses a local knowledge base for IT support topics and integrates with AWS IAM via boto3 to list users, view permissons, check MFA, and review acess keys.  

## ✨ Key Features

**IT Support (Local Knowledge Base)**
- Password reset guidance
- Permissions / access request steps
- Webcam & microphone troubleshooting
- Hardware / software request instructions
- Wi-Fi / network troubleshooting

**AWS IAM Security Automation**
- `list iam users` – show all IAM users in the account
- `check iam permissions for <user>` – summarize groups and policies
- `check iam mfa for <user>` – report whether MFA is enabled
- `check iam access keys for <user>` – list keys
- `show iam policy <name>` – view policy JSON for a given IAM policy

**Extras**
- Conversation logging to `grace_chat.log`
- Simple rule-based intent detection
- Easy to customize by editing `knowledgebase.txt`

## 🎥 [Watch Demo Video](Grace%20Demo.mov)

*(Grace walks through Wi-Fi troubleshooting, password resets, and fallback handling.)*

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 💜 How to Use Grace (No Coding Needed)

**Prerequisites**
- Python 3.8+ installed
- An AWS account with IAM permissions to list users/policies
- AWS credentials configured locally (via `aws configure` or environment variables)

**Download Grace**
- Click the green **Code** button → **Download ZIP**
- Extract the folder.

**Run Grace**
1. Open a terminal in the extracted folder.
2. (Optional but recommended) activate the virtual environment (see Developer Setup below).
3. Run:

   ```bash
   python3 grace_agent.py

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

-Run Grace
```bash
python3 grace_agent.py
```
Grace will start in interactive mode — ready to handle basic IT support queries through her local knowledge base.

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

# 🔐 IAM Setup (Step-by-Step Guide)

Grace can run without AWS, but to unlock her cloud-security features  listing IAM users, checking permissions, reviewing MFA, and analyzing access keys you’ll need a small IAM environment set up in your AWS account.

This setup takes only a few minutes and gives Grace real data to analyze.

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 1. Sign in to AWS IAM
- Log in to the AWS Console
- Open **IAM** from the Services menu

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 2. Create Test IAM Users

Create a few sample users Grace can inspect:

- `developer-user`
- `analyst-user`
- `support-user`

**Steps:**

1. Go to **IAM → Users → Create user**
2. Enter a username (e.g., `developer-user`)
3. Choose whether they need:
   - Console access (optional)
   - Programmatic access (optional)
4. Complete setup and repeat for the remaining users

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 3. Create IAM Groups

Groups represent roles in a real organization. Create three groups:

- `Developer`
- `Analyst`
- `Support`

**Steps:**

1. Open **IAM → User groups → Create group**
2. Name the group (e.g., `Developer`)
3. Add the appropriate user(s)
4. Repeat for the other groups

Grace will later identify group membership, such as:

> “developer-user belongs to the Developer group.”

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## 4. Add Inline Policies to Groups

This project uses inline policies attached directly to groups.  
All groups and users are intentionally configured as **sandbox** or **read-only** roles to demonstrate  **least privilege** access control. 

Example inline policies used in this project:

- `DeveloperSandboxAccess`  
  → Minimal developer testing permissions (no write access to production resources)

- `AnalystReadOnlyLogs`  
  → Read-only access focused on log review and investigation

- `SupportReadOnlySandbox`  
  → Basic support troubleshooting permissions with sandbox-only visibility

**Steps to add the policies:**
1. Go to **IAM → User groups**
2. Select a group (e.g., `Developer`)
3. Open the **Permissions** tab
4. Choose **Add permissions → Create inline policy**
5. Use the visual editor to assign minimal permissions needed for that group
6. Save the policy using the names above


**Steps:**
1. Go to **IAM → User groups**
2. Select a group (e.g., `Developer`)
3. Open the **Permissions** tab
4. Choose **Add permissions → Create inline policy**
5. Use the visual editor to assign a few simple permissions
6. Save the policy with a clear name:
   - `DeveloperBasicAccess`
   - `AnalystReadOnly`
   - `SupportTroubleshooting`

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## After Setup, Grace Can Perform:

1. **List IAM users**  
   - Run: `list iam users`  
   - Grace will show all IAM users in your AWS account.

2. **Check IAM permissions**  
   - Run: `check iam permissions for developer-user`  
   - Grace summarizes inline and group policies.

3. **Check MFA status**  
   - Run: `check iam mfa for analyst-user`  
   - Grace indicates whether MFA is enabled.

4. **Review access keys**  
   - Run: `check iam access keys for support-user`  
   - Grace shows key IDs,

⋆｡°✩｡⋆☁︎⋆｡°✩｡⋆

## ✨ Project Vision

Grace started as a small IT helper, but she’s grown into a full IT + Cloud Security assistant.  
She blends logic, structure, and gentle human-like interaction while performing real AWS IAM checks like permissions, MFA, and access keys.

Her purpose is to make technical workflows feel seamless, secure, and beautifully simple — all through Python.