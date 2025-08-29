"""
Conversation Manager for maintaining context and session history
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import uuid

class ConversationManager:
    def __init__(self, max_history=100):
        self.logger = logging.getLogger(__name__)
        self.max_history = max_history
        
        # Conversation state
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now()
        self.conversation_history = deque(maxlen=max_history)
        self.context_memory = {}
        self.user_intent_history = deque(maxlen=20)
        
        # Active conversation tracking
        self.last_interaction = datetime.now()
        self.conversation_timeout = timedelta(minutes=10)
        self.is_in_conversation = False
        
        # Session storage
        self.sessions_dir = Path.home() / '.jarvis_assistant' / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Conversation Manager initialized - Session: {self.session_id[:8]}")

    def add_user_input(self, user_input, intent=None, entities=None):
        """Add user input to conversation history"""
        interaction = {
            'type': 'user_input',
            'content': user_input,
            'intent': intent,
            'entities': entities or {},
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        
        self.conversation_history.append(interaction)
        
        if intent:
            self.user_intent_history.append(intent)
        
        self.last_interaction = datetime.now()
        self.is_in_conversation = True
        
        self.logger.debug(f"Added user input: {user_input[:50]}...")

    def add_assistant_response(self, response, response_type='text', metadata=None):
        """Add assistant response to conversation history"""
        interaction = {
            'type': 'assistant_response',
            'content': response,
            'response_type': response_type,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        
        self.conversation_history.append(interaction)
        self.last_interaction = datetime.now()
        
        self.logger.debug(f"Added assistant response: {str(response)[:50]}...")

    def get_recent_context(self, num_interactions=5):
        """Get recent conversation context"""
        recent_history = list(self.conversation_history)[-num_interactions:]
        
        context = {
            'recent_interactions': recent_history,
            'last_user_intent': self.get_last_user_intent(),
            'session_duration': self.get_session_duration(),
            'interaction_count': len(self.conversation_history)
        }
        
        return context

    def get_last_user_intent(self):
        """Get the last identified user intent"""
        if self.user_intent_history:
            return self.user_intent_history[-1]
        return None

    def get_intent_pattern(self, lookback=10):
        """Analyze user intent patterns"""
        recent_intents = list(self.user_intent_history)[-lookback:]
        
        if not recent_intents:
            return {}
        
        # Count intent frequencies
        intent_counts = {}
        for intent in recent_intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Calculate patterns
        total_intents = len(recent_intents)
        intent_patterns = {
            intent: {
                'count': count,
                'frequency': count / total_intents,
                'recent': intent in recent_intents[-3:]  # In last 3 interactions
            }
            for intent, count in intent_counts.items()
        }
        
        return intent_patterns

    def is_in_active_conversation(self):
        """Check if user is in an active conversation"""
        time_since_last = datetime.now() - self.last_interaction
        
        # Consider conversation active if:
        # 1. Recent interaction (within timeout)
        # 2. OR conversation flag is set and within extended timeout
        if time_since_last < self.conversation_timeout:
            return True
        elif self.is_in_conversation and time_since_last < (self.conversation_timeout * 2):
            return True
        else:
            self.is_in_conversation = False
            return False

    def get_session_duration(self):
        """Get current session duration"""
        return datetime.now() - self.session_start

    def get_conversation_summary(self):
        """Generate a summary of the current conversation"""
        if not self.conversation_history:
            return "No conversation history"
        
        total_interactions = len(self.conversation_history)
        user_inputs = len([i for i in self.conversation_history if i['type'] == 'user_input'])
        assistant_responses = len([i for i in self.conversation_history if i['type'] == 'assistant_response'])
        
        # Most common intents
        intent_patterns = self.get_intent_pattern()
        top_intents = sorted(intent_patterns.items(), key=lambda x: x[1]['count'], reverse=True)[:3]
        
        summary = {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'session_duration': str(self.get_session_duration()),
            'total_interactions': total_interactions,
            'user_inputs': user_inputs,
            'assistant_responses': assistant_responses,
            'top_intents': [intent for intent, data in top_intents],
            'is_active': self.is_in_active_conversation()
        }
        
        return summary

    def find_similar_interactions(self, query, limit=5):
        """Find similar past interactions"""
        similar_interactions = []
        
        query_lower = query.lower()
        
        for interaction in self.conversation_history:
            if interaction['type'] == 'user_input':
                content = interaction['content'].lower()
                
                # Simple similarity check (can be enhanced with more sophisticated methods)
                common_words = set(query_lower.split()) & set(content.split())
                similarity_score = len(common_words) / max(len(query_lower.split()), 1)
                
                if similarity_score > 0.3:  # 30% word overlap threshold
                    similar_interactions.append({
                        'interaction': interaction,
                        'similarity': similarity_score
                    })
        
        # Sort by similarity and return top results
        similar_interactions.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_interactions[:limit]

    def set_context_memory(self, key, value, expiry_minutes=60):
        """Set context memory with optional expiry"""
        expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
        
        self.context_memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'expiry': expiry_time.isoformat()
        }
        
        self.logger.debug(f"Set context memory: {key}")

    def get_context_memory(self, key):
        """Get value from context memory if not expired"""
        if key not in self.context_memory:
            return None
        
        memory_item = self.context_memory[key]
        expiry_time = datetime.fromisoformat(memory_item['expiry'])
        
        if datetime.now() > expiry_time:
            # Memory expired, remove it
            del self.context_memory[key]
            return None
        
        return memory_item['value']

    def clear_expired_memory(self):
        """Clear expired context memory"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, memory_item in self.context_memory.items():
            expiry_time = datetime.fromisoformat(memory_item['expiry'])
            if current_time > expiry_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.context_memory[key]
        
        if expired_keys:
            self.logger.debug(f"Cleared {len(expired_keys)} expired memory items")

    def get_contextual_suggestions(self):
        """Get contextual suggestions based on conversation history"""
        suggestions = []
        
        # Clear expired memory first
        self.clear_expired_memory()
        
        # Analyze recent intent patterns
        intent_patterns = self.get_intent_pattern(lookback=5)
        
        # Suggest based on common patterns
        if 'application' in intent_patterns and intent_patterns['application']['frequency'] > 0.3:
            suggestions.append("Would you like me to open another application?")
        
        if 'question' in intent_patterns and intent_patterns['question']['frequency'] > 0.4:
            suggestions.append("I can help answer more questions or search for information.")
        
        if 'web' in intent_patterns:
            suggestions.append("I can open websites or search the web for you.")
        
        # Time-based suggestions
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 10 and not any('email' in str(i).lower() for i in self.conversation_history):
            suggestions.append("Would you like me to check your emails?")
        
        if 17 <= current_hour <= 19 and not any('weather' in str(i).lower() for i in self.conversation_history):
            suggestions.append("Want to check tomorrow's weather?")
        
        return suggestions[:3]  # Return top 3 suggestions

    def save_session(self):
        """Save current session to file"""
        try:
            session_data = {
                'session_id': self.session_id,
                'session_start': self.session_start.isoformat(),
                'session_end': datetime.now().isoformat(),
                'conversation_history': list(self.conversation_history),
                'context_memory': self.context_memory,
                'summary': self.get_conversation_summary()
            }
            
            session_file = self.sessions_dir / f"session_{self.session_id[:8]}.json"
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Session saved: {session_file}")
            return str(session_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return None

    def load_session(self, session_file):
        """Load session from file"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Restore session data
            self.session_id = session_data.get('session_id', str(uuid.uuid4()))
            self.session_start = datetime.fromisoformat(session_data.get('session_start', datetime.now().isoformat()))
            
            # Restore conversation history
            history = session_data.get('conversation_history', [])
            self.conversation_history = deque(history, maxlen=self.max_history)
            
            # Restore context memory (check for expiry)
            self.context_memory = session_data.get('context_memory', {})
            self.clear_expired_memory()
            
            # Rebuild intent history
            self.user_intent_history = deque(maxlen=20)
            for interaction in self.conversation_history:
                if interaction['type'] == 'user_input' and interaction.get('intent'):
                    self.user_intent_history.append(interaction['intent'])
            
            self.logger.info(f"Session loaded: {session_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load session: {e}")
            return False

    def get_recent_sessions(self, limit=10):
        """Get list of recent session files"""
        try:
            session_files = []
            for session_file in self.sessions_dir.glob("session_*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    session_info = {
                        'file': str(session_file),
                        'session_id': session_data.get('session_id'),
                        'start_time': session_data.get('session_start'),
                        'end_time': session_data.get('session_end'),
                        'interaction_count': len(session_data.get('conversation_history', []))
                    }
                    session_files.append(session_info)
                    
                except Exception as e:
                    self.logger.debug(f"Skipping invalid session file {session_file}: {e}")
            
            # Sort by start time (most recent first)
            session_files.sort(key=lambda x: x['start_time'], reverse=True)
            return session_files[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent sessions: {e}")
            return []

    def cleanup_old_sessions(self, days_to_keep=30):
        """Clean up session files older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            for session_file in self.sessions_dir.glob("session_*.json"):
                try:
                    # Check file modification time
                    file_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                    
                    if file_time < cutoff_date:
                        session_file.unlink()
                        removed_count += 1
                        
                except Exception as e:
                    self.logger.debug(f"Error cleaning up {session_file}: {e}")
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old session files")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old sessions: {e}")
            return 0

    def reset_conversation(self):
        """Reset current conversation but keep session"""
        self.conversation_history.clear()
        self.user_intent_history.clear()
        self.context_memory.clear()
        self.is_in_conversation = False
        self.last_interaction = datetime.now()
        
        self.logger.info("Conversation reset")

    def export_conversation(self, export_file):
        """Export current conversation to file"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'session_summary': self.get_conversation_summary(),
                'conversation_history': list(self.conversation_history),
                'context_memory': self.context_memory
            }
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Conversation exported to {export_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export conversation: {e}")
            return False