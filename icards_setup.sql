-- ============================================================================
-- ICards Setup: 5 Customer + 20 Vendor + 20 Visitor cards
-- ============================================================================

-- Clear existing cards (optional - remove if you want to keep existing data)
DELETE FROM icards;

-- Reset sequence
ALTER SEQUENCE icards_id_seq RESTART WITH 1;

-- ============================================================================
-- Customer Cards: CU001 - CU005
-- ============================================================================
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('CU001', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('CU002', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('CU003', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('CU004', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('CU005', false, NULL);

-- ============================================================================
-- Vendor Cards: VE001 - VE020
-- ============================================================================
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE001', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE002', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE003', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE004', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE005', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE006', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE007', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE008', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE009', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE010', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE011', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE012', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE013', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE014', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE015', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE016', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE017', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE018', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE019', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VE020', false, NULL);

-- ============================================================================
-- Visitor Cards: VI001 - VI020
-- ============================================================================
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI001', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI002', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI003', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI004', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI005', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI006', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI007', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI008', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI009', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI010', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI011', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI012', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI013', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI014', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI015', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI016', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI017', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI018', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI019', false, NULL);
INSERT INTO icards (card_name, occ_status, occ_to) VALUES ('VI020', false, NULL);

-- ============================================================================
-- Verify
-- ============================================================================
SELECT card_name, occ_status FROM icards ORDER BY card_name;
