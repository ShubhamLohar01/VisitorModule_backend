-- Create vis_appointment table for Google Form submissions
-- This table stores appointment booking data from Google Forms

CREATE TABLE IF NOT EXISTS vis_appointment (
    id BIGSERIAL PRIMARY KEY,
    
    -- Visitor Information
    visitor_name VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(20) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    
    -- Appointment Details
    person_to_meet VARCHAR(255) NOT NULL,
    purpose_of_visit VARCHAR(500) NOT NULL,
    preferred_time_slot VARCHAR(100),
    
    -- Additional Information
    carrying_items TEXT,
    additional_remarks TEXT,
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'google_form',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sheet_name VARCHAR(255),
    row_number INTEGER,
    
    -- Status and Tracking
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, CONFIRMED, CANCELLED, COMPLETED
    visitor_id BIGINT, -- Reference to vis_visitors table if converted to visitor
    
    -- QR Code
    qr_code VARCHAR(500), -- Unique QR code identifier
    qr_code_sent VARCHAR(10) DEFAULT 'NO', -- YES/NO - whether QR was sent via email
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_appointment_mobile ON vis_appointment(mobile_number);
CREATE INDEX IF NOT EXISTS idx_appointment_email ON vis_appointment(email_address);
CREATE INDEX IF NOT EXISTS idx_appointment_person_to_meet ON vis_appointment(person_to_meet);
CREATE INDEX IF NOT EXISTS idx_appointment_status ON vis_appointment(status);
CREATE INDEX IF NOT EXISTS idx_appointment_created_at ON vis_appointment(created_at);
CREATE INDEX IF NOT EXISTS idx_appointment_visitor_id ON vis_appointment(visitor_id);

-- Add comment to table
COMMENT ON TABLE vis_appointment IS 'Stores appointment booking data from Google Forms';

-- Add comments to columns
COMMENT ON COLUMN vis_appointment.visitor_name IS 'Full Name of Visitor';
COMMENT ON COLUMN vis_appointment.mobile_number IS 'Mobile Number';
COMMENT ON COLUMN vis_appointment.email_address IS 'Email Id';
COMMENT ON COLUMN vis_appointment.company IS 'Company / Organization Name';
COMMENT ON COLUMN vis_appointment.person_to_meet IS 'Enter Person Name You Want to Meet';
COMMENT ON COLUMN vis_appointment.purpose_of_visit IS 'Purpose of Visit (options)';
COMMENT ON COLUMN vis_appointment.preferred_time_slot IS 'Preferred Time Slot (options)';
COMMENT ON COLUMN vis_appointment.carrying_items IS 'Are you carrying any items inside the premises?';
COMMENT ON COLUMN vis_appointment.additional_remarks IS 'Additional Remarks(if any)';
COMMENT ON COLUMN vis_appointment.source IS 'Source of submission (google_form, web_form, etc.)';
COMMENT ON COLUMN vis_appointment.status IS 'Appointment status: PENDING, CONFIRMED, CANCELLED, COMPLETED';
COMMENT ON COLUMN vis_appointment.visitor_id IS 'Reference to vis_visitors table if appointment is converted to visitor check-in';

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_appointment_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_appointment_updated_at
    BEFORE UPDATE ON vis_appointment
    FOR EACH ROW
    EXECUTE FUNCTION update_appointment_updated_at();

