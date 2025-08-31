# """
# Enhanced Action Handler with advanced command processing and AI integration
# """

# import os
# import re
# import json
# import time
# import logging
# import requests
# import subprocess
# import webbrowser
# import platform
# import smtplib
# import imaplib
# import email
# import psutil
# import openai
# from datetime import datetime, timedelta
# from difflib import get_close_matches
# from email.header import decode_header
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from bs4 import BeautifulSoup
# from fuzzywuzzy import fuzz
# import speech_recognition as sr
# import wolframalpha
# import wikipedia

# class EnhancedActionHandler:
#     def __init__(self, config_manager, tts_engine):
#         self.logger = logging.getLogger(__name__)
#         self.config = config_manager
#         self.tts = tts_engine
#         self.system = platform.system().lower()
        
#         # API keys from environment
#         self.openai_key = os.getenv('OPENAI_API_KEY')
#         self.wolfram_key = os.getenv('WOLFRAM_API_KEY')
#         self.weather_key = os.getenv('WEATHER_API_KEY')
        
#         # Initialize external services
#         self._initialize_services()
        
#         # Command patterns and handlers
#         self.command_patterns = self._build_command_patterns()
#         self.intent_classifiers = self._build_intent_classifiers()
        
#         # Context and conversation state
#         self.context = {
#             'last_intent': None,
#             'last_entity': None,
#             'conversation_history': [],
#             'user_preferences': {}
#         }
        
#         self.logger.info("Enhanced Action Handler initialized")

#     def _initialize_services(self):
#         """Initialize external API services"""
#         # OpenAI
#         if self.openai_key:
#             openai.api_key = self.openai_key
#             self.openai_available = True
#         else:
#             self.openai_available = False
            
#         # Wolfram Alpha
#         if self.wolfram_key:
#             try:
#                 self.wolfram_client = wolframalpha.Client(self.wolfram_key)
#                 self.wolfram_available = True
#             except Exception as e:
#                 self.logger.warning(f"Wolfram Alpha unavailable: {e}")
#                 self.wolfram_available = False
#         else:
#             self.wolfram_available = False

#     def _build_command_patterns(self):
#         """Build regex patterns for command recognition"""
#         return {
#             'greeting': [
#                 r'hello|hi|hey|good morning|good afternoon|good evening',
#                 r'how are you|what\'s up|sup'
#             ],
#             'application': [
#                 r'open|start|launch|run (.+)',
#                 r'close|quit|exit (.+)'
#             ],
#             'web': [
#                 r'go to|open|visit (.+)',
#                 r'search for|google|find (.+)',
#                 r'browse (.+)'
#             ],
#             'media': [
#                 r'play (.+)',
#                 r'pause|stop|resume',
#                 r'volume (up|down|\d+)',
#                 r'next|previous|skip'
#             ],
#             'system': [
#                 r'shutdown|restart|sleep|lock',
#                 r'battery|power|cpu|memory|storage',
#                 r'wifi|network|bluetooth'
#             ],
#             'email': [
#                 r'check|read (my )?email',
#                 r'send email to (.+)',
#                 r'compose email'
#             ],
#             'weather': [
#                 r'weather in (.+)|(.+) weather',
#                 r'temperature|forecast|rain|sunny'
#             ],
#             'time': [
#                 r'what time|current time|time now',
#                 r'set (alarm|timer|reminder)',
#                 r'date|today|tomorrow'
#             ],
#             'calculation': [
#                 r'calculate|compute|math',
#                 r'what is \d+.*\d+',
#                 r'convert (.+) to (.+)'
#             ],
#             'question': [
#                 r'what is|who is|when is|where is|why is|how is',
#                 r'tell me about|information about',
#                 r'define|meaning of'
#             ],
#             'control': [
#                 r'increase|decrease|adjust (.+)',
#                 r'set (.+) to (.+)',
#                 r'turn (on|off) (.+)'
#             ]
#         }

#     def _build_intent_classifiers(self):
#         """Build intent classification rules"""
#         return {
#             'greeting': ['hello', 'hi', 'hey', 'morning', 'afternoon', 'evening'],
#             'question': ['what', 'who', 'when', 'where', 'why', 'how', 'tell', 'explain'],
#             'command': ['open', 'close', 'start', 'stop', 'play', 'pause', 'set'],
#             'search': ['search', 'find', 'look', 'google', 'browse'],
#             'system': ['shutdown', 'restart', 'battery', 'volume', 'wifi'],
#             'personal': ['email', 'calendar', 'reminder', 'note']
#         }

#     def handle_command(self, command, conversation_manager=None):
#         """Main command handling with enhanced processing"""
#         try:
#             self.logger.info(f"Processing command: {command}")
            
#             # Preprocess command
#             processed_command = self._preprocess_command(command)
            
#             # Classify intent
#             intent = self._classify_intent(processed_command)
#             self.context['last_intent'] = intent
            
#             # Extract entities
#             entities = self._extract_entities(processed_command, intent)
#             self.context['last_entity'] = entities
            
#             # Handle based on intent
#             response = self._route_command(intent, processed_command, entities, conversation_manager)
            
#             # Update conversation history
#             self.context['conversation_history'].append({
#                 'command': command,
#                 'intent': intent,
#                 'entities': entities,
#                 'response': response,
#                 'timestamp': datetime.now().isoformat()
#             })
            
#             return response
            
#         except Exception as e:
#             self.logger.error(f"Command handling error: {e}")
#             self.tts.speak("I encountered an error processing that command.")
#             return False

#     def _preprocess_command(self, command):
#         """Preprocess and clean command text"""
#         # Convert to lowercase
#         command = command.lower().strip()
        
#         # Remove filler words
#         filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically']
#         words = command.split()
#         words = [word for word in words if word not in filler_words]
        
#         # Rejoin and clean
#         command = ' '.join(words)
#         command = re.sub(r'\s+', ' ', command)  # Multiple spaces to single
        
#         return command

#     def _classify_intent(self, command):
#         """Classify command intent using multiple methods"""
#         scores = {}
        
#         # Pattern matching
#         for intent, patterns in self.command_patterns.items():
#             score = 0
#             for pattern in patterns:
#                 if re.search(pattern, command):
#                     score += 10
#             scores[intent] = score
        
#         # Keyword matching
#         for intent, keywords in self.intent_classifiers.items():
#             score = scores.get(intent, 0)
#             for keyword in keywords:
#                 if keyword in command:
#                     score += 5
#             scores[intent] = score
        
#         # Return highest scoring intent
#         if scores:
#             return max(scores, key=scores.get)
#         return 'unknown'

#     def _extract_entities(self, command, intent):
#         """Extract relevant entities from command"""
#         entities = {}
        
#         # Extract based on intent
#         if intent == 'application':
#             # Extract app name
#             match = re.search(r'(?:open|start|launch|run|close|quit|exit)\s+(.+)', command)
#             if match:
#                 entities['app_name'] = match.group(1).strip()
                
#         elif intent == 'web':
#             # Extract website or search query
#             match = re.search(r'(?:go to|open|visit|search for|google|find|browse)\s+(.+)', command)
#             if match:
#                 entities['query'] = match.group(1).strip()
                
