-- Insert ICards into the database
-- Customer Cards (CU001-CU005)
INSERT INTO icards (card_name, icard_name, occ_status, occ_to, created_at, updated_at) VALUES
('CU001', 'customer_1_card', FALSE, NULL, NOW(), NOW()),
('CU002', 'customer_2_card', FALSE, NULL, NOW(), NOW()),
('CU003', 'customer_3_card', FALSE, NULL, NOW(), NOW()),
('CU004', 'customer_4_card', FALSE, NULL, NOW(), NOW()),
('CU005', 'customer_5_card', FALSE, NULL, NOW(), NOW()),

-- Vendor Cards (VE001-VE005)
('VE001', 'vendor_1_card', FALSE, NULL, NOW(), NOW()),
('VE002', 'vendor_2_card', FALSE, NULL, NOW(), NOW()),
('VE003', 'vendor_3_card', FALSE, NULL, NOW(), NOW()),
('VE004', 'vendor_4_card', FALSE, NULL, NOW(), NOW()),
('VE005', 'vendor_5_card', FALSE, NULL, NOW(), NOW()),

-- Visitor Cards (VI001-VI005)
('VI001', 'visitor_1_card', FALSE, NULL, NOW(), NOW()),
('VI002', 'visitor_2_card', FALSE, NULL, NOW(), NOW()),
('VI003', 'visitor_3_card', FALSE, NULL, NOW(), NOW()),
('VI004', 'visitor_4_card', FALSE, NULL, NOW(), NOW()),
('VI005', 'visitor_5_card', FALSE, NULL, NOW(), NOW());

-- Verify the insert
SELECT COUNT(*) as total_cards FROM icards;
SELECT card_name, icard_name, occ_status FROM icards ORDER BY card_name;
