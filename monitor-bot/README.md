# 🎧 Lavalink Monitor Bot

A powerful & real-time Discord bot that monitors Lavalink nodes and system health, auto-updates a single embed in your Discord channel every 10 seconds — built for reliability and professional-grade observability 🔥

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.x-lightblue)
![Status](https://img.shields.io/badge/Live%20Monitor-Auto--Update%20Every%2010s-green)

---

## 🧩 Purpose

Monitor Lavalink & host system health, and post a single **live-refreshing embed** to a specific Discord channel every **10 seconds**, with real-time indicators, emojis, and node-region display.

---

## 🔧 Features

| Category          | Feature Description                             |
|-------------------|--------------------------------------------------|
| 🔁 Real-Time       | Auto-refresh every 10 seconds                    |
| 📊 Lavalink Stats  | Players, Playing, CPU%, RAM%, Ping              |
| 🧠 Host System     | CPU, RAM, Disk, OS, Architecture                |
| 🌍 Region Display  | Node region (🇩🇪 Germany, 🇮🇳 India, etc.)       |
| 🟢 Emoji Indicators| Status: 🟢 Good / 🟠 Moderate / 🔴 Critical       |
| 🔁 Message Update  | Edits the same message — no spam!               |
| 📂 Multi-Node      | Supports multiple Lavalink nodes                |
| 📝 Lavalink.ini    | Auto-parses Lavalink info from `.ini` config    |
| 🗃️ Persistent Msg  | Saves message ID in file for persistent updates |

---

## 🚀 Quick Start

### 1. Download & Setup
```bash
git clone https://github.com/NICK-FURY-6023/lavalink-monitor-bot.git
cd lavalink-monitor-bot
python setup.py
```

### 2. Configure
Edit `.env` file:
```env
BOT_TOKEN=your_discord_bot_token_here
CHANNEL_ID=1234567890123456789
```

Edit `lavalink.ini` file:
```ini
[node-india]
host = lavalink.india.com
port = 2333
password = supersecret
secure = false
region = India
```

### 3. Run
```bash
python bot.py
```

---

## 🧱 Project Structure

```
lavalink-monitor-bot/
├── bot.py                 # Main bot runner & embed loop
├── config.py              # Bot token, channel ID, thresholds
├── lavalink_parser.py     # Parses lavalink.ini → node list
├── monitor.py             # Fetch Lavalink & system stats
├── utils.py               # Emoji/health logic & utilities
├── setup.py               # Easy setup script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .env.example           # Environment template
├── lavalink.ini           # Lavalink server(s) config
├── message_id.txt         # Stores last embed message ID
└── README.md              # This file
```

---

## ⚙️ Configuration Files

### `.env` - Bot Settings
```env
BOT_TOKEN=your_discord_bot_token_here
CHANNEL_ID=1234567890123456789
UPDATE_INTERVAL=10
TIMEOUT=5
```

### `lavalink.ini` - Lavalink Nodes
```ini
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
```

**Configuration Options:**
- `host`: Lavalink server hostname
- `port`: Lavalink server port
- `password`: Lavalink server password
- `secure`: Use HTTPS (true) or HTTP (false)
- `region`: Display name with auto-emoji detection

---

## 📊 Health Thresholds

| Metric        | Good 🟢 | Moderate 🟠 | Critical 🔴 |
|---------------|---------|-------------|-------------|
| CPU Usage     | < 50%   | 50-80%      | > 80%       |
| RAM Usage     | < 50%   | 50-80%      | > 80%       |
| Disk Usage    | < 50%   | 50-80%      | > 80%       |
| Ping Time     | < 100ms | 100-200ms   | > 200ms     |
| Player Count  | < 5     | 5-15        | > 15        |

*Thresholds can be customized in `config.py`*

---

## 🌍 Supported Regions

The bot automatically adds flag emojis for these regions:

| Region | Emoji | Region | Emoji |
|--------|-------|--------|-------|
| Germany | 🇩🇪 | India | 🇮🇳 |
| USA | 🇺🇸 | UK | 🇬🇧 |
| Singapore | 🇸🇬 | Canada | 🇨🇦 |
| Australia | 🇦🇺 | Japan | 🇯🇵 |
| France | 🇫🇷 | Brazil | 🇧🇷 |
| Russia | 🇷🇺 | South Korea | 🇰🇷 |
| Netherlands | 🇳🇱 | Sweden | 🇸🇪 |
| Norway | 🇳🇴 | Finland | 🇫🇮 |

*More regions can be added in `config.py`*

---

## 🔧 Bot Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `!restart` | Restart monitor (creates new embed) | Administrator |

---

## 🖼️ Example Embed Output

```
🎧 Lavalink Monitor Dashboard

🎧 India Node
🟢 CPU: 23.4%
🟢 RAM: 12.1%
🟠 Ping: 187ms
🟢 Players: 3 / 12
🌍 Region: 🇮🇳 India
⏰ Uptime: 2d 4h

🎧 Germany Node
🟢 CPU: 45.2%
🟢 RAM: 38.7%
🟢 Ping: 89ms
🟠 Players: 8 / 15
🌍 Region: 🇩🇪 Germany
⏰ Uptime: 1d 12h

🖥️ Host System
CPU: Intel Core i7-9700K (8C/8T) @ 3.6GHz
🟢 CPU Usage: 12.3%
🟢 RAM: 34.2%
🟢 Disk: 105GB / 230GB
OS: Linux x86_64
⌚ Bot Uptime: 4h 23m

Updates every 10 seconds • Lavalink Monitor Bot
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Discord bot token
- Lavalink server(s) running

### Step 1: Clone Repository
```bash
git clone https://github.com/NICK-FURY-6023/lavalink-monitor-bot.git
cd lavalink-monitor-bot
```

### Step 2: Run Setup Script
```bash
python setup.py
```

### Step 3: Configure Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Copy the bot token
5. Edit `.env` file and paste your token

### Step 4: Configure Channel ID
1. Enable Developer Mode in Discord
2. Right-click on your target channel
3. Copy Channel ID
4. Edit `.env` file and paste the channel ID

### Step 5: Configure Lavalink Nodes
Edit `lavalink.ini` with your actual Lavalink server details:
```ini
[node-myserver]
host = your.lavalink.server.com
port = 2333
password = your_password
secure = false
region = Your Region
```

### Step 6: Run the Bot
```bash
python bot.py
```

---

## 🔧 Advanced Configuration

### Custom Health Thresholds
Edit `config.py` to customize thresholds:
```python
HEALTH_THRESHOLDS = {
    'cpu': {'good': 60, 'moderate': 85},
    'ram': {'good': 70, 'moderate': 90},
    'ping': {'good': 50, 'moderate': 150}
}
```

### Custom Update Interval
Change update frequency in `.env`:
```env
UPDATE_INTERVAL=15  # Update every 15 seconds
```

### Adding New Regions
Add new regions in `config.py`:
```python
REGION_EMOJIS = {
    'your_region': '🏴',
    'another_region': '🚩'
}
```

---

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't start:**
- Check bot token in `.env`
- Ensure bot has proper permissions
- Verify Python version (3.8+)

**Lavalink nodes show offline:**
- Check `lavalink.ini` configuration
- Verify Lavalink server is running
- Check firewall/network settings
- Ensure correct password

**Embed doesn't update:**
- Check channel permissions
- Verify channel ID is correct
- Check bot has "Send Messages" permission

**Permission errors:**
- Ensure bot has "Send Messages" permission
- Check channel permissions
- Verify bot role hierarchy

### Debug Mode
Run with debug output:
```bash
python bot.py --debug
```

---

## 📋 Requirements

### Python Packages
```
discord.py>=2.3.0
aiohttp>=3.8.0
psutil>=5.9.0
py-cpuinfo>=9.0.0
python-dotenv>=1.0.0
```

### System Requirements
- Python 3.8+
- 50MB+ RAM
- Network access to Lavalink servers
- Discord bot permissions

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
git clone https://github.com/NICK-FURY-6023/lavalink-monitor-bot.git
cd lavalink-monitor-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Lavalink](https://github.com/freyacodes/Lavalink) - Audio server
- [psutil](https://github.com/giampaolo/psutil) - System information

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/NICK-FURY-6023/lavalink-monitor-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NICK-FURY-6023/lavalink-monitor-bot/discussions)
- **Discord**: [Support Server](https://discord.gg/UKXMITT68)

---

*Made with ❤️ for the Discord music bot community*