#         elif intent == 'media':
#             # Extract media commands
#             if 'play' in command:
#                 match = re.search(r'play\s+(.+)', command)
#                 if match:
#                     entities['media_name'] = match.group(1).strip()
#             elif any(word in command for word in ['volume', 'sound']):
#                 match = re.search(r'volume\s+(up|down|\d+)', command)
#                 if match:
#                     entities['volume_action'] = match.group(1)
                    
#         elif intent == 'weather':
#             # Extract location
#             match = re.search(r'weather in (.+)|(.+) weather', command)
#             if match:
#                 entities['location'] = (match.group(1) or match.group(2)).strip()
                
#         elif intent == 'calculation':
#             # Extract math expression
#             entities['expression'] = command
            
#         elif intent == 'question':
#             # Extract question topic
#             entities['topic'] = command
            
#         return entities

#     def _route_command(self, intent, command, entities, conversation_manager):
#         """Route command to appropriate handler"""
#         handlers = {
#             'greeting': self._handle_greeting,
#             'application': self._handle_application,
#             'web': self._handle_web,
#             'media': self._handle_media,
#             'system': self._handle_system,
#             'email': self._handle_email,
#             'weather': self._handle_weather,
#             'time': self._handle_time,
#             'calculation': self._handle_calculation,
#             'question': self._handle_question,
#             'control': self._handle_control
#         }
        
#         handler = handlers.get(intent, self._handle_unknown)
#         return handler(command, entities, conversation_manager)

#     def _handle_greeting(self, command, entities, conversation_manager):
#         """Handle greeting commands"""
#         greetings = [
#             "Hello! How can I assist you today?",
#             "Hi there! What would you like me to help you with?",
#             "Good to see you! How may I help?",
#             "Hello! I'm ready to assist you."
#         ]
        
#         # Personalize based on time
#         hour = datetime.now().hour
#         if hour < 12:
#             time_greeting = "Good morning! "
#         elif hour < 18:
#             time_greeting = "Good afternoon! "
#         else:
#             time_greeting = "Good evening! "
            
#         import random
#         response = time_greeting + random.choice(greetings).replace("Hello! ", "")
#         self.tts.speak(response)
#         return response

#     def _handle_application(self, command, entities, conversation_manager):
#         """Handle application commands"""
#         app_name = entities.get('app_name')
#         if not app_name:
#             self.tts.speak("Which application would you like me to open?")
#             return False
            
#         # Check if it's a close command
#         if any(word in command for word in ['close', 'quit', 'exit']):
#             return self._close_application(app_name)
#         else:
#             return self._open_application(app_name)

#     def _open_application(self, app_name):
#         """Open application with enhanced path resolution"""
#         try:
#             # Get app path from config
#             app_path = self._get_application_path(app_name)
            
#             if app_path:
#                 if self.system == "windows":
#                     os.startfile(app_path)
#                 elif self.system == "darwin":  # macOS
#                     subprocess.run(['open', app_path])
#                 elif self.system == "linux":
#                     subprocess.Popen([app_path])
                
#                 self.tts.speak(f"Opening {app_name}")
#                 return True
#             else:
#                 # Try common application names
#                 common_apps = {
#                     'chrome': ['google-chrome', 'chrome', 'Google Chrome'],
#                     'firefox': ['firefox', 'Firefox'],
#                     'notepad': ['notepad', 'gedit', 'TextEdit'],
#                     'calculator': ['calc', 'gnome-calculator', 'Calculator'],
#                     'terminal': ['cmd', 'gnome-terminal', 'Terminal'],
#                     'file manager': ['explorer', 'nautilus', 'Finder']
#                 }
                
#                 for common_name, executables in common_apps.items():
#                     if common_name in app_name.lower():
#                         for exe in executables:
#                             try:
#                                 if self.system == "windows":
#                                     subprocess.run([exe], check=True)
#                                 else:
#                                     subprocess.run([exe], check=True)
#                                 self.tts.speak(f"Opening {app_name}")
#                                 return True
#                             except:
#                                 continue
                
#                 self.tts.speak(f"I couldn't find {app_name}. Please check if it's installed or add it to the configuration.")
#                 return False
                
#         except Exception as e:
#             self.logger.error(f"Failed to open {app_name}: {e}")
#             self.tts.speak(f"Failed to open {app_name}")
#             return False

#     def _close_application(self, app_name):
#         """Close running application"""
#         try:
#             # Find running processes
#             for proc in psutil.process_iter(['pid', 'name']):
#                 if app_name.lower() in proc.info['name'].lower():
#                     proc.terminate()
#                     self.tts.speak(f"Closing {app_name}")
#                     return True
            
#             self.tts.speak(f"{app_name} is not running")
#             return False
            
#         except Exception as e:
#             self.logger.error(f"Failed to close {app_name}: {e}")
#             self.tts.speak(f"Failed to close {app_name}")
#             return False

#     def _handle_web(self, command, entities, conversation_manager):
#         """Handle web-related commands"""
#         query = entities.get('query', '').strip()
        
#         if not query:
#             self.tts.speak("What would you like me to search for or which website should I open?")
#             return False
        
#         # Check if it's a direct website
#         if self._is_website_url(query):
#             return self._open_website(query)
        
#         # Check configured websites
#         websites = self.config.get_websites()
#         for site_name, url in websites.items():
#             if site_name.lower() in query.lower():
#                 return self._open_website(url, site_name)
        
#         # Default to search
#         return self._perform_web_search(query)

#     def _is_website_url(self, text):
#         """Check if text is a URL"""
#         url_patterns = [
#             r'https?://',
#             r'www\.',
#             r'\.com', r'\.org', r'\.net', r'\.edu', r'\.gov'
#         ]
#         return any(re.search(pattern, text) for pattern in url_patterns)

#     def _open_website(self, url, name=None):
#         """Open website in browser"""
#         try:
#             if not url.startswith(('http://', 'https://')):
#                 url = 'https://' + url
                
#             webbrowser.open(url)
            
#             if name:
#                 self.tts.speak(f"Opening {name}")
#             else:
#                 self.tts.speak("Opening website")
#             return True
            
#         except Exception as e:
#             self.logger.error(f"Failed to open website: {e}")
#             self.tts.speak("Failed to open the website")
#             return False

#     def _perform_web_search(self, query):
#         """Perform web search"""
#         try:
#             search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
#             webbrowser.open(search_url)
#             self.tts.speak(f"Here's what I found for {query}")
#             return True
            
#         except Exception as e:
#             self.logger.error(f"Search failed: {e}")
#             self.tts.speak("Search failed")
#             return False

#     def _handle_media(self, command, entities, conversation_manager):
#         """Handle media playback commands"""
#         if 'play' in command:
#             media_name = entities.get('media_name')
#             if media_name:
#                 return self._play_media(media_name)
#         elif 'volume' in command:
#             volume_action = entities.get('volume_action')
#             return self._adjust_volume(volume_action)
#         elif any(word in command for word in ['pause', 'stop', 'resume']):
#             return self._control_playback(command)
        
