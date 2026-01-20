-- ============================================================================
-- Visitor Management System - Database Schema
-- PostgreSQL Database Tables
-- ============================================================================

-- Drop tables if they exist (for clean reinstall)
-- WARNING: This will delete all data!
-- DROP TABLE IF EXISTS visitors CASCADE;
-- DROP TABLE IF EXISTS approvers CASCADE;

-- ============================================================================
-- Table 1: approvers
-- Purpose: Store approver credentials and authentication information
-- ============================================================================

CREATE TABLE IF NOT EXISTS approvers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    superuser BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_approvers_username ON approvers(username);
CREATE INDEX IF NOT EXISTS idx_approvers_email ON approvers(email);
CREATE INDEX IF NOT EXISTS idx_approvers_is_active ON approvers(is_active);

-- Add comment to table
COMMENT ON TABLE approvers IS 'Stores approver authentication and authorization information';
COMMENT ON COLUMN approvers.id IS 'Primary key - auto-incrementing ID';
COMMENT ON COLUMN approvers.username IS 'Unique username for login (max 50 characters)';
COMMENT ON COLUMN approvers.email IS 'Unique email address';
COMMENT ON COLUMN approvers.name IS 'Full name of the approver';
COMMENT ON COLUMN approvers.hashed_password IS 'Bcrypt hashed password (never stores plain text)';
COMMENT ON COLUMN approvers.superuser IS 'Flag indicating if user has admin privileges';
COMMENT ON COLUMN approvers.is_active IS 'Flag indicating if account is active';
COMMENT ON COLUMN approvers.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN approvers.updated_at IS 'Timestamp when record was last updated';

