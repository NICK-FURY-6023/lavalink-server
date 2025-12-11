#!/bin/bash

# ==============================================================================
# IP Health Monitor Script
# Monitors exit node health and manages IP rotation
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
REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"
COOLDOWN_DURATION="${COOLDOWN_DURATION:-300}"
LOG_FILE="/var/log/ip-monitor.log"
CONFIG_FILE="${CONFIG_FILE:-/app/config/ip-pool.yml}"

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
    
    echo -e "${color}[$timestamp][$level]${NC} $message" | tee -a "$LOG_FILE"
}

# Initialize Redis connection
init_redis() {
    log "INFO" "Initializing Redis connection..."
    
    # Test Redis connection
    if ! redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
        log "ERROR" "Failed to connect to Redis at $REDIS_URL"
        return 1
    fi
    
    log "SUCCESS" "Redis connection established"
}

# Load IP pool from configuration
load_ip_pool() {
    log "INFO" "Loading IP pool configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log "ERROR" "Configuration file not found: $CONFIG_FILE"
        return 1
    fi
    
    # Parse YAML and load IPs (simplified)
    IP_POOL=()
    
    # For demo purposes, using environment variables
    [ -n "$SG_IP_1" ] && IP_POOL+=("$SG_IP_1:sg1:singapore")
    [ -n "$SG_IP_2" ] && IP_POOL+=("$SG_IP_2:sg2:singapore")
    [ -n "$DE_IP_1" ] && IP_POOL+=("$DE_IP_1:de1:germany")
    [ -n "$DE_IP_2" ] && IP_POOL+=("$DE_IP_2:de2:germany")
    [ -n "$US_IP_1" ] && IP_POOL+=("$US_IP_1:us1:us-east")
    [ -n "$US_IP_2" ] && IP_POOL+=("$US_IP_2:us2:us-east")
    [ -n "$BACKUP_IP_1" ] && IP_POOL+=("$BACKUP_IP_1:backup1:india")
    [ -n "$BACKUP_IP_2" ] && IP_POOL+=("$BACKUP_IP_2:backup2:japan")
    
    log "SUCCESS" "Loaded ${#IP_POOL[@]} IPs from configuration"
}

# Check IP health
check_ip_health() {
    local ip="$1"
    local name="$2"
    
    # Test connectivity with YouTube
    local start_time=$(date +%s%N)
    local response=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 10 \
        --max-time 30 \
        --proxy "http://${ip}:443" \
        "https://www.youtube.com/generate_204" 2>/dev/null || echo "000")
    local end_time=$(date +%s%N)
    
    local latency=$(( (end_time - start_time) / 1000000 ))
    
    # Store metrics in Redis
    redis-cli -u "$REDIS_URL" HSET "ip:${name}:health" \
        "last_check" "$(date +%s)" \
        "status_code" "$response" \
        "latency" "$latency" > /dev/null 2>&1
    
    case $response in
        204|200)
            log "SUCCESS" "[$name] $ip - OK (${latency}ms)"
            redis-cli -u "$REDIS_URL" SET "ip:${name}:status" "active" > /dev/null 2>&1
            return 0
            ;;
        429)
            log "WARNING" "[$name] $ip - Rate Limited (429)"
            handle_rate_limit "$ip" "$name"
            return 1
            ;;
        403)
            log "WARNING" "[$name] $ip - Forbidden (403)"
            handle_ip_block "$ip" "$name"
            return 1
            ;;
        000)
            log "ERROR" "[$name] $ip - Connection Failed"
            handle_connection_failure "$ip" "$name"
            return 1
            ;;
        *)
            log "WARNING" "[$name] $ip - Unknown Response: $response"
            return 1
            ;;
    esac
}

# Handle rate limiting (429)
handle_rate_limit() {
    local ip="$1"
    local name="$2"
    
    # Get current 429 count
    local count=$(redis-cli -u "$REDIS_URL" INCR "ip:${name}:429_count" 2>/dev/null || echo "1")
    
    log "WARNING" "[$name] 429 count: $count"
    
    if [ "$count" -ge 3 ]; then
        log "WARNING" "[$name] Cooling down for ${COOLDOWN_DURATION}s"
        
        # Set cooldown
        redis-cli -u "$REDIS_URL" SET "ip:${name}:status" "cooldown" > /dev/null 2>&1
        redis-cli -u "$REDIS_URL" SET "ip:${name}:cooldown_until" "$(( $(date +%s) + COOLDOWN_DURATION ))" > /dev/null 2>&1
        
        # Send alert
        send_alert "warning" "IP Rate Limited" "[$name] $ip has been rate limited and is cooling down for ${COOLDOWN_DURATION}s"
    fi
}

# Handle IP block
handle_ip_block() {
    local ip="$1"
    local name="$2"
    
    log "ERROR" "[$name] IP appears to be blocked"
    
    redis-cli -u "$REDIS_URL" SET "ip:${name}:status" "blocked" > /dev/null 2>&1
    
    # Send critical alert
    send_alert "critical" "IP Blocked" "[$name] $ip appears to be blocked by YouTube"
}

# Handle connection failure
handle_connection_failure() {
    local ip="$1"
    local name="$2"
    
    # Get failure count
    local count=$(redis-cli -u "$REDIS_URL" INCR "ip:${name}:fail_count" 2>/dev/null || echo "1")
    
    if [ "$count" -ge 5 ]; then
        log "ERROR" "[$name] Too many failures, marking as down"
        redis-cli -u "$REDIS_URL" SET "ip:${name}:status" "down" > /dev/null 2>&1
        
        # Send alert
        send_alert "critical" "IP Down" "[$name] $ip is unresponsive after $count failures"
    fi
}

