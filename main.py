import time
from voice_input import listen_command
from tts import speak
from actions import handle_command

def main():
    speak("Jarvis is online and listening.")
    while True:
        command = listen_command()
        if command:
            handled = handle_command(command)
            if not handled:
                speak("I didn't catch that. Could you please repeat?")
        # If no command detected, silently continue (no repeated error)
        time.sleep(0.2)  # Small sleep to reduce CPU usage

if __name__ == "__main__":
    main()