-- ============================================================================
-- Table 2: visitors
-- Purpose: Store visitor check-in information and tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS visitors (
    id BIGINT PRIMARY KEY,
    visitor_name VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    email_address VARCHAR(255),
    company VARCHAR(255),
    person_to_meet VARCHAR(255) NOT NULL,
    reason_to_visit VARCHAR(500) NOT NULL,
    expected_duration VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'waiting' NOT NULL,
    check_in_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_status CHECK (status IN ('waiting', 'checked_in', 'in_meeting', 'checked_out', 'cancelled'))
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_visitors_visitor_name ON visitors(visitor_name);
CREATE INDEX IF NOT EXISTS idx_visitors_mobile_number ON visitors(mobile_number);
CREATE INDEX IF NOT EXISTS idx_visitors_status ON visitors(status);
CREATE INDEX IF NOT EXISTS idx_visitors_check_in_time ON visitors(check_in_time DESC);
CREATE INDEX IF NOT EXISTS idx_visitors_person_to_meet ON visitors(person_to_meet);
CREATE INDEX IF NOT EXISTS idx_visitors_company ON visitors(company);

-- Add comments to table
COMMENT ON TABLE visitors IS 'Stores visitor check-in and tracking information';
COMMENT ON COLUMN visitors.id IS 'Primary key - auto-incrementing ID';
COMMENT ON COLUMN visitors.visitor_name IS 'Name of the visitor';
COMMENT ON COLUMN visitors.mobile_number IS 'Mobile contact number (10-20 characters)';
COMMENT ON COLUMN visitors.email_address IS 'Email address (optional)';
COMMENT ON COLUMN visitors.company IS 'Company name (optional)';
COMMENT ON COLUMN visitors.person_to_meet IS 'Name of person the visitor wants to meet';
COMMENT ON COLUMN visitors.reason_to_visit IS 'Purpose of visit (max 500 characters)';
COMMENT ON COLUMN visitors.expected_duration IS 'Expected visit duration (e.g., "1 hour", "30 minutes")';
COMMENT ON COLUMN visitors.status IS 'Current status: waiting, checked_in, in_meeting, checked_out, cancelled';
COMMENT ON COLUMN visitors.check_in_time IS 'Timestamp when visitor checked in';
COMMENT ON COLUMN visitors.check_out_time IS 'Timestamp when visitor checked out (NULL if not checked out)';
COMMENT ON COLUMN visitors.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN visitors.updated_at IS 'Timestamp when record was last updated';

-- ============================================================================
-- Trigger: Auto-update updated_at timestamp
-- Purpose: Automatically update updated_at column when record is modified
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for approvers table
DROP TRIGGER IF EXISTS update_approvers_updated_at ON approvers;
CREATE TRIGGER update_approvers_updated_at
    BEFORE UPDATE ON approvers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for visitors table
DROP TRIGGER IF EXISTS update_visitors_updated_at ON visitors;
CREATE TRIGGER update_visitors_updated_at
    BEFORE UPDATE ON visitors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Trigger: Auto-generate visitor ID in YYYYMMDDHHMMSS format
-- Purpose: Automatically set visitor ID based on timestamp
-- ============================================================================

-- Function to generate visitor ID in YYYYMMDDHHMMSS format
CREATE OR REPLACE FUNCTION generate_visitor_id()
RETURNS TRIGGER AS $$
DECLARE
    new_id BIGINT;
    max_attempts INT := 100;
    attempt INT := 0;
BEGIN
    -- Loop to handle potential collisions (if multiple inserts in same second)
    LOOP
        -- Generate ID in format YYYYMMDDHHMMSS
        new_id := TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS')::BIGINT;

        -- Check if this ID already exists
        IF NOT EXISTS (SELECT 1 FROM visitors WHERE id = new_id) THEN
            NEW.id := new_id;
            EXIT;
        END IF;

        -- If ID exists, wait a tiny bit and try again
        attempt := attempt + 1;
        IF attempt >= max_attempts THEN
            RAISE EXCEPTION 'Could not generate unique visitor ID after % attempts', max_attempts;
        END IF;

        -- Small delay to ensure different timestamp
        PERFORM pg_sleep(0.001);
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate visitor ID before insert
DROP TRIGGER IF EXISTS generate_visitor_id_trigger ON visitors;
CREATE TRIGGER generate_visitor_id_trigger
    BEFORE INSERT ON visitors
    FOR EACH ROW
    WHEN (NEW.id IS NULL)
    EXECUTE FUNCTION generate_visitor_id();

-- ============================================================================
-- Insert Default Admin Account
-- Purpose: Create default superuser for first-time setup
-- ============================================================================

-- Default password: "admin123" (hashed with bcrypt)
-- IMPORTANT: Change this password immediately after first login!
INSERT INTO approvers (username, email, name, hashed_password, superuser, is_active)
VALUES (
    'admin',
    'admin@example.com',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKKLK4xQwm', -- Password: admin123
    TRUE,
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- Sample Data (Optional - for testing)
-- Uncomment to insert sample data
-- ============================================================================

/*
-- Sample Approvers
INSERT INTO approvers (username, email, name, hashed_password, superuser, is_active)
VALUES
    ('john_doe', 'john@example.com', 'John Doe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKKLK4xQwm', FALSE, TRUE),
    ('jane_smith', 'jane@example.com', 'Jane Smith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKKLK4xQwm', FALSE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Sample Visitors
INSERT INTO visitors (visitor_name, mobile_number, email_address, company, person_to_meet, reason_to_visit, expected_duration, status)
VALUES
    ('Alice Johnson', '1234567890', 'alice@acme.com', 'Acme Corp', 'John Doe', 'Business meeting', '1 hour', 'waiting'),
    ('Bob Williams', '9876543210', 'bob@techco.com', 'Tech Co', 'Jane Smith', 'Product demo', '2 hours', 'in_meeting'),
    ('Carol Davis', '5555551234', 'carol@startup.io', 'Startup Inc', 'John Doe', 'Interview', '45 minutes', 'checked_in');
*/

-- ============================================================================
-- Verification Queries
-- Run these to verify tables were created successfully
-- ============================================================================

-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('approvers', 'visitors')
ORDER BY table_name;

-- Count records in each table
SELECT 'approvers' as table_name, COUNT(*) as record_count FROM approvers
UNION ALL
SELECT 'visitors' as table_name, COUNT(*) as record_count FROM visitors;

-- View default admin account (should exist)
SELECT id, username, email, name, superuser, is_active, created_at
FROM approvers
WHERE username = 'admin';

-- ============================================================================
-- Useful Queries for Management
-- ============================================================================

-- View all approvers
-- SELECT id, username, email, name, superuser, is_active, created_at FROM approvers ORDER BY id;

-- View all active visitors today
-- SELECT * FROM visitors
-- WHERE DATE(check_in_time) = CURRENT_DATE
--   AND status IN ('waiting', 'checked_in', 'in_meeting')
-- ORDER BY check_in_time DESC;

-- Visitor statistics
-- SELECT
--     status,
--     COUNT(*) as count
-- FROM visitors
-- GROUP BY status
-- ORDER BY count DESC;

-- Recent check-ins (last 10)
-- SELECT id, visitor_name, company, person_to_meet, status, check_in_time
-- FROM visitors
-- ORDER BY check_in_time DESC
-- LIMIT 10;

-- ============================================================================
-- End of Schema
-- ============================================================================
