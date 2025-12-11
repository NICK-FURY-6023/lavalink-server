#!/usr/bin/env python3
"""
🎧 PREMIUM LAVALINK MONITOR BOT - AUTO DEVOPS
==============================================
By: NICK-FURY-6023

Features:
- Auto IP detection (works on Pterodactyl)
- Auto channel & webhook creation
- IP tracking & blocking detection
- Real-time alerts
- Premium dashboard
"""

import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import json
import os
import socket
import platform
import psutil
import time
import configparser
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 30))

# ============================================================================
# AUTO IP DETECTION - Works on Pterodactyl!
# ============================================================================
class IPManager:
    def __init__(self):
        self.current_ip = None
        self.ip_history = []
        self.blocked_ips = []
        self.ip_rotation_count = 0
        self.last_rotation = None
        self.youtube_status = "Checking..."
        self.rate_limit_count = 0
        
    def get_public_ip(self) -> str:
        """Auto-detect public IP"""
        try:
            import urllib.request
            services = ['https://api.ipify.org', 'https://ifconfig.me/ip', 'https://icanhazip.com']
            for service in services:
                try:
                    with urllib.request.urlopen(service, timeout=5) as r:
                        ip = r.read().decode('utf-8').strip()
                        if ip: return ip
                except: continue
            # Fallback
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"
    
    def get_hostname(self) -> str:
        try: return socket.gethostname()
        except: return "Unknown"
    
    def get_pterodactyl_info(self) -> dict:
        """Detect Pterodactyl environment"""
        info = {
            'is_pterodactyl': False,
            'server_id': None,
            'node': None,
            'ip': self.get_public_ip(),
            'port': '2333'
        }
        
        if os.getenv('P_SERVER_UUID'):
            info['is_pterodactyl'] = True
            info['server_id'] = os.getenv('P_SERVER_UUID')
            info['node'] = os.getenv('P_SERVER_NODE', 'Unknown')
            info['ip'] = os.getenv('SERVER_IP', info['ip'])
            info['port'] = os.getenv('SERVER_PORT', '2333')
        
        return info
    
    def track_ip_change(self, new_ip: str):
        if self.current_ip and self.current_ip != new_ip:
            self.ip_history.append({'ip': self.current_ip, 'changed_at': datetime.now().isoformat()})
            self.ip_rotation_count += 1
            self.last_rotation = datetime.now()
        self.current_ip = new_ip

ip_manager = IPManager()

