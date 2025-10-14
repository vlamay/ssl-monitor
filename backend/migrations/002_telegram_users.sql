-- SSL Monitor Pro - Telegram Users and Preferences Migration
-- Migration: 002_telegram_users.sql
-- Description: Create tables for Telegram user management and preferences

-- Telegram users table
CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    notification_enabled BOOLEAN DEFAULT true,
    alert_threshold_days INTEGER DEFAULT 30,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '08:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    subscription_status VARCHAR(20) DEFAULT 'trial',
    subscription_plan VARCHAR(50),
    subscription_ends_at TIMESTAMP,
    last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification preferences per domain
CREATE TABLE IF NOT EXISTS telegram_notification_preferences (
    id SERIAL PRIMARY KEY,
    telegram_user_id INTEGER REFERENCES telegram_users(id) ON DELETE CASCADE,
    domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- 'warning', 'critical', 'expired', 'renewed'
    enabled BOOLEAN DEFAULT true,
    custom_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(telegram_user_id, domain_id, alert_type)
);

-- Telegram notification history
CREATE TABLE IF NOT EXISTS telegram_notifications (
    id SERIAL PRIMARY KEY,
    telegram_user_id INTEGER REFERENCES telegram_users(id) ON DELETE CASCADE,
    domain_id INTEGER REFERENCES domains(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'ssl_warning', 'ssl_critical', 'ssl_expired', 'payment', etc.
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered BOOLEAN DEFAULT false,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

-- Telegram bot settings (global configuration)
CREATE TABLE IF NOT EXISTS telegram_bot_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default bot settings
INSERT INTO telegram_bot_settings (setting_key, setting_value, description) VALUES
('bot_username', 'CloudereMonitorBot', 'Telegram bot username'),
('webhook_url', '', 'Webhook URL for receiving updates'),
('webhook_enabled', 'false', 'Whether webhook is enabled'),
('max_message_length', '4096', 'Maximum message length'),
('default_language', 'en', 'Default language for new users'),
('welcome_message_enabled', 'true', 'Whether to send welcome message'),
('help_message_enabled', 'true', 'Whether to show help message'),
('rate_limit_per_minute', '20', 'Rate limit for messages per minute'),
('notification_retry_attempts', '3', 'Number of retry attempts for failed notifications'),
('quiet_hours_enabled', 'true', 'Whether quiet hours are enabled by default')
ON CONFLICT (setting_key) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_username ON telegram_users(username);
CREATE INDEX IF NOT EXISTS idx_telegram_users_language ON telegram_users(language);
CREATE INDEX IF NOT EXISTS idx_telegram_users_notification_enabled ON telegram_users(notification_enabled);
CREATE INDEX IF NOT EXISTS idx_telegram_users_subscription_status ON telegram_users(subscription_status);

CREATE INDEX IF NOT EXISTS idx_telegram_notification_preferences_user_id ON telegram_notification_preferences(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_notification_preferences_domain_id ON telegram_notification_preferences(domain_id);
CREATE INDEX IF NOT EXISTS idx_telegram_notification_preferences_alert_type ON telegram_notification_preferences(alert_type);

CREATE INDEX IF NOT EXISTS idx_telegram_notifications_user_id ON telegram_notifications(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_domain_id ON telegram_notifications(domain_id);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_sent_at ON telegram_notifications(sent_at);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_delivered ON telegram_notifications(delivered);
CREATE INDEX IF NOT EXISTS idx_telegram_notifications_type ON telegram_notifications(notification_type);

-- Create updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
DROP TRIGGER IF EXISTS update_telegram_users_updated_at ON telegram_users;
CREATE TRIGGER update_telegram_users_updated_at
    BEFORE UPDATE ON telegram_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_telegram_notification_preferences_updated_at ON telegram_notification_preferences;
CREATE TRIGGER update_telegram_notification_preferences_updated_at
    BEFORE UPDATE ON telegram_notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to get user notification preferences
CREATE OR REPLACE FUNCTION get_telegram_user_preferences(p_telegram_id BIGINT)
RETURNS TABLE (
    user_id INTEGER,
    telegram_id BIGINT,
    username VARCHAR,
    language VARCHAR,
    notification_enabled BOOLEAN,
    alert_threshold_days INTEGER,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR,
    subscription_status VARCHAR,
    subscription_plan VARCHAR,
    subscription_ends_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tu.id,
        tu.telegram_id,
        tu.username,
        tu.language,
        tu.notification_enabled,
        tu.alert_threshold_days,
        tu.quiet_hours_start,
        tu.quiet_hours_end,
        tu.timezone,
        tu.subscription_status,
        tu.subscription_plan,
        tu.subscription_ends_at
    FROM telegram_users tu
    WHERE tu.telegram_id = p_telegram_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to get domains for telegram user
CREATE OR REPLACE FUNCTION get_telegram_user_domains(p_telegram_id BIGINT)
RETURNS TABLE (
    domain_id INTEGER,
    domain_name VARCHAR,
    is_active BOOLEAN,
    alert_threshold_days INTEGER,
    last_ssl_check TIMESTAMP,
    ssl_status VARCHAR,
    expires_in_days INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.name,
        d.is_active,
        d.alert_threshold_days,
        sc.checked_at,
        CASE 
            WHEN sc.expires_in <= 0 THEN 'expired'
            WHEN sc.expires_in <= 7 THEN 'critical'
            WHEN sc.expires_in <= 30 THEN 'warning'
            ELSE 'healthy'
        END as ssl_status,
        sc.expires_in
    FROM telegram_users tu
    JOIN domains d ON d.is_active = true
    LEFT JOIN (
        SELECT DISTINCT ON (domain_id) 
            domain_id, checked_at, expires_in
        FROM ssl_checks 
        ORDER BY domain_id, checked_at DESC
    ) sc ON sc.domain_id = d.id
    WHERE tu.telegram_id = p_telegram_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to log telegram notification
CREATE OR REPLACE FUNCTION log_telegram_notification(
    p_telegram_user_id INTEGER,
    p_domain_id INTEGER,
    p_notification_type VARCHAR,
    p_message TEXT,
    p_delivered BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    notification_id INTEGER;
BEGIN
    INSERT INTO telegram_notifications (
        telegram_user_id,
        domain_id,
        notification_type,
        message,
        delivered,
        error_message
    ) VALUES (
        p_telegram_user_id,
        p_domain_id,
        p_notification_type,
        p_message,
        p_delivered,
        p_error_message
    ) RETURNING id INTO notification_id;
    
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql;

-- Create view for telegram user statistics
CREATE OR REPLACE VIEW telegram_user_stats AS
SELECT 
    tu.id,
    tu.telegram_id,
    tu.username,
    tu.first_name,
    tu.language,
    tu.subscription_status,
    tu.created_at,
    COUNT(DISTINCT tn.id) as total_notifications,
    COUNT(DISTINCT CASE WHEN tn.delivered = true THEN tn.id END) as delivered_notifications,
    COUNT(DISTINCT CASE WHEN tn.sent_at >= CURRENT_DATE THEN tn.id END) as notifications_today,
    COUNT(DISTINCT tnp.domain_id) as monitored_domains,
    tu.last_interaction_at
FROM telegram_users tu
LEFT JOIN telegram_notifications tn ON tn.telegram_user_id = tu.id
LEFT JOIN telegram_notification_preferences tnp ON tnp.telegram_user_id = tu.id
GROUP BY tu.id, tu.telegram_id, tu.username, tu.first_name, tu.language, 
         tu.subscription_status, tu.created_at, tu.last_interaction_at;

-- Insert sample telegram user (for testing)
INSERT INTO telegram_users (
    telegram_id, username, first_name, language, 
    notification_enabled, alert_threshold_days, subscription_status
) VALUES (
    8159854958, 'vmaidaniuk', 'Vladislav', 'en',
    true, 30, 'trial'
) ON CONFLICT (telegram_id) DO UPDATE SET
    username = EXCLUDED.username,
    first_name = EXCLUDED.first_name,
    last_interaction_at = CURRENT_TIMESTAMP;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON telegram_users TO ssl_monitor_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON telegram_notification_preferences TO ssl_monitor_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON telegram_notifications TO ssl_monitor_user;
-- GRANT SELECT ON telegram_bot_settings TO ssl_monitor_user;
-- GRANT SELECT ON telegram_user_stats TO ssl_monitor_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ssl_monitor_user;

COMMENT ON TABLE telegram_users IS 'Telegram bot users and their preferences';
COMMENT ON TABLE telegram_notification_preferences IS 'Per-domain notification preferences for telegram users';
COMMENT ON TABLE telegram_notifications IS 'History of sent telegram notifications';
COMMENT ON TABLE telegram_bot_settings IS 'Global telegram bot configuration settings';
COMMENT ON VIEW telegram_user_stats IS 'Statistics view for telegram users';

-- Migration completed
SELECT 'Migration 002_telegram_users completed successfully' as status;
