# import os
# import webbrowser
# import subprocess
# import platform
# import json
# import smtplib
# import imaplib
# import email
# from email.header import decode_header
# import re
# from tts import speak
# from voice_input import listen_command
# import requests
# from bs4 import BeautifulSoup

# # Load config
# with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
#     CONFIG = json.load(f)

# SYSTEM = platform.system().lower()

# # --- Helper functions ---
# def get_app_path(app_name):
#     """Return path for app (OS-detected)."""
#     apps = CONFIG.get("applications", {})
#     # Support dict: {"chrome": {"windows": path, "linux": path}}
#     info = apps.get(app_name.lower())
#     if isinstance(info, dict):
#         return info.get(SYSTEM)
#     return info

# def open_application(app_name):
#     app_path = get_app_path(app_name)
#     if not app_path:
#         speak(f"I can't find the path for {app_name} on this computer. You can configure it in the config file.")
#         return False
#     try:
#         if SYSTEM == "windows":
#             os.startfile(app_path)
#         elif SYSTEM == "linux":
#             subprocess.Popen([app_path])
#         else:
#             speak(f"I'm not sure how to open applications on this operating system.")
#             return False
#         speak(f"Sure, opening {app_name}.")
#         return True
#     except Exception:
#         speak(f"Sorry, I had trouble opening {app_name}.")
#         return False

# def open_website(site_name):
#     urls = CONFIG.get("websites", {})
#     url = urls.get(site_name.lower())
#     if not url:
#         speak(f"I don't have a URL for {site_name}. You can add it to the config file.")
#         return False
#     webbrowser.open(url)
#     speak(f"Alright, opening {site_name}.")
#     return True

# def google_search(query):
#     """Open Google with the given search query."""
#     search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
#     webbrowser.open(search_url)
#     speak(f"Here is what I found for {query} on Google.")
#     return True

# def answer_question(query):
#     """Search Google and speak the answer."""
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
#         }
#         response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         # Try to find a direct answer
#         answer = soup.find("div", class_="BNeawe iBp4i AP7Wnd")
#         if answer:
#             speak(answer.text)
#             return True

#         # If no direct answer, try to find a snippet
#         snippet = soup.find("div", class_="BNeawe s3v9rd AP7Wnd")
#         if snippet:
#             speak(snippet.text)
#             return True

#         speak("I couldn't find a direct answer, but here are the search results.")
#         google_search(query)
#         return True

#     except Exception as e:
#         print(e)
#         speak("I'm having trouble searching right now. Please try again later.")
#         return False


# def play_song_on_youtube(song_name):
#     query = song_name.replace("play", "").replace("on youtube", "").strip()
#     if not query:
#         speak("What song would you like to play?")
#         return False
#     url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
#     webbrowser.open(url)
#     speak(f"Now playing {query} on YouTube.")
#     return True

# def read_emails():
#     creds = CONFIG.get("gmail")
#     if not creds or not creds.get("email") or not creds.get("app_password"):
#         speak("I need your email credentials to be configured before I can read your emails.")
#         return False
#     try:
#         email_user = creds["email"]
#         email_pass = creds["app_password"]
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         mail.login(email_user, email_pass)
#         mail.select("inbox")
#         status, messages = mail.search(None, "UNSEEN")
#         mail_ids = messages[0].split()
#         if not mail_ids:
#             speak("It looks like you have no new emails.")
#             return True
#         speak(f"You have {len(mail_ids)} new emails. Here are the latest ones.")
#         for i in mail_ids[:3]:
#             status, msg_data = mail.fetch(i, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])
#             subject, encoding = decode_header(msg["Subject"])[0]
#             if isinstance(subject, bytes):
#                 subject = subject.decode(encoding or "utf-8")
#             from_ = msg.get("From")
#             speak(f"You have an email from {from_} with the subject: {subject}.")
#         mail.logout()
#         return True
#     except Exception:
#         speak("I'm having trouble accessing your emails right now.")
#         return False

# def create_file(file_name):
#     try:
#         with open(file_name, "w") as f:
#             f.write("")
#         speak(f"I've created the file {file_name} for you.")
#         return True
#     except Exception:
#         speak(f"Sorry, I couldn't create the file {file_name}.")
#         return False

# def open_file(file_name):
#     try:
#         abs_path = os.path.abspath(file_name)
#         if not os.path.exists(abs_path):
#             speak(f"I can't seem to find the file {file_name}.")
#             return False
#         if SYSTEM == "windows":
#             os.startfile(abs_path)
#         elif SYSTEM == "linux":
#             subprocess.Popen(["xdg-open", abs_path])
#         else:
#             speak("I'm not sure how to open files on this operating system.")
#             return False
#         speak(f"Opening {file_name}.")
#         return True
#     except Exception:
#         speak(f"I had trouble opening the file {file_name}.")
#         return False

