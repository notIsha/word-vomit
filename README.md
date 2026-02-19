# Word Vomit - Desktop Vocab Notifier

A Python desktop application that displays vocabulary word notifications on Windows every hour. Each notification includes a random word and its definition from the Free Dictionary API. This app was built with the help of a Cursor agent.

## Features

- 🎲 Fetches random words from Random Word API
- 📖 Retrieves definitions from Free Dictionary API (no API key required)
- 🔔 Shows Windows desktop notifications using winotify
- ⏰ Runs automatically every hour
- 📝 Tracks word history to avoid repetition
- 🛡️ Graceful error handling for API failures
- 🔐 Optional environment variables for future config

## Prerequisites

- Python 3.7 or higher
- Windows operating system

## Setup Instructions

### 1. Clone or Download the Project

```bash
cd word-vomit
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Environment Variables

Copy `.env.example` to `.env` if you need to add API keys or config for future use. The Free Dictionary API requires no API key.

## Running the Application

### Run Once (for testing)

```bash
python main.py
```

Press `Ctrl+C` to stop.

### Run in Background

To run the application continuously in the background:

1. **Using Task Scheduler (Windows)**:
   - Open Task Scheduler
   - Create a new task
   - Set trigger to run every hour
   - Set action to run: `python.exe` with arguments: `"C:\path\to\word-vomit\main.py"`
   - Set "Start in" directory to your project folder

2. **Using a terminal that stays open**:
   - Run `python main.py` in a terminal window
   - Keep the terminal window open

3. **Using a batch file**:
   Create `run.bat`:
   ```batch
   @echo off
   cd /d "%~dp0"
   python main.py
   ```
   Then double-click `run.bat` or add it to Windows startup

## How It Works

1. The application fetches a random word from the Random Word API
2. It checks the word history to avoid showing recently used words
3. It fetches the definition from the Free Dictionary API
4. A Windows notification is displayed with the word and definition
5. The word is saved to `word_history.json` for future reference
6. The process repeats every hour

## File Structure

```
word-vomit/
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env.example        # Example environment file
├── .env                # Optional config (not in git)
├── .gitignore          # Git ignore rules
└── word_history.json   # Word history (created automatically)
```

## Configuration

You can modify these settings in `main.py`:

- `MAX_HISTORY_SIZE`: Maximum number of words to keep in history (default: 100)
- `NOTIFICATION_DURATION`: Notification display duration - "short" or "long" (default: "short")
- `HISTORY_FILE`: Name of the history JSON file (default: "word_history.json")

## Troubleshooting

### Notification Not Showing

- Ensure Windows notifications are enabled for Python
- Check Windows notification settings in Settings > System > Notifications

### API Errors

- Check your internet connection
- The Free Dictionary API may not have definitions for all words (e.g., very obscure terms)
- The application will continue running even if API calls fail

### Word Repetition

- The app checks the last 50 words to avoid repetition
- If you see repeated words, increase `MAX_HISTORY_SIZE` or adjust the repetition check logic

## License

This project is open source and available for personal use.
