import json
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import winotify

# Load environment variables
load_dotenv()

# Configuration
RANDOM_WORD_API = "https://random-word-api.herokuapp.com/word"
FREE_DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"
HISTORY_FILE = "word_history.json"
MAX_HISTORY_SIZE = 100  # Keep last 100 words to avoid repetition
NOTIFICATION_DURATION = "short"  # "short" or "long"


def _get_icon_path():
    """Return absolute path to word-vomit.png icon."""
    icon_path = Path(__file__).resolve().parent / "word-vomit.png"
    return str(icon_path)


def load_history():
    """Load word history from JSON file."""
    if Path(HISTORY_FILE).exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """Save word history to JSON file."""
    # Keep only the most recent words
    if len(history) > MAX_HISTORY_SIZE:
        history = history[-MAX_HISTORY_SIZE:]
    
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving history: {e}")


def fetch_random_word():
    """Fetch a random word from the API."""
    try:
        response = requests.get(RANDOM_WORD_API, timeout=10)
        response.raise_for_status() #checks for non200 status codes
        words = response.json()
        if words and isinstance(words, list) and len(words) > 0:
            return words[0].lower()
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random word: {e}")
        return None


def fetch_definition(word):
    """Fetch word definition from Free Dictionary API."""
    try:
        url = f"{FREE_DICTIONARY_API}/{word}"
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return None, 404

        response.raise_for_status()

        data = response.json()

        # Extract the first available definition
        definition = None
        if isinstance(data, list) and data:
            entry = data[0]
            if isinstance(entry, dict):
                for meaning in entry.get("meanings", []) or []:
                    for d in meaning.get("definitions", []) or []:
                        if isinstance(d, dict) and d.get("definition"):
                            definition = d["definition"]
                            break
                    if definition:
                        break

        return definition, response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error fetching definition: {e}")
        return None, None


def show_notification(word, definition=None):
    """Show Windows notification with word and definition."""
    try:
        app_id = "Word Vomit"
        title = f"Word of the Hour: {word.capitalize()}"

        # Keep the toast short; show full meaning when user clicks the action button.
        if definition:
            message = "Click 'Show meaning' to view the definition."
        else:
            message = f"Learn a new word: {word.capitalize()}"

        toast = winotify.Notification(
            app_id=app_id,
            title=title,
            msg=message,
            icon=_get_icon_path(),
            duration=NOTIFICATION_DURATION
        )

        # When clicked, open a page that shows the word's meaning.
        # Using Wiktionary as a simple, public dictionary front-end.
        toast.add_actions(
            label="Show meaning",
            launch=f"https://www.merriam-webster.com/dictionary/{word}"
        )
        
        toast.show()
        print(f"Notification shown: {word.capitalize()}")
        return True
    except Exception as e:
        print(f"Error showing notification: {e}")
        return False


def get_new_word(history, exclude_words=None):
    """Get a new word that hasn't been used recently."""
    max_attempts = 20  # Prevent infinite loops
    attempts = 0
    exclude_words = exclude_words or set()
    
    while attempts < max_attempts:
        word = fetch_random_word()
        
        if not word:
            attempts += 1
            continue
        
        # Check if word is in recent history
        recent_words = [h["word"] for h in history[-50:]]  # Check last 50 words
        if word not in recent_words and word not in exclude_words:
            return word
        
        attempts += 1
    
    # If we couldn't find a new word after max attempts, return the last fetched word
    return word


def main():
    """Main function to fetch word, definition, and show notification."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting vocab notifier...")
    
    # Load history
    history = load_history()

    # Keep trying new words on 404 from dictionary API
    max_definition_attempts = 25
    attempted_words = set()
    word = None
    definition = None
    definition_status = None

    for _ in range(max_definition_attempts):
        word = get_new_word(history, exclude_words=attempted_words)
        if not word:
            continue

        attempted_words.add(word)
        definition, definition_status = fetch_definition(word)

        # Network or other request error: try a different word
        if definition_status is None:
            print(f"Error while fetching definition for '{word}'. Trying a new word...")
            continue

        # Non-200 and non-404 responses: retry with a new word
        if definition_status not in (200, 404):
            print(
                f"Dictionary API returned unexpected status {definition_status} "
                f"for '{word}'. Trying a new word..."
            )
            continue

        if definition_status == 404:
            print(f"No dictionary entry for '{word}' (404). Trying a new word...")
            continue

        # If we got a 200 but couldn't parse a definition, try another word.
        if definition_status == 200 and not definition:
            print(f"No usable definition for '{word}' despite 200. Trying a new word...")
            continue

        break

    if not word:
        print("Failed to fetch a random word. Skipping this notification.")
        return
    
    # Show notification
    success = show_notification(word, definition)
    
    if success:
        # Add to history
        history.append({
            "word": word,
            "definition": definition,
            "timestamp": datetime.now().isoformat()
        })
        save_history(history)
        print(f"Added '{word}' to history")
    else:
        print("Failed to show notification")


def run_scheduler():
    """Run the notifier every hour."""
    print("Vocab Notifier started. Running every hour...")
    print("Press Ctrl+C to stop.")
    
    # Run immediately on start
    main()
    
    # Then run every hour
    while True:
        try:
            time.sleep(3600)  # Sleep for 1 hour (3600 seconds)
            main()
        except KeyboardInterrupt:
            print("\nStopping vocab notifier...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Continuing...")
            time.sleep(60)  # Wait a minute before retrying on error


if __name__ == "__main__":
    run_scheduler()
