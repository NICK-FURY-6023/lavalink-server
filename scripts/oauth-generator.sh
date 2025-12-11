#!/bin/bash

# ==============================================================================
# YouTube OAuth Token Generator
# Generates refresh token for YouTube OAuth2 authentication
# ==============================================================================

set -e

echo "=============================================="
echo "   YouTube OAuth Token Generator"
echo "   Premium Lavalink Anti-Block System"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLIENT_ID="861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com"
CLIENT_SECRET="SboVhoG9s0rNafixCSGGKXAT"
SCOPE="https://www.googleapis.com/auth/youtube"
TOKEN_FILE="./youtube_tokens.json"

# Function to display colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed."
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. Installing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y jq
        elif command -v yum &> /dev/null; then
            sudo yum install -y jq
        elif command -v brew &> /dev/null; then
            brew install jq
        else
            log_error "Could not install jq. Please install it manually."
            exit 1
        fi
    fi
    
    log_success "All dependencies are available."
}

# Step 1: Get device code
get_device_code() {
    log_info "Requesting device code from Google..."
    
    DEVICE_CODE_RESPONSE=$(curl -s -X POST \
        "https://oauth2.googleapis.com/device/code" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=${CLIENT_ID}" \
        -d "scope=${SCOPE}")
    
    DEVICE_CODE=$(echo "$DEVICE_CODE_RESPONSE" | jq -r '.device_code')
    USER_CODE=$(echo "$DEVICE_CODE_RESPONSE" | jq -r '.user_code')
    VERIFICATION_URL=$(echo "$DEVICE_CODE_RESPONSE" | jq -r '.verification_url')
    EXPIRES_IN=$(echo "$DEVICE_CODE_RESPONSE" | jq -r '.expires_in')
    INTERVAL=$(echo "$DEVICE_CODE_RESPONSE" | jq -r '.interval')
    
    if [ "$DEVICE_CODE" == "null" ] || [ -z "$DEVICE_CODE" ]; then
        log_error "Failed to get device code"
        echo "$DEVICE_CODE_RESPONSE"
        exit 1
    fi
    
    echo ""
    echo "=============================================="
    echo -e "${GREEN}  DEVICE CODE GENERATED SUCCESSFULLY${NC}"
    echo "=============================================="
    echo ""
    echo -e "${YELLOW}Please follow these steps:${NC}"
    echo ""
    echo -e "  1. Open this URL in your browser:"
    echo -e "     ${BLUE}${VERIFICATION_URL}${NC}"
    echo ""
    echo -e "  2. Enter this code:"
    echo -e "     ${GREEN}${USER_CODE}${NC}"
    echo ""
    echo -e "  3. Sign in with a YouTube/Google account"
    echo -e "     ${YELLOW}(Use a burner account for safety!)${NC}"
    echo ""
    echo -e "  4. Click 'Allow' to grant access"
    echo ""
    echo "=============================================="
    echo -e "Code expires in: ${EXPIRES_IN} seconds"
    echo "=============================================="
    echo ""
}

# Step 2: Poll for authorization
poll_for_token() {
    log_info "Waiting for authorization..."
    echo -e "${YELLOW}Press Ctrl+C to cancel${NC}"
    echo ""
    
    MAX_ATTEMPTS=$((EXPIRES_IN / INTERVAL))
    ATTEMPT=0
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        sleep $INTERVAL
        ATTEMPT=$((ATTEMPT + 1))
        
        TOKEN_RESPONSE=$(curl -s -X POST \
            "https://oauth2.googleapis.com/token" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "client_id=${CLIENT_ID}" \
            -d "client_secret=${CLIENT_SECRET}" \
            -d "device_code=${DEVICE_CODE}" \
            -d "grant_type=urn:ietf:params:oauth:grant-type:device_code")
        
        ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
        REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token')
        ERROR=$(echo "$TOKEN_RESPONSE" | jq -r '.error')
        
        if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
            log_success "Authorization successful!"
            save_tokens
            return 0
        elif [ "$ERROR" == "authorization_pending" ]; then
            echo -ne "\rWaiting for authorization... (${ATTEMPT}/${MAX_ATTEMPTS})   "
        elif [ "$ERROR" == "slow_down" ]; then
            INTERVAL=$((INTERVAL + 1))
        elif [ "$ERROR" == "access_denied" ]; then
            log_error "Access denied by user"
            exit 1
        elif [ "$ERROR" == "expired_token" ]; then
            log_error "Device code expired. Please run the script again."
            exit 1
        else
            log_error "Unknown error: $ERROR"
            echo "$TOKEN_RESPONSE"
            exit 1
        fi
    done
    
    log_error "Timeout waiting for authorization"
    exit 1
}

# Save tokens to file
save_tokens() {
    echo ""
    echo "=============================================="
    echo -e "${GREEN}  TOKENS GENERATED SUCCESSFULLY${NC}"
    echo "=============================================="
    echo ""
    
    # Save to file
    echo "$TOKEN_RESPONSE" | jq '.' > "$TOKEN_FILE"
    
    echo -e "${YELLOW}Your Refresh Token:${NC}"
    echo ""
    echo -e "${GREEN}${REFRESH_TOKEN}${NC}"
    echo ""
    echo "=============================================="
    echo ""
    echo -e "${BLUE}Tokens saved to:${NC} $TOKEN_FILE"
    echo ""
    echo -e "${YELLOW}Add this to your .env file:${NC}"
    echo ""
    echo -e "YOUTUBE_REFRESH_TOKEN=${REFRESH_TOKEN}"
    echo ""
    echo "=============================================="
    echo ""
    echo -e "${YELLOW}Or add to your application.yml:${NC}"
    echo ""
    echo "plugins:"
    echo "  youtube:"
    echo "    oauth:"
    echo "      enabled: true"
    echo "      refreshToken: \"${REFRESH_TOKEN}\""
    echo ""
    echo "=============================================="
}

# Refresh existing token
refresh_token() {
    if [ ! -f "$TOKEN_FILE" ]; then
        log_error "Token file not found: $TOKEN_FILE"
        exit 1
    fi
    
    STORED_REFRESH_TOKEN=$(jq -r '.refresh_token' "$TOKEN_FILE")
    
    if [ "$STORED_REFRESH_TOKEN" == "null" ] || [ -z "$STORED_REFRESH_TOKEN" ]; then
        log_error "No refresh token found in $TOKEN_FILE"
        exit 1
    fi
    
    log_info "Refreshing access token..."
    
    TOKEN_RESPONSE=$(curl -s -X POST \
        "https://oauth2.googleapis.com/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "client_id=${CLIENT_ID}" \
        -d "client_secret=${CLIENT_SECRET}" \
        -d "refresh_token=${STORED_REFRESH_TOKEN}" \
        -d "grant_type=refresh_token")
    
    NEW_ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
    
    if [ "$NEW_ACCESS_TOKEN" != "null" ] && [ -n "$NEW_ACCESS_TOKEN" ]; then
        log_success "Token refreshed successfully!"
        echo ""
        echo -e "${BLUE}New Access Token:${NC}"
        echo "$NEW_ACCESS_TOKEN"
        
        # Update token file
        jq --arg token "$NEW_ACCESS_TOKEN" '.access_token = $token' "$TOKEN_FILE" > "${TOKEN_FILE}.tmp" && mv "${TOKEN_FILE}.tmp" "$TOKEN_FILE"
    else
        log_error "Failed to refresh token"
        echo "$TOKEN_RESPONSE"
        exit 1
    fi
}

# Validate existing token
validate_token() {
    if [ ! -f "$TOKEN_FILE" ]; then
        log_error "Token file not found: $TOKEN_FILE"
        exit 1
    fi
    
    ACCESS_TOKEN=$(jq -r '.access_token' "$TOKEN_FILE")
    
    if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
        log_error "No access token found in $TOKEN_FILE"
        exit 1
    fi
    
    log_info "Validating access token..."
    
    VALIDATION_RESPONSE=$(curl -s \
        "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${ACCESS_TOKEN}")
    
    ERROR=$(echo "$VALIDATION_RESPONSE" | jq -r '.error')
    
    if [ "$ERROR" == "null" ] || [ -z "$ERROR" ]; then
        log_success "Token is valid!"
        echo ""
        echo -e "${BLUE}Token Info:${NC}"
        echo "$VALIDATION_RESPONSE" | jq '.'
    else
        log_error "Token is invalid or expired"
        echo "$VALIDATION_RESPONSE"
        echo ""
        log_info "Run with --refresh to get a new access token"
    fi
}

# Main
main() {
    case "${1:-}" in
        --refresh)
            check_dependencies
            refresh_token
            ;;
        --validate)
            check_dependencies
            validate_token
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no args)    Generate new OAuth tokens"
            echo "  --refresh    Refresh the access token using stored refresh token"
            echo "  --validate   Validate the current access token"
            echo "  --help       Show this help message"
            echo ""
            ;;
        *)
            check_dependencies
            get_device_code
            poll_for_token
            ;;
    esac
}

main "$@"
