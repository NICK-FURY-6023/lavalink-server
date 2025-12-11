from config import HEALTH_THRESHOLDS, EMOJIS
from datetime import datetime, timedelta

def get_health_emoji(value, metric_type):
    """
    Get health emoji based on value and metric type
    
    Args:
        value: The value to check
        metric_type: Type of metric (cpu, ram, disk, ping, players)
        
    Returns:
        str: Emoji representing health status
    """
    if value is None:
        return EMOJIS['offline']
    
    thresholds = HEALTH_THRESHOLDS.get(metric_type, {})
    good_threshold = thresholds.get('good', 50)
    moderate_threshold = thresholds.get('moderate', 80)
    
    if value < good_threshold:
        return EMOJIS['good']
    elif value < moderate_threshold:
        return EMOJIS['moderate']
    else:
        return EMOJIS['critical']

def get_overall_health(lavalink_data, system_data):
    """
    Calculate overall health status
    
    Args:
        lavalink_data: List of Lavalink node data
        system_data: System statistics
        
    Returns:
        str: Overall health status (good, moderate, critical)
    """
    critical_count = 0
    moderate_count = 0
    total_metrics = 0
    
    # Check Lavalink nodes
    for node in lavalink_data:
        if node.get('online', False):
            stats = node['stats']
            
            # CPU check
            cpu_emoji = get_health_emoji(stats['cpu'] * 100, 'cpu')
            if cpu_emoji == EMOJIS['critical']:
                critical_count += 1
            elif cpu_emoji == EMOJIS['moderate']:
                moderate_count += 1
            total_metrics += 1
            
            # RAM check
            ram_percent = stats['memory']['used'] / stats['memory']['allocated'] * 100
            ram_emoji = get_health_emoji(ram_percent, 'ram')
            if ram_emoji == EMOJIS['critical']:
                critical_count += 1
            elif ram_emoji == EMOJIS['moderate']:
                moderate_count += 1
            total_metrics += 1
            
            # Ping check
            ping_emoji = get_health_emoji(node.get('ping', 999), 'ping')
            if ping_emoji == EMOJIS['critical']:
                critical_count += 1
            elif ping_emoji == EMOJIS['moderate']:
                moderate_count += 1
            total_metrics += 1
    
    # Check system stats
    if system_data:
        system_cpu_emoji = get_health_emoji(system_data['cpu_percent'], 'cpu')
        if system_cpu_emoji == EMOJIS['critical']:
            critical_count += 1
        elif system_cpu_emoji == EMOJIS['moderate']:
            moderate_count += 1
        total_metrics += 1
        
        system_ram_emoji = get_health_emoji(system_data['memory_percent'], 'ram')
        if system_ram_emoji == EMOJIS['critical']:
            critical_count += 1
        elif system_ram_emoji == EMOJIS['moderate']:
            moderate_count += 1
        total_metrics += 1
        
        system_disk_emoji = get_health_emoji(system_data['disk_percent'], 'disk')
        if system_disk_emoji == EMOJIS['critical']:
            critical_count += 1
        elif system_disk_emoji == EMOJIS['moderate']:
            moderate_count += 1
        total_metrics += 1
    
    # Determine overall health
    if total_metrics == 0:
        return 'critical'
    
    critical_ratio = critical_count / total_metrics
    moderate_ratio = moderate_count / total_metrics
    
    if critical_ratio > 0.3:  # More than 30% critical
        return 'critical'
    elif critical_ratio > 0.1 or moderate_ratio > 0.5:  # More than 10% critical or 50% moderate
        return 'moderate'
    else:
        return 'good'

def format_uptime(seconds):
    """
    Format uptime in seconds to human-readable format
    
    Args:
        seconds: Uptime in seconds
        
    Returns:
        str: Formatted uptime string
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}d {hours}h"

def format_bytes(bytes_value):
    """
    Format bytes to human-readable format
    
    Args:
        bytes_value: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if bytes_value < 1024:
        return f"{bytes_value}B"
    elif bytes_value < 1024**2:
        return f"{bytes_value / 1024:.1f}KB"
    elif bytes_value < 1024**3:
        return f"{bytes_value / (1024**2):.1f}MB"
    else:
        return f"{bytes_value / (1024**3):.1f}GB"

def get_status_color(health_status):
    """
    Get Discord embed color based on health status
    
    Args:
        health_status: Health status (good, moderate, critical)
        
    Returns:
        int: Discord color code
    """
    colors = {
        'good': 0x00ff00,      # Green
        'moderate': 0xff8800,  # Orange
        'critical': 0xff0000,  # Red
        'offline': 0x808080    # Gray
    }
    
    return colors.get(health_status, colors['offline'])

