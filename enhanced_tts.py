"""
Enhanced Text-to-Speech System with multiple voices and better quality
"""

import pyttsx3
import threading
import queue
import time
import logging
import os
import pygame
from gtts import gTTS
import io
import tempfile
from pydub import AudioSegment
from pydub.playback import play
import azure.cognitiveservices.speech as speechsdk

class EnhancedTTS:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Speech engines
        self.pyttsx_engine = None
        self.azure_key = os.getenv('AZURE_SPEECH_KEY')
        self.azure_region = os.getenv('AZURE_SPEECH_REGION')
        
        # Voice settings
        self.current_voice = "pyttsx3"  # pyttsx3, gtts, azure
        self.voice_settings = {
            'rate': 165,
            'volume': 0.9,
            'voice_id': None
        }
        
        # Speech queue for handling multiple requests
        self.speech_queue = queue.PriorityQueue()
        self.is_speaking = False
        self.speech_thread = None
        
        # Initialize pygame for better audio playback
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_available = True
        except Exception as e:
            self.logger.warning(f"Pygame initialization failed: {e}")
            self.pygame_available = False
        
        self._initialize_engines()
        self._start_speech_worker()
        
        self.logger.info("Enhanced TTS system initialized")

    def _initialize_engines(self):
        """Initialize all available TTS engines"""
        # Initialize pyttsx3
        try:
            self.pyttsx_engine = pyttsx3.init()
            self._configure_pyttsx3()
            self.logger.info("Pyttsx3 engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
        
        # Check Azure availability
        if self.azure_key and self.azure_region:
            try:
                self.azure_config = speechsdk.SpeechConfig(
                    subscription=self.azure_key,
                    region=self.azure_region
                )
                self.azure_config.speech_synthesis_voice_name = "en-US-JennyNeural"
                self.azure_available = True
                self.logger.info("Azure Speech Services available")
            except Exception as e:
                self.logger.warning(f"Azure Speech Services unavailable: {e}")
                self.azure_available = False
        else:
            self.azure_available = False

    def _configure_pyttsx3(self):
        """Configure pyttsx3 with optimal settings"""
        if not self.pyttsx_engine:
            return
            
        try:
            # Get available voices
            voices = self.pyttsx_engine.getProperty('voices')
            
            # Try to find a high-quality voice
            preferred_voices = ['Zira', 'David', 'Microsoft Zira Desktop', 'Microsoft David Desktop']
            selected_voice = None
            
            for voice in voices:
                for preferred in preferred_voices:
                    if preferred.lower() in voice.name.lower():
                        selected_voice = voice.id
                        break
                if selected_voice:
                    break
            
            # Use first available voice if no preferred voice found
            if not selected_voice and voices:
                selected_voice = voices[0].id
            
            if selected_voice:
                self.pyttsx_engine.setProperty('voice', selected_voice)
                self.voice_settings['voice_id'] = selected_voice
                self.logger.info(f"Selected voice: {selected_voice}")
            
            # Set speech rate and volume
            self.pyttsx_engine.setProperty('rate', self.voice_settings['rate'])
            self.pyttsx_engine.setProperty('volume', self.voice_settings['volume'])
            
        except Exception as e:
            self.logger.error(f"Failed to configure pyttsx3: {e}")

    def _start_speech_worker(self):
        """Start the background speech worker thread"""
        self.speech_worker_running = True
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    def _speech_worker(self):
        """Background worker to handle speech queue"""
        while self.speech_worker_running:
            try:
                # Get next speech task (priority, timestamp, text, options)
                priority, timestamp, text, options = self.speech_queue.get(timeout=1)
                
                self.is_speaking = True
                self._perform_speech(text, options)
                self.is_speaking = False
                
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Speech worker error: {e}")
                self.is_speaking = False

    def _perform_speech(self, text, options):
        """Perform the actual text-to-speech conversion"""
        engine = options.get('engine', self.current_voice)
        
        try:
            if engine == 'azure' and self.azure_available:
                self._speak_azure(text, options)
            elif engine == 'gtts':
                self._speak_gtts(text, options)
            else:
                self._speak_pyttsx3(text, options)
                
        except Exception as e:
            self.logger.error(f"Speech synthesis failed with {engine}: {e}")
            # Fallback to pyttsx3
            if engine != 'pyttsx3':
                self._speak_pyttsx3(text, options)

    def _speak_pyttsx3(self, text, options):
        """Speak using pyttsx3 engine"""
        if not self.pyttsx_engine:
            return
            
        try:
            # Import voice input here to avoid circular imports
            from voice_input import VoiceInput
            
            # Temporarily mute voice input
            # This should be handled by the calling code
            
            self.pyttsx_engine.say(text)
            self.pyttsx_engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Pyttsx3 speech error: {e}")

    def _speak_gtts(self, text, options):
        """Speak using Google Text-to-Speech"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play using pygame if available
                if self.pygame_available:
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                else:
                    # Fallback to pydub
                    audio = AudioSegment.from_mp3(tmp_file.name)
                    play(audio)
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            self.logger.error(f"GTTS speech error: {e}")
            raise

    def _speak_azure(self, text, options):
        """Speak using Azure Speech Services"""
        try:
            # Configure voice if specified
            voice_name = options.get('voice', 'en-US-JennyNeural')
            self.azure_config.speech_synthesis_voice_name = voice_name
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.azure_config)
            
            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.logger.debug("Azure speech synthesis completed")
            else:
                raise Exception(f"Azure synthesis failed: {result.reason}")
                
        except Exception as e:
            self.logger.error(f"Azure speech error: {e}")
            raise

    def speak(self, text, priority="normal", engine=None, voice=None, interrupt=False):
        """
        Add text to speech queue
        
        Args:
            text: Text to speak
            priority: "high", "normal", "low"
            engine: Override default engine
            voice: Specific voice to use
            interrupt: Clear queue and speak immediately
        """
        if not text or not text.strip():
            return
        
        # Priority mapping
        priority_map = {"high": 1, "normal": 2, "low": 3}
        priority_value = priority_map.get(priority, 2)
        
        # Options
        options = {
            'engine': engine or self.current_voice,
            'voice': voice
        }
        
        # Clear queue if interrupting
        if interrupt:
            self.clear_speech_queue()
        
        # Add to queue
        self.speech_queue.put((priority_value, time.time(), text, options))
        self.logger.debug(f"Added to speech queue: '{text[:50]}...'")

    def speak_immediately(self, text, engine=None):
        """Speak text immediately, bypassing the queue"""
        if not text or not text.strip():
            return
            
        options = {'engine': engine or self.current_voice}
        self._perform_speech(text, options)

    def clear_speech_queue(self):
        """Clear all pending speech requests"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
        self.logger.debug("Speech queue cleared")

    def set_voice_engine(self, engine):
        """Change the default voice engine"""
        valid_engines = ['pyttsx3', 'gtts', 'azure']
        if engine in valid_engines:
            self.current_voice = engine
            self.logger.info(f"Voice engine changed to: {engine}")
        else:
            self.logger.warning(f"Invalid engine: {engine}")

    def adjust_voice_settings(self, rate=None, volume=None):
        """Adjust voice settings for pyttsx3"""
        if not self.pyttsx_engine:
            return
            
        try:
            if rate is not None:
                self.voice_settings['rate'] = max(50, min(300, rate))
                self.pyttsx_engine.setProperty('rate', self.voice_settings['rate'])
                
            if volume is not None:
                self.voice_settings['volume'] = max(0.0, min(1.0, volume))
                self.pyttsx_engine.setProperty('volume', self.voice_settings['volume'])
                
            self.logger.info(f"Voice settings updated: rate={self.voice_settings['rate']}, volume={self.voice_settings['volume']}")
            
        except Exception as e:
            self.logger.error(f"Failed to adjust voice settings: {e}")

    def get_available_voices(self):
        """Get list of available voices"""
        voices = []
        
        if self.pyttsx_engine:
            try:
                pyttsx_voices = self.pyttsx_engine.getProperty('voices')
                for voice in pyttsx_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'engine': 'pyttsx3'
                    })
            except Exception as e:
                self.logger.error(f"Failed to get pyttsx3 voices: {e}")
        
        # Add Azure voices if available
        if self.azure_available:
            azure_voices = [
                'en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-AriaNeural',
                'en-GB-SoniaNeural', 'en-AU-NatashaNeural'
            ]
            for voice in azure_voices:
                voices.append({
                    'id': voice,
                    'name': voice,
                    'engine': 'azure'
                })
        
        return voices

    def is_currently_speaking(self):
        """Check if TTS is currently speaking"""
        return self.is_speaking

    def wait_for_speech_completion(self, timeout=30):
        """Wait for all speech to complete"""
        start_time = time.time()
        while (not self.speech_queue.empty() or self.is_speaking) and (time.time() - start_time) < timeout:
            time.sleep(0.1)

    def shutdown(self):
        """Shutdown the TTS system"""
        self.speech_worker_running = False
        self.clear_speech_queue()
        
        if self.speech_thread:
            self.speech_thread.join(timeout=2)
            
        if self.pygame_available:
            pygame.mixer.quit()
            
        self.logger.info("Enhanced TTS system shutdown")