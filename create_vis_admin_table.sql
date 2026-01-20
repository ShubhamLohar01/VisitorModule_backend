-- Create vis_admin table for admin accounts
-- This table stores admin-specific accounts separate from approvers

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

-- Add comment to table
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

CREATE TRIGGER update_vis_admin_updated_at_trigger
    BEFORE UPDATE ON vis_admin
    FOR EACH ROW
    EXECUTE FUNCTION update_vis_admin_updated_at();

