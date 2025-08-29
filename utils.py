"""
Utility functions and logging configuration for AI Voice Assistant
"""

import os
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
import hashlib
import re
import unicodedata
from typing import List, Dict, Any, Optional

def setup_logging(log_level='INFO', max_file_size='10MB', backup_count=5):
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    # Create logs directory
    log_dir = Path.home() / '.jarvis_assistant' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert max_file_size to bytes
    size_multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    size_match = re.match(r'(\d+)(KB|MB|GB)', max_file_size.upper())
    if size_match:
        size_value, size_unit = size_match.groups()
        max_bytes = int(size_value) * size_multipliers[size_unit]
    else:
        max_bytes = 10 * 1024 * 1024  # Default 10MB
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'jarvis_assistant.log',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Error file handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'jarvis_errors.log',
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(error_handler)
    
    # Log the setup
    logging.info(f"Logging configured - Level: {log_level}, Log dir: {log_dir}")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Normalize unicode characters
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Trim whitespace and dots
    filename = filename.strip('. ')
    
    # Ensure it's not empty
    if not filename:
        filename = 'untitled'
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL format
    """
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def get_file_hash(filepath: str) -> str:
    """
    Get SHA256 hash of file
    
    Args:
        filepath: Path to file
        
    Returns:
        SHA256 hash as hex string
    """
    hash_sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Failed to hash file {filepath}: {e}")
        return ""


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: int) -> str:
    """
    Format duration in human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2h 30m 45s")
    """
    if seconds < 0:
        return "0s"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    # Common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Clean and tokenize
    text = clean_text(text.lower())
    words = re.findall(r'\b[a-z]+\b', text)
    
    # Filter keywords
    keywords = [
        word for word in words
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Remove duplicates while preserving order
    unique_keywords = []
    seen = set()
    for keyword in keywords:
        if keyword not in seen:
            unique_keywords.append(keyword)
            seen.add(keyword)
    
    return unique_keywords


def fuzzy_match(query: str, candidates: List[str], threshold: float = 0.6) -> List[tuple]:
    """
    Perform fuzzy matching on candidate strings
    
    Args:
        query: Query string
        candidates: List of candidate strings
        threshold: Minimum similarity threshold (0-1)
        
    Returns:
        List of (candidate, similarity_score) tuples, sorted by score
    """
    from difflib import SequenceMatcher
    
    matches = []
    query_lower = query.lower()
    
    for candidate in candidates:
        candidate_lower = candidate.lower()
        similarity = SequenceMatcher(None, query_lower, candidate_lower).ratio()
        
        if similarity >= threshold:
            matches.append((candidate, similarity))
    
    # Sort by similarity score (descending)
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def parse_time_expression(expression: str) -> Optional[int]:
    """
    Parse time expressions into seconds
    
    Args:
        expression: Time expression (e.g., "5 minutes", "1 hour", "30s")
        
    Returns:
        Time in seconds, or None if parsing failed
    """
    expression = expression.lower().strip()
    
    # Time unit mappings
    time_units = {
        's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
        'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
        'h': 3600, 'hr': 3600, 'hour': 3600, 'hours': 3600,
        'd': 86400, 'day': 86400, 'days': 86400
    }
    
    # Try to match patterns like "5 minutes", "30s", "1 hour"
    pattern = r'(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hr|hour|hours|d|day|days)(?:\s|$)'
    matches = re.findall(pattern, expression)
    
    if matches:
        total_seconds = 0
        for value, unit in matches:
            total_seconds += int(value) * time_units.get(unit, 0)
        return total_seconds
    
    # Try to match just numbers (assume seconds)
    number_match = re.match(r'^(\d+)$', expression)
    if number_match:
        return int(number_match.group(1))
    
    return None


def create_backup(source_path: str, backup_dir: str = None) -> Optional[str]:
    """
    Create backup of file or directory
    
    Args:
        source_path: Path to source file/directory
        backup_dir: Directory to store backup (optional)
        
    Returns:
        Path to backup file, or None if backup failed
    """
    import shutil
    
    source = Path(source_path)
    if not source.exists():
        logging.error(f"Source path does not exist: {source_path}")
        return None
    
    # Default backup directory
    if backup_dir is None:
        backup_dir = source.parent / 'backups'
    
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{source.stem}_{timestamp}{source.suffix}"
    backup_path = backup_dir / backup_name
    
    try:
        if source.is_file():
            shutil.copy2(source, backup_path)
        elif source.is_dir():
            shutil.copytree(source, backup_path)
        
        logging.info(f"Backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        logging.error(f"Backup failed: {e}")
        return None


def load_json_safely(filepath: str, default: Any = None) -> Any:
    """
    Safely load JSON file with error handling
    
    Args:
        filepath: Path to JSON file
        default: Default value if loading fails
        
    Returns:
        Loaded JSON data or default value
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.debug(f"JSON file not found: {filepath}")
        return default
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {filepath}: {e}")
        return default
    except Exception as e:
        logging.error(f"Failed to load JSON {filepath}: {e}")
        return default


