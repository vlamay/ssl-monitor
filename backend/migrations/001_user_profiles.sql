-- =============================================
-- SSL Monitor Pro - User Profiles Schema
-- Version: 1.0
-- Purpose: Store user preferences including i18n
-- =============================================

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- i18n Preferences
    preferred_language VARCHAR(5) NOT NULL DEFAULT 'en',
    signup_language VARCHAR(5) NOT NULL DEFAULT 'en',
    
    -- Analytics
    device_languages JSONB DEFAULT '[]'::jsonb,
    timezone VARCHAR(50),
    country_code VARCHAR(2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Subscription info (reference to existing subscription)
    subscription_id INTEGER,
    
    -- GDPR compliance
    data_processing_consent BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_language ON user_profiles(preferred_language);
CREATE INDEX idx_user_profiles_created_at ON user_profiles(created_at);
CREATE INDEX idx_user_profiles_country ON user_profiles(country_code);

-- Language change log for analytics
CREATE TABLE IF NOT EXISTS language_change_log (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    old_language VARCHAR(5),
    new_language VARCHAR(5) NOT NULL,
    device_type VARCHAR(50),
    user_agent TEXT,
    ip_address INET,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_language_log_user ON language_change_log(user_id);
CREATE INDEX idx_language_log_date ON language_change_log(changed_at);

-- Function to update updated_at automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-updating updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Constraints
ALTER TABLE user_profiles
    ADD CONSTRAINT check_preferred_language 
    CHECK (preferred_language IN ('en', 'de', 'fr', 'es', 'it', 'ru'));

ALTER TABLE user_profiles
    ADD CONSTRAINT check_signup_language 
    CHECK (signup_language IN ('en', 'de', 'fr', 'es', 'it', 'ru'));

ALTER TABLE language_change_log
    ADD CONSTRAINT check_new_language 
    CHECK (new_language IN ('en', 'de', 'fr', 'es', 'it', 'ru'));

-- Comments for documentation
COMMENT ON TABLE user_profiles IS 'User profiles with i18n preferences and analytics';
COMMENT ON COLUMN user_profiles.device_languages IS 'Array of {language, device, timestamp} objects';
COMMENT ON COLUMN user_profiles.preferred_language IS 'User selected language for UI and emails';
COMMENT ON COLUMN user_profiles.signup_language IS 'Language at registration time (never changes)';
COMMENT ON TABLE language_change_log IS 'Audit log for all language preference changes';

-- Initial data (optional test user)
-- Password: Test1234! (bcrypt hash)
-- INSERT INTO user_profiles (email, password_hash, preferred_language, email_verified)
-- VALUES ('test@cloudsre.xyz', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ufD8tJuQS2Em', 'en', true);

-- Analytics view
CREATE OR REPLACE VIEW language_distribution AS
SELECT 
    preferred_language,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM user_profiles
WHERE is_active = TRUE
GROUP BY preferred_language
ORDER BY user_count DESC;

COMMENT ON VIEW language_distribution IS 'Real-time distribution of users by language';

-- Recent language changes view
CREATE OR REPLACE VIEW recent_language_changes AS
SELECT 
    lcl.id,
    up.email,
    lcl.old_language,
    lcl.new_language,
    lcl.device_type,
    lcl.changed_at
FROM language_change_log lcl
JOIN user_profiles up ON lcl.user_id = up.id
ORDER BY lcl.changed_at DESC
LIMIT 100;

COMMENT ON VIEW recent_language_changes IS 'Last 100 language preference changes';