# Check cooldown status
check_cooldown() {
    local name="$1"
    
    local cooldown_until=$(redis-cli -u "$REDIS_URL" GET "ip:${name}:cooldown_until" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    
    if [ "$cooldown_until" -gt "$current_time" ]; then
        local remaining=$(( cooldown_until - current_time ))
        log "INFO" "[$name] Still in cooldown (${remaining}s remaining)"
        return 1
    else
        # Clear cooldown
        redis-cli -u "$REDIS_URL" DEL "ip:${name}:cooldown_until" > /dev/null 2>&1
        redis-cli -u "$REDIS_URL" DEL "ip:${name}:429_count" > /dev/null 2>&1
        redis-cli -u "$REDIS_URL" DEL "ip:${name}:fail_count" > /dev/null 2>&1
        return 0
    fi
}

# Send alert
send_alert() {
    local severity="$1"
    local title="$2"
    local message="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Discord webhook
    if [ -n "$DISCORD_WEBHOOK" ]; then
        local color
        case $severity in
            critical) color=16711680 ;;  # Red
            warning)  color=16776960 ;;  # Yellow
            info)     color=65535 ;;     # Cyan
            *)        color=8421504 ;;   # Gray
        esac
        
        curl -s -X POST "$DISCORD_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"embeds\": [{
                    \"title\": \"🔔 $title\",
                    \"description\": \"$message\",
                    \"color\": $color,
                    \"timestamp\": \"$timestamp\",
                    \"footer\": {\"text\": \"Lavalink IP Monitor\"}
                }]
            }" > /dev/null 2>&1
    fi
    
    # Slack webhook
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"text\": \"*[$severity]* $title\n$message\"
            }" > /dev/null 2>&1
    fi
}

# Get cluster health summary
get_health_summary() {
    local active=0
    local cooldown=0
    local blocked=0
    local down=0
    
    for ip_entry in "${IP_POOL[@]}"; do
        IFS=':' read -r ip name region <<< "$ip_entry"
        local status=$(redis-cli -u "$REDIS_URL" GET "ip:${name}:status" 2>/dev/null || echo "unknown")
        
        case $status in
            active)   ((active++)) ;;
            cooldown) ((cooldown++)) ;;
            blocked)  ((blocked++)) ;;
            down)     ((down++)) ;;
        esac
    done
    
    echo ""
    echo "=============================================="
    echo "           IP POOL HEALTH SUMMARY"
    echo "=============================================="
    echo -e "  ${GREEN}Active:${NC}   $active"
    echo -e "  ${YELLOW}Cooldown:${NC} $cooldown"
    echo -e "  ${RED}Blocked:${NC}  $blocked"
    echo -e "  ${RED}Down:${NC}     $down"
    echo "=============================================="
    echo ""
    
    # Alert if too few active IPs
    if [ $active -lt 3 ]; then
        send_alert "critical" "Low Available IPs" "Only $active IPs are active. Cooldown: $cooldown, Blocked: $blocked, Down: $down"
    fi
}

# Main monitoring loop
run_monitor() {
    log "INFO" "Starting IP Health Monitor..."
    log "INFO" "Check interval: ${CHECK_INTERVAL}s"
    log "INFO" "Cooldown duration: ${COOLDOWN_DURATION}s"
    
    init_redis || exit 1
    load_ip_pool || exit 1
    
    while true; do
        log "INFO" "Starting health check cycle..."
        
        for ip_entry in "${IP_POOL[@]}"; do
            IFS=':' read -r ip name region <<< "$ip_entry"
            
            # Skip if in cooldown
            if ! check_cooldown "$name"; then
                continue
            fi
            
            # Check health
            check_ip_health "$ip" "$name"
            
            # Small delay between checks
            sleep 1
        done
        
        # Print summary
        get_health_summary
        
        # Wait for next cycle
        log "INFO" "Next check in ${CHECK_INTERVAL}s..."
        sleep "$CHECK_INTERVAL"
    done
}

# HTTP health endpoint
start_health_server() {
    while true; do
        echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK" | nc -l -p 8080 -q 1
    done &
}

# Main
main() {
    case "${1:-}" in
        --check)
            init_redis || exit 1
            load_ip_pool || exit 1
            for ip_entry in "${IP_POOL[@]}"; do
                IFS=':' read -r ip name region <<< "$ip_entry"
                check_ip_health "$ip" "$name"
            done
            get_health_summary
            ;;
        --summary)
            init_redis || exit 1
            load_ip_pool || exit 1
            get_health_summary
            ;;
        --reset)
            log "INFO" "Resetting all IP statuses..."
            init_redis || exit 1
            load_ip_pool || exit 1
            for ip_entry in "${IP_POOL[@]}"; do
                IFS=':' read -r ip name region <<< "$ip_entry"
                redis-cli -u "$REDIS_URL" DEL "ip:${name}:status" > /dev/null 2>&1
                redis-cli -u "$REDIS_URL" DEL "ip:${name}:cooldown_until" > /dev/null 2>&1
                redis-cli -u "$REDIS_URL" DEL "ip:${name}:429_count" > /dev/null 2>&1
                redis-cli -u "$REDIS_URL" DEL "ip:${name}:fail_count" > /dev/null 2>&1
                log "SUCCESS" "[$name] Reset"
            done
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no args)    Start monitoring daemon"
            echo "  --check      Run single health check"
            echo "  --summary    Show health summary"
            echo "  --reset      Reset all IP statuses"
            echo "  --help       Show this help"
            ;;
        *)
            start_health_server
            run_monitor
            ;;
    esac
}

main "$@"
