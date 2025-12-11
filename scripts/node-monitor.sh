#!/bin/bash

# ==============================================================================
# Lavalink Node Health Monitor
# Monitors cluster node health and performance
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
NODES=(
    "lavalink-node1:2333:singapore"
    "lavalink-node2:2334:germany"
    "lavalink-node3:2335:us-east"
    "lavalink-backup:2336:india"
)
PASSWORD="${LAVALINK_PASSWORD:-SecurePassword123!}"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"
ALERT_THRESHOLD_CPU="${ALERT_THRESHOLD_CPU:-80}"
ALERT_THRESHOLD_MEMORY="${ALERT_THRESHOLD_MEMORY:-80}"
ALERT_THRESHOLD_PLAYERS="${ALERT_THRESHOLD_PLAYERS:-500}"

# Logging
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)    color=$BLUE ;;
        SUCCESS) color=$GREEN ;;
        WARNING) color=$YELLOW ;;
        ERROR)   color=$RED ;;
        *)       color=$NC ;;
    esac
    
    echo -e "${color}[$timestamp][$level]${NC} $message"
}

# Check node health
check_node() {
    local host="$1"
    local port="$2"
    local region="$3"
    local name="${host}:${port}"
    
    # Get version info
    local version_response=$(curl -s --connect-timeout 5 --max-time 10 \
        "http://${host}:${port}/version" 2>/dev/null || echo "")
    
    if [ -z "$version_response" ]; then
        log "ERROR" "[$region] $name - Connection Failed"
        echo "STATUS:down"
        return 1
    fi
    
    # Get stats
    local stats_response=$(curl -s --connect-timeout 5 --max-time 10 \
        -H "Authorization: $PASSWORD" \
        "http://${host}:${port}/v4/stats" 2>/dev/null || echo "")
    
    if [ -z "$stats_response" ]; then
        log "WARNING" "[$region] $name - Stats Unavailable"
        echo "STATUS:degraded"
        return 1
    fi
    
    # Parse stats
    local players=$(echo "$stats_response" | jq -r '.players // 0' 2>/dev/null || echo "0")
    local playing=$(echo "$stats_response" | jq -r '.playingPlayers // 0' 2>/dev/null || echo "0")
    local uptime=$(echo "$stats_response" | jq -r '.uptime // 0' 2>/dev/null || echo "0")
    local memory_used=$(echo "$stats_response" | jq -r '.memory.used // 0' 2>/dev/null || echo "0")
    local memory_free=$(echo "$stats_response" | jq -r '.memory.free // 0' 2>/dev/null || echo "0")
    local memory_allocated=$(echo "$stats_response" | jq -r '.memory.allocated // 0' 2>/dev/null || echo "0")
    local cpu_cores=$(echo "$stats_response" | jq -r '.cpu.cores // 0' 2>/dev/null || echo "0")
    local cpu_system=$(echo "$stats_response" | jq -r '.cpu.systemLoad // 0' 2>/dev/null || echo "0")
    local cpu_lavalink=$(echo "$stats_response" | jq -r '.cpu.lavalinkLoad // 0' 2>/dev/null || echo "0")
    
    # Calculate percentages
    local memory_percent=0
    if [ "$memory_allocated" -gt 0 ]; then
        memory_percent=$((memory_used * 100 / memory_allocated))
    fi
    
    local cpu_percent=$(echo "$cpu_system * 100" | bc 2>/dev/null || echo "0")
    cpu_percent=${cpu_percent%.*}
    
    # Format uptime
    local uptime_hours=$((uptime / 3600000))
    local uptime_days=$((uptime_hours / 24))
    
    # Display status
    log "SUCCESS" "[$region] $name - Online"
    echo "  ├─ Version:  $version_response"
    echo "  ├─ Uptime:   ${uptime_days}d ${uptime_hours}h"
    echo "  ├─ Players:  $playing playing / $players total"
    echo "  ├─ Memory:   $memory_percent% ($(numfmt --to=iec $memory_used) / $(numfmt --to=iec $memory_allocated))"
    echo "  └─ CPU:      ${cpu_percent}% (${cpu_cores} cores)"
    echo ""
    
    # Check thresholds
    if [ "$cpu_percent" -gt "$ALERT_THRESHOLD_CPU" ]; then
        log "WARNING" "[$region] High CPU usage: ${cpu_percent}%"
        send_alert "warning" "High CPU" "[$region] $name CPU at ${cpu_percent}%"
    fi
    
    if [ "$memory_percent" -gt "$ALERT_THRESHOLD_MEMORY" ]; then
        log "WARNING" "[$region] High memory usage: ${memory_percent}%"
        send_alert "warning" "High Memory" "[$region] $name Memory at ${memory_percent}%"
    fi
    
    if [ "$players" -gt "$ALERT_THRESHOLD_PLAYERS" ]; then
        log "WARNING" "[$region] High player count: $players"
        send_alert "warning" "High Players" "[$region] $name has $players players"
    fi
    
    echo "STATUS:online"
    return 0
}