# def delete_file(file_name):
#     try:
#         abs_path = os.path.abspath(file_name)
#         if not os.path.exists(abs_path):
#             speak(f"The file {file_name} doesn't seem to exist.")
#             return False
#         os.remove(abs_path)
#         speak(f"I've deleted the file {file_name}.")
#         return True
#     except Exception:
#         speak(f"I couldn't delete the file {file_name}.")
#         return False

# def get_weather(location):
#     """Get the weather for a given location and speak it."""
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
#         }
#         response = requests.get(f"https://www.google.com/search?q=weather in {location}", headers=headers)
#         soup = BeautifulSoup(response.text, "html.parser")
        
#         temp = soup.find("div", class_="BNeawe iBp4i AP7Wnd").text
#         condition = soup.find("div", class_="BNeawe tAd8D AP7Wnd").text
        
#         if temp and condition:
#             speak(f"The current weather in {location} is {condition} with a temperature of {temp}.")
#             return True
#         else:
#             speak("I couldn't get the weather for you. Maybe try a different location?")
#             return False
#     except Exception:
#         speak("I'm having trouble getting the weather right now.")
#         return False

# def send_email(recipient, subject, body):
#     """Send an email using configured credentials."""
#     creds = CONFIG.get("gmail")
#     if not creds or not creds.get("email") or not creds.get("app_password"):
#         speak("I need your email credentials to be configured before I can send emails.")
#         return False
#     try:
#         email_user = creds["email"]
#         email_pass = creds["app_password"]
        
#         msg = email.message.EmailMessage()
#         msg.set_content(body)
#         msg['Subject'] = subject
#         msg['From'] = email_user
#         msg['To'] = recipient
        
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         server.login(email_user, email_pass)
#         server.send_message(msg)
#         server.quit()
        
#         speak(f"I've sent the email to {recipient}.")
#         return True
#     except Exception:
#         speak("I had trouble sending the email.")
#         return False

# def greet():
#     """A simple greeting."""
#     speak("Hello! How can I help you today?")
#     return True

# # --- Main Flexible Command Handler ---
# def handle_command(command):
#     command = command.lower()

#     # Greeting
#     if "hello" in command or "hi" in command or "hey" in command:
#         return greet()

#     # Open Applications
#     for app_name in CONFIG.get("applications", {}):
#         if f"open {app_name.lower()}" in command or f"start {app_name.lower()}" in command:
#             return open_application(app_name)

#     # Open Websites
#     for site in CONFIG.get("websites", {}):
#         if f"open {site.lower()}" in command or f"go to {site.lower()}" in command:
#             return open_website(site)

#     # Play Song on YouTube
#     if "play" in command and "on youtube" in command:
#         return play_song_on_youtube(command)

#     # Read Emails
#     if "read my email" in command or "check my email" in command:
#         return read_emails()

#     # File operations
#     m = re.search(r'create file ([\w_.-]+)', command)
#     if m:
#         return create_file(m.group(1))
#     m = re.search(r'open file ([\w_.-]+)', command)
#     if m:
#         return open_file(m.group(1))
#     m = re.search(r'delete file ([\w_.-]+)', command)
#     if m:
#         return delete_file(m.group(1))

#     # Weather
#     m = re.search(r'weather in (.+)', command)
#     if m:
#         return get_weather(m.group(1))

#     # Send Email
#     m = re.search(r'send an email to (.+)', command)
#     if m:
#         recipient = m.group(1)
#         speak("What should the subject be?")
#         subject = listen_command()
#         speak("And what should the email say?")
#         body = listen_command()
#         return send_email(recipient, subject, body)

#     # General question
#     if "what is" in command or "who is" in command or "what are" in command or "tell me about" in command:
#         return answer_question(command)

#     # Fallback to Google search
#     m = re.search(r'(search for|google|find) (.+)', command)
#     if m:
#         q = m.group(2).replace("on google", "").strip()
#         return google_search(q)

#     speak("I'm not sure how to help with that. Would you like me to search for it?")
#     return False

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
from voice_input import listen_command
import requests
from bs4 import BeautifulSoup
import datetime

# Load config
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
    CONFIG = json.load(f)

SYSTEM = platform.system().lower()

# --- Context memory (for conversational flow) ---
CONTEXT = {"last_intent": None, "last_entity": None}


# --- Helper functions ---
def get_app_path(app_name):
    apps = CONFIG.get("applications", {})
    info = apps.get(app_name.lower())
    if isinstance(info, dict):
        return info.get(SYSTEM)
    return info

