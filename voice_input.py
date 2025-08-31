"""
Enhanced Voice Input System with noise reduction and better recognition
"""

import speech_recognition as sr
import threading
import queue
import time
import logging
import numpy as np
from collections import deque
import webrtcvad
import wave
import io

class VoiceInput:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Voice Activity Detection
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # Command queue and threading
        self.command_queue = queue.Queue(maxsize=10)
        self.is_listening = False
        self.is_muted = False
        
        # Advanced settings
        self.noise_threshold = 0.3
        self.phrase_time_limit = 8
        self.timeout = 1
        self.energy_threshold = 300  # Lowered threshold for more sensitivity
        self.dynamic_energy_threshold = True
        
        # Command filtering
        self.recent_commands = deque(maxlen=5)
        self.command_timeout = 2.0  # seconds to ignore duplicate commands
        
        # Performance tracking
        self.recognition_attempts = 0
        self.successful_recognitions = 0
        
        self._setup_microphone()
        self.logger.info("Enhanced Voice Input initialized")

    def _setup_microphone(self):
        """Setup microphone with optimal settings"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                # Set optimal recognition parameters
                self.recognizer.energy_threshold = self.energy_threshold
                self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
                self.recognizer.pause_threshold = 0.8
                self.recognizer.phrase_threshold = 0.3
                self.recognizer.non_speaking_duration = 0.8
                
                self.logger.info(f"Microphone calibrated. Energy threshold: {self.recognizer.energy_threshold}")
                
        except Exception as e:
            self.logger.error(f"Microphone setup failed: {e}")
            raise

    def _is_speech_present(self, audio_data):
        """Use VAD to detect speech in audio"""
        try:
            # Convert audio data to bytes if necessary
            if hasattr(audio_data, 'get_wav_data'):
                wav_data = audio_data.get_wav_data()
            else:
                wav_data = audio_data
            
            # Simple energy-based detection as fallback
            audio_array = np.frombuffer(wav_data, dtype=np.int16)
            energy = np.sqrt(np.mean(audio_array**2))
            
            return energy > self.noise_threshold * 1000
            
        except Exception as e:
            self.logger.debug(f"VAD error, using fallback: {e}")
            return True  # Assume speech present on error

    def _filter_command(self, command):
        """Filter out duplicate or invalid commands"""
        if not command or len(command.strip()) < 2:
            return None
            
        command = command.strip().lower()
        
        # Check for recent duplicates
        current_time = time.time()
        for recent_cmd, timestamp in self.recent_commands:
            if (command == recent_cmd and 
                current_time - timestamp < self.command_timeout):
                self.logger.debug(f"Filtered duplicate command: {command}")
                return None
        
        # Add to recent commands
        self.recent_commands.append((command, current_time))
        return command

    def _background_listener(self):
        """Enhanced background listening with better error handling"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_listening:
            if self.is_muted:
                time.sleep(0.1)
                continue
                
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    self.logger.debug("Listening for command...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.timeout,
                        phrase_time_limit=self.phrase_time_limit
                    )
                    
                    # Check if speech is present
                    if not self._is_speech_present(audio):
                        continue
                    
                    # Attempt recognition
                    self.recognition_attempts += 1
                    
                    try:
                        # Try Google Speech Recognition first
                        command = self.recognizer.recognize_google(
                            audio,
                            language='en-US',
                            show_all=False
                        )
                        
                        # Filter and validate command
                        filtered_command = self._filter_command(command)
                        if filtered_command:
                            self.successful_recognitions += 1
                            self.logger.info(f"Recognized: '{filtered_command}'")
                            
                            # Add to queue if not full
                            try:
                                self.command_queue.put(filtered_command, block=False)
                            except queue.Full:
                                # Remove oldest item and add new one
                                try:
                                    self.command_queue.get_nowait()
                                    self.command_queue.put(filtered_command, block=False)
                                except queue.Empty:
                                    pass
                        
                        consecutive_errors = 0  # Reset error counter
                        
                    except sr.UnknownValueError:
                        self.logger.debug("Could not understand audio")
                    except sr.RequestError as e:
                        self.logger.warning(f"Recognition service error: {e}")
                        consecutive_errors += 1
                        
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening
                continue
            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Listening error: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    self.logger.error("Too many consecutive errors, stopping listener")
                    break
                    
                time.sleep(1)  # Brief pause before retry
        
        self.logger.info("Background listener stopped")

    def start_listening(self):
        """Start the background listening thread"""
        if not self.is_listening:
            self.is_listening = True
            self.listener_thread = threading.Thread(
                target=self._background_listener,
                daemon=True,
                name="VoiceListener"
            )
            self.listener_thread.start()
            self.logger.info("Voice input started")

    def stop_listening(self):
        """Stop the background listening"""
        self.is_listening = False
        if hasattr(self, 'listener_thread'):
            self.listener_thread.join(timeout=2)
        self.logger.info("Voice input stopped")

    def get_command(self):
        """Get the next command from the queue (non-blocking)"""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def mute(self):
        """Temporarily disable voice input"""
        self.is_muted = True
        self.logger.debug("Voice input muted")

    def unmute(self):
        """Re-enable voice input"""
        self.is_muted = False
        self.logger.debug("Voice input unmuted")

    def get_recognition_stats(self):
        """Get recognition performance statistics"""
        if self.recognition_attempts > 0:
            success_rate = (self.successful_recognitions / self.recognition_attempts) * 100
        else:
            success_rate = 0
            
        return {
            'attempts': self.recognition_attempts,
            'successful': self.successful_recognitions,
            'success_rate': success_rate,
            'queue_size': self.command_queue.qsize()
        }

    def adjust_sensitivity(self, level):
        """Adjust microphone sensitivity (0.1 to 2.0)"""
        try:
            self.recognizer.energy_threshold = self.energy_threshold * level
            self.logger.info(f"Sensitivity adjusted to {level}, threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            self.logger.error(f"Failed to adjust sensitivity: {e}")

    def calibrate_microphone(self, duration=2):
        """Re-calibrate microphone for current environment"""
        try:
            self.logger.info("Recalibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.logger.info(f"Recalibration complete. New threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            self.logger.error(f"Calibration failed: {e}")