-- ============================================================================
-- Release all ICards (set all to available)
-- Use when the UI shows "All cards are currently occupied" but no cards
-- were actually assigned. Run this in your database client (pgAdmin, psql, etc.)
-- ============================================================================

UPDATE icards
SET occ_status = false,
    occ_to = NULL
WHERE occ_status = true;

-- Verify (optional)
-- SELECT card_name, occ_status, occ_to FROM icards ORDER BY card_name;
