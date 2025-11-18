-- Migration: Add translations table
-- This table stores custom translations that override the default ones from locales.py

CREATE TABLE IF NOT EXISTS translations (
    key TEXT PRIMARY KEY,
    text_ru TEXT NOT NULL,
    text_kk TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_translations_key ON translations(key);
