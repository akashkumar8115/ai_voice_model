<!-- # AI Voice Assistant - Production Level

A sophisticated, production-ready AI voice assistant with advanced speech recognition, natural language processing, and comprehensive system integration capabilities.

## 🌟 Features

### Core Capabilities
- **Advanced Voice Recognition** with noise reduction and VAD
- **High-Quality Text-to-Speech** with multiple engine support
- **Natural Language Processing** with intent classification
- **Contextual Conversations** with memory and learning
- **System Integration** for applications and web browsing
- **Email Management** with Gmail integration
- **Weather Information** with multiple data sources
- **Smart Search** with AI-powered responses
- **Performance Monitoring** and detailed logging

### AI Integration
- **OpenAI GPT** for intelligent conversations
- **Wolfram Alpha** for mathematical and factual queries
- **Wikipedia** for general knowledge
- **Azure Speech Services** for premium voice quality
- **Google Text-to-Speech** for additional voice options

### System Control
- **Application Management** - Open, close, and control applications
- **Web Browser Control** - Navigate websites and search
- **Media Control** - Play music, adjust volume, control playback
- **System Information** - Battery, CPU, memory, network status
- **File Operations** - Basic file management capabilities

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the files
# Navigate to project directory
cd ai-voice-assistant

# Install required packages
pip install -r requirements.txt

# For Linux/Ubuntu users:
sudo apt update
sudo apt install python3-pyaudio portaudio19-dev espeak espeak-data