#         self.tts.speak("I can help with playing music, adjusting volume, or controlling playback.")
#         return False

#     def _play_media(self, media_name):
#         """Play media on YouTube or local system"""
#         try:
#             # Try YouTube first
#             youtube_url = f"https://www.youtube.com/results?search_query={media_name.replace(' ', '+')}"
#             webbrowser.open(youtube_url)
#             self.tts.speak(f"Playing {media_name} on YouTube")
#             return True
            
#         except Exception as e:
#             self.logger.error(f"Failed to play media: {e}")
#             self.tts.speak("Failed to play media")
#             return False

#     def _handle_system(self, command, entities, conversation_manager):
#         """Handle system commands"""
#         if any(word in command for word in ['shutdown', 'restart', 'sleep', 'lock']):
#             return self._system_power_command(command)
#         elif any(word in command for word in ['battery', 'power']):
#             return self._get_battery_status()
#         elif any(word in command for word in ['cpu', 'memory', 'storage']):
#             return self._get_system_stats()
#         elif any(word in command for word in ['wifi', 'network']):
#             return self._get_network_status()
        
#         self.tts.speak("I can help with system status, power management, and network information.")
#         return False

#     def _get_battery_status(self):
#         """Get battery status"""
#         try:
#             battery = psutil.sensors_battery()
#             if battery:
#                 percent = round(battery.percent)
#                 status = "charging" if battery.power_plugged else "on battery"
                
#                 if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
#                     hours, remainder = divmod(battery.secsleft, 3600)
#                     minutes = remainder // 60
#                     time_left = f"{hours} hours and {minutes} minutes"
#                     response = f"Battery is at {percent}% and {status}. Time remaining: {time_left}"
#                 else:
#                     response = f"Battery is at {percent}% and {status}"
                
#                 self.tts.speak(response)
#                 return True
#             else:
#                 self.tts.speak("No battery information available")
#                 return False
                
#         except Exception as e:
#             self.logger.error(f"Battery status error: {e}")
#             self.tts.speak("Could not get battery status")
#             return False

#     def _handle_weather(self, command, entities, conversation_manager):
#         """Handle weather requests with multiple APIs"""
#         location = entities.get('location', 'current location')
        
#         try:
#             # Try multiple weather sources
#             weather_info = self._get_weather_info(location)
#             if weather_info:
#                 self.tts.speak(weather_info)
#                 return True
#             else:
#                 self.tts.speak("Could not get weather information right now")
#                 return False
                
#         except Exception as e:
#             self.logger.error(f"Weather error: {e}")
#             self.tts.speak("Weather service is unavailable")
#             return False

#     def _get_weather_info(self, location):
#         """Get weather information from multiple sources"""
#         # Try OpenWeatherMap API first if available
#         if self.weather_key:
#             try:
#                 url = f"http://api.openweathermap.org/data/2.5/weather"
#                 params = {
#                     'q': location,
#                     'appid': self.weather_key,
#                     'units': 'metric'
#                 }
#                 response = requests.get(url, params=params, timeout=10)
#                 data = response.json()
                
#                 if response.status_code == 200:
#                     temp = round(data['main']['temp'])
#                     description = data['weather'][0]['description']
#                     humidity = data['main']['humidity']
                    
#                     return f"The weather in {location} is {description} with a temperature of {temp} degrees Celsius and {humidity}% humidity."
                    
#             except Exception as e:
#                 self.logger.debug(f"OpenWeatherMap API failed: {e}")
        
#         # Fallback to web scraping
#         try:
#             headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
#             url = f"https://www.google.com/search?q=weather+{location.replace(' ', '+')}"
#             response = requests.get(url, headers=headers, timeout=10)
            
#             soup = BeautifulSoup(response.text, 'html.parser')
            
#             # Try to find weather information in Google results
#             temp_element = soup.find('div', class_='BNeawe iBp4i AP7Wnd')
#             desc_element = soup.find('div', class_='BNeawe tAd8D AP7Wnd')
            
#             if temp_element and desc_element:
#                 temp = temp_element.text
#                 desc = desc_element.text.split('\n')[0]  # Get first line
#                 return f"The weather in {location} is {desc} with a temperature of {temp}."
                
#         except Exception as e:
#             self.logger.debug(f"Weather web scraping failed: {e}")
        
#         return None

#     def _handle_calculation(self, command, entities, conversation_manager):
#         """Handle mathematical calculations"""
#         expression = entities.get('expression', command)
        
#         # Try Wolfram Alpha first
#         if self.wolfram_available:
#             try:
#                 res = self.wolfram_client.query(expression)
#                 answer = next(res.results).text
#                 self.tts.speak(f"The answer is {answer}")
#                 return True
#             except Exception as e:
#                 self.logger.debug(f"Wolfram Alpha failed: {e}")
        
#         # Fallback to basic math evaluation
#         try:
#             # Extract mathematical expression
#             math_match = re.search(r'[\d\+\-\*/\.\(\)\s]+', expression)
#             if math_match:
#                 math_expr = math_match.group().strip()
#                 # Safe evaluation
#                 result = eval(math_expr)
#                 self.tts.speak(f"The answer is {result}")
#                 return True
#         except Exception as e:
#             self.logger.debug(f"Math evaluation failed: {e}")
        
#         self.tts.speak("I couldn't calculate that. Please try rephrasing your question.")
#         return False

#     def _handle_question(self, command, entities, conversation_manager):
#         """Handle general questions using multiple sources"""
#         topic = entities.get('topic', command)
        
#         # Try OpenAI GPT first
#         if self.openai_available:
#             try:
#                 response = openai.ChatCompletion.create(
#                     model="gpt-3.5-turbo",
#                     messages=[
#                         {"role": "system", "content": "You are a helpful AI assistant. Provide concise, accurate answers."},
#                         {"role": "user", "content": topic}
#                     ],
#                     max_tokens=150,
#                     temperature=0.7
#                 )
#                 answer = response.choices[0].message.content.strip()
#                 self.tts.speak(answer)
#                 return True
#             except Exception as e:
#                 self.logger.debug(f"OpenAI API failed: {e}")
        
#         # Try Wolfram Alpha for factual questions
#         if self.wolfram_available:
#             try:
#                 res = self.wolfram_client.query(topic)
#                 answer = next(res.results).text
#                 self.tts.speak(answer)
#                 return True
#             except Exception as e:
#                 self.logger.debug(f"Wolfram Alpha failed: {e}")
        
#         # Try Wikipedia
#         try:
#             # Extract key terms for Wikipedia search
#             search_terms = re.sub(r'\b(what|who|when|where|why|how|is|are|was|were|tell|me|about)\b', '', topic, flags=re.IGNORECASE)
#             search_terms = search_terms.strip()
            
#             if search_terms:
#                 summary = wikipedia.summary(search_terms, sentences=2)
#                 self.tts.speak(summary)
#                 return True
#         except Exception as e:
#             self.logger.debug(f"Wikipedia search failed: {e}")
        