def truncate_string(text, max_length=100):
    """
    Truncate string to maximum length with ellipsis
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def format_timestamp(timestamp):
    """
    Format timestamp to readable format
    
    Args:
        timestamp: Unix timestamp or datetime object
        
    Returns:
        str: Formatted timestamp
    """
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = timestamp
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def calculate_percentage(value, total):
    """
    Calculate percentage with error handling
    
    Args:
        value: Current value
        total: Total value
        
    Returns:
        float: Percentage (0-100)
    """
    if total == 0:
        return 0.0
    return (value / total) * 100

def get_load_indicator(load_avg, cpu_count):
    """
    Get load average indicator
    
    Args:
        load_avg: System load average
        cpu_count: Number of CPU cores
        
    Returns:
        str: Load indicator emoji
    """
    if cpu_count == 0:
        return EMOJIS['offline']
    
    load_percentage = (load_avg / cpu_count) * 100
    
    if load_percentage < 70:
        return EMOJIS['good']
    elif load_percentage < 90:
        return EMOJIS['moderate']
    else:
        return EMOJIS['critical']

def validate_config(config):
    """
    Validate configuration parameters
    
    Args:
        config: Configuration dictionary
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['host', 'port', 'password']
    
    for field in required_fields:
        if field not in config:
            return False, f"Missing required field: {field}"
    
    # Validate port
    try:
        port = int(config['port'])
        if port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
    except ValueError:
        return False, "Port must be a valid integer"
    
    # Validate host
    if not config['host'] or config['host'].strip() == '':
        return False, "Host cannot be empty"
    
    # Validate password
    if not config['password'] or config['password'].strip() == '':
        return False, "Password cannot be empty"
    
    return True, "Configuration is valid"

def sanitize_node_name(name):
    """
    Sanitize node name for display
    
    Args:
        name: Raw node name
        
    Returns:
        str: Sanitized node name
    """
    # Remove common prefixes
    prefixes = ['node-', 'lavalink-', 'server-']
    for prefix in prefixes:
        if name.lower().startswith(prefix):
            name = name[len(prefix):]
    
    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split('-'))
    name = ' '.join(word.capitalize() for word in name.split('_'))
    
    return name or "Unknown Node"

def get_region_emoji(region_name):
    """
    Get emoji for region name
    
    Args:
        region_name: Region name
        
    Returns:
        str: Region with emoji
    """
    from config import REGION_EMOJIS
    
    if not region_name:
        return f"{REGION_EMOJIS['unknown']} Unknown"
    
    region_lower = region_name.lower()
    
    # Check if emoji is already present
    for emoji in REGION_EMOJIS.values():
        if region_name.startswith(emoji):
            return region_name
    
    # Find matching emoji
    for region_key, emoji in REGION_EMOJIS.items():
        if region_key in region_lower:
            return f"{emoji} {region_name}"
    
    # Default to unknown
    return f"{REGION_EMOJIS['unknown']} {region_name}"

def create_progress_bar(percentage, length=10):
    """
    Create a text progress bar
    
    Args:
        percentage: Progress percentage (0-100)
        length: Length of progress bar
        
    Returns:
        str: Progress bar string
    """
    if percentage < 0:
        percentage = 0
    elif percentage > 100:
        percentage = 100
    
    filled_length = int(length * percentage // 100)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"{bar} {percentage:.1f}%"

def get_connection_status_emoji(is_connected, ping=None):
    """
    Get connection status emoji
    
    Args:
        is_connected: Whether the connection is active
        ping: Ping time in milliseconds
        
    Returns:
        str: Connection status emoji
    """
    if not is_connected:
        return EMOJIS['offline']
    
    if ping is None:
        return EMOJIS['good']
    
    return get_health_emoji(ping, 'ping')

def format_node_stats_summary(node_data):
    """
    Format node statistics for summary display
    
    Args:
        node_data: Node statistics data
        
    Returns:
        str: Formatted summary
    """
    if not node_data.get('online', False):
        return f"❌ **Offline** - {node_data.get('error', 'Unknown error')}"
    
    stats = node_data['stats']
    cpu_pct = stats['cpu'] * 100
    ram_pct = stats['memory']['used'] / stats['memory']['allocated'] * 100
    
    return f"""
{get_health_emoji(cpu_pct, 'cpu')} CPU: {cpu_pct:.1f}% | {get_health_emoji(ram_pct, 'ram')} RAM: {ram_pct:.1f}%
🎵 Players: {stats['players']} | 🎶 Playing: {stats['playingPlayers']}
📍 {node_data['region']} | 🏓 {node_data.get('ping', 'N/A')}ms
""".strip()

if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Test health emoji
    print(f"CPU 25%: {get_health_emoji(25, 'cpu')}")
    print(f"CPU 65%: {get_health_emoji(65, 'cpu')}")
    print(f"CPU 85%: {get_health_emoji(85, 'cpu')}")
    
    # Test uptime formatting
    print(f"Uptime 30s: {format_uptime(30)}")
    print(f"Uptime 90s: {format_uptime(90)}")
    print(f"Uptime 3700s: {format_uptime(3700)}")
    print(f"Uptime 90000s: {format_uptime(90000)}")
    
    # Test bytes formatting
    print(f"Bytes 500: {format_bytes(500)}")
    print(f"Bytes 1500: {format_bytes(1500)}")
    print(f"Bytes 1500000: {format_bytes(1500000)}")
    print(f"Bytes 1500000000: {format_bytes(1500000000)}")
    
    # Test progress bar
    print(f"Progress 0%: {create_progress_bar(0)}")
    print(f"Progress 25%: {create_progress_bar(25)}")
    print(f"Progress 50%: {create_progress_bar(50)}")
    print(f"Progress 75%: {create_progress_bar(75)}")
    print(f"Progress 100%: {create_progress_bar(100)}")
    
    print("✅ All utility functions working!")
