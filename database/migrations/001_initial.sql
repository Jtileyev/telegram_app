-- Migration 001: Initial schema
-- This migration is a placeholder for the initial schema
-- The actual schema is in schema.sql

-- Create migrations tracking table if not exists
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