# ============================================================================
# LAVALINK MANAGER
# ============================================================================
class LavalinkManager:
    def __init__(self):
        self.nodes = []
        self.peak_players = 0
        
    def load_nodes(self, config_file='lavalink.ini'):
        """Load or auto-create lavalink config"""
        nodes = []
        
        if not os.path.exists(config_file):
            ptero = ip_manager.get_pterodactyl_info()
            with open(config_file, 'w') as f:
                f.write(f"""# Auto-generated Lavalink Config
[node-main]
host = {ptero['ip']}
port = {ptero['port']}
password = SatzzDev
secure = false
region = Auto
""")
            print(f"✅ Auto-created {config_file}")
        
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            for section in config.sections():
                if section.startswith('node-'):
                    c = dict(config[section])
                    node = {
                        'name': section.replace('node-', '').title(),
                        'host': c.get('host', 'localhost'),
                        'port': int(c.get('port', 2333)),
                        'password': c.get('password', 'youshallnotpass'),
                        'secure': c.get('secure', 'false').lower() == 'true',
                        'region': c.get('region', 'Unknown')
                    }
                    protocol = 'https' if node['secure'] else 'http'
                    node['url'] = f"{protocol}://{node['host']}:{node['port']}"
                    nodes.append(node)
                    print(f"✅ Loaded: {node['name']} ({node['url']})")
        except Exception as e:
            print(f"❌ Config error: {e}")
        
        self.nodes = nodes
        return nodes
    
    async def fetch_stats(self, session, node) -> dict:
        """Fetch node stats"""
        try:
            headers = {'Authorization': node['password']}
            start = time.time()
            
            async with session.get(f"{node['url']}/v4/stats", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as r:
                ping = (time.time() - start) * 1000
                if r.status == 200:
                    data = await r.json()
                    if data.get('players', 0) > self.peak_players:
                        self.peak_players = data['players']
                    return {'name': node['name'], 'region': node['region'], 'url': node['url'], 
                            'online': True, 'ping': round(ping, 1), 'stats': data, 'ip': node['host']}
                return {'name': node['name'], 'region': node['region'], 'online': False, 'error': f"HTTP {r.status}", 'ip': node['host']}
        except asyncio.TimeoutError:
            return {'name': node['name'], 'region': node['region'], 'online': False, 'error': 'Timeout', 'ip': node['host']}
        except Exception as e:
            return {'name': node['name'], 'region': node['region'], 'online': False, 'error': str(e)[:30], 'ip': node['host']}
    
    async def fetch_all(self) -> list:
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[self.fetch_stats(session, n) for n in self.nodes])
    
    async def check_youtube(self):
        """Check YouTube access"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.youtube.com', timeout=aiohttp.ClientTimeout(total=5)) as r:
                    if r.status == 200: ip_manager.youtube_status = "✅ Working"
                    elif r.status == 429: ip_manager.youtube_status = "⚠️ Rate Limited"; ip_manager.rate_limit_count += 1
                    elif r.status == 403: ip_manager.youtube_status = "🚫 Blocked"
                    else: ip_manager.youtube_status = f"❓ {r.status}"
        except Exception as e:
            ip_manager.youtube_status = f"❌ Error"

lavalink = LavalinkManager()

# ============================================================================
# HELPERS
# ============================================================================
def get_health_emoji(value: float, metric: str) -> str:
    thresholds = {'cpu': (50, 80), 'ram': (60, 85), 'ping': (100, 200)}
    t = thresholds.get(metric, (50, 80))
    if value < t[0]: return '🟢'
    elif value < t[1]: return '🟠'
    else: return '🔴'

def format_uptime(seconds: float) -> str:
    if seconds < 60: return f"{int(seconds)}s"
    elif seconds < 3600: return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    elif seconds < 86400: return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
    else: return f"{int(seconds // 86400)}d {int((seconds % 86400) // 3600)}h"

def format_bytes(b: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024: return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"

def get_system_stats() -> dict:
    try:
        import cpuinfo
        cpu_name = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown')[:40]
    except:
        cpu_name = platform.processor()[:40] or 'Unknown'
    
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu_info': cpu_name,
        'cpu_percent': psutil.cpu_percent(interval=0.5),
        'memory_percent': mem.percent,
        'memory_used_gb': (mem.total - mem.available) / (1024**3),
        'memory_total_gb': mem.total / (1024**3),
        'disk_percent': disk.percent,
        'disk_used_gb': disk.used / (1024**3),
        'disk_total_gb': disk.total / (1024**3),
        'os_info': f"{platform.system()} {platform.machine()}"
    }

# ============================================================================
# EMBED CREATOR
# ============================================================================
def create_embed(lavalink_data: list, system_data: dict) -> discord.Embed:
    online = [n for n in lavalink_data if n.get('online')]
    total_players = sum(n['stats'].get('players', 0) for n in online) if online else 0
    total_playing = sum(n['stats'].get('playingPlayers', 0) for n in online) if online else 0
    
    color = 0x00ff00 if len(online) == len(lavalink_data) else (0xff8800 if online else 0xff0000)
    
    embed = discord.Embed(
        title="👑 Premium Lavalink Monitor",
        description="```ansi\n\u001b[1;36m⚡ Real-Time Auto-DevOps Dashboard\u001b[0m```",
        color=color,
        timestamp=datetime.now()
    )
    
    # Server Info
    ptero = ip_manager.get_pterodactyl_info()
    server_info = f"""🌐 **IP:** `{ptero['ip']}`
🔌 **Port:** `{ptero['port']}`
🖥️ **Host:** `{ip_manager.get_hostname()}`"""
    if ptero['is_pterodactyl']:
        server_info += f"\n🦎 **Pterodactyl:** `{ptero['node']}`"
    embed.add_field(name="📡 Server Info", value=server_info, inline=False)
    
    # IP Tracking
    ip_info = f"""🔄 **Rotations:** `{ip_manager.ip_rotation_count}`
⚠️ **Rate Limits:** `{ip_manager.rate_limit_count}`
🚫 **Blocked:** `{len(ip_manager.blocked_ips)}`
📺 **YouTube:** {ip_manager.youtube_status}"""
    if ip_manager.last_rotation:
        ago = (datetime.now() - ip_manager.last_rotation).total_seconds()
        ip_info += f"\n⏱️ **Last Rotation:** `{format_uptime(ago)} ago`"
    embed.add_field(name="🔒 IP Tracking", value=ip_info, inline=True)
    
    # Quick Stats
    embed.add_field(name="📊 Quick Stats", value=f"""🎵 **Players:** `{total_players}`
