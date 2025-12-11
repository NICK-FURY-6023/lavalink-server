#!/bin/bash

# ==============================================================================
# Cluster Deployment Script
# Deploy and manage Lavalink cluster
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)    echo -e "${BLUE}[$timestamp][INFO]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[$timestamp][SUCCESS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[$timestamp][WARNING]${NC} $message" ;;
        ERROR)   echo -e "${RED}[$timestamp][ERROR]${NC} $message" ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    local missing=()
    
    command -v docker &> /dev/null || missing+=("docker")
    command -v docker-compose &> /dev/null || command -v "docker compose" &> /dev/null || missing+=("docker-compose")
    command -v curl &> /dev/null || missing+=("curl")
    command -v jq &> /dev/null || missing+=("jq")
    
    if [ ${#missing[@]} -gt 0 ]; then
        log "ERROR" "Missing dependencies: ${missing[*]}"
        exit 1
    fi
    
    log "SUCCESS" "All prerequisites met"
}

# Initialize environment
init_env() {
    log "INFO" "Initializing environment..."
    
    cd "$PROJECT_DIR"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log "WARNING" "Created .env from .env.example - Please configure it!"
        else
            log "ERROR" ".env file not found"
            exit 1
        fi
    fi
    
    # Create SSL directory
    mkdir -p ssl
    
    # Generate self-signed certificate if not exists
    if [ ! -f "ssl/cert.pem" ]; then
        log "INFO" "Generating self-signed SSL certificate..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/CN=lavalink.local" 2>/dev/null
        log "SUCCESS" "SSL certificate generated"
    fi
    
    log "SUCCESS" "Environment initialized"
}

# Build images
build() {
    log "INFO" "Building Docker images..."
    
    cd "$PROJECT_DIR"
    
    docker compose build --no-cache
    
    log "SUCCESS" "Images built successfully"
}

# Start cluster
start() {
    log "INFO" "Starting Lavalink cluster..."
    
    cd "$PROJECT_DIR"
    
    # Start in correct order
    docker compose up -d redis
    sleep 5
    
    docker compose up -d haproxy cipher-server
    sleep 5
    
    docker compose up -d lavalink-node1 lavalink-node2 lavalink-node3 lavalink-backup
    sleep 10
    
    docker compose up -d nginx ip-monitor prometheus grafana
    
    log "SUCCESS" "Cluster started successfully"
    
    # Show status
    status
}

# Stop cluster
stop() {
    log "INFO" "Stopping Lavalink cluster..."
    
    cd "$PROJECT_DIR"
    
    docker compose down
    
    log "SUCCESS" "Cluster stopped"
}

# Restart cluster
restart() {
    log "INFO" "Restarting Lavalink cluster..."
    stop
    sleep 5
    start
}

# Show status
status() {
    echo ""
    echo "=============================================="
    echo "       LAVALINK CLUSTER STATUS"
    echo "=============================================="
    
    cd "$PROJECT_DIR"
    
    docker compose ps
    
    echo ""
    echo "=============================================="
    echo "              ENDPOINTS"
    echo "=============================================="
    echo "  Lavalink Node 1 (SG): http://localhost:2333"
    echo "  Lavalink Node 2 (DE): http://localhost:2334"
    echo "  Lavalink Node 3 (US): http://localhost:2335"
    echo "  Lavalink Backup (IN): http://localhost:2336"
    echo ""
    echo "  HAProxy Stats:        http://localhost:8404/stats"
    echo "  Prometheus:           http://localhost:9090"
    echo "  Grafana:              http://localhost:3000"
    echo "=============================================="
    echo ""
}

# View logs
logs() {
    local service="${1:-}"
    
    cd "$PROJECT_DIR"
    
    if [ -n "$service" ]; then
        docker compose logs -f "$service"
    else
        docker compose logs -f
    fi
}

# Scale nodes
scale() {
    local node="$1"
    local count="${2:-1}"
    
    if [ -z "$node" ]; then
        echo "Usage: $0 scale <node-name> <count>"
        exit 1
    fi
    
    log "INFO" "Scaling $node to $count instances..."
    
    cd "$PROJECT_DIR"
    
    docker compose up -d --scale "$node=$count"
    
    log "SUCCESS" "Scaled $node to $count instances"
}

# Clean up
clean() {
    log "WARNING" "This will remove all containers, volumes, and images"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_DIR"
        
        docker compose down -v --rmi all
        
        log "SUCCESS" "Cleanup complete"
    else
        log "INFO" "Cleanup cancelled"
    fi
}

# Generate OAuth token
oauth() {
    log "INFO" "Starting YouTube OAuth token generator..."
    
    bash "$SCRIPT_DIR/oauth-generator.sh" "$@"
}

# Run health check
health() {
    log "INFO" "Running health checks..."
    
    bash "$SCRIPT_DIR/node-monitor.sh" --check
    bash "$SCRIPT_DIR/ip-monitor.sh" --check
}

# Show help
show_help() {
    echo ""
    echo "=============================================="
    echo "   Lavalink Cluster Deployment Script"
    echo "=============================================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  init        Initialize environment"
    echo "  build       Build Docker images"
    echo "  start       Start the cluster"
    echo "  stop        Stop the cluster"
    echo "  restart     Restart the cluster"
    echo "  status      Show cluster status"
    echo "  logs [svc]  View logs (optionally for specific service)"
    echo "  scale       Scale a service"
    echo "  clean       Remove all containers and volumes"
    echo "  oauth       Generate YouTube OAuth token"
    echo "  health      Run health checks"
    echo "  help        Show this help"
    echo ""
}

# Main
main() {
    case "${1:-}" in
        init)
            check_prerequisites
            init_env
            ;;
        build)
            build
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            logs "${2:-}"
            ;;
        scale)
            scale "${2:-}" "${3:-1}"
            ;;
        clean)
            clean
            ;;
        oauth)
            shift
            oauth "$@"
            ;;
        health)
            health
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

main "$@"
