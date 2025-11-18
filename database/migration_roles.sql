-- Add password field to landlords table for admin panel access
ALTER TABLE landlords ADD COLUMN password TEXT;

-- Add email field to landlord_requests table
ALTER TABLE landlord_requests ADD COLUMN email TEXT NOT NULL DEFAULT '';

-- Add role field to admins to distinguish between admin and landlord
-- Note: In SQLite we can't modify existing columns easily, so we track roles differently
-- Admins table keeps admins, landlords table now has password for panel access