def open_application(app_name):
    app_path = get_app_path(app_name)
    if not app_path:
        speak(f"I couldn't find {app_name}. Please update config.json.")
        return False
    try:
        if SYSTEM == "windows":
            os.startfile(app_path)
        elif SYSTEM == "linux":
            subprocess.Popen([app_path])
        else:
            speak(f"Unsupported OS for launching apps.")
            return False
        speak(f"Opening {app_name} for you.")
        return True
    except Exception:
        speak(f"Failed to open {app_name}.")
        return False

def open_website(site_name):
    urls = CONFIG.get("websites", {})
    url = urls.get(site_name.lower())
    if not url:
        speak(f"I don't know {site_name}. Add it to config.json.")
        return False
    webbrowser.open(url)
    speak(f"Taking you to {site_name}.")
    return True

def google_search(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    speak(f"Here’s what I found for {query}.")
    return True

def answer_question(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        answer = soup.find("div", class_="BNeawe iBp4i AP7Wnd")
        if answer:
            speak(answer.text)
            return True

        snippet = soup.find("div", class_="BNeawe s3v9rd AP7Wnd")
        if snippet:
            speak(snippet.text)
            return True

        speak("I couldn't find a direct answer, but here are some search results.")
        google_search(query)
        return True
    except Exception:
        speak("I had trouble fetching that answer.")
        return False

def play_song_on_youtube(song_name):
    query = song_name.replace("play", "").replace("on youtube", "").strip()
    if not query:
        speak("What song would you like me to play?")
        return False
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    speak(f"Now playing {query} on YouTube.")
    return True

def read_emails():
    creds = CONFIG.get("gmail")
    if not creds or not creds.get("email") or not creds.get("app_password"):
        speak("I need Gmail credentials in config.json first.")
        return False
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(creds["email"], creds["app_password"])
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN")
        mail_ids = messages[0].split()
        if not mail_ids:
            speak("You don’t have any new emails.")
            return True
        speak(f"You have {len(mail_ids)} new emails. Here are the latest:")
        for i in mail_ids[:3]:
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
        speak("I couldn’t check your emails.")
        return False

def get_weather(location):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"https://www.google.com/search?q=weather in {location}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        temp = soup.find("div", class_="BNeawe iBp4i AP7Wnd").text
        condition = soup.find("div", class_="BNeawe tAd8D AP7Wnd").text
        speak(f"In {location}, it’s {condition} with a temperature of {temp}.")
        return True
    except Exception:
        speak("Couldn't get the weather right now.")
        return False

def send_email(recipient, subject, body):
    creds = CONFIG.get("gmail")
    if not creds or not creds.get("email") or not creds.get("app_password"):
        speak("I need Gmail credentials in config.json.")
        return False
    try:
        msg = email.message.EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = creds["email"]
        msg['To'] = recipient

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(creds["email"], creds["app_password"])
        server.send_message(msg)
        server.quit()

        speak(f"I sent the email to {recipient}.")
        return True
    except Exception:
        speak("Couldn't send that email.")
        return False

def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        greet_text = "Good morning!"
    elif hour < 18:
        greet_text = "Good afternoon!"
    else:
        greet_text = "Good evening!"
    speak(f"{greet_text} How can I assist you?")
    return True


# --- Main Command Handler ---
def handle_command(command):
    command = command.lower().strip()

    # Greeting
    if any(greet in command for greet in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return greet()

    # Open Apps
    for app_name in CONFIG.get("applications", {}):
        if f"open {app_name.lower()}" in command or f"start {app_name.lower()}" in command:
            return open_application(app_name)

    # Open Sites
    for site in CONFIG.get("websites", {}):
        if site.lower() in command and ("open" in command or "go to" in command):
            return open_website(site)

    # Play Music
    if "play" in command and "youtube" in command:
        return play_song_on_youtube(command)

    # Emails
    if "read my email" in command or "check my email" in command:
        return read_emails()

    # Weather
    m = re.search(r'weather in (.+)', command)
    if m:
        return get_weather(m.group(1))

    # Email Sending
    if "send email" in command or "compose email" in command:
        speak("Who should I send it to?")
        recipient = listen_command()
        speak("What’s the subject?")
        subject = listen_command()
        speak("And the content?")
        body = listen_command()
        return send_email(recipient, subject, body)

    # Questions
    if any(x in command for x in ["what is", "who is", "what are", "tell me about"]):
        return answer_question(command)

    # Fallback search
    if any(x in command for x in ["search for", "google", "find"]):
        q = command.replace("search for", "").replace("google", "").replace("find", "").strip()
        return google_search(q)

    speak("I didn't quite get that. Do you want me to search it online?")
    CONTEXT["last_intent"] = "unclear"
    CONTEXT["last_entity"] = command
    return False
