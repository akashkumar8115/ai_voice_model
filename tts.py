import pyttsx3
import platform
import threading

_engine = None
_voice_set = False

# Singleton pattern to reuse the same engine
def _get_engine():
    global _engine, _voice_set
    if _engine is None:
        _engine = pyttsx3.init()
        # Set female voice if available
        voices = _engine.getProperty('voices')
        female_voice = None
        for v in voices:
            # Many platforms mark female with 'female', Windows with 'Zira', etc.
            if ('female' in v.name.lower() or 'zira' in v.id.lower() or 'female' in str(v.gender).lower()):
                female_voice = v.id
                break
        if female_voice:
            _engine.setProperty('voice', female_voice)
        _voice_set = True
        # Optional: Tweak properties
        if platform.system() == 'Windows':
            _engine.setProperty('rate', 165)
        else:
            _engine.setProperty('rate', 175)
    return _engine

def speak(text):
    """
    Speak text using the best-available (usually female) system voice.
    For more natural voices, integrate Google TTS, Coqui TTS, or Amazon Polly!
    """
    def _speak():
        engine = _get_engine()
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

# To use studio-quality voices, consider implementing with Coqui-TTS, Google Cloud TTS, Azure or Amazon Polly.
# This file stays clean/simple for now, but can be replaced with those APIs for even higher quality.