#         # Fallback to web search
#         search_query = topic.replace(' ', '+')
#         search_url = f"https://www.google.com/search?q={search_query}"
#         webbrowser.open(search_url)
#         self.tts.speak("I've opened a web search for that question.")
#         return True

#     def _handle_email(self, command, entities, conversation_manager):
#         """Handle email operations"""
#         if any(phrase in command for phrase in ['check', 'read']):
#             return self._read_emails()
#         elif 'send' in command:
#             return self._compose_email()
        
#         self.tts.speak("I can help you check emails or send new ones.")
#         return False

#     def _read_emails(self):
#         """Read recent emails"""
#         try:
#             gmail_config = self.config.get_gmail_config()
#             if not gmail_config or not gmail_config.get('email') or not gmail_config.get('app_password'):
#                 self.tts.speak("Gmail configuration is missing. Please add your credentials to the config.")
#                 return False
            
#             mail = imaplib.IMAP4_SSL("imap.gmail.com")
#             mail.login(gmail_config['email'], gmail_config['app_password'])
#             mail.select("inbox")
            
#             status, messages = mail.search(None, "UNSEEN")
#             mail_ids = messages[0].split()
            
#             if not mail_ids:
#                 self.tts.speak("You have no new emails.")
#                 return True
            
#             count = min(3, len(mail_ids))
#             self.tts.speak(f"You have {len(mail_ids)} new emails. Here are the latest {count}:")
            
#             for i in mail_ids[-count:]:
#                 status, msg_data = mail.fetch(i, "(RFC822)")
#                 msg = email.message_from_bytes(msg_data[0][1])
                
#                 subject, encoding = decode_header(msg["Subject"])[0]
#                 if isinstance(subject, bytes):
#                     subject = subject.decode(encoding or "utf-8")
                
#                 sender = msg.get("From")
#                 # Extract sender name from email format
#                 sender_match = re.search(r'([^<]+)<', sender)
#                 if sender_match:
#                     sender_name = sender_match.group(1).strip()
#                 else:
#                     sender_name = sender.split('@')[0]
                
#                 self.tts.speak(f"Email from {sender_name}: {subject}")
            
#             mail.logout()
#             return True
            
#         except Exception as e:
#             self.logger.error(f"Email reading failed: {e}")
#             self.tts.speak("I couldn't access your emails. Please check your configuration.")
#             return False

#     def _handle_time(self, command, entities, conversation_manager):
#         """Handle time and date requests"""
#         now = datetime.now()
        
#         if any(word in command for word in ['time', 'clock']):
#             time_str = now.strftime("%I:%M %p")
#             self.tts.speak(f"The current time is {time_str}")
#             return True
            
#         elif any(word in command for word in ['date', 'today']):
#             date_str = now.strftime("%A, %B %d, %Y")
#             self.tts.speak(f"Today is {date_str}")
#             return True
            
#         elif 'tomorrow' in command:
#             tomorrow = now + timedelta(days=1)
#             date_str = tomorrow.strftime("%A, %B %d, %Y")
#             self.tts.speak(f"Tomorrow is {date_str}")
#             return True
        
#         # Default to current time
#         time_str = now.strftime("%I:%M %p on %A, %B %d")
#         self.tts.speak(f"It's currently {time_str}")
#         return True

#     def _handle_control(self, command, entities, conversation_manager):
#         """Handle system control commands"""
#         self.tts.speak("System control features are being developed.")
#         return False

#     def _handle_unknown(self, command, entities, conversation_manager):
#         """Handle unknown commands with suggestions"""
#         suggestions = self.get_command_suggestions(command)
        
#         if suggestions:
#             suggestion_text = f"I'm not sure about that. Did you mean: {', '.join(suggestions[:3])}?"
#         else:
#             suggestion_text = "I didn't understand that. Try commands like 'open chrome', 'play music', 'check weather', or ask me questions."
        
#         self.tts.speak(suggestion_text)
#         return False

#     def get_command_suggestions(self, command):
#         """Get command suggestions based on similarity"""
#         common_commands = [
#             "open chrome", "play music", "check weather", "what time is it",
#             "read my email", "search for", "shutdown computer", "battery status",
#             "take a note", "set reminder", "calculator", "current weather"
#         ]
        
#         # Use fuzzy matching to find similar commands
#         suggestions = []
#         for cmd in common_commands:
#             similarity = fuzz.ratio(command.lower(), cmd.lower())
#             if similarity > 60:  # 60% similarity threshold
#                 suggestions.append((cmd, similarity))
        
#         # Sort by similarity and return top suggestions
#         suggestions.sort(key=lambda x: x[1], reverse=True)
#         return [cmd for cmd, _ in suggestions[:5]]

#     def _get_application_path(self, app_name):
#         """Get application path from configuration"""
#         apps = self.config.get_applications()
#         app_info = apps.get(app_name.lower())
        
#         if isinstance(app_info, dict):
#             return app_info.get(self.system)
#         return app_info

#     def get_context(self):
#         """Get current conversation context"""
#         return self.context.copy()

#     def update_user_preferences(self, preferences):
#         """Update user preferences"""
#         self.context['user_preferences'].update(preferences)
#         self.logger.info("User preferences updated")











"""
Enhanced Action Handler with FREE open-source services only
No paid APIs required - uses only free alternatives
"""

import os
import re
import json
import time
import logging
import requests
import subprocess
import webbrowser
import platform
import smtplib
import imaplib
import email
import psutil
from datetime import datetime, timedelta
from difflib import get_close_matches
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import speech_recognition as sr
import wikipedia
import urllib.parse
import random

