-- ====================================================================
-- SUPABASE POSTGRESQL SCHEMA FOR DDCET PREP CLOUD SYNC & BATTLE ARENA
-- Run this in your Supabase Project -> SQL Editor
-- ====================================================================

-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS public.ddcet_profiles (
    email TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    avatar TEXT DEFAULT '⚡',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Detailed User Stats Table (for Head-to-Head Battle & Leaderboards)
CREATE TABLE IF NOT EXISTS public.ddcet_user_stats (
    email TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    avatar TEXT DEFAULT '⚡',
    total_questions INTEGER NOT NULL DEFAULT 0,
    correct_count INTEGER NOT NULL DEFAULT 0,
    incorrect_count INTEGER NOT NULL DEFAULT 0,
    accuracy_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    total_score NUMERIC(7, 2) NOT NULL DEFAULT 0.00,
    study_time_minutes NUMERIC(7, 1) NOT NULL DEFAULT 0.0,
    streak_days INTEGER NOT NULL DEFAULT 1,
    avg_speed_seconds NUMERIC(6, 1) NOT NULL DEFAULT 0.0,
    topics_mastered INTEGER NOT NULL DEFAULT 0,
    topics_total INTEGER NOT NULL DEFAULT 0,
    topic_stats JSONB NOT NULL DEFAULT '{}'::jsonb,
    mock_stats JSONB NOT NULL DEFAULT '[]'::jsonb,
    last_active TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Friends & Competitor Relationships Table
CREATE TABLE IF NOT EXISTS public.ddcet_friends (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_email TEXT NOT NULL,
    friend_email TEXT NOT NULL,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_email, friend_email)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_ddcet_user_stats_score ON public.ddcet_user_stats(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_ddcet_user_stats_acc ON public.ddcet_user_stats(accuracy_pct DESC);
CREATE INDEX IF NOT EXISTS idx_ddcet_user_stats_email ON public.ddcet_user_stats(email);
CREATE INDEX IF NOT EXISTS idx_ddcet_friends_user ON public.ddcet_friends(user_email);

-- Enable Row Level Security (RLS) with permissive read/write policies for anon access
ALTER TABLE public.ddcet_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ddcet_user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ddcet_friends ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public select on ddcet_profiles" 
ON public.ddcet_profiles FOR SELECT USING (true);

CREATE POLICY "Allow public insert/update on ddcet_profiles" 
ON public.ddcet_profiles FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public select on ddcet_user_stats" 
ON public.ddcet_user_stats FOR SELECT USING (true);

CREATE POLICY "Allow public insert/update on ddcet_user_stats" 
ON public.ddcet_user_stats FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow public select on ddcet_friends" 
ON public.ddcet_friends FOR SELECT USING (true);

CREATE POLICY "Allow public insert/delete on ddcet_friends" 
ON public.ddcet_friends FOR ALL USING (true) WITH CHECK (true);
