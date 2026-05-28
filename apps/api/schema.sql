-- ==========================================
-- PROMPTPILOT AI — DATABASE SCHEMA MIGRATION
-- ==========================================
-- Run this in your Supabase SQL Editor or raw PostgreSQL database.

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Compressions Metrics Table
CREATE TABLE IF NOT EXISTS compressions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  original_tokens INT NOT NULL,
  compressed_tokens INT NOT NULL,
  model TEXT NOT NULL,
  savings_percent FLOAT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Daily Usage Aggregation Table (for Dashboard Analytics)
CREATE TABLE IF NOT EXISTS usage_daily (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  total_compressions INT DEFAULT 1,
  total_tokens_saved INT DEFAULT 0,
  PRIMARY KEY (user_id, date)
);

-- Indices for faster dashboards query
CREATE INDEX IF NOT EXISTS idx_compressions_user_id ON compressions(user_id);
CREATE INDEX IF NOT EXISTS idx_compressions_created_at ON compressions(created_at);

-- Trigger / Function to automatically aggregate daily usage on new compression log
CREATE OR REPLACE FUNCTION log_daily_usage()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO usage_daily (user_id, date, total_compressions, total_tokens_saved)
  VALUES (
    NEW.user_id, 
    CURRENT_DATE, 
    1, 
    NEW.original_tokens - NEW.compressed_tokens
  )
  ON CONFLICT (user_id, date) 
  DO UPDATE SET 
    total_compressions = usage_daily.total_compressions + 1,
    total_tokens_saved = usage_daily.total_tokens_saved + (NEW.original_tokens - NEW.compressed_tokens);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_on_compression_logged
AFTER INSERT ON compressions
FOR EACH ROW
EXECUTE FUNCTION log_daily_usage();