class EnhancedActionHandler:
    def __init__(self, config_manager, tts_engine):
        self.logger = logging.getLogger(__name__)
        self.config = config_manager
        self.tts = tts_engine
        self.system = platform.system().lower()
        
        # Initialize free services only
        self._initialize_free_services()
        
        # Command patterns and handlers
        self.command_patterns = self._build_command_patterns()
        self.intent_classifiers = self._build_intent_classifiers()
        
        # Context and conversation state
        self.context = {
            'last_intent': None,
            'last_entity': None,
            'conversation_history': [],
            'user_preferences': {}
        }
        
        # Free knowledge base for common questions
        self.knowledge_base = self._build_knowledge_base()
        
        self.logger.info("Free Enhanced Action Handler initialized (no paid APIs)")

    def _initialize_free_services(self):
        """Initialize only free services"""
        # All services used are free
        self.logger.info("Using only free and open-source services")
        
        # Free weather service (OpenWeatherMap has a free tier)
        self.free_weather_key = os.getenv('OPENWEATHER_FREE_KEY')  # Optional free tier
        
        # Wikipedia is always free
        self.wikipedia_available = True
        
        # Free APIs that don't require keys
        self.duckduckgo_available = True
        self.wttr_weather_available = True  # wttr.in - completely free weather

    def _build_knowledge_base(self):
        """Build a simple knowledge base for common questions"""
        return {
            'what is ai': 'Artificial Intelligence is the simulation of human intelligence in machines that are programmed to think and learn.',
            'what is python': 'Python is a high-level programming language known for its simplicity and readability.',
            'what is machine learning': 'Machine learning is a subset of AI that enables computers to learn without being explicitly programmed.',
            'what is the internet': 'The internet is a global network of interconnected computers that communicate using standardized protocols.',
            'how does a computer work': 'A computer works by processing data through its CPU, storing information in memory, and following programmed instructions.',
            'what is programming': 'Programming is the process of creating instructions for computers to execute tasks and solve problems.',
            'what is open source': 'Open source refers to software whose source code is freely available for anyone to inspect, modify, and distribute.',
            'what is linux': 'Linux is a free and open-source operating system kernel that forms the basis of many operating systems.',
            'what is github': 'GitHub is a web-based platform for version control and collaboration using Git.',
            'what is javascript': 'JavaScript is a programming language primarily used for web development to create interactive websites.'
        }

    def _build_command_patterns(self):
        """Build regex patterns for command recognition"""
        return {
            'greeting': [
                r'hello|hi|hey|good morning|good afternoon|good evening',
                r'how are you|what\'s up|sup'
            ],
            'application': [
                r'open|start|launch|run (.+)',
                r'close|quit|exit (.+)'
            ],
            'web': [
                r'go to|open|visit (.+)',
                r'search for|google|find (.+)',
                r'browse (.+)'
            ],
            'media': [
                r'play (.+)',
                r'pause|stop|resume',
                r'volume (up|down|\d+)',
                r'next|previous|skip'
            ],
            'system': [
                r'shutdown|restart|sleep|lock',
                r'battery|power|cpu|memory|storage',
                r'wifi|network|bluetooth'
            ],
            'email': [
                r'check|read (my )?email',
                r'send email to (.+)',
                r'compose email'
            ],
            'weather': [
                r'weather in (.+)|(.+) weather',
                r'temperature|forecast|rain|sunny'
            ],
            'time': [
                r'what time|current time|time now',
                r'set (alarm|timer|reminder)',
                r'date|today|tomorrow'
            ],
            'calculation': [
                r'calculate|compute|math',
                r'what is \d+.*\d+',
                r'convert (.+) to (.+)'
            ],
            'question': [
                r'what is|who is|when is|where is|why is|how is',
                r'tell me about|information about',
                r'define|meaning of'
            ],
            'control': [
                r'increase|decrease|adjust (.+)',
                r'set (.+) to (.+)',
                r'turn (on|off) (.+)'
            ]
        }

    def _build_intent_classifiers(self):
        """Build intent classification rules"""
        return {
            'greeting': ['hello', 'hi', 'hey', 'morning', 'afternoon', 'evening'],
            'question': ['what', 'who', 'when', 'where', 'why', 'how', 'tell', 'explain'],
            'command': ['open', 'close', 'start', 'stop', 'play', 'pause', 'set'],
            'search': ['search', 'find', 'look', 'google', 'browse'],
            'system': ['shutdown', 'restart', 'battery', 'volume', 'wifi'],
            'personal': ['email', 'calendar', 'reminder', 'note']
        }

    def handle_command(self, command, conversation_manager=None):
        """Main command handling with enhanced processing"""
        try:
            self.logger.info(f"Processing command: {command}")
            
            # Preprocess command
            processed_command = self._preprocess_command(command)
            
            # Classify intent
            intent = self._classify_intent(processed_command)
            self.context['last_intent'] = intent
            
            # Extract entities
            entities = self._extract_entities(processed_command, intent)
            self.context['last_entity'] = entities
            
            # Handle based on intent
            response = self._route_command(intent, processed_command, entities, conversation_manager)
            
            # Update conversation history
            self.context['conversation_history'].append({
                'command': command,
                'intent': intent,
                'entities': entities,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Command handling error: {e}")
            self.tts.speak("I encountered an error processing that command.")
            return False

    def _preprocess_command(self, command):
        """Preprocess and clean command text"""
        # Convert to lowercase
        command = command.lower().strip()
        
        # Remove filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically']
        words = command.split()
        words = [word for word in words if word not in filler_words]
        
        # Rejoin and clean
        command = ' '.join(words)
        command = re.sub(r'\s+', ' ', command)  # Multiple spaces to single
        
        return command

    def _classify_intent(self, command):
        """Classify command intent using multiple methods"""
        scores = {}
        
        # Pattern matching
        for intent, patterns in self.command_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, command):
                    score += 10
            scores[intent] = score
        
        # Keyword matching
        for intent, keywords in self.intent_classifiers.items():
            score = scores.get(intent, 0)
            for keyword in keywords:
                if keyword in command:
                    score += 5
            scores[intent] = score
        
        # Return highest scoring intent
        if scores:
            return max(scores, key=scores.get)
        return 'unknown'

    def _extract_entities(self, command, intent):
        """Extract relevant entities from command"""
        entities = {}
        
        # Extract based on intent
        if intent == 'application':
            # Extract app name
            match = re.search(r'(?:open|start|launch|run|close|quit|exit)\s+(.+)', command)
            if match:
                entities['app_name'] = match.group(1).strip()
                
        elif intent == 'web':
            # Extract website or search query
            match = re.search(r'(?:go to|open|visit|search for|google|find|browse)\s+(.+)', command)
            if match:
                entities['query'] = match.group(1).strip()
                
        elif intent == 'media':
            # Extract media commands
            if 'play' in command:
                match = re.search(r'play\s+(.+)', command)
                if match:
                    entities['media_name'] = match.group(1).strip()
            elif any(word in command for word in ['volume', 'sound']):
                match = re.search(r'volume\s+(up|down|\d+)', command)
                if match:
                    entities['volume_action'] = match.group(1)
                    
        elif intent == 'weather':
            # Extract location
            match = re.search(r'weather in (.+)|(.+) weather', command)
            if match:
                entities['location'] = (match.group(1) or match.group(2)).strip()
                
        elif intent == 'calculation':
            # Extract math expression
            entities['expression'] = command
            
        elif intent == 'question':
            # Extract question topic
            entities['topic'] = command
            
        return entities

    def _route_command(self, intent, command, entities, conversation_manager):
        """Route command to appropriate handler"""
        handlers = {
            'greeting': self._handle_greeting,
            'application': self._handle_application,
            'web': self._handle_web,
            'media': self._handle_media,
            'system': self._handle_system,
            'email': self._handle_email,
            'weather': self._handle_weather,
            'time': self._handle_time,
            'calculation': self._handle_calculation,
            'question': self._handle_question,
            'control': self._handle_control
        }
        
        handler = handlers.get(intent, self._handle_unknown)
        return handler(command, entities, conversation_manager)

    def _handle_greeting(self, command, entities, conversation_manager):
        """Handle greeting commands"""
        greetings = [
            "Hello! How can I assist you today?",
            "Hi there! What would you like me to help you with?",
            "Good to see you! How may I help?",
            "Hello! I'm ready to assist you."
        ]
        
        # Personalize based on time
        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "Good morning! "
        elif hour < 18:
            time_greeting = "Good afternoon! "
        else:
            time_greeting = "Good evening! "
            
        response = time_greeting + random.choice(greetings).replace("Hello! ", "")
        self.tts.speak(response)
        return response

    def _handle_application(self, command, entities, conversation_manager):
        """Handle application commands"""
        app_name = entities.get('app_name')
        if not app_name:
            self.tts.speak("Which application would you like me to open?")
            return False
            
        # Check if it's a close command
        if any(word in command for word in ['close', 'quit', 'exit']):
            return self._close_application(app_name)
        else:
            return self._open_application(app_name)

    def _open_application(self, app_name):
        """Open application with enhanced path resolution"""
        try:
            # Get app path from config
            app_path = self._get_application_path(app_name)
            
            if app_path:
                if self.system == "windows":
                    os.startfile(app_path)
                elif self.system == "darwin":  # macOS
                    subprocess.run(['open', app_path])
                elif self.system == "linux":
                    subprocess.Popen([app_path])
                
                self.tts.speak(f"Opening {app_name}")
                return True
            else:
                # Try common application names
                common_apps = {
                    'chrome': ['google-chrome', 'chrome', 'Google Chrome'],
                    'firefox': ['firefox', 'Firefox'],
                    'notepad': ['notepad', 'gedit', 'TextEdit'],
                    'calculator': ['calc', 'gnome-calculator', 'Calculator'],
                    'terminal': ['cmd', 'gnome-terminal', 'Terminal'],
                    'file manager': ['explorer', 'nautilus', 'Finder']
                }
                
                for common_name, executables in common_apps.items():
                    if common_name in app_name.lower():
                        for exe in executables:
                            try:
                                if self.system == "windows":
                                    subprocess.run([exe], check=True)
                                else:
                                    subprocess.run([exe], check=True)
                                self.tts.speak(f"Opening {app_name}")
                                return True
                            except:
                                continue
                
                self.tts.speak(f"I couldn't find {app_name}. Please check if it's installed or add it to the configuration.")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to open {app_name}: {e}")
            self.tts.speak(f"Failed to open {app_name}")
            return False

    def _close_application(self, app_name):
        """Close running application"""
        try:
            # Find running processes
            for proc in psutil.process_iter(['pid', 'name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    self.tts.speak(f"Closing {app_name}")
                    return True
            
            self.tts.speak(f"{app_name} is not running")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to close {app_name}: {e}")
            self.tts.speak(f"Failed to close {app_name}")
            return False

    def _handle_web(self, command, entities, conversation_manager):
        """Handle web-related commands"""
        query = entities.get('query', '').strip()
        
        if not query:
            self.tts.speak("What would you like me to search for or which website should I open?")
            return False
        
        # Check if it's a direct website
        if self._is_website_url(query):
            return self._open_website(query)
        
        # Check configured websites
        websites = self.config.get_websites()
        for site_name, url in websites.items():
            if site_name.lower() in query.lower():
                return self._open_website(url, site_name)
        
        # Default to search using DuckDuckGo (privacy-focused, free)
        return self._perform_web_search(query)

    def _is_website_url(self, text):
        """Check if text is a URL"""
        url_patterns = [
            r'https?://',
            r'www\.',
            r'\.com', r'\.org', r'\.net', r'\.edu', r'\.gov'
        ]
        return any(re.search(pattern, text) for pattern in url_patterns)

    def _open_website(self, url, name=None):
        """Open website in browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            webbrowser.open(url)
            
            if name:
                self.tts.speak(f"Opening {name}")
            else:
                self.tts.speak("Opening website")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open website: {e}")
            self.tts.speak("Failed to open the website")
            return False

    def _perform_web_search(self, query):
        """Perform web search using DuckDuckGo (free and privacy-focused)"""
        try:
            # Use DuckDuckGo for privacy-focused search
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            self.tts.speak(f"Here's what I found for {query}")
            return True
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            # Fallback to Google
            try:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                self.tts.speak(f"Here's what I found for {query}")
                return True
            except:
                self.tts.speak("Search failed")
                return False

    def _handle_media(self, command, entities, conversation_manager):
        """Handle media playback commands"""
        if 'play' in command:
            media_name = entities.get('media_name')
            if media_name:
                return self._play_media(media_name)
        elif 'volume' in command:
            volume_action = entities.get('volume_action')
            return self._adjust_volume(volume_action)
        elif any(word in command for word in ['pause', 'stop', 'resume']):
            return self._control_playback(command)
        
        self.tts.speak("I can help with playing music, adjusting volume, or controlling playback.")
        return False

    def _play_media(self, media_name):
        """Play media on YouTube (free)"""
        try:
            # YouTube is free to use
            youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(media_name)}"
            webbrowser.open(youtube_url)
            self.tts.speak(f"Playing {media_name} on YouTube")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to play media: {e}")
            self.tts.speak("Failed to play media")
            return False

    def _adjust_volume(self, volume_action):
        """Adjust system volume (free)"""
        try:
            if self.system == "windows":
                if volume_action == "up":
                    subprocess.run(["powershell", "-c", "(New-Object -comObject WScript.Shell).SendKeys([char]175)"])
                elif volume_action == "down":
                    subprocess.run(["powershell", "-c", "(New-Object -comObject WScript.Shell).SendKeys([char]174)"])
                elif volume_action.isdigit():
                    vol = min(100, max(0, int(volume_action)))
                    subprocess.run(["powershell", "-c", f"(New-Object -comObject WScript.Shell).SendKeys([char]173); Start-Sleep 1; (New-Object -ComObject WScript.Shell).SendKeys('{vol}')"])
            
            elif self.system == "linux":
                if volume_action == "up":
                    subprocess.run(["amixer", "sset", "Master", "5%+"])
                elif volume_action == "down":
                    subprocess.run(["amixer", "sset", "Master", "5%-"])
                elif volume_action.isdigit():
                    vol = min(100, max(0, int(volume_action)))
                    subprocess.run(["amixer", "sset", "Master", f"{vol}%"])
            
            elif self.system == "darwin":  # macOS
                if volume_action == "up":
                    subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 10)"])
                elif volume_action == "down":
                    subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 10)"])
                elif volume_action.isdigit():
                    vol = min(100, max(0, int(volume_action)))
                    subprocess.run(["osascript", "-e", f"set volume output volume {vol}"])
            
            self.tts.speak(f"Volume {volume_action}")
            return True
            
        except Exception as e:
            self.logger.error(f"Volume control failed: {e}")
            self.tts.speak("Volume control not available")
            return False

    def _control_playbook(self, command):
        """Control media playbook (free)"""
        try:
            if self.system == "windows":
                if "pause" in command or "stop" in command:
                    subprocess.run(["powershell", "-c", "(New-Object -comObject WScript.Shell).SendKeys([char]179)"])
                elif "resume" in command:
                    subprocess.run(["powershell", "-c", "(New-Object -comObject WScript.Shell).SendKeys([char]179)"])
            
            # For Linux and macOS, you would need specific media player controls
            # This is basic implementation
            
            self.tts.speak("Media control executed")
            return True
            
        except Exception as e:
            self.logger.error(f"Media control failed: {e}")
            self.tts.speak("Media control not available")
            return False

    def _handle_system(self, command, entities, conversation_manager):
        """Handle system commands"""
        if any(word in command for word in ['shutdown', 'restart', 'sleep', 'lock']):
            return self._system_power_command(command)
        elif any(word in command for word in ['battery', 'power']):
            return self._get_battery_status()
        elif any(word in command for word in ['cpu', 'memory', 'storage']):
            return self._get_system_stats()
        elif any(word in command for word in ['wifi', 'network']):
            return self._get_network_status()
        
        self.tts.speak("I can help with system status, power management, and network information.")
        return False

    def _system_power_command(self, command):
        """Handle system power commands with confirmation"""
        action = None
        if 'shutdown' in command:
            action = 'shutdown'
        elif 'restart' in command:
            action = 'restart'
        elif 'sleep' in command:
            action = 'sleep'
        elif 'lock' in command:
            action = 'lock'
        
        if action:
            self.tts.speak(f"Are you sure you want to {action} the system? Say yes to confirm.")
            # This would need voice input confirmation in a real implementation
            # For now, just inform about the command
            self.tts.speak(f"System {action} command received. Please execute manually for safety.")
            return True
        
        return False

    def _get_battery_status(self):
        """Get battery status (free using psutil)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = round(battery.percent)
                status = "charging" if battery.power_plugged else "on battery"
                
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    hours, remainder = divmod(battery.secsleft, 3600)
                    minutes = remainder // 60
                    time_left = f"{hours} hours and {minutes} minutes"
                    response = f"Battery is at {percent}% and {status}. Time remaining: {time_left}"
                else:
                    response = f"Battery is at {percent}% and {status}"
                
                self.tts.speak(response)
                return True
            else:
                self.tts.speak("No battery information available")
                return False
                
        except Exception as e:
            self.logger.error(f"Battery status error: {e}")
            self.tts.speak("Could not get battery status")
            return False

    def _get_system_stats(self):
        """Get system statistics (free using psutil)"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = round((disk.used / disk.total) * 100, 1)
            
            response = f"System status: CPU at {cpu_percent}%, Memory at {memory_percent}%, Disk at {disk_percent}% usage."
            self.tts.speak(response)
            return True
            
        except Exception as e:
            self.logger.error(f"System stats error: {e}")
            self.tts.speak("Could not get system statistics")
            return False

    def _get_network_status(self):
        """Get network status (free using psutil)"""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            active_interfaces = []
            
            for interface_name, interface_addresses in interfaces.items():
                for address in interface_addresses:
                    if str(address.family) == 'AddressFamily.AF_INET':
                        if not address.address.startswith('127.'):
                            active_interfaces.append(interface_name)
            
            if active_interfaces:
                response = f"Network interfaces active: {', '.join(set(active_interfaces))}"
            else:
                response = "No active network connections found"
            
            self.tts.speak(response)
            return True
            
        except Exception as e:
            self.logger.error(f"Network status error: {e}")
            self.tts.speak("Could not get network status")
            return False

    def _handle_weather(self, command, entities, conversation_manager):
        """Handle weather requests using free services"""
        location = entities.get('location', 'current location')
        
        try:
            # Try free weather service
            weather_info = self._get_free_weather_info(location)
            if weather_info:
                self.tts.speak(weather_info)
                return True
            else:
                self.tts.speak("Could not get weather information right now")
                return False
                
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            self.tts.speak("Weather service is unavailable")
            return False

    def _get_free_weather_info(self, location):
        """Get weather information from FREE services"""
        # Try wttr.in - completely free weather service
        try:
            url = f"http://wttr.in/{location}?format=3"  # Simple format
            headers = {'User-Agent': 'curl/7.68.0'}  # wttr.in expects curl user agent
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                weather_text = response.text.strip()
                return f"The weather {weather_text}"
                
        except Exception as e:
            self.logger.debug(f"wttr.in weather failed: {e}")
        
        # Fallback to web scraping Google weather (free)
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            url = f"https://www.google.com/search?q=weather+{location.replace(' ', '+')}"
            response = requests.get(url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find weather information in Google results
            temp_element = soup.find('div', class_='BNeawe iBp4i AP7Wnd')
            desc_element = soup.find('div', class_='BNeawe tAd8D AP7Wnd')
            
            if temp_element and desc_element:
                temp = temp_element.text
                desc = desc_element.text.split('\n')[0]  # Get first line
                return f"The weather in {location} is {desc} with a temperature of {temp}."
                
        except Exception as e:
            self.logger.debug(f"Weather web scraping failed: {e}")
        
        return None

    def _handle_calculation(self, command, entities, conversation_manager):
        """Handle mathematical calculations (free using Python's eval)"""
        expression = entities.get('expression', command)
        
        # Try basic math evaluation (completely free)
        try:
            # Extract mathematical expression
            math_expr = re.search(r'[\d\+\-\*/\.\(\)\s]+', expression)
            if math_expr:
                math_string = math_expr.group().strip()
                # Safe evaluation for basic math
                allowed_chars = set('0123456789+-*/(). ')
                if all(c in allowed_chars for c in math_string):
                    result = eval(math_string)
                    self.tts.speak(f"The answer is {result}")
                    return True
        except Exception as e:
            self.logger.debug(f"Math evaluation failed: {e}")
        
        # Try unit conversions (free)
        if 'convert' in expression:
            result = self._handle_unit_conversion(expression)
            if result:
                return result
        
        self.tts.speak("I couldn't calculate that. Please try a simpler mathematical expression.")
        return False

    def _handle_unit_conversion(self, expression):
        """Handle basic unit conversions (free)"""
        try:
            # Basic temperature conversions
            if 'celsius to fahrenheit' in expression or 'c to f' in expression:
                celsius_match = re.search(r'(\d+(?:\.\d+)?)', expression)
                if celsius_match:
                    celsius = float(celsius_match.group(1))
                    fahrenheit = (celsius * 9/5) + 32
                    self.tts.speak(f"{celsius} degrees Celsius is {fahrenheit:.1f} degrees Fahrenheit")
                    return True
                    
            elif 'fahrenheit to celsius' in expression or 'f to c' in expression:
                fahrenheit_match = re.search(r'(\d+(?:\.\d+)?)', expression)
                if fahrenheit_match:
                    fahrenheit = float(fahrenheit_match.group(1))
                    celsius = (fahrenheit - 32) * 5/9
                    self.tts.speak(f"{fahrenheit} degrees Fahrenheit is {celsius:.1f} degrees Celsius")
                    return True
            
            # Basic length conversions
            elif 'feet to meters' in expression or 'ft to m' in expression:
                feet_match = re.search(r'(\d+(?:\.\d+)?)', expression)
                if feet_match:
                    feet = float(feet_match.group(1))
                    meters = feet * 0.3048
                    self.tts.speak(f"{feet} feet is {meters:.2f} meters")
                    return True
                    
            elif 'meters to feet' in expression or 'm to ft' in expression:
                meters_match = re.search(r'(\d+(?:\.\d+)?)', expression)
                if meters_match:
                    meters = float(meters_match.group(1))
                    feet = meters * 3.28084
                    self.tts.speak(f"{meters} meters is {feet:.2f} feet")
                    return True
                    
        except Exception as e:
            self.logger.debug(f"Unit conversion failed: {e}")
        
        return False

    def _handle_question(self, command, entities, conversation_manager):
        """Handle general questions using FREE sources only"""
        topic = entities.get('topic', command)
        
        # First check our local knowledge base (completely free)
        answer = self._check_knowledge_base(topic)
        if answer:
            self.tts.speak(answer)
            return True
        
        # Try Wikipedia (free)
        try:
            # Extract key terms for Wikipedia search
            search_terms = re.sub(r'\b(what|who|when|where|why|how|is|are|was|were|tell|me|about)\b', '', topic, flags=re.IGNORECASE)
            search_terms = search_terms.strip()
            
            if search_terms:
                try:
                    summary = wikipedia.summary(search_terms, sentences=2, auto_suggest=True)
                    self.tts.speak(summary)
                    return True
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try the first option
                    summary = wikipedia.summary(e.options[0], sentences=2)
                    self.tts.speak(summary)
                    return True
                except wikipedia.exceptions.PageError:
                    # Page not found, continue to web search
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Wikipedia search failed: {e}")
        
        # Fallback to web search (free)
        search_query = topic.replace(' ', '+')
        search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(topic)}"
        webbrowser.open(search_url)
        self.tts.speak("I've opened a web search for that question.")
        return True

    def _check_knowledge_base(self, query):
        """Check local knowledge base for answers"""
        query_lower = query.lower()
        
        # Direct match
        if query_lower in self.knowledge_base:
            return self.knowledge_base[query_lower]
        
        # Fuzzy matching
        for key, answer in self.knowledge_base.items():
            if fuzz.ratio(query_lower, key) > 80:  # 80% similarity
                return answer
        
        # Keyword matching
        query_words = set(query_lower.split())
        for key, answer in self.knowledge_base.items():
            key_words = set(key.split())
            if len(query_words & key_words) >= 2:  # At least 2 common words
                return answer
        
        return None

    def _handle_email(self, command, entities, conversation_manager):
        """Handle email operations (free using IMAP/SMTP)"""
        if any(phrase in command for phrase in ['check', 'read']):
            return self._read_emails()
        elif 'send' in command:
            return self._compose_email()
        
        self.tts.speak("I can help you check emails or send new ones.")
        return False

    def _read_emails(self):
        """Read recent emails (free using IMAP)"""
        try:
            gmail_config = self.config.get_gmail_config()
            if not gmail_config or not gmail_config.get('email') or not gmail_config.get('app_password'):
                self.tts.speak("Gmail configuration is missing. Please add your credentials to the config.")
                return False
            
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(gmail_config['email'], gmail_config['app_password'])
            mail.select("inbox")
            
            status, messages = mail.search(None, "UNSEEN")
            mail_ids = messages[0].split()
            
            if not mail_ids:
                self.tts.speak("You have no new emails.")
                return True
            
            count = min(3, len(mail_ids))
            self.tts.speak(f"You have {len(mail_ids)} new emails. Here are the latest {count}:")
            
            for i in mail_ids[-count:]:
                status, msg_data = mail.fetch(i, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                
                sender = msg.get("From")
                # Extract sender name from email format
                sender_match = re.search(r'([^<]+)<', sender)
                if sender_match:
                    sender_name = sender_match.group(1).strip()
                else:
                    sender_name = sender.split('@')[0]
                
                self.tts.speak(f"Email from {sender_name}: {subject}")
            
            mail.logout()
            return True
            
        except Exception as e:
            self.logger.error(f"Email reading failed: {e}")
            self.tts.speak("I couldn't access your emails. Please check your configuration.")
            return False

    def _compose_email(self):
        """Simple email composition guide"""
        self.tts.speak("To send emails, please configure your Gmail credentials in the config file with an app-specific password.")
        return False

    def _handle_time(self, command, entities, conversation_manager):
        """Handle time and date requests (completely free)"""
        now = datetime.now()
        
        if any(word in command for word in ['time', 'clock']):
            time_str = now.strftime("%I:%M %p")
            self.tts.speak(f"The current time is {time_str}")
            return True
            
        elif any(word in command for word in ['date', 'today']):
            date_str = now.strftime("%A, %B %d, %Y")
            self.tts.speak(f"Today is {date_str}")
            return True
            
        elif 'tomorrow' in command:
            tomorrow = now + timedelta(days=1)
            date_str = tomorrow.strftime("%A, %B %d, %Y")
            self.tts.speak(f"Tomorrow is {date_str}")
            return True
        
        # Default to current time
        time_str = now.strftime("%I:%M %p on %A, %B %d")
        self.tts.speak(f"It's currently {time_str}")
        return True

    def _handle_control(self, command, entities, conversation_manager):
        """Handle system control commands"""
        self.tts.speak("System control features are available for basic operations.")
        return False

    def _handle_unknown(self, command, entities, conversation_manager):
        """Handle unknown commands with suggestions"""
        suggestions = self.get_command_suggestions(command)
        
        if suggestions:
            suggestion_text = f"I'm not sure about that. Did you mean: {', '.join(suggestions[:3])}?"
        else:
            suggestion_text = "I didn't understand that. Try commands like 'open chrome', 'play music', 'check weather', or ask me questions."
        
        self.tts.speak(suggestion_text)
        return False

    def get_command_suggestions(self, command):
        """Get command suggestions based on similarity"""
        common_commands = [
            "open chrome", "play music", "check weather", "what time is it",
            "read my email", "search for", "battery status", "system stats",
            "what is python", "calculate 2 plus 2", "current time", "today's date"
        ]
        
        # Use fuzzy matching to find similar commands
        suggestions = []
        for cmd in common_commands:
            similarity = fuzz.ratio(command.lower(), cmd.lower())
            if similarity > 60:  # 60% similarity threshold
                suggestions.append((cmd, similarity))
        
        # Sort by similarity and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, _ in suggestions[:5]]

    def _get_application_path(self, app_name):
        """Get application path from configuration"""
        apps = self.config.get_applications()
        app_info = apps.get(app_name.lower())
        
        if isinstance(app_info, dict):
            return app_info.get(self.system)
        return app_info

    def get_context(self):
        """Get current conversation context"""
        return self.context.copy()

    def update_user_preferences(self, preferences):
        """Update user preferences"""
        self.context['user_preferences'].update(preferences)
        self.logger.info("User preferences updated")

    def add_to_knowledge_base(self, question, answer):
        """Add new knowledge to local knowledge base"""
        self.knowledge_base[question.lower()] = answer
        self.logger.info(f"Added to knowledge base: {question}")

    def get_free_service_status(self):
        """Get status of all free services"""
        status = {
            'wikipedia': self.wikipedia_available,
            'duckduckgo_search': self.duckduckgo_available,
            'wttr_weather': self.wttr_weather_available,
            'system_monitoring': True,  # psutil is always available
            'web_browsing': True,  # webbrowser is built-in
            'local_knowledge_base': len(self.knowledge_base) > 0
        }
        return status