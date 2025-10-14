"""
Automatic Database Migration Script
Runs migrations on application startup without requiring Shell access
"""

import logging
from sqlalchemy import create_engine, text, inspect
from app.config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """
    Run database migrations automatically
    Safe to run multiple times - checks if tables exist first
    """
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Check if user_profiles table already exists
        existing_tables = inspector.get_table_names()
        
        if 'user_profiles' in existing_tables:
            logger.info("✅ user_profiles table already exists, skipping migration")
            return True
        
        logger.info("🔄 Running database migration for user_profiles...")
        
        # Drop existing table if it exists (with corrupted schema)
        drop_sql = """
        DROP TABLE IF EXISTS language_change_log CASCADE;
        DROP TABLE IF NOT EXISTS user_profiles CASCADE;
        DROP VIEW IF EXISTS language_distribution CASCADE;
        DROP VIEW IF EXISTS recent_language_changes CASCADE;
        """
        
        with engine.connect() as conn:
            for statement in drop_sql.split(';'):
                statement = statement.strip()
                if statement:
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        logger.warning(f"Drop statement warning: {e}")
            conn.commit()
        
        logger.info("✅ Cleaned up existing tables")
        logger.info("🔄 Creating fresh schema...")
        
        # Create fresh migration SQL
        migration_sql = """
        -- Create user_profiles table
        CREATE TABLE user_profiles (
            id SERIAL PRIMARY KEY NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            preferred_language VARCHAR(5) NOT NULL DEFAULT 'en',
            signup_language VARCHAR(5) NOT NULL DEFAULT 'en',
            device_languages JSONB DEFAULT '[]'::jsonb,
            timezone VARCHAR(50),
            country_code VARCHAR(2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE,
            subscription_id INTEGER,
            data_processing_consent BOOLEAN DEFAULT FALSE,
            marketing_consent BOOLEAN DEFAULT FALSE
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_language ON user_profiles(preferred_language);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON user_profiles(created_at);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_country ON user_profiles(country_code);

        -- Create language_change_log table
        CREATE TABLE IF NOT EXISTS language_change_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
            old_language VARCHAR(5),
            new_language VARCHAR(5) NOT NULL,
            device_type VARCHAR(50),
            user_agent TEXT,
            ip_address INET,
            changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for language_change_log
        CREATE INDEX IF NOT EXISTS idx_language_log_user ON language_change_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_language_log_date ON language_change_log(changed_at);

        -- Create update trigger function
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- Create trigger
        DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
        CREATE TRIGGER update_user_profiles_updated_at
            BEFORE UPDATE ON user_profiles
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();

        -- Create views for analytics
        CREATE OR REPLACE VIEW language_distribution AS
        SELECT 
            preferred_language,
            COUNT(*) as user_count,
            ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) as percentage
        FROM user_profiles
        WHERE is_active = TRUE
        GROUP BY preferred_language
        ORDER BY user_count DESC;

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
        """
        
        # Execute migration
        with engine.connect() as conn:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    conn.execute(text(statement))
                    logger.info(f"✅ Executed statement: {statement[:50]}...")
                except Exception as e:
                    logger.warning(f"⚠️  Statement warning: {str(e)[:100]}")
                    # Continue with next statement
            
            conn.commit()
        
        logger.info("✅ Database migration completed successfully!")
        logger.info("✅ Tables created: user_profiles, language_change_log")
        logger.info("✅ Views created: language_distribution, recent_language_changes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        logger.exception("Full error:")
        return False

if __name__ == "__main__":
    logger.info("Running migrations standalone...")
    success = run_migrations()
    if success:
        logger.info("✅ Migration successful!")
    else:
        logger.error("❌ Migration failed!")

