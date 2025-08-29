import os
import webbrowser
import subprocess
import platform
import json
import smtplib
import imaplib
import email
from email.header import decode_header
import re
from tts import speak

# Load config
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
    CONFIG = json.load(f)

SYSTEM = platform.system().lower()

# --- Helper functions ---
def get_app_path(app_name):
    """Return path for app (OS-detected)."""
    apps = CONFIG.get("applications", {})
    # Support dict: {"chrome": {"windows": path, "linux": path}}
    info = apps.get(app_name.lower())
    if isinstance(info, dict):
        return info.get(SYSTEM)
    return info

def open_application(app_name):
    app_path = get_app_path(app_name)
    if not app_path:
        speak(f"No path configured for {app_name} on {SYSTEM}.")
        return False
    try:
        if SYSTEM == "windows":
            os.startfile(app_path)
        elif SYSTEM == "linux":
            subprocess.Popen([app_path])
        else:
            speak(f"Unsupported OS for opening apps.")
            return False
        speak(f"Opening {app_name}.")
        return True
    except Exception:
        speak(f"Failed to open {app_name}.")
        return False

def open_website(site_name):
    urls = CONFIG.get("websites", {})
    url = urls.get(site_name.lower())
    if not url:
        speak(f"No URL configured for {site_name}.")
        return False
    webbrowser.open(url)
    speak(f"Opening {site_name}.")
    return True

def google_search(query):
    """Open Google with the given search query."""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    speak(f"Here's what I found for {query} on Google.")
    return True

def play_song_on_youtube(song_name):
    query = song_name.replace("play ", "").replace("on youtube", "").strip()
    if not query:
        speak("Please specify a song name.")
        return False
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"Playing {query} on YouTube.")
    return True

def read_emails():
    creds = CONFIG.get("gmail")
    if not creds or not creds.get("email") or not creds.get("app_password"):
        speak("Email credentials not configured.")
        return False
    try:
        email_user = creds["email"]
        email_pass = creds["app_password"]
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN")
        mail_ids = messages[0].split()
        if not mail_ids:
            speak("You have no new emails.")
            return True
        speak(f"You have {len(mail_ids)} new emails. Reading them.")
        for i in mail_ids[:5]:
            status, msg_data = mail.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")
            from_ = msg.get("From")
            speak(f"Email from {from_}, subject: {subject}.")
        mail.logout()
        return True
    except Exception:
        speak("Failed to read emails. Check your config.")
        return False

def create_file(file_name):
    try:
        with open(file_name, "w") as f:
            pass
        speak(f"File {file_name} created.")
        return True
    except Exception:
        speak(f"Could not create {file_name}.")
        return False

def open_file(file_name):
    try:
        abs_path = os.path.abspath(file_name)
        if not os.path.exists(abs_path):
            speak(f"The file {file_name} does not exist.")
            return False
        if SYSTEM == "windows":
            os.startfile(abs_path)
        elif SYSTEM == "linux":
            subprocess.Popen(["xdg-open", abs_path])
        else:
            speak("Unsupported OS for opening files.")
            return False
        speak(f"Opening {file_name}.")
        return True
    except Exception:
        speak(f"Could not open {file_name}.")
        return False

def delete_file(file_name):
    try:
        abs_path = os.path.abspath(file_name)
        if not os.path.exists(abs_path):
            speak(f"The file {file_name} does not exist.")
            return False
        os.remove(abs_path)
        speak(f"Deleted {file_name}.")
        return True
    except Exception:
        speak(f"Could not delete {file_name}.")
        return False

# --- Main Flexible Command Handler ---
def handle_command(command):
    command = command.lower()

    # Open Applications: allow 'open chrome', 'start vscode', etc.
    for app_name in CONFIG.get("applications", {}):
        if (f"open {app_name.lower()}" in command or
            f"start {app_name.lower()}" in command or
            app_name.lower() in command):
            return open_application(app_name)

    # Open Websites
    for site in CONFIG.get("websites", {}):
        if (f"open {site.lower()}" in command or
            f"go to {site.lower()}" in command or
            site.lower() in command):
            return open_website(site)

    # General Google search
    m = re.search(r'(search for|google|find) (.+)', command)
    if m:
        q = m.group(2).replace("on google", "").strip()
        return google_search(q)

    # Play Song on YouTube: 'play <song> [on youtube]'
    if command.startswith("play ") and ("on youtube" in command or "youtube" in command):
        return play_song_on_youtube(command)

    # Read Emails
    if "read my emails" in command or "check my emails" in command:
        return read_emails()

    # File operations
    m = re.search(r'create file ([\w_.-]+)', command)
    if m:
        return create_file(m.group(1))
    m = re.search(r'open file ([\w_.-]+)', command)
    if m:
        return open_file(m.group(1))
    m = re.search(r'delete file ([\w_.-]+)', command)
    if m:
        return delete_file(m.group(1))

    speak("Sorry, I don't recognize that command.")
    return False