# Send alert
send_alert() {
    local severity="$1"
    local title="$2"
    local message="$3"
    
    # Discord webhook
    if [ -n "$DISCORD_WEBHOOK" ]; then
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"embeds\": [{
                    \"title\": \"🎵 Lavalink: $title\",
                    \"description\": \"$message\",
                    \"color\": $([ "$severity" = "critical" ] && echo "16711680" || echo "16776960"),
                    \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"
                }]
            }" > /dev/null 2>&1
    fi
}

# Cluster summary
cluster_summary() {
    local online=0
    local offline=0
    local degraded=0
    local total_players=0
    local total_playing=0
    
    echo ""
    echo "=============================================="
    echo "       LAVALINK CLUSTER HEALTH CHECK"
    echo "=============================================="
    echo ""
    
    for node in "${NODES[@]}"; do
        IFS=':' read -r host port region <<< "$node"
        local status=$(check_node "$host" "$port" "$region" | grep "^STATUS:" | cut -d: -f2)
        
        case $status in
            online)   ((online++)) ;;
            degraded) ((degraded++)) ;;
            down)     ((offline++)) ;;
        esac
    done
    
    echo "=============================================="
    echo "              CLUSTER SUMMARY"
    echo "=============================================="
    echo -e "  ${GREEN}Online:${NC}   $online"
    echo -e "  ${YELLOW}Degraded:${NC} $degraded"
    echo -e "  ${RED}Offline:${NC}  $offline"
    echo "=============================================="
    echo ""
    
    # Critical alert if all nodes down
    if [ $online -eq 0 ]; then
        send_alert "critical" "Cluster Down" "All Lavalink nodes are offline!"
    elif [ $offline -gt 0 ]; then
        send_alert "warning" "Node(s) Offline" "$offline node(s) are offline"
    fi
}

# Monitor loop
run_monitor() {
    log "INFO" "Starting Lavalink Node Monitor..."
    log "INFO" "Check interval: ${CHECK_INTERVAL}s"
    
    while true; do
        cluster_summary
        log "INFO" "Next check in ${CHECK_INTERVAL}s..."
        sleep "$CHECK_INTERVAL"
    done
}

# Main
main() {
    case "${1:-}" in
        --check|-c)
            cluster_summary
            ;;
        --node|-n)
            if [ -z "${2:-}" ]; then
                echo "Usage: $0 --node <host:port>"
                exit 1
            fi
            IFS=':' read -r host port <<< "$2"
            check_node "$host" "$port" "custom"
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no args)         Start monitoring daemon"
            echo "  --check, -c       Run single health check"
            echo "  --node, -n HOST   Check specific node"
            echo "  --help, -h        Show this help"
            ;;
        *)
            run_monitor
            ;;
    esac
}

main "$@"
