import speech_recognition as sr
import threading
import queue

recognizer = sr.Recognizer()

# Shared queue for commands to be handled
audio_commands = queue.Queue()

LISTEN_TIMEOUT = 7  # seconds before resetting mic
def _background_listener(q):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Listening (background)...")
                audio = recognizer.listen(source, phrase_time_limit=LISTEN_TIMEOUT)
                command = recognizer.recognize_google(audio)
                print(f"Recognized: {command}")
                q.put(command.lower())
            except sr.UnknownValueError:
                pass  # Ignore and keep listening
            except sr.RequestError:
                pass
            except Exception as e:
                print(f"Mic error: {e}")

# Start background thread once at module import
def start_listening():
    threading.Thread(target=_background_listener, args=(audio_commands,), daemon=True).start()

# Main loop can poll this for new commands
def listen_command():
    try:
        # Non-blocking get, returns None if queue is empty
        return audio_commands.get_nowait()
    except queue.Empty:
        return None

# Start listening as soon as this module is loaded
start_listening()
