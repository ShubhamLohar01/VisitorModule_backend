-- ============================================================================
-- Create vis_admin table and insert admin accounts
-- ============================================================================

-- Step 1: Create the vis_admin table
CREATE TABLE IF NOT EXISTS vis_admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    warehouse VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_vis_admin_username ON vis_admin(username);
CREATE INDEX IF NOT EXISTS idx_vis_admin_email ON vis_admin(email);
CREATE INDEX IF NOT EXISTS idx_vis_admin_warehouse ON vis_admin(warehouse);

-- Add comments
COMMENT ON TABLE vis_admin IS 'Admin accounts for admin page access';
COMMENT ON COLUMN vis_admin.warehouse IS 'Warehouse assignment for admin (W202, A68, A185, F53, etc.)';

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_vis_admin_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_vis_admin_updated_at_trigger ON vis_admin;
CREATE TRIGGER update_vis_admin_updated_at_trigger
    BEFORE UPDATE ON vis_admin
    FOR EACH ROW
    EXECUTE FUNCTION update_vis_admin_updated_at();

-- ============================================================================
-- Step 2: Insert admin accounts
-- ============================================================================

-- Admin 01 - Warehouse: W202
INSERT INTO vis_admin (username, email, name, hashed_password, warehouse, is_active, created_at, updated_at)
VALUES (
    'admin01',
    'admin01@candorfoods.in',
    'Admin 01',
    '$2b$12$LLHKT/Q9//YOO3x.y069MO9nRBqB9DJmIqX5w6lB/0864MFECAPze',
    'W202',
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    hashed_password = EXCLUDED.hashed_password,
    warehouse = EXCLUDED.warehouse,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Admin 02 - Warehouse: A68
INSERT INTO vis_admin (username, email, name, hashed_password, warehouse, is_active, created_at, updated_at)
VALUES (
    'admin02',
    'admin02@candorfoods.in',
    'Admin 02',
    '$2b$12$Frw7HDyYvhzeORTOOtl.gO2uf2iKwAxeyXbCMOmJm78BespKBCZVa',
    'A68',
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    hashed_password = EXCLUDED.hashed_password,
    warehouse = EXCLUDED.warehouse,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Admin 03 - Warehouse: A185
INSERT INTO vis_admin (username, email, name, hashed_password, warehouse, is_active, created_at, updated_at)
VALUES (
    'admin03',
    'admin03@candorfoods.in',
    'Admin 03',
    '$2b$12$0oqmkvz4ymYArmryR1LBtuAIn3w4JSap463ktNtnVi8qV9gj9Ofui',
    'A185',
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    hashed_password = EXCLUDED.hashed_password,
    warehouse = EXCLUDED.warehouse,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Admin 04 - Warehouse: F53
INSERT INTO vis_admin (username, email, name, hashed_password, warehouse, is_active, created_at, updated_at)
VALUES (
    'admin04',
    'admin04@candorfoods.in',
    'Admin 04',
    '$2b$12$K1lHhtvDojYBdrdUlmS5m.axCUeBrpvp3jZfiR6rcgPcV42zdQmye',
    'F53',
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    hashed_password = EXCLUDED.hashed_password,
    warehouse = EXCLUDED.warehouse,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Admin 05 - Warehouse: 101
INSERT INTO vis_admin (username, email, name, hashed_password, warehouse, is_active, created_at, updated_at)
VALUES (
    'admin05',
    'admin05@candorfoods.in',
    'Admin 05',
    '$2b$12$KzhER47qGfJsUqbjUUbUmeaTEBhkZL0p4c4FW.3szYmkkPH85/XYO',
    '101',
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (username) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    hashed_password = EXCLUDED.hashed_password,
    warehouse = EXCLUDED.warehouse,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- ============================================================================
-- Verify the inserts
-- ============================================================================
SELECT 
    id,
    username,
    email,
    name,
    warehouse,
    is_active,
    created_at
FROM vis_admin
ORDER BY username;