🎶 **Playing:** `{total_playing}`
🏆 **Peak:** `{lavalink.peak_players}`
✅ **Nodes:** `{len(online)}/{len(lavalink_data)}`""", inline=True)
    
    # Nodes
    for node in lavalink_data:
        if node.get('online'):
            s = node['stats']
            cpu = s.get('cpu', {}).get('systemLoad', 0) * 100
            if cpu == 0: cpu = s.get('cpu', {}).get('lavalinkLoad', 0) * 100
            mem = s.get('memory', {})
            ram_pct = (mem.get('used', 0) / mem.get('allocated', 1)) * 100 if mem.get('allocated', 0) > 0 else 0
            
            val = f"""{get_health_emoji(cpu, 'cpu')} **CPU:** `{cpu:.1f}%`
{get_health_emoji(ram_pct, 'ram')} **RAM:** `{format_bytes(mem.get('used', 0))}` / `{format_bytes(mem.get('allocated', 0))}`
{get_health_emoji(node.get('ping', 999), 'ping')} **Ping:** `{node.get('ping', 'N/A')}ms`
🎵 **Players:** `{s.get('players', 0)}` | 🎶 `{s.get('playingPlayers', 0)}`
⏰ **Uptime:** `{format_uptime(s.get('uptime', 0) / 1000)}`"""
        else:
            val = f"🔴 **Offline**\n❌ `{node.get('error', 'Unknown')}`"
        
        icon = "🟢" if node.get('online') else "🔴"
        embed.add_field(name=f"{icon} {node.get('name', 'Unknown')} Node", value=val, inline=True)
    
    # System
    if system_data:
        embed.add_field(name="🖥️ Host System", value=f"""💻 **CPU:** `{system_data['cpu_info']}`
{get_health_emoji(system_data['cpu_percent'], 'cpu')} **Usage:** `{system_data['cpu_percent']:.1f}%`
{get_health_emoji(system_data['memory_percent'], 'ram')} **RAM:** `{system_data['memory_percent']:.1f}%` ({system_data['memory_used_gb']:.1f}GB)
💾 **Disk:** `{system_data['disk_percent']:.1f}%` ({system_data['disk_used_gb']:.1f}GB)
🖥️ **OS:** `{system_data['os_info']}`""", inline=False)
    
    embed.set_footer(text=f"🤖 Bot Uptime: {format_uptime((datetime.now() - bot.start_time).total_seconds())} • Updates every {UPDATE_INTERVAL}s")
    return embed

# ============================================================================
# DISCORD BOT
# ============================================================================
class PremiumBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.monitor_channel_id = None
        self.alerts_channel_id = None
        self.webhook_url = None
        self.start_time = datetime.now()
        
    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Commands synced!")

bot = PremiumBot()

# ============================================================================
# SLASH COMMANDS
# ============================================================================
@bot.tree.command(name="setup", description="🔧 Auto-setup monitoring channels")
@app_commands.describe(category_name="Category name for channels")
async def setup_cmd(interaction: discord.Interaction, category_name: str = "🎧 Lavalink Monitor"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Need Admin permission!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    
    try:
        # Create category & channels
        category = await guild.create_category(category_name)
        monitor = await category.create_text_channel("📊-live-status", topic="Real-time Lavalink dashboard")
        alerts = await category.create_text_channel("🚨-alerts", topic="Rate limit & IP alerts")
        logs = await category.create_text_channel("📝-logs", topic="Detailed logs")
        
        # Create webhook
        webhook = await alerts.create_webhook(name="Lavalink Alerts")
        
        # Save config
        bot.monitor_channel_id = monitor.id
        bot.alerts_channel_id = alerts.id
        bot.webhook_url = webhook.url
        
        config = {
            'guild_id': guild.id,
            'monitor_channel_id': monitor.id,
            'alerts_channel_id': alerts.id,
            'webhook_url': webhook.url,
            'setup_at': datetime.now().isoformat()
        }
        with open('monitor_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        embed = discord.Embed(
            title="✅ Setup Complete!",
            description=f"""**Created:**
📊 {monitor.mention} - Live dashboard
🚨 {alerts.mention} - Alerts
📝 {logs.mention} - Logs

**Auto-Detected:**
🌐 IP: `{ip_manager.get_public_ip()}`
🖥️ Host: `{ip_manager.get_hostname()}`

Monitoring started! ✨""",
            color=0x00ff00
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        if not monitor_loop.is_running():
            monitor_loop.start()
        await update_monitor()
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="status", description="📊 Show current status")
async def status_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    data = await lavalink.fetch_all()
    sys = get_system_stats()
    await interaction.followup.send(embed=create_embed(data, sys))

@bot.tree.command(name="ip", description="🌐 Show IP information")
async def ip_cmd(interaction: discord.Interaction):
    ptero = ip_manager.get_pterodactyl_info()
    embed = discord.Embed(title="🌐 IP & Network Info", color=0x00aaff, timestamp=datetime.now())
    embed.add_field(name="📡 Server", value=f"""🌐 **IP:** `{ptero['ip']}`
🔌 **Port:** `{ptero['port']}`
🖥️ **Host:** `{ip_manager.get_hostname()}`
🦎 **Pterodactyl:** `{'Yes' if ptero['is_pterodactyl'] else 'No'}`""", inline=False)
    embed.add_field(name="📊 Stats", value=f"""🔄 **Rotations:** `{ip_manager.ip_rotation_count}`
