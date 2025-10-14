#!/bin/bash

# SSL Monitor Pro - Production Deployment Script
# This script handles the complete production deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="SSL Monitor Pro"
ENVIRONMENT="production"
RENDER_SERVICE_ID="${RENDER_PRODUCTION_SERVICE_ID}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL}"
TELEGRAM_WEBHOOK="${TELEGRAM_WEBHOOK_URL}"

# Functions
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

send_notification() {
    local message="$1"
    local status="$2"
    
    # Send to Slack
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK" || true
    fi
    
    # Send to Telegram
    if [ -n "$TELEGRAM_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$TELEGRAM_WEBHOOK" || true
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required environment variables are set
    if [ -z "$RENDER_API_KEY" ]; then
        log_error "RENDER_API_KEY environment variable is not set"
        exit 1
    fi
    
    if [ -z "$RENDER_SERVICE_ID" ]; then
        log_error "RENDER_PRODUCTION_SERVICE_ID environment variable is not set"
        exit 1
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. JSON parsing will be limited"
    fi
    
    log_success "Prerequisites check completed"
}

pre_deployment_tests() {
    log_info "Running pre-deployment tests..."
    
    # Run tests locally
    if [ -f "backend/requirements.txt" ]; then
        log_info "Installing test dependencies..."
        pip install -r backend/requirements.txt || {
            log_error "Failed to install dependencies"
            exit 1
        }
    fi
    
    # Run unit tests
    if [ -f "backend/tests" ]; then
        log_info "Running unit tests..."
        cd backend && python -m pytest tests/ -v || {
            log_error "Unit tests failed"
            exit 1
        }
        cd ..
    fi
    
    # Run linting
    if command -v flake8 &> /dev/null; then
        log_info "Running linting..."
        flake8 backend/ || {
            log_warning "Linting issues found, but continuing deployment"
        }
    fi
    
    log_success "Pre-deployment tests completed"
}

trigger_deployment() {
    log_info "Triggering deployment to Render..."
    
    # Trigger deployment
    DEPLOY_RESPONSE=$(curl -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -s "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys")
    
    if [ $? -eq 0 ]; then
        log_success "Deployment triggered successfully"
        
        # Extract deploy ID if jq is available
        if command -v jq &> /dev/null; then
            DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.id')
            log_info "Deploy ID: $DEPLOY_ID"
        fi
    else
        log_error "Failed to trigger deployment"
        exit 1
    fi
}

wait_for_deployment() {
    log_info "Waiting for deployment to complete..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Checking deployment status (attempt $attempt/$max_attempts)..."
        
        # Get deployment status
        STATUS_RESPONSE=$(curl -s \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys")
        
        if command -v jq &> /dev/null; then
            LATEST_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.deploys[0].status')
            log_info "Latest deployment status: $LATEST_STATUS"
            
            case $LATEST_STATUS in
                "live")
                    log_success "Deployment completed successfully!"
                    return 0
                    ;;
                "build_failed"|"update_failed")
                    log_error "Deployment failed with status: $LATEST_STATUS"
                    return 1
                    ;;
                "building"|"updating")
                    log_info "Deployment in progress..."
                    ;;
                *)
                    log_info "Deployment status: $LATEST_STATUS"
                    ;;
            esac
        else
            log_info "Deployment check completed (jq not available for detailed status)"
        fi
        
        sleep 30
        ((attempt++))
    done
    
    log_warning "Deployment status check timed out"
    return 1
}

run_health_checks() {
    log_info "Running post-deployment health checks..."
    
    local health_urls=(
        "https://ssl-monitor-api.onrender.com/health"
        "https://ssl-monitor-api.onrender.com/ready"
        "https://ssl-monitor-api.onrender.com/metrics"
    )
    
    local failed_checks=0
    
    for url in "${health_urls[@]}"; do
        log_info "Checking $url..."
        
        if curl -f -s --max-time 30 "$url" > /dev/null; then
            log_success "Health check passed: $url"
        else
            log_error "Health check failed: $url"
            ((failed_checks++))
        fi
    done
    
    # Test API endpoints
    local api_urls=(
        "https://ssl-monitor-api.onrender.com/api/trial/test"
        "https://ssl-monitor-api.onrender.com/billing/webhook/test"
        "https://ssl-monitor-api.onrender.com/telegram/webhook/test"
    )
    
    for url in "${api_urls[@]}"; do
        log_info "Testing API endpoint: $url..."
        
        if curl -f -s --max-time 30 "$url" > /dev/null; then
            log_success "API endpoint test passed: $url"
        else
            log_warning "API endpoint test failed: $url"
            ((failed_checks++))
        fi
    done
    
    if [ $failed_checks -eq 0 ]; then
        log_success "All health checks passed!"
        return 0
    else
        log_warning "$failed_checks health checks failed"
        return 1
    fi
}

rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # Get previous deployment
    PREVIOUS_DEPLOY=$(curl -s \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" | \
        jq -r '.deploys[1].id' 2>/dev/null)
    
    if [ -n "$PREVIOUS_DEPLOY" ] && [ "$PREVIOUS_DEPLOY" != "null" ]; then
        log_info "Rolling back to deployment: $PREVIOUS_DEPLOY"
        
        curl -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys/$PREVIOUS_DEPLOY/rollback"
        
        log_success "Rollback initiated"
    else
        log_error "No previous deployment found for rollback"
    fi
}

main() {
    log_info "Starting $PROJECT_NAME deployment to $ENVIRONMENT"
    
    # Start deployment notification
    send_notification "🚀 Starting $PROJECT_NAME deployment to $ENVIRONMENT" "start"
    
    # Check prerequisites
    check_prerequisites
    
    # Run pre-deployment tests
    pre_deployment_tests
    
    # Trigger deployment
    trigger_deployment
    
    # Wait for deployment to complete
    if wait_for_deployment; then
        log_success "Deployment completed successfully"
        
        # Run health checks
        if run_health_checks; then
            log_success "All health checks passed"
            send_notification "✅ $PROJECT_NAME deployed to $ENVIRONMENT successfully! All systems operational." "success"
        else
            log_warning "Some health checks failed, but deployment completed"
            send_notification "⚠️ $PROJECT_NAME deployed to $ENVIRONMENT with some health check failures" "warning"
        fi
    else
        log_error "Deployment failed or timed out"
        send_notification "❌ $PROJECT_NAME deployment to $ENVIRONMENT failed!" "error"
        
        # Attempt rollback
        rollback_deployment
        exit 1
    fi
    
    log_success "Deployment process completed"
}

# Run main function
main "$@"
