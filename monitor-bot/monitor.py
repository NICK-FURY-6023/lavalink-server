import aiohttp
import asyncio
import time
import psutil
import platform
import cpuinfo
from config import TIMEOUT

async def get_lavalink_stats(nodes):
    """
    Fetch stats from all Lavalink nodes
    
    Args:
        nodes: List of node configurations
        
    Returns:
        list: List of node stats
    """
    results = []
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as session:
        tasks = []
        
        for node in nodes:
            task = asyncio.create_task(fetch_node_stats(session, node))
            tasks.append(task)
        
        # Wait for all tasks to complete
        node_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(node_results):
            if isinstance(result, Exception):
                # Node failed to respond
                results.append({
                    'name': nodes[i]['name'],
                    'region': nodes[i]['region'],
                    'url': nodes[i]['url'],
                    'online': False,
                    'error': str(result)
                })
            else:
                results.append(result)
    
    return results

async def fetch_node_stats(session, node):
    """
    Fetch stats from a single Lavalink node
    
    Args:
        session: aiohttp session
        node: Node configuration
        
    Returns:
        dict: Node stats or error info
    """
    try:
        # Prepare headers
        headers = {
            'Authorization': node['password'],
            'Content-Type': 'application/json'
        }
        
        # Measure ping time
        start_time = time.time()
        
        # Fetch stats from Lavalink v4 API
        stats_url = f"{node['url']}/v4/stats"
        
        async with session.get(stats_url, headers=headers) as response:
            ping_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status == 200:
                stats_data = await response.json()
                
                return {
                    'name': node['name'],
                    'region': node['region'],
                    'url': node['url'],
                    'online': True,
                    'ping': round(ping_time, 1),
                    'stats': stats_data
                }
            else:
                return {
                    'name': node['name'],
                    'region': node['region'],
                    'url': node['url'],
                    'online': False,
                    'error': f"HTTP {response.status}"
                }
                
    except asyncio.TimeoutError:
        return {
            'name': node['name'],
            'region': node['region'],
            'url': node['url'],
            'online': False,
            'error': "Timeout"
        }
    except Exception as e:
        return {
            'name': node['name'],
            'region': node['region'],
            'url': node['url'],
            'online': False,
            'error': str(e)
        }

def get_system_stats():
    """
    Get system statistics for the host machine
    
    Returns:
        dict: System statistics
    """
    try:
        # CPU Information
        cpu_info_obj = cpuinfo.get_cpu_info()
        cpu_name = cpu_info_obj.get('brand_raw', 'Unknown CPU')
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        # Format CPU info
        cpu_info_str = f"{cpu_name}"
        if cpu_cores:
            cpu_info_str += f" ({cpu_cores}C/{cpu_threads}T)"
        if cpu_freq:
            cpu_info_str += f" @ {cpu_freq.current/1000:.1f}GHz"
        
        # Memory Information
        memory = psutil.virtual_memory()
        
        # Disk Information
        disk = psutil.disk_usage('/')
        
        # System Information
        system_info = platform.system()
        architecture = platform.machine()
        os_info = f"{system_info} {architecture}"
        
        # Network Information (optional)
        try:
            network_stats = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network_stats.bytes_sent,
                'bytes_recv': network_stats.bytes_recv
            }
        except:
            network_info = None
        
        return {
            'cpu_info': cpu_info_str,
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_cores': cpu_cores,
            'cpu_threads': cpu_threads,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent,
            'memory_used_gb': (memory.total - memory.available) / (1024**3),
            'memory_total_gb': memory.total / (1024**3),
            'disk_total': disk.total,
            'disk_used': disk.used,
            'disk_free': disk.free,
            'disk_percent': disk.percent,
            'disk_used_gb': disk.used / (1024**3),
            'disk_total_gb': disk.total / (1024**3),
            'os_info': os_info,
            'network': network_info
        }
        
    except Exception as e:
        print(f"❌ Error getting system stats: {e}")
        return None

def get_process_stats():
    """
    Get statistics for the current Python process
    
    Returns:
        dict: Process statistics
    """
    try:
        process = psutil.Process()
        
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_mb': process.memory_info().rss / (1024**2),
            'threads': process.num_threads(),
            'connections': len(process.connections()),
            'pid': process.pid
        }
        
    except Exception as e:
        print(f"❌ Error getting process stats: {e}")
        return None

if __name__ == "__main__":
    # Test system stats
    stats = get_system_stats()
    if stats:
        print("System Statistics:")
        print(f"  CPU: {stats['cpu_info']}")
        print(f"  CPU Usage: {stats['cpu_percent']:.1f}%")
        print(f"  Memory: {stats['memory_percent']:.1f}%")
        print(f"  Disk: {stats['disk_percent']:.1f}%")
        print(f"  OS: {stats['os_info']}")
    
    # Test process stats
    proc_stats = get_process_stats()
    if proc_stats:
        print("\nProcess Statistics:")
        print(f"  PID: {proc_stats['pid']}")
        print(f"  CPU: {proc_stats['cpu_percent']:.1f}%")
        print(f"  Memory: {proc_stats['memory_mb']:.1f}MB")
        print(f"  Threads: {proc_stats['threads']}")
