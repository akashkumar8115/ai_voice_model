# Voice AI: Cross-Platform Voice Command OS Assistant

## Overview
Voice AI is a cross-platform (Linux & Windows) smart assistant for controlling your computer with voice commands. It can open applications, websites, files, play YouTube songs, check emails, run Google searches, and more—all with hands-free interaction.

## Features
- **Always-listening**: Responds to commands at any time.
- **Voice feedback**: Provides real-time spoken responses.
- **Open apps & websites**: Configurable for both Linux and Windows.
- **Google search integration**: Search the web seamlessly.
- **YouTube music by voice**.
- **Basic file/email management.**
- **Easy extension/configuration.**

## Prerequisites
- Python 3.7+
- Microphone and speakers

## Installation
```bash
# Clone or download this repository
cd /path/to/voice_ai
pip install -r requirements.txt
```
Additional dependencies:
- **Linux:** Install required system packages for PyAudio:
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  ```
- **Windows:** All dependencies are handled by `pip`.

## Configuration
Edit `config.json` for your OS and preferences:
- `applications`: Map names to application paths (add Linux paths as needed).
- `websites`: Add frequently-used sites.
- `gmail`: For email reading, set your Gmail address and [App Password](https://support.google.com/accounts/answer/185833).

Example for Linux:
```json
"applications": {
  "chrome": "/usr/bin/google-chrome-stable",
  "vscode": "/usr/bin/code"
}
```

## Usage
Run the assistant:
```bash
python main.py
```
Speak your command (e.g. “open chrome”, “open youtube”, “play despacito on youtube”, “search for weather in New York on google”, “create file notes.txt”, “read my emails”, etc.).

## Adding Commands
- Edit `actions.py` to add more commands or logic. 
- Add apps and websites to `config.json`.

## Troubleshooting
- Microphone errors: Check if OS recognized the microphone.
- TTS not working: Ensure speakers are connected and `pyttsx3` is installed.
- Application opening: Ensure app paths in `config.json` are correct and executable.

## Security Warning
Voice assistants can execute commands and control apps/files: secure your environment and never share app passwords.

---
**Contributions welcome!**
