-- Database initialization script
CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    alert_threshold_days INTEGER DEFAULT 30
);

CREATE TABLE IF NOT EXISTS ssl_checks (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id) ON DELETE CASCADE,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_in INTEGER,
    is_valid BOOLEAN,
    error_message TEXT,
    issuer VARCHAR(255),
    subject VARCHAR(255),
    not_valid_before TIMESTAMP,
    not_valid_after TIMESTAMP
);

CREATE INDEX idx_domain_id ON ssl_checks(domain_id);
CREATE INDEX idx_checked_at ON ssl_checks(checked_at);

-- Insert some test domains
INSERT INTO domains (name) VALUES 
    ('google.com'),
    ('github.com'),
    ('stackoverflow.com')
ON CONFLICT (name) DO NOTHING;

