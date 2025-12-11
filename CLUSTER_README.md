# 🚀 Ultimate Production Lavalink Cluster

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Lavalink](https://img.shields.io/badge/Lavalink-v4-purple.svg)](https://github.com/lavalink-devs/Lavalink)

> **Enterprise-grade, anti-block, multi-region, multi-IP Lavalink streaming cluster for YouTube, Spotify, Apple Music, SoundCloud, and Deezer.**

This is a **production-ready Lavalink cluster** with the same architecture used by premium paid providers like lava.host, omnitone, and mengmade nodes.

---

## ✨ Features

### 🛡️ Anti-Block System (Zero 429)
- **Multi-IP Proxy Rotation** - Premium-grade IP pool with automatic rotation
- **YouTube OAuth2** - Device-code flow with automatic token refresh
- **TLS Fingerprint Spoofing** - Evade detection
- **User-Agent Randomization** - Rotate between real browser UAs
- **Circuit Breaker Logic** - Auto-cooldown on rate limits

### 🌍 Multi-Region Cluster
- **Singapore** - Asia Pacific primary
- **Germany** - Europe primary
- **US-East** - Americas primary
- **India** - Backup/Failover

### 🎵 Music Sources
- YouTube (with anti-block)
- Spotify (with LavaSrc)
- Apple Music
- Deezer
- SoundCloud
- Bandcamp
- Twitch
- And more...

### 📊 Monitoring & Observability
- Prometheus metrics
- Grafana dashboards
- Health check endpoints
- Discord/Slack alerts

### 🐳 Deployment Options
- Docker Compose
- Docker Swarm
- Pterodactyl Panel
- Kubernetes (coming soon)

---

## 📁 Project Structure

```
lavalink-server/
├── cluster/                    # Lavalink node configurations
│   ├── node1.yml              # Singapore node
│   ├── node2.yml              # Germany node
│   ├── node3.yml              # US-East node
│   └── node-backup.yml        # India backup node
├── proxy/                      # Proxy layer configurations
│   ├── haproxy.cfg            # HAProxy multi-IP rotation
│   ├── nginx.conf             # Nginx reverse proxy
│   └── ip-pool.yml            # Multi-IP exit node pool
├── scripts/                    # Helper scripts
│   ├── deploy.sh              # Deployment script
│   ├── oauth-generator.sh     # YouTube OAuth token generator
│   ├── ip-monitor.sh          # IP health monitor
│   ├── node-monitor.sh        # Node health monitor
│   ├── cipher-server.js       # YouTube cipher resolver
│   ├── Dockerfile.monitor     # Monitor container
│   └── Dockerfile.cipher      # Cipher server container
├── monitoring/                 # Monitoring configuration
│   ├── prometheus.yml         # Prometheus config
│   └── grafana/               # Grafana dashboards
├── pterodactyl/               # Pterodactyl Panel files
│   ├── egg-lavalink.json      # Pterodactyl egg
│   └── Dockerfile             # Pterodactyl Dockerfile
├── .github/workflows/          # CI/CD pipelines
│   └── deploy.yml             # GitHub Actions workflow
├── docker-compose.yml         # Docker Compose config
├── docker-compose.swarm.yml   # Docker Swarm config
├── .env.example               # Environment template
└── application.yml            # Legacy single-node config
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM per node
- Multiple exit IPs (for premium anti-block)

### 1. Clone the Repository
```bash
git clone https://github.com/SatzzDev/lavalink-server.git
cd lavalink-server
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```

Fill in your credentials:
- `LAVALINK_PASSWORD` - Secure password for Lavalink
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` - From [Spotify Developer](https://developer.spotify.com/dashboard)
- `YOUTUBE_REFRESH_TOKEN` - Generated via OAuth script
- Multi-IP addresses (SG_IP_1, DE_IP_1, US_IP_1, etc.)

### 3. Generate YouTube OAuth Token
```bash
chmod +x scripts/oauth-generator.sh
./scripts/oauth-generator.sh
```
Follow the on-screen instructions to authenticate with Google.

### 4. Deploy the Cluster
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh init
./scripts/deploy.sh start
```

### 5. Verify Deployment
```bash
./scripts/deploy.sh status
```

---

## 📝 Configuration Guide

### Node Configuration

Each node has its own configuration file in `cluster/`:

| File | Port | Region | Role |
|------|------|--------|------|
| `node1.yml` | 2333 | Singapore | Primary (Asia) |
| `node2.yml` | 2334 | Germany | Primary (Europe) |
| `node3.yml` | 2335 | US-East | Primary (Americas) |
| `node-backup.yml` | 2336 | India | Backup/Failover |

### Multi-IP Configuration

Edit `proxy/ip-pool.yml` to add your exit IPs:

```yaml
SINGAPORE_NODES:
  - ip: "103.xxx.xxx.1"
    port: 443
    region: "ap-southeast-1"
    weight: 100
    status: "active"
```

### HAProxy Configuration

The HAProxy config (`proxy/haproxy.cfg`) handles:
- Round-robin IP rotation
- Health checking
- 429 detection and IP cooldown
- Load balancing across nodes

---

## 🔧 Deployment Options

### Docker Compose (Single Server)
```bash
docker compose up -d
```

### Docker Swarm (Multi-Server Cluster)
```bash
# Initialize swarm
docker swarm init

# Label nodes by region
docker node update --label-add region=singapore node1
docker node update --label-add region=germany node2
docker node update --label-add region=us-east node3

# Create secrets
echo "your-password" | docker secret create lavalink-password -

# Deploy stack
docker stack deploy -c docker-compose.swarm.yml lavalink
```

### Pterodactyl Panel
1. Import `pterodactyl/egg-lavalink.json` as a new egg
2. Create a new server with the egg
3. Configure the variables in the panel

---

## 📊 Monitoring

### Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Node 1 | `http://localhost:2333` | Singapore Lavalink |
| Node 2 | `http://localhost:2334` | Germany Lavalink |
| Node 3 | `http://localhost:2335` | US-East Lavalink |
| Backup | `http://localhost:2336` | India Backup |
| HAProxy Stats | `http://localhost:8404/stats` | Proxy statistics |
| Prometheus | `http://localhost:9090` | Metrics |
| Grafana | `http://localhost:3000` | Dashboards |

### Health Checks
```bash
# Check all nodes
./scripts/node-monitor.sh --check

# Check IP pool health
./scripts/ip-monitor.sh --check
```

---

## 🔌 Connecting Your Bot

### Node.js (erela.js / lavalink-client)
```javascript
const nodes = [
  {
    identifier: "singapore",
    host: "your-server-ip",
    port: 2333,
    password: "your-password",
    secure: false
  },
  {
    identifier: "germany",
    host: "your-server-ip",
    port: 2334,
    password: "your-password",
    secure: false
  },
  {
    identifier: "us-east",
    host: "your-server-ip",
    port: 2335,
    password: "your-password",
    secure: false
  }
];
```

### Python (Lavalink.py)
```python
nodes = [
    {"host": "your-server-ip", "port": 2333, "password": "your-password", "identifier": "singapore"},
    {"host": "your-server-ip", "port": 2334, "password": "your-password", "identifier": "germany"},
    {"host": "your-server-ip", "port": 2335, "password": "your-password", "identifier": "us-east"},
]
```

---

## 🛠️ Troubleshooting

### 429 Errors (Rate Limited)
1. Ensure OAuth token is valid: `./scripts/oauth-generator.sh --validate`
2. Check IP pool health: `./scripts/ip-monitor.sh --check`
3. Add more exit IPs to the pool
4. Verify HAProxy is rotating IPs correctly

### Connection Issues
```bash
# Check container logs
docker compose logs lavalink-node1

# Verify node is responding
curl http://localhost:2333/version

# Check network connectivity
docker compose exec lavalink-node1 ping youtube.com
```

### Memory Issues
Adjust JVM settings in `docker-compose.yml`:
```yaml
environment:
  - _JAVA_OPTIONS=-Xmx8G -Xms4G
```

---

## 📈 Performance Tuning

### Recommended Resources

| Component | CPU | RAM | Storage |
|-----------|-----|-----|---------|
| Lavalink Node | 4 cores | 6GB | 10GB |
| HAProxy | 2 cores | 1GB | 1GB |
| Redis | 1 core | 512MB | 1GB |
| Prometheus | 1 core | 2GB | 20GB |

### JVM Tuning
```bash
-Xmx4G -Xms2G 
-XX:+UseG1GC 
-XX:+ParallelRefProcEnabled 
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
```

---

## 🔒 Security Best Practices

1. **Change default passwords** - Never use default credentials
2. **Use strong Lavalink password** - Minimum 16 characters
3. **Enable HTTPS** - Use SSL certificates in production
4. **Restrict network access** - Use firewall rules
5. **Monitor for anomalies** - Set up alerts in Grafana
6. **Rotate OAuth tokens** - Refresh tokens periodically
7. **Use dedicated IPs** - Don't share exit IPs with other services

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 💬 Support

- [Discord Server](https://discord.gg/nvcznzhkTF)
- [GitHub Issues](https://github.com/SatzzDev/lavalink-server/issues)

---

## ⭐ Star History

If this project helped you, please consider giving it a star!

---

Made with ❤️ for the Discord music bot community