def save_json_safely(data: Any, filepath: str, backup: bool = True) -> bool:
    """
    Safely save data to JSON file with backup
    
    Args:
        data: Data to save
        filepath: Target file path
        backup: Whether to create backup of existing file
        
    Returns:
        True if save successful
    """
    filepath = Path(filepath)
    
    try:
        # Create backup if requested and file exists
        if backup and filepath.exists():
            create_backup(str(filepath))
        
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to save JSON to {filepath}: {e}")
        return False


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information
    
    Returns:
        Dictionary with system information
    """
    import platform
    import psutil
    
    try:
        # Basic system info
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
        }
        
        # Memory info
        memory = psutil.virtual_memory()
        info['memory'] = {
            'total': format_file_size(memory.total),
            'available': format_file_size(memory.available),
            'used': format_file_size(memory.used),
            'percentage': memory.percent
        }
        
        # Disk info
        disk = psutil.disk_usage('/')
        info['disk'] = {
            'total': format_file_size(disk.total),
            'used': format_file_size(disk.used),
            'free': format_file_size(disk.free),
            'percentage': (disk.used / disk.total) * 100
        }
        
        # CPU info
        info['cpu'] = {
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'frequency': f"{psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "Unknown"
        }
        
        return info
        
    except Exception as e:
        logging.error(f"Failed to get system info: {e}")
        return {'error': str(e)}


def check_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies are available
    
    Returns:
        Dictionary with dependency availability status
    """
    dependencies = {
        'speech_recognition': False,
        'pyttsx3': False,
        'requests': False,
        'beautifulsoup4': False,
        'pygame': False,
        'psutil': False,
        'fuzzywuzzy': False,
        'openai': False,
        'wolframalpha': False,
        'wikipedia': False,
        'gtts': False,
        'pydub': False,
        'webrtcvad': False
    }
    
    for package in dependencies:
        try:
            __import__(package.replace('-', '_'))
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies


class PerformanceTimer:
    """Context manager for measuring execution time"""
    
    def __init__(self, name: str = "Operation", log_result: bool = True):
        self.name = name
        self.log_result = log_result
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        if self.log_result:
            logging.debug(f"{self.name} completed in {duration.total_seconds():.3f} seconds")
    
    @property
    def duration(self) -> float:
        """Get duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


def rate_limiter(max_calls: int, time_window: int = 60):
    """
    Decorator for rate limiting function calls
    
    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
    """
    from functools import wraps
    from collections import deque
    
    def decorator(func):
        call_times = deque(maxlen=max_calls)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            
            # Remove calls outside the time window
            while call_times and (now - call_times[0]).seconds > time_window:
                call_times.popleft()
            
            # Check if limit exceeded
            if len(call_times) >= max_calls:
                sleep_time = time_window - (now - call_times[0]).seconds
                logging.warning(f"Rate limit exceeded for {func.__name__}, sleeping for {sleep_time}s")
                import time
                time.sleep(sleep_time)
            
            # Record this call
            call_times.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator