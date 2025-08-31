"""
Configuration Manager for AI Voice Assistant
"""

import os
import json
import logging
from pathlib import Path
import platform

class ConfigManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path.home() / '.jarvis_assistant'
        self.config_file = self.config_dir / 'config.json'
        self.system = platform.system().lower()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load or create configuration
        self.config = self._load_config()
        self.logger.info("Configuration Manager initialized")

    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info("Configuration loaded from file")
                return config
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _create_default_config(self):
        """Create default configuration"""
        default_config = {
            "version": "2.0",
            "applications": self._get_default_applications(),
            "websites": self._get_default_websites(),
            "voice_settings": {
                "engine": "pyttsx3",
                "rate": 165,
                "volume": 0.9,
                "voice_id": None
            },
            "recognition_settings": {
                "energy_threshold": 4000,
                "pause_threshold": 0.8,
                "phrase_time_limit": 8,
                "timeout": 1
            },
            "gmail": {
                "email": "",
                "app_password": "",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "imap_server": "imap.gmail.com",
                "imap_port": 993
            },
            "api_keys": {
                "openai": "",
                "wolfram_alpha": "",
                "weather_api": "",
                "azure_speech_key": "",
                "azure_speech_region": ""
            },
            "user_preferences": {
                "wake_words": ["jarvis", "hey jarvis", "ok jarvis"],
                "response_style": "friendly",
                "default_location": "",
                "preferred_browser": "default",
                "news_sources": [],
                "music_service": "youtube"
            },
            "security": {
                "require_confirmation": ["shutdown", "restart", "delete"],
                "blocked_commands": [],
                "safe_mode": False
            },
            "logging": {
                "level": "INFO",
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
        
        self._save_config(default_config)
        self.logger.info("Default configuration created")
        return default_config

    def _get_default_applications(self):
        """Get default applications based on OS"""
        if self.system == "windows":
            return {
                "chrome": {
                    "windows": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    "linux": "google-chrome",
                    "darwin": "/Applications/Google Chrome.app"
                },
                "firefox": {
                    "windows": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    "linux": "firefox",
                    "darwin": "/Applications/Firefox.app"
                },
                "notepad": {
                    "windows": "notepad.exe",
                    "linux": "gedit",
                    "darwin": "/Applications/TextEdit.app"
                },
                "calculator": {
                    "windows": "calc.exe",
                    "linux": "gnome-calculator",
                    "darwin": "/Applications/Calculator.app"
                },
                "file_manager": {
                    "windows": "explorer.exe",
                    "linux": "nautilus",
                    "darwin": "/Applications/Finder.app"
                },
                "terminal": {
                    "windows": "cmd.exe",
                    "linux": "gnome-terminal",
                    "darwin": "/Applications/Terminal.app"
                },
                "vscode": {
                    "windows": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                    "linux": "code",
                    "darwin": "/Applications/Visual Studio Code.app"
                },
                "spotify": {
                    "windows": r"C:\Users\{username}\AppData\Roaming\Spotify\Spotify.exe",
                    "linux": "spotify",
                    "darwin": "/Applications/Spotify.app"
                }
            }
        elif self.system == "linux":
            return {
                "chrome": "google-chrome",
                "firefox": "firefox",
                "notepad": "gedit",
                "calculator": "gnome-calculator",
                "file_manager": "nautilus",
                "terminal": "gnome-terminal",
                "vscode": "code",
                "spotify": "spotify"
            }
        else:  # macOS
            return {
                "chrome": "/Applications/Google Chrome.app",
                "firefox": "/Applications/Firefox.app",
                "notepad": "/Applications/TextEdit.app",
                "calculator": "/Applications/Calculator.app",
                "file_manager": "/System/Library/CoreServices/Finder.app",
                "terminal": "/Applications/Terminal.app",
                "vscode": "/Applications/Visual Studio Code.app",
                "spotify": "/Applications/Spotify.app"
            }

    def _get_default_websites(self):
        """Get default websites"""
        return {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "stackoverflow": "https://stackoverflow.com",
            "reddit": "https://www.reddit.com",
            "gmail": "https://mail.google.com",
            "drive": "https://drive.google.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.com",
            "weather": "https://weather.com",
            "news": "https://news.google.com",
            "maps": "https://maps.google.com"
        }

    def _save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.debug("Configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self._save_config()
        self.logger.info(f"Configuration updated: {key}")

    def get_applications(self):
        """Get applications configuration"""
        return self.config.get('applications', {})

    def get_websites(self):
        """Get websites configuration"""
        return self.config.get('websites', {})

    def get_gmail_config(self):
        """Get Gmail configuration"""
        return self.config.get('gmail', {})

    def get_api_keys(self):
        """Get API keys configuration"""
        return self.config.get('api_keys', {})

    def get_voice_settings(self):
        """Get voice settings"""
        return self.config.get('voice_settings', {})

    def get_recognition_settings(self):
        """Get speech recognition settings"""
        return self.config.get('recognition_settings', {})

    def get_user_preferences(self):
        """Get user preferences"""
        return self.config.get('user_preferences', {})

    def get_security_settings(self):
        """Get security settings"""
        return self.config.get('security', {})

    def add_application(self, name, path):
        """Add new application"""
        if 'applications' not in self.config:
            self.config['applications'] = {}
        
        self.config['applications'][name.lower()] = path
        self._save_config()
        self.logger.info(f"Added application: {name}")

    def add_website(self, name, url):
        """Add new website"""
        if 'websites' not in self.config:
            self.config['websites'] = {}
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.config['websites'][name.lower()] = url
        self._save_config()
        self.logger.info(f"Added website: {name} -> {url}")

    def update_gmail_config(self, email, app_password):
        """Update Gmail configuration"""
        if 'gmail' not in self.config:
            self.config['gmail'] = {}
        
        self.config['gmail']['email'] = email
        self.config['gmail']['app_password'] = app_password
        self._save_config()
        self.logger.info("Gmail configuration updated")

    def update_api_key(self, service, api_key):
        """Update API key for service"""
        if 'api_keys' not in self.config:
            self.config['api_keys'] = {}
        
        self.config['api_keys'][service] = api_key
        self._save_config()
        self.logger.info(f"API key updated for {service}")

    def update_voice_settings(self, engine=None, rate=None, volume=None, voice_id=None):
        """Update voice settings"""
        if 'voice_settings' not in self.config:
            self.config['voice_settings'] = {}
        
        voice_settings = self.config['voice_settings']
        
        if engine is not None:
            voice_settings['engine'] = engine
        if rate is not None:
            voice_settings['rate'] = rate
        if volume is not None:
            voice_settings['volume'] = volume
        if voice_id is not None:
            voice_settings['voice_id'] = voice_id
        
        self._save_config()
        self.logger.info("Voice settings updated")

    def update_recognition_settings(self, **kwargs):
        """Update speech recognition settings"""
        if 'recognition_settings' not in self.config:
            self.config['recognition_settings'] = {}
        
        self.config['recognition_settings'].update(kwargs)
        self._save_config()
        self.logger.info("Recognition settings updated")

    def add_wake_word(self, wake_word):
        """Add new wake word"""
        if 'user_preferences' not in self.config:
            self.config['user_preferences'] = {}
        if 'wake_words' not in self.config['user_preferences']:
            self.config['user_preferences']['wake_words'] = []
        
        wake_words = self.config['user_preferences']['wake_words']
        if wake_word.lower() not in [w.lower() for w in wake_words]:
            wake_words.append(wake_word.lower())
            self._save_config()
            self.logger.info(f"Added wake word: {wake_word}")

    def remove_wake_word(self, wake_word):
        """Remove wake word"""
        if 'user_preferences' in self.config and 'wake_words' in self.config['user_preferences']:
            wake_words = self.config['user_preferences']['wake_words']
            self.config['user_preferences']['wake_words'] = [
                w for w in wake_words if w.lower() != wake_word.lower()
            ]
            self._save_config()
            self.logger.info(f"Removed wake word: {wake_word}")

    def set_default_location(self, location):
        """Set default location for weather and other services"""
        if 'user_preferences' not in self.config:
            self.config['user_preferences'] = {}
        
        self.config['user_preferences']['default_location'] = location
        self._save_config()
        self.logger.info(f"Default location set to: {location}")

    def is_command_blocked(self, command):
        """Check if command is blocked"""
        blocked_commands = self.config.get('security', {}).get('blocked_commands', [])
        return any(blocked in command.lower() for blocked in blocked_commands)

    def requires_confirmation(self, command):
        """Check if command requires confirmation"""
        confirm_commands = self.config.get('security', {}).get('require_confirmation', [])
        return any(confirm in command.lower() for confirm in confirm_commands)

    def is_safe_mode(self):
        """Check if safe mode is enabled"""
        return self.config.get('security', {}).get('safe_mode', False)

    def export_config(self, export_path):
        """Export configuration to file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuration exported to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export config: {e}")
            return False

    def import_config(self, import_path):
        """Import configuration from file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            if self._validate_config(imported_config):
                self.config = imported_config
                self._save_config()
                self.logger.info(f"Configuration imported from {import_path}")
                return True
            else:
                self.logger.error("Invalid configuration format")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to import config: {e}")
            return False

    def _validate_config(self, config):
        """Validate configuration structure"""
        required_keys = ['version', 'applications', 'websites', 'voice_settings']
        return all(key in config for key in required_keys)

    def reset_to_default(self):
        """Reset configuration to default values"""
        self.config = self._create_default_config()
        self.logger.info("Configuration reset to default")

    def get_config_info(self):
        """Get configuration information"""
        return {
            'config_file': str(self.config_file),
            'config_dir': str(self.config_dir),
            'version': self.config.get('version', 'unknown'),
            'applications_count': len(self.get_applications()),
            'websites_count': len(self.get_websites()),
            'api_keys_configured': len([k for k, v in self.get_api_keys().items() if v]),
            'gmail_configured': bool(self.get_gmail_config().get('email')),
            'safe_mode': self.is_safe_mode()
        }