# For macOS users:
brew install portaudio espeak
```

### 2. Basic Setup

```bash
# Run the assistant for first time
python main.py
```

The assistant will create necessary directories and configuration files automatically.

### 3. Configuration

Edit the generated `~/.jarvis_assistant/config.json` file to customize:

- **Applications**: Add paths to your favorite applications
- **Websites**: Configure website shortcuts  
- **Voice Settings**: Adjust speech rate, volume, and voice selection
- **User Preferences**: Set location, wake words, and response style

### 4. API Keys (Optional but Recommended)

Create a `.env` file in the project directory:

```env
OPENAI_API_KEY=your_openai_key_here
WOLFRAM_API_KEY=your_wolfram_alpha_key_here  
WEATHER_API_KEY=your_openweather_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=your_azure_region_here
```

### 5. Gmail Setup (Optional)

1. Enable 2-Factor Authentication in Gmail
2. Generate an App Password for the assistant
3. Add credentials to config.json:

```json
"gmail": {
  "email": "your-email@gmail.com",
  "app_password": "your-app-password"
}
```

## 💬 Usage Examples

### Voice Commands

**Basic Interactions:**
- "Hello Jarvis"
- "What time is it?"
- "How are you?"

**Application Control:**
- "Open Chrome"
- "Start Spotify" 
- "Close notepad"
- "Launch calculator"

**Web Browsing:**
- "Go to YouTube"
- "Open Gmail"
- "Search for Python tutorials"
- "Find restaurants near me"

**System Information:**
- "Check battery status"
- "What's my CPU usage?"
- "Show memory information"
- "Network status"

**Email Management:**
- "Check my email"
- "Read my emails"
- "Send email to John"
- "Compose email"

**Weather and Time:**
- "What's the weather like?"
- "Weather in London"
- "Will it rain tomorrow?"
- "Current time"

**Questions and Search:**
- "What is artificial intelligence?"
- "Who invented the telephone?"
- "Calculate 15% of 250"
- "Convert 100 dollars to euros"

**Media Control:**
- "Play some music"
- "Play Bohemian Rhapsody on YouTube"
- "Volume up"
- "Pause music"

### Advanced Features

**Conversation Context:**
```
You: "Open Chrome"
Assistant: "Opening Chrome for you."
You: "Go to GitHub" (remembers you're using browser)
Assistant: "Taking you to GitHub."
```

**Smart Suggestions:**
The assistant learns your patterns and provides contextual suggestions based on time, usage, and conversation history.

**Multi-Engine TTS:**
Automatically falls back to different TTS engines for optimal voice quality and reliability.

## 🛠️ Configuration Options

### Voice Settings
```json
"voice_settings": {
  "engine": "pyttsx3",       // pyttsx3, gtts, azure
  "rate": 165,               // Speech rate (50-300)
  "volume": 0.9,             // Volume (0.0-1.0)
  "voice_id": null           // Specific voice ID
}
```

### Recognition Settings
```json
"recognition_settings": {
  "energy_threshold": 4000,      // Microphone sensitivity
  "pause_threshold": 0.8,        // Pause detection
  "phrase_time_limit": 8,        // Max phrase length
  "timeout": 1                   // Listen timeout
}
```

### Security Settings
```json
"security": {
  "require_confirmation": ["shutdown", "restart"],
  "blocked_commands": ["rm -rf", "format"],
  "safe_mode": false,
  "rate_limiting": {
    "enabled": true,
    "max_commands_per_minute": 30
  }
}
```

## 📁 Project Structure

```
ai-voice-assistant/
├── main.py                    # Main application entry point
├── voice_input.py            # Enhanced voice recognition
├── enhanced_tts.py           # Advanced text-to-speech
├── enhanced_actions.py       # Command processing and AI integration
├── config_manager.py         # Configuration management
├── conversation_manager.py   # Context and conversation handling
├── utils.py                  # Utility functions and logging
├── requirements.txt          # Python dependencies
├── sample_config.json        # Sample configuration
└── README.md                # This file

Generated directories:
~/.jarvis_assistant/
├── config.json              # User configuration
├── logs/                    # Application logs
├── sessions/                # Conversation sessions
└── backups/                 # Configuration backups
```

## 🔧 Advanced Configuration

### Custom Applications

Add your applications to config.json:

```json
"applications": {
  "my_app": {
    "windows": "C:\\Path\\To\\MyApp.exe",
    "linux": "/usr/bin/myapp", 
    "darwin": "/Applications/MyApp.app"
  }
}
```

### Custom Websites

Add website shortcuts:

```json
"websites": {
  "my_site": "https://example.com",
  "local_server": "http://localhost:3000"
}
```

### Wake Words

Customize wake words:

```json
"user_preferences": {
  "wake_words": [
    "jarvis",
    "computer", 
    "assistant",
    "hey ai"
  ]
}
```

### Response Personality

Customize the assistant's personality:

```json
"user_preferences": {
  "personality": {
    "humor_level": "high",        // low, medium, high
    "formality": "casual",        // formal, casual, friendly  
    "verbosity": "concise"        // concise, normal, detailed
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**Microphone Not Working:**
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Check permissions (Linux)
sudo usermod -a -G audio $USER

# Install audio dependencies
sudo apt install pulseaudio pavucontrol
```

**TTS Not Working:**
```bash
# Install TTS dependencies
pip install pyttsx3 gtts pygame pydub

# Linux TTS
sudo apt install espeak espeak-data libespeak-dev

# Test TTS
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"
```

**Import Errors:**
```bash
# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# For PyAudio issues:
# Ubuntu: sudo apt install python3-pyaudio
# Windows: pip install pipwin && pipwin install pyaudio
```

**Performance Issues:**
- Reduce `energy_threshold` in config
- Increase `phrase_time_limit` 
- Close other audio applications
- Check CPU usage and memory

### Debugging

Enable debug mode in config:
```json
"advanced": {
  "developer_options": {
    "debug_mode": true,
    "verbose_logging": true
  }
}
```

Check logs:
```bash
# View main log
tail -f ~/.jarvis_assistant/logs/jarvis_assistant.log

# View error log  
tail -f ~/.jarvis_assistant/logs/jarvis_errors.log
```

## 📊 Performance Optimization

### Memory Usage
- Limit conversation history: `max_history` in conversation manager
- Enable auto-cleanup: `auto_delete_logs_after_days` in config
- Adjust cache size: `cache_size_mb` in performance settings

### CPU Usage  
- Reduce background processing: `background_processing: false`
- Lower audio quality: Use pyttsx3 instead of Azure TTS
- Optimize threading: Adjust `max_worker_threads`

### Network Usage
- Cache responses: `cache_responses: true`
- Limit API calls: Configure rate limiting
- Use local services when possible

## 🔒 Security Considerations

### Safe Practices
1. **API Keys**: Store in environment variables, not config files
2. **Permissions**: Run with minimal required system permissions  
3. **Commands**: Use confirmation for destructive operations
4. **Network**: Validate all URLs and external requests
5. **Logs**: Be careful with sensitive information in logs

### Safe Mode
Enable safe mode for restricted environments:
```json
"security": {
  "safe_mode": true,
  "require_confirmation": ["*"]  // Confirm all commands
}
```

## 📈 Monitoring and Analytics

### Performance Metrics
The assistant tracks:
- Command success rates
- Response times  
- Memory/CPU usage
- API call statistics
- Error frequency

### Conversation Analytics
- Intent patterns
- User preferences
- Command frequency
- Session duration
- Context effectiveness

## 🔄 Updates and Maintenance

### Regular Maintenance
1. **Update Dependencies**: `pip install -r requirements.txt --upgrade`
2. **Clear Old Logs**: Automatic with `auto_delete_logs_after_days`
3. **Backup Configuration**: Manual backup or enable auto-backup
4. **Check API Limits**: Monitor usage for rate-limited services

### Version Updates
1. Backup current configuration
2. Update source files
3. Run compatibility check
4. Update configuration if needed
5. Test core functionality

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes with proper logging
4. Add tests for new functionality
5. Update documentation
6. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check this README and troubleshooting section
2. Review log files for error details
3. Test with minimal configuration
4. Check GitHub issues and discussions
5. Create detailed bug report with logs

## 🔮 Future Features

Planned enhancements:
- [ ] Multi-language support
- [ ] Voice training and customization  
- [ ] Smart home integration
- [ ] Calendar and task management
- [ ] Plugin system for extensions
- [ ] Mobile app companion
- [ ] Web dashboard interface
- [ ] Advanced AI conversations
- [ ] Gesture and visual recognition
- [ ] Cloud synchronization

---

**Enjoy your AI Voice Assistant!** 🎉

For the best experience, take time to configure the settings according to your preferences and system setup. The assistant learns from your usage patterns and becomes more helpful over time. -->






# Free AI Voice Assistant - Quick Start Guide

## 🎯 **Zero Cost, Maximum Privacy**

This voice assistant uses **only free and open-source services** - no paid API keys required! All features work without any subscription fees.

---

## 🚀 **Quick Installation**

### 1. Install Dependencies
```bash
pip install -r free_requirements.txt
```

### 2. System Setup (Linux/macOS only)
```bash
# Ubuntu/Debian
sudo apt install python3-pyaudio portaudio19-dev espeak

# macOS  
brew install portaudio espeak
```

### 3. Run the Assistant
```bash
python main.py
```

That's it! No API keys needed to get started.

---

## 🎤 **Voice Commands**

### **Basic Interaction**
- "Hey Jarvis, hello"
- "What time is it?"
- "What's today's date?"

### **Open Applications**
- "Open Chrome"
- "Start Calculator" 
- "Launch Terminal"
- "Close Firefox"

### **Web & Search**
- "Go to YouTube"
- "Search for Python tutorials"
- "Open Gmail"
- "Find restaurants near me"

### **System Information**
- "Check battery status"
- "Show system stats"  
- "Network status"
- "CPU usage"

### **Weather (Completely Free)**
- "What's the weather?"
- "Weather in London"
- "Temperature outside"

### **Questions (Wikipedia + Local Knowledge)**
- "What is Python?"
- "Who invented the computer?"
- "Tell me about artificial intelligence"
- "Define machine learning"

### **Math & Conversions (Built-in)**
- "Calculate 15 times 23"
- "What's 20% of 150?"
- "Convert 32 Fahrenheit to Celsius"
- "How many meters in 10 feet?"

### **Media Control**
- "Play music on YouTube"
- "Volume up"
- "Volume down" 
- "Set volume to 50"

### **Email (Free Gmail IMAP)**
- "Check my email"
- "Read my emails"

---

## 🔧 **Configuration**

### Gmail Setup (Optional)
1. Enable 2-Factor Authentication in Gmail
2. Generate App Password
3. Add to `~/.jarvis_assistant/config.json`:

```json
"gmail": {
  "email": "your-email@gmail.com",
  "app_password": "your-app-password"
}
```

### Add Your Applications
Edit `config.json` to add your favorite apps:

```json
"applications": {
  "my_app": {
    "windows": "C:\\Path\\To\\App.exe",
    "linux": "/usr/bin/myapp",
    "darwin": "/Applications/MyApp.app"
  }
}
```

### Customize Wake Words
```json
"user_preferences": {
  "wake_words": ["jarvis", "computer", "assistant"]
}
```

---

## 🆓 **Free Services Used**

| Feature | Service | Cost |
|---------|---------|------|
| Speech Recognition | Google Speech API | Free |
| Text-to-Speech | pyttsx3 + gTTS | Free |
| Weather | wttr.in | Free |
| Search | DuckDuckGo | Free |
| Knowledge | Wikipedia | Free |
| System Info | psutil | Free |
| Email | Gmail IMAP | Free |
| Maps/Web | Google/YouTube | Free |

---

## 🔒 **Privacy Benefits**

- ✅ **No tracking** - Uses privacy-focused DuckDuckGo for search
- ✅ **Local processing** - Most operations happen on your device  
- ✅ **No data mining** - No paid AI services collecting your data
- ✅ **Open source** - All code is auditable
- ✅ **Minimal external calls** - Only necessary web requests

---

## ⚡ **Performance Tips**

### Speed Optimization
- **Local knowledge base** caches common questions
- **System voices** work offline (pyttsx3)
- **Local calculations** for math operations
- **Cached responses** for frequently used commands

### Reduce Internet Dependency
- Most features work offline
- Only weather, search, and online questions need internet
- Speech recognition can work offline on some systems

---

## 🛠️ **Troubleshooting**

### Speech Recognition Issues
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Check permissions (Linux)
sudo usermod -a -G audio $USER
```

### TTS Not Working
```bash
# Test system TTS
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('test'); engine.runAndWait()"

# Install TTS dependencies (Linux)
sudo apt install espeak espeak-data
```

### Weather Service Down
- The assistant automatically falls back from wttr.in to Google weather scraping
- Both services are completely free

---

## 📈 **Upgrade Options (Optional)**

If you want enhanced AI features later, you can optionally add:

### OpenAI GPT (Paid)
- Better conversation abilities
- More nuanced responses
- Cost: ~$0.01-0.03 per conversation

### Wolfram Alpha (Paid)
- Advanced mathematical calculations
- Scientific queries
- Cost: $5/month

### Azure Speech (Paid)  
- Premium voice quality
- More voice options
- Cost: $1 per 1M characters

**But remember: The free version already provides 90% of the functionality!**

---

## 🎯 **What Makes This Special**

### Compared to Paid Assistants:
- **Siri/Alexa**: Limited customization, privacy concerns
- **Google Assistant**: Data collection, cloud dependency  
- **This Assistant**: Full control, privacy-first, completely customizable

### Compared to Paid AI APIs:
- **ChatGPT API**: $20-50/month for heavy usage
- **Azure/AWS**: $10-100/month depending on usage
- **This Assistant**: $0/month, forever

---

## 🤝 **Contributing**

Since this is free and open-source:
- Report bugs and suggest features
- Add to the local knowledge base
- Contribute new free service integrations
- Help improve privacy and performance

---

## 📋 **Command Summary**

**Basic Commands:**
```
"Hello" - Greeting
"What time is it?" - Current time
"Open [app]" - Launch application
"Go to [website]" - Open website
"Search for [query]" - Web search
"What's the weather?" - Weather info
"Check battery" - System status
"What is [topic]?" - Knowledge query
"Calculate [math]" - Mathematics
"Play [song]" - YouTube search
"Check email" - Gmail IMAP
"Volume [up/down/50]" - Audio control
```

**Advanced Commands:**
```
"Convert 32 F to C" - Unit conversion
"System stats" - CPU/memory info
"Network status" - Connection info
"Weather in Tokyo" - Location weather
"Define artificial intelligence" - Definitions
"Calculate 15% of 200" - Percentage math
```

---

**Enjoy your completely free, privacy-focused AI voice assistant!** 

No subscriptions, no tracking, no limits - just helpful AI assistance powered by open-source technology.

---

*Last Updated: 2024 - Always free, always open-source*