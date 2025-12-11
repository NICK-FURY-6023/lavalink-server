#!/usr/bin/env python3
"""
Lavalink Monitor Bot Setup Script
Run this script to set up the bot for first-time use
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🎧 LAVALINK MONITOR BOT SETUP")
    print("=" * 60)
    print()

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_config_files():
    """Create configuration files"""
    print("\n🔧 Creating configuration files...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from template")
        else:
            with open('.env', 'w') as f:
                f.write("BOT_TOKEN=your_discord_bot_token_here\n")
                f.write("CHANNEL_ID=1234567890123456789\n")
            print("✅ Created basic .env file")
    else:
        print("ℹ️  .env file already exists")
    
    # Create lavalink.ini if it doesn't exist
    if not os.path.exists('lavalink.ini'):
        from lavalink_parser import create_sample_config
        create_sample_config()
        print("✅ Created sample lavalink.ini file")
    else:
        print("ℹ️  lavalink.ini file already exists")
    
    # Create empty message_id.txt
    if not os.path.exists('message_id.txt'):
        with open('message_id.txt', 'w') as f:
            f.write("")
        print("✅ Created message_id.txt file")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def validate_setup():
    """Validate the setup"""
    print("\n🔍 Validating setup...")
    
    required_files = [
        'bot.py',
        'config.py',
        'lavalink_parser.py',
        'monitor.py',
        'utils.py',
        'requirements.txt',
        '.env',
        'lavalink.ini'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def print_next_steps():
    """Print what to do next"""
    print("\n" + "=" * 60)
    print("🚀 SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🔑 Edit .env file:")
    print("   - Add your Discord bot token")
    print("   - Add your Discord channel ID")
    print()
    print("2. 🎵 Edit lavalink.ini file:")
    print("   - Configure your Lavalink nodes")
    print("   - Set correct host, port, password, and region")
    print()
    print("3. 🤖 Create a Discord bot:")
    print("   - Go to https://discord.com/developers/applications")
    print("   - Create a new application and bot")
    print("   - Copy the bot token to .env file")
    print("   - Invite bot to your server with 'Send Messages' permission")
    print()
    print("4. ▶️  Run the bot:")
    print("   python bot.py")
    print()
    print("💡 For help, check the README or run: python bot.py --help")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create config files
    create_config_files()
    
    # Validate setup
    if not validate_setup():
        print("\n❌ Setup validation failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
