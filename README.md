# MLPCompanion

MLPCompanion is a Telegram companion bot with long-term memory, relationship progression, internal state, and autonomous messages.

The current character is Iskorka. The project is built as a digital companion, not just a command bot: it remembers users, reacts to relationship level, keeps emotional/internal state, can process text, stickers, and images, and can initiate messages.

## What Is Inside

- Telegram bot entry point: `main.py`
- AI response manager: `ai/ai_manager.py`
- Character style/personality: `ai/personalities.py`
- Long-term memory manager: `memory_manager.py`
- Memory analysis: `memory/memory_brain.py`
- Relationship system: `memory/relationship_brain.py`
- Internal state system: `memory/iskorka_state.py`
- Event logging helpers: `bot_events.py`

## What Is Not Stored In Git

Private runtime data is intentionally ignored:

- `.env`
- Telegram bot token
- Gemini/OpenAI API keys
- user memory files
- chat history
- relationship state files
- bot logs
- virtual environment files

This is important because the repository may be public.

## Requirements

- Python 3.12 or newer is recommended
- Telegram bot token from BotFather
- Gemini API key

OpenAI API key is optional unless OpenAI-specific code is used.

## Local Setup

Clone the repository:

```powershell
git clone https://github.com/matvey600/Repositoriy-MLP-Bot.git
cd Repositoriy-MLP-Bot
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `.env` from the example:

```powershell
copy .env.example .env
```

Fill `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=
```

Run the bot:

```powershell
python main.py
```

## Updating Code

After changing files:

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```

Before pushing, make sure `.env` and `memory/users/` are not staged.

## Server Notes

On a server, the same setup is used:

```bash
git clone https://github.com/matvey600/Repositoriy-MLP-Bot.git
cd Repositoriy-MLP-Bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The server must have environment variables:

```env
BOT_TOKEN=...
GEMINI_API_KEY=...
OPENAI_API_KEY=
```

For 24/7 hosting, use a process manager or platform service so `python main.py` restarts automatically if it crashes.

## Memory

Runtime memory is created locally under `memory/`.

User-specific memory is stored under:

```text
memory/users/<telegram_user_id>/
```

These files should stay private and should not be uploaded to GitHub.
