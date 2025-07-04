# 🧠 AskMyPC

**AskMyPC** is a local desktop assistant powered by Google's Gemini Pro 2.5, enabling users to control their Windows PC using natural language queries. Think of it as "Chat with your computer" — but with real power.

---

## ✨ Features

- 💬 Ask in plain English — "Shut down my PC", "List running tasks", "Clear temp files", etc.
- ⚡ Executes safe PowerShell commands under the hood
- 🔐 Keeps your API keys and environment variables secure
- 🧠 Powered by Gemini 2.5 Pro LLM (or any Gemini model)
- 🪟 Native to Windows (PowerShell-based command execution)
- 🖼️ Planned GUI support (WIP)

---

## 🛠️ Setup

### 1. Clone the Repo

```bash
git clone https://github.com/Dead-Pixel-cmd/AskMyPc.git
cd AskMyPc

2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt


3. Set Up .env
Create a .env file in the root folder:

env
Copy
Edit
GEMINI_API_KEY=your_gemini_api_key_here

Usage
```
python main.py
```
You'll be prompted to ask your PC something. Examples:
- Shut down the PC
- List all installed programs
- Empty the recycle bin
- Disable Wi-Fi
- Get system info
Example
You: Shut down the computer
AskMyPC: Do you want to run: shutdown /s /t 0 ? (y/n)
You: y
[OK] PC will shut down
Security
AskMyPC always confirms before executing a command. You remain in control.
(!) Be cautious when extending command sets. This tool is powerful.


Roadmap
- [x] Text-based natural language assistant
- [ ] GUI version (Tkinter or PyQt)
- [ ] Context memory using local storage
- [ ] Plugin system (for browsing files, media control, etc.)
- [ ] Local LLM support (for offline use)


Contributing
PRs are welcome! If you'd like to add features or improve code quality, feel free to fork and contribute.
License
This project is licensed under the MIT License