-- ═══════════════════════════════════════
-- USERS & AUTH (Leveraging Supabase Auth)
-- ═══════════════════════════════════════
-- Supabase automatically handles the auth.users table.
-- We create a public profiles table that links to auth.users

CREATE TABLE profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username        VARCHAR(100) UNIQUE NOT NULL,
    role            VARCHAR(20) DEFAULT 'analyst',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Note: We no longer need an explicit `users` table since we use auth.users and profiles
-- Note: We no longer need `hashed_password` since Supabase handles passwords

CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES profiles(id) ON DELETE CASCADE,
    key_hash        TEXT NOT NULL,
    name            VARCHAR(100),
    scopes          TEXT[],
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════
-- SCAN JOBS & RESULTS
-- ═══════════════════════════════════════
CREATE TABLE scan_jobs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID REFERENCES profiles(id) ON DELETE CASCADE,
    status           VARCHAR(30) DEFAULT 'pending',
    job_type         VARCHAR(20) NOT NULL,
    file_name        VARCHAR(500),
    file_hash_sha256 VARCHAR(64),
    file_size_bytes  BIGINT,
    mime_type        VARCHAR(100),
    minio_path       TEXT,
    priority         INTEGER DEFAULT 5,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    error_message    TEXT
);

CREATE TABLE scan_results (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_job_id       UUID REFERENCES scan_jobs(id) ON DELETE CASCADE,
    is_stego          BOOLEAN NOT NULL,
    confidence        FLOAT NOT NULL,
    detection_methods JSONB,
    threat_level      VARCHAR(20),
    payload_map       JSONB,
    feature_vector    JSONB,
    yara_matches      JSONB,
    metadata          JSONB,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════
-- NEUTRALIZATION
-- ═══════════════════════════════════════
CREATE TABLE neutralization_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_result_id  UUID REFERENCES scan_results(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES profiles(id) ON DELETE SET NULL,
    status          VARCHAR(30) DEFAULT 'pending',
    strategy_used   VARCHAR(50)[],
    original_path   TEXT NOT NULL,
    sanitized_path  TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE TABLE integrity_reports (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    neutralization_id       UUID REFERENCES neutralization_jobs(id) ON DELETE CASCADE,
    ssim_score              FLOAT,
    psnr_db                 FLOAT,
    mse                     FLOAT,
    perceptual_hash_match   BOOLEAN,
    pixel_diff_percent      FLOAT,
    model_accuracy_before   FLOAT,
    model_accuracy_after    FLOAT,
    verification_scan_clean BOOLEAN,
    quality_approved        BOOLEAN,
    details                 JSONB,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════
-- REPORTS & AUDIT
-- ═══════════════════════════════════════
CREATE TABLE reports (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_job_id       UUID REFERENCES scan_jobs(id) ON DELETE CASCADE,
    neutralization_id UUID REFERENCES neutralization_jobs(id) ON DELETE CASCADE,
    user_id           UUID REFERENCES profiles(id) ON DELETE CASCADE,
    report_type       VARCHAR(30),
    format            VARCHAR(10),
    minio_path        TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE audit_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES profiles(id) ON DELETE SET NULL,
    action        VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id   UUID,
    ip_address    INET,
    user_agent    TEXT,
    details       JSONB,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════
-- THREAT INTELLIGENCE
-- ═══════════════════════════════════════
CREATE TABLE threat_signatures (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    category    VARCHAR(50),
    yara_rule   TEXT,
    description TEXT,
    severity    VARCHAR(20),
    source      VARCHAR(100),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════
-- WEBHOOKS
-- ═══════════════════════════════════════
CREATE TABLE webhooks (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id   UUID REFERENCES profiles(id) ON DELETE CASCADE,
    url       TEXT NOT NULL,
    events    TEXT[],
    secret    TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════
CREATE INDEX idx_scan_jobs_user     ON scan_jobs(user_id);
CREATE INDEX idx_scan_jobs_status   ON scan_jobs(status);
CREATE INDEX idx_scan_jobs_hash     ON scan_jobs(file_hash_sha256);
CREATE INDEX idx_results_threat     ON scan_results(threat_level);
CREATE INDEX idx_neutral_status     ON neutralization_jobs(status);
CREATE INDEX idx_audit_user         ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_action       ON audit_log(action, created_at DESC);

-- Setup RLS (Row Level Security) for user data isolation
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scan_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE neutralization_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrity_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;

-- Allow users to see only their own data (Basic Policies)
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own scan jobs" ON scan_jobs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own scan jobs" ON scan_jobs FOR ALL USING (auth.uid() = user_id);
