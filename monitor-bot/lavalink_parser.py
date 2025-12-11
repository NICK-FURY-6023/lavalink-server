import configparser
import os
from config import LAVALINK_CONFIG_FILE, REGION_EMOJIS

def parse_lavalink_config(config_file=LAVALINK_CONFIG_FILE):
    """
    Parse lavalink.ini file to extract node configurations
    
    Returns:
        list: List of dictionaries containing node configurations
    """
    nodes = []
    
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found!")
        return nodes
    
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        for section_name in config.sections():
            if section_name.startswith('node-') or section_name.startswith('lavalink-'):
                node_config = dict(config[section_name])
                
                # Extract node information
                node = {
                    'name': section_name.replace('node-', '').replace('lavalink-', '').title(),
                    'host': node_config.get('host', 'localhost'),
                    'port': int(node_config.get('port', 2333)),
                    'password': node_config.get('password', 'youshallnotpass'),
                    'secure': node_config.get('secure', 'false').lower() == 'true',
                    'region': node_config.get('region', '🌍 Unknown'),
                    'identifier': section_name
                }
                
                # Build the full URL
                protocol = 'https' if node['secure'] else 'http'
                node['url'] = f"{protocol}://{node['host']}:{node['port']}"
                
                # Process region emoji
                region_lower = node['region'].lower()
                for region_key, emoji in REGION_EMOJIS.items():
                    if region_key in region_lower:
                        if not node['region'].startswith(emoji):
                            node['region'] = f"{emoji} {node['region']}"
                        break
                
                nodes.append(node)
                print(f"✅ Loaded Lavalink node: {node['name']} ({node['url']})")
        
        if not nodes:
            print("⚠️  No Lavalink nodes found in config file!")
            
    except Exception as e:
        print(f"❌ Error parsing config file: {e}")
    
    return nodes

def create_sample_config(config_file=LAVALINK_CONFIG_FILE):
    """
    Create a sample lavalink.ini file
    """
    sample_config = """# Lavalink Monitor Bot Configuration
# Add your Lavalink nodes here

[node-india]
host = lavalink.india.com
port = 2333
password = supersecret
secure = false
region = India

[node-germany]
host = lavalink.germany.net
port = 2333
password = secretpass
secure = true
region = Germany

[node-usa]
host = lavalink.usa.com
port = 443
password = mypassword
secure = true
region = USA

# Add more nodes as needed
# [node-singapore]
# host = lavalink.singapore.com
# port = 2333
# password = password123
# secure = false
# region = Singapore
"""
    
    try:
        with open(config_file, 'w') as f:
            f.write(sample_config)
        print(f"✅ Sample config created: {config_file}")
        print("📝 Please edit the file with your actual Lavalink node details!")
    except Exception as e:
        print(f"❌ Error creating sample config: {e}")

if __name__ == "__main__":
    # Test the parser
    nodes = parse_lavalink_config()
    
    if not nodes:
        print("Creating sample config file...")
        create_sample_config()
    else:
        print(f"Found {len(nodes)} Lavalink nodes:")
        for node in nodes:
            print(f"  - {node['name']}: {node['url']} ({node['region']})")