⚠️ **Rate Limits:** `{ip_manager.rate_limit_count}`
🚫 **Blocked:** `{len(ip_manager.blocked_ips)}`
📺 **YouTube:** {ip_manager.youtube_status}""", inline=True)
    
    if ip_manager.ip_history:
        history = "\n".join([f"• `{h['ip']}`" for h in ip_manager.ip_history[-5:]])
        embed.add_field(name="📜 IP History", value=history, inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="nodes", description="🎧 List all nodes")
async def nodes_cmd(interaction: discord.Interaction):
    if not lavalink.nodes:
        await interaction.response.send_message("❌ No nodes!", ephemeral=True)
        return
    
    embed = discord.Embed(title="🎧 Lavalink Nodes", color=0x00ff00)
    for n in lavalink.nodes:
        embed.add_field(name=f"📍 {n['name']}", value=f"""🌐 `{n['url']}`
🌍 {n['region']}
🔒 {'HTTPS' if n['secure'] else 'HTTP'}""", inline=True)
    await interaction.response.send_message(embed=embed)

# ============================================================================
# MONITORING
# ============================================================================
async def update_monitor():
    if not bot.monitor_channel_id:
        return
    
    try:
        channel = bot.get_channel(bot.monitor_channel_id)
        if not channel: return
        
        data = await lavalink.fetch_all()
        sys = get_system_stats()
        await lavalink.check_youtube()
        ip_manager.track_ip_change(ip_manager.get_public_ip())
        
        embed = create_embed(data, sys)
        
        try:
            if os.path.exists('message_id.txt'):
                with open('message_id.txt', 'r') as f:
                    msg_id = int(f.read().strip())
                msg = await channel.fetch_message(msg_id)
                await msg.edit(embed=embed)
            else:
                raise FileNotFoundError
        except:
            msg = await channel.send(embed=embed)
            with open('message_id.txt', 'w') as f:
                f.write(str(msg.id))
        
        # Send alerts
        await send_alerts(data)
        
    except Exception as e:
        print(f"❌ Update error: {e}")

async def send_alerts(data: list):
    if not bot.webhook_url: return
    
    alerts = []
    for n in data:
        if not n.get('online'):
            alerts.append(f"🔴 **{n['name']}** offline: {n.get('error', 'Unknown')}")
        elif n.get('ping', 0) > 200:
            alerts.append(f"🟠 **{n['name']}** high ping: {n['ping']}ms")
    
    if ip_manager.rate_limit_count > 0 and ip_manager.rate_limit_count % 3 == 0:
        alerts.append(f"⚠️ Rate limit count: {ip_manager.rate_limit_count}")
    
    if alerts:
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(bot.webhook_url, json={
                    "embeds": [{"title": "🚨 Alert", "description": "\n".join(alerts), "color": 0xff0000}]
                })
        except: pass

@tasks.loop(seconds=UPDATE_INTERVAL)
async def monitor_loop():
    await update_monitor()

@monitor_loop.before_loop
async def before_monitor():
    await bot.wait_until_ready()

# ============================================================================
# EVENTS
# ============================================================================
@bot.event
async def on_ready():
    print(f"""
╔════════════════════════════════════════════════════════╗
║     👑 PREMIUM LAVALINK MONITOR - AUTO DEVOPS          ║
╠════════════════════════════════════════════════════════╣
║  Bot: {bot.user.name:<48} ║
║  ID: {bot.user.id:<49} ║
║  Servers: {len(bot.guilds):<44} ║
╠════════════════════════════════════════════════════════╣
║  🌐 IP: {ip_manager.get_public_ip():<47} ║
║  🖥️  Host: {ip_manager.get_hostname():<44} ║
╠════════════════════════════════════════════════════════╣
║  Commands: /setup /status /ip /nodes                   ║
╚════════════════════════════════════════════════════════╝
""")
    
    # Load config
    if os.path.exists('monitor_config.json'):
        try:
            with open('monitor_config.json', 'r') as f:
                c = json.load(f)
            bot.monitor_channel_id = c.get('monitor_channel_id')
            bot.alerts_channel_id = c.get('alerts_channel_id')
            bot.webhook_url = c.get('webhook_url')
            print(f"✅ Config loaded - Channel: {bot.monitor_channel_id}")
            if not monitor_loop.is_running():
                monitor_loop.start()
        except Exception as e:
            print(f"⚠️ Config error: {e}")
    else:
        print("ℹ️ Use /setup to configure!")
    
    lavalink.load_nodes()

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Set BOT_TOKEN in .env!")
        exit(1)
    
    print("🚀 Starting Premium Monitor Bot...")
    bot.run(BOT_TOKEN)
