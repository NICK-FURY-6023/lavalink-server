import asyncio
import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
from config import BOT_TOKEN, CHANNEL_ID
from lavalink_parser import parse_lavalink_config
from monitor import get_lavalink_stats, get_system_stats
from utils import get_health_emoji, format_uptime

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables
message_id_file = "message_id.txt"
lavalink_nodes = []
start_time = datetime.now()

def load_message_id():
    """Load the last message ID from file"""
    try:
        with open(message_id_file, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None

def save_message_id(message_id):
    """Save message ID to file"""
    with open(message_id_file, 'w') as f:
        f.write(str(message_id))

def create_embed(lavalink_data, system_data):
    """Create the monitoring embed"""
    embed = discord.Embed(
        title="🎧 Lavalink Monitor Dashboard",
        color=0x00ff00,
        timestamp=datetime.now()
    )
    
    # Add Lavalink nodes
    for i, node_data in enumerate(lavalink_data):
        node_name = node_data.get('name', f'Node {i+1}')
        region = node_data.get('region', '🌍 Unknown')
        
        if node_data.get('online', False):
            stats = node_data['stats']
            cpu_emoji = get_health_emoji(stats['cpu'] * 100, 'cpu')
            ram_emoji = get_health_emoji(stats['memory']['used'] / stats['memory']['allocated'] * 100, 'ram')
            ping_emoji = get_health_emoji(node_data.get('ping', 999), 'ping')
            players_emoji = get_health_emoji(stats['players'], 'players')
            
            node_value = f"""
{cpu_emoji} **CPU:** {stats['cpu'] * 100:.1f}%
{ram_emoji} **RAM:** {stats['memory']['used'] / stats['memory']['allocated'] * 100:.1f}%
{ping_emoji} **Ping:** {node_data.get('ping', 'N/A')}ms
{players_emoji} **Players:** {stats['players']} / {stats['playingPlayers']}
🌍 **Region:** {region}
⏰ **Uptime:** {format_uptime(stats.get('uptime', 0))}
"""
        else:
            node_value = f"""
🔴 **Status:** Offline
🌍 **Region:** {region}
❌ **Connection:** Failed
"""
        
        embed.add_field(
            name=f"🎧 {node_name}",
            value=node_value,
            inline=True
        )
    
    # Add system stats
    if system_data:
        cpu_emoji = get_health_emoji(system_data['cpu_percent'], 'cpu')
        ram_emoji = get_health_emoji(system_data['memory_percent'], 'ram')
        disk_emoji = get_health_emoji(system_data['disk_percent'], 'disk')
        
        system_value = f"""
**CPU:** {system_data['cpu_info']}
{cpu_emoji} **CPU Usage:** {system_data['cpu_percent']:.1f}%
{ram_emoji} **RAM:** {system_data['memory_percent']:.1f}%
{disk_emoji} **Disk:** {system_data['disk_used_gb']:.1f}GB / {system_data['disk_total_gb']:.1f}GB
**OS:** {system_data['os_info']}
⌚ **Bot Uptime:** {format_uptime((datetime.now() - start_time).total_seconds())}
"""
        
        embed.add_field(
            name="🖥️ Host System",
            value=system_value,
            inline=True
        )
    
    embed.set_footer(text="Updates every 10 seconds • Lavalink Monitor Bot")
    return embed

@bot.event
async def on_ready():
    print(f'🎧 Lavalink Monitor Bot logged in as {bot.user}')
    print(f'📊 Monitoring {len(lavalink_nodes)} Lavalink nodes')
    
    # Start the monitoring loop
    monitor_loop.start()

@tasks.loop(seconds=10)
async def monitor_loop():
    """Main monitoring loop that updates the embed every 10 seconds"""
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"❌ Channel {CHANNEL_ID} not found!")
            return
        
        # Fetch data
        lavalink_data = await get_lavalink_stats(lavalink_nodes)
        system_data = get_system_stats()
        
        # Create embed
        embed = create_embed(lavalink_data, system_data)
        
        # Try to edit existing message or send new one
        message_id = load_message_id()
        
        if message_id:
            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
                print(f"✅ Updated embed at {datetime.now().strftime('%H:%M:%S')}")
            except discord.NotFound:
                # Message was deleted, send new one
                new_message = await channel.send(embed=embed)
                save_message_id(new_message.id)
                print(f"🆕 Sent new embed (old message not found)")
            except discord.HTTPException as e:
                print(f"❌ Failed to edit message: {e}")
        else:
            # No existing message, send new one
            new_message = await channel.send(embed=embed)
            save_message_id(new_message.id)
            print(f"🆕 Sent initial embed")
            
    except Exception as e:
        print(f"❌ Error in monitor loop: {e}")

@monitor_loop.before_loop
async def before_monitor_loop():
    """Wait for bot to be ready before starting the loop"""
    await bot.wait_until_ready()

@bot.command(name='restart')
async def restart_monitor(ctx):
    """Restart the monitoring embed (creates new message)"""
    if ctx.author.guild_permissions.administrator:
        # Delete the old message ID file
        if os.path.exists(message_id_file):
            os.remove(message_id_file)
        
        await ctx.send("🔄 Monitor restarted! New embed will be created.")
    else:
        await ctx.send("❌ You need administrator permissions to restart the monitor.")

if __name__ == "__main__":
    # Load Lavalink nodes from config
    lavalink_nodes = parse_lavalink_config()
    
    if not lavalink_nodes:
        print("❌ No Lavalink nodes found in lavalink.ini!")
        exit(1)
    
    print(f"🚀 Starting Lavalink Monitor Bot...")
    print(f"📊 Loaded {len(lavalink_nodes)} Lavalink nodes")
    
    # Start the bot
    bot.run(BOT_TOKEN)
