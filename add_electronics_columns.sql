-- ============================================================================
-- Migration Script: Add Electronics Carrying Fields to vis_visitors Table
-- Date: February 2026
-- Purpose: Add support for tracking electronics items carried by visitors
-- ============================================================================

-- Add new columns for electronics tracking
ALTER TABLE vis_visitors 
ADD COLUMN IF NOT EXISTS carrying_electronics VARCHAR(10) DEFAULT 'false',
ADD COLUMN IF NOT EXISTS electronics_items TEXT;

-- Add comments to explain the columns
COMMENT ON COLUMN vis_visitors.carrying_electronics IS 'Boolean flag (as string) indicating if visitor is carrying electronic devices (true/false)';
COMMENT ON COLUMN vis_visitors.electronics_items IS 'JSON string containing array of electronics items with details (type, brand, serial_number, quantity, photo_url)';

-- Create index for faster filtering by electronics carrying status
CREATE INDEX IF NOT EXISTS idx_vis_visitors_carrying_electronics ON vis_visitors(carrying_electronics);

-- Sample data structure for electronics_items column:
-- [
--   {
--     "type": "Laptop",
--     "brand": "Dell",
--     "serialNumber": "DL123456789",
--     "quantity": 1,
--     "photo": "base64_encoded_image_data_or_s3_url"
--   },
--   {
--     "type": "Mobile",
--     "brand": "iPhone",
--     "serialNumber": "IP987654321", 
--     "quantity": 1,
--     "photo": "base64_encoded_image_data_or_s3_url"
--   }
-- ]

-- ============================================================================
-- Verification Query - Run after migration to verify the changes
-- ============================================================================

-- Check if columns were added successfully
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'vis_visitors' 
AND column_name IN ('carrying_electronics', 'electronics_items');

-- Sample query to test the new columns
-- SELECT id, visitor_name, carrying_electronics, electronics_items 
-- FROM vis_visitors 
-- WHERE carrying_electronics = 'true' 
-- LIMIT 5;