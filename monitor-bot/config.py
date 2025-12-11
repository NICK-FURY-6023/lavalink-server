import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token_here')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '1234567890123456789'))  # Replace with your channel ID

# Lavalink Configuration
LAVALINK_CONFIG_FILE = 'lavalink.ini'

# Health Thresholds
HEALTH_THRESHOLDS = {
    'cpu': {
        'good': 50,      # < 50% = good
        'moderate': 80   # 50-80% = moderate, >80% = critical
    },
    'ram': {
        'good': 50,
        'moderate': 80
    },
    'disk': {
        'good': 50,
        'moderate': 80
    },
    'ping': {
        'good': 100,     # < 100ms = good
        'moderate': 200  # 100-200ms = moderate, >200ms = critical
    },
    'players': {
        'good': 5,       # < 5 = good
        'moderate': 15   # 5-15 = moderate, >15 = critical
    }
}

# Monitoring Settings
UPDATE_INTERVAL = 10  # seconds
TIMEOUT = 5  # seconds for HTTP requests

# Emoji Configuration
EMOJIS = {
    'good': '🟢',
    'moderate': '🟠',
    'critical': '🔴',
    'offline': '⚫'
}

# Regional Emojis (add more as needed)
REGION_EMOJIS = {
    'germany': '🇩🇪',
    'india': '🇮🇳',
    'usa': '🇺🇸',
    'uk': '🇬🇧',
    'singapore': '🇸🇬',
    'canada': '🇨🇦',
    'australia': '🇦🇺',
    'japan': '🇯🇵',
    'france': '🇫🇷',
    'brazil': '🇧🇷',
    'russia': '🇷🇺',
    'south_korea': '🇰🇷',
    'netherlands': '🇳🇱',
    'sweden': '🇸🇪',
    'norway': '🇳🇴',
    'finland': '🇫🇮',
    'unknown': '🌍'
}
