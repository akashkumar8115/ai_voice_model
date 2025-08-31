"""
Enhanced AI Voice Assistant - Production Level
Main Application Entry Point
"""

import time
import threading
import logging
from datetime import datetime
from voice_input import VoiceInput
from enhanced_tts import EnhancedTTS
from enhanced_actions import EnhancedActionHandler
from config_manager import ConfigManager
from conversation_manager import ConversationManager
from utils import setup_logging

class AIVoiceAssistant:
    def __init__(self):
        # Setup logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.voice_input = VoiceInput()
        self.tts = EnhancedTTS()
        self.action_handler = EnhancedActionHandler(self.config_manager, self.tts)
        self.conversation_manager = ConversationManager()
        
        # System state
        self.is_running = False
        self.is_busy = False
        self.wake_words = ["jarvis", "hey jarvis", "ok jarvis"]
        self.shutdown_phrases = ["goodbye jarvis", "shutdown", "exit", "quit"]
        
        # Performance monitoring
        self.command_count = 0
        self.session_start = datetime.now()
        
        self.logger.info("AI Voice Assistant initialized successfully")

    def startup_greeting(self):
        """Enhanced startup with personality"""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning! Jarvis is online and ready to assist you."
        elif hour < 18:
            greeting = "Good afternoon! Jarvis at your service."
        else:
            greeting = "Good evening! Jarvis is here to help you."
        
        # Add system status
        greeting += f" All systems operational. How can I help you today?"
        self.tts.speak(greeting, priority="high")

    def is_wake_word_detected(self, command):
        """Check if command contains wake word"""
        return any(wake_word in command.lower() for wake_word in self.wake_words)

    def is_shutdown_command(self, command):
        """Check if command is a shutdown request"""
        return any(phrase in command.lower() for phrase in self.shutdown_phrases)

    def process_command(self, command):
        """Enhanced command processing with context awareness"""
        try:
            self.is_busy = True
            self.command_count += 1
            
            self.logger.info(f"Processing command #{self.command_count}: {command}")
            
            # Add to conversation history
            self.conversation_manager.add_user_input(command)
            
            # Remove wake word from command
            clean_command = command
            for wake_word in self.wake_words:
                clean_command = clean_command.replace(wake_word, "").strip()
            
            # Check for shutdown
            if self.is_shutdown_command(clean_command):
                return self.shutdown()
            
            # Process with enhanced action handler
            response = self.action_handler.handle_command(clean_command, self.conversation_manager)
            
            if response:
                self.conversation_manager.add_assistant_response(response)
                return True
            else:
                # Fallback with conversation context
                fallback_response = self.handle_fallback(clean_command)
                self.conversation_manager.add_assistant_response(fallback_response)
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self.tts.speak("I encountered an error processing that request. Please try again.")
            return False
        finally:
            self.is_busy = False

    def handle_fallback(self, command):
        """Intelligent fallback with suggestions"""
        suggestions = self.action_handler.get_command_suggestions(command)
        
        if suggestions:
            response = f"I'm not sure about '{command}'. Did you mean: {', '.join(suggestions[:3])}?"
        else:
            response = "I didn't understand that. You can try commands like 'open chrome', 'play music', 'check weather', or ask me questions."
        
        self.tts.speak(response)
        return response

    def monitor_performance(self):
        """Background performance monitoring"""
        while self.is_running:
            try:
                # Log performance stats every 5 minutes
                time.sleep(300)
                uptime = datetime.now() - self.session_start
                self.logger.info(f"Session uptime: {uptime}, Commands processed: {self.command_count}")
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")

    def run(self):
        """Main application loop with enhanced error handling"""
        try:
            self.is_running = True
            self.startup_greeting()
            
            # Start performance monitoring thread
            perf_thread = threading.Thread(target=self.monitor_performance, daemon=True)
            perf_thread.start()
            
            # Start voice input
            self.voice_input.start_listening()
            
            while self.is_running:
                if not self.is_busy:
                    # Get voice command
                    command = self.voice_input.get_command()
                    
                    if command:
                        self.logger.info(f"Received command from queue: {command}")
                        # Check for wake word or if in conversation
                        if (self.is_wake_word_detected(command) or 
                            self.conversation_manager.is_in_active_conversation()):
                            
                            self.process_command(command)
                        else:
                            # Log passive commands but don't process
                            self.logger.debug(f"Command without wake word: {command}")
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Critical error in main loop: {e}")
            self.tts.speak("A critical error occurred. Shutting down.")
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown with cleanup"""
        self.logger.info("Initiating shutdown sequence")
        self.is_running = False
        
        # Farewell message
        session_duration = datetime.now() - self.session_start
        hours = int(session_duration.total_seconds() // 3600)
        minutes = int((session_duration.total_seconds() % 3600) // 60)
        
        farewell = f"Goodbye! I processed {self.command_count} commands in "
        if hours > 0:
            farewell += f"{hours} hours and {minutes} minutes. "
        else:
            farewell += f"{minutes} minutes. "
        farewell += "Have a great day!"
        
        self.tts.speak(farewell)
        
        # Cleanup
        self.voice_input.stop_listening()
        self.conversation_manager.save_session()
        
        self.logger.info("Shutdown complete")
        return True

def main():
    """Application entry point"""
    try:
        assistant = AIVoiceAssistant()
        assistant.run()
    except Exception as e:
        logging.error(f"Failed to start AI Voice Assistant: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()