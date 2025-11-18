-- Add password field to landlords table for admin panel access
ALTER TABLE landlords ADD COLUMN password TEXT;

-- Add role field to admins to distinguish between admin and landlord
-- Note: In SQLite we can't modify existing columns easily, so we track roles differently
-- Admins table keeps admins, landlords table now has password for panel access
