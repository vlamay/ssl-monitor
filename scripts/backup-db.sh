#!/bin/bash

# SSL Monitor Pro - Database Backup Script
# Run daily via cron or GitLab CI schedule

set -e

# Configuration
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"
BACKUP_FILE="ssl_monitor_backup_$DATE.sql.gz"
LOG_FILE="/var/log/ssl-monitor-backup.log"

# Environment variables (set by GitLab CI or system)
POSTGRES_HOST=${POSTGRES_HOST:-"localhost"}
POSTGRES_PORT=${POSTGRES_PORT:-"5432"}
POSTGRES_USER=${POSTGRES_USER:-"ssl_monitor"}
POSTGRES_DB=${POSTGRES_DB:-"ssl_monitor"}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Cloud storage settings (optional)
S3_BUCKET=${BACKUP_S3_BUCKET:-""}
S3_REGION=${BACKUP_S3_REGION:-"eu-west-1"}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-""}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-""}

# Retention settings
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "ERROR: $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if pg_dump is available
    if ! command -v pg_dump &> /dev/null; then
        handle_error "pg_dump command not found. Please install PostgreSQL client tools."
    fi
    
    # Check if gzip is available
    if ! command -v gzip &> /dev/null; then
        handle_error "gzip command not found. Please install gzip."
    fi
    
    # Check if required environment variables are set
    if [ -z "$POSTGRES_PASSWORD" ]; then
        handle_error "POSTGRES_PASSWORD environment variable is required"
    fi
    
    if [ -z "$POSTGRES_DB" ]; then
        handle_error "POSTGRES_DB environment variable is required"
    fi
    
    log "Prerequisites check passed"
}

# Create backup directory
create_backup_dir() {
    log "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        handle_error "Failed to create backup directory: $BACKUP_DIR"
    fi
    
    log "Backup directory created successfully"
}

# Perform database backup
perform_backup() {
    log "Starting database backup..."
    
    # Set PGPASSWORD for non-interactive authentication
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    # Perform backup with compression
    log "Backing up database: $POSTGRES_DB from host: $POSTGRES_HOST"
    
    if pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --format=custom \
        --compress=9 \
        --verbose \
        --no-password \
        | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then
        
        log "Database backup completed successfully: $BACKUP_FILE"
    else
        handle_error "Database backup failed"
    fi
    
    # Verify backup file
    if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        handle_error "Backup file was not created: $BACKUP_DIR/$BACKUP_FILE"
    fi
    
    # Check backup file size
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    log "Backup file size: $BACKUP_SIZE"
    
    if [ ! -s "$BACKUP_DIR/$BACKUP_FILE" ]; then
        handle_error "Backup file is empty"
    fi
    
    log "Backup verification completed"
}

# Upload to cloud storage (optional)
upload_to_cloud() {
    if [ -n "$S3_BUCKET" ] && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        log "Uploading backup to S3..."
        
        # Check if AWS CLI is available
        if ! command -v aws &> /dev/null; then
            log "WARNING: AWS CLI not found, skipping cloud upload"
            return 0
        fi
        
        # Upload to S3
        if aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$S3_BUCKET/ssl-monitor-backups/" \
            --region "$S3_REGION" \
            --storage-class STANDARD_IA; then
            
            log "Backup uploaded to S3 successfully: s3://$S3_BUCKET/ssl-monitor-backups/$BACKUP_FILE"
        else
            log "WARNING: Failed to upload backup to S3, but local backup is available"
        fi
    else
        log "Cloud storage not configured, skipping upload"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Count files before cleanup
    FILES_BEFORE=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
    log "Backups before cleanup: $FILES_BEFORE"
    
    # Remove old backup files
    DELETED_FILES=$(find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
    
    # Count files after cleanup
    FILES_AFTER=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
    
    log "Deleted $DELETED_FILES old backup files"
    log "Backups after cleanup: $FILES_AFTER"
}

# Test backup restore (optional)
test_backup_restore() {
    if [ "$TEST_RESTORE" = "true" ]; then
        log "Testing backup restore..."
        
        # Create test database
        TEST_DB="ssl_monitor_test_restore"
        
        # Drop test database if it exists
        psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres \
            -c "DROP DATABASE IF EXISTS $TEST_DB;" || true
        
        # Create test database
        psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres \
            -c "CREATE DATABASE $TEST_DB;"
        
        # Restore backup to test database
        if zcat "$BACKUP_DIR/$BACKUP_FILE" | psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$TEST_DB"; then
            log "Backup restore test completed successfully"
            
            # Cleanup test database
            psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres \
                -c "DROP DATABASE $TEST_DB;"
        else
            log "WARNING: Backup restore test failed"
        fi
    fi
}

# Generate backup report
generate_report() {
    log "Generating backup report..."
    
    REPORT_FILE="$BACKUP_DIR/backup_report_$DATE.txt"
    
    cat > "$REPORT_FILE" << EOF
SSL Monitor Pro - Database Backup Report
========================================
Date: $(date)
Backup File: $BACKUP_FILE
Backup Size: $(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
Database: $POSTGRES_DB
Host: $POSTGRES_HOST:$POSTGRES_PORT
User: $POSTGRES_USER

Backup Directory: $BACKUP_DIR
Total Backups: $(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
Available Space: $(df -h "$BACKUP_DIR" | tail -1 | awk '{print $4}')

Backup Status: SUCCESS
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    log "Backup report generated: $REPORT_FILE"
}

# Main execution
main() {
    log "=========================================="
    log "SSL Monitor Pro - Database Backup Started"
    log "=========================================="
    
    START_TIME=$(date +%s)
    
    check_prerequisites
    create_backup_dir
    perform_backup
    upload_to_cloud
    cleanup_old_backups
    test_backup_restore
    generate_report
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    log "=========================================="
    log "Backup completed successfully in ${DURATION} seconds"
    log "Backup file: $BACKUP_DIR/$BACKUP_FILE"
    log "=========================================="
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "SSL Monitor Pro - Database Backup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test-restore Test backup restore functionality"
        echo ""
        echo "Environment Variables:"
        echo "  POSTGRES_HOST          Database host (default: localhost)"
        echo "  POSTGRES_PORT          Database port (default: 5432)"
        echo "  POSTGRES_USER          Database user (default: ssl_monitor)"
        echo "  POSTGRES_DB            Database name (default: ssl_monitor)"
        echo "  POSTGRES_PASSWORD      Database password (required)"
        echo "  BACKUP_S3_BUCKET       S3 bucket for cloud storage (optional)"
        echo "  BACKUP_S3_REGION       S3 region (default: eu-west-1)"
        echo "  AWS_ACCESS_KEY_ID      AWS access key (optional)"
        echo "  AWS_SECRET_ACCESS_KEY  AWS secret key (optional)"
        echo "  BACKUP_RETENTION_DAYS  Days to retain backups (default: 7)"
        echo "  TEST_RESTORE           Test backup restore (default: false)"
        echo ""
        echo "Examples:"
        echo "  # Basic backup"
        echo "  POSTGRES_PASSWORD=mypass $0"
        echo ""
        echo "  # Backup with S3 upload"
        echo "  POSTGRES_PASSWORD=mypass BACKUP_S3_BUCKET=my-bucket AWS_ACCESS_KEY_ID=key AWS_SECRET_ACCESS_KEY=secret $0"
        echo ""
        echo "  # Backup with restore test"
        echo "  POSTGRES_PASSWORD=mypass TEST_RESTORE=true $0"
        exit 0
        ;;
    --test-restore)
        TEST_RESTORE=true
        main
        ;;
    *)
        main
        ;;
esac
