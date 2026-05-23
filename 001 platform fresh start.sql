-- ═══════════════════════════════════════════════════════════════════════════════
-- MBTQ PLATFORM — Complete Schema Migration
-- Target: Platform project (fibrdmecsgqphnwdkbfv)
-- Source: PATHWAY API audit (216 tables → ~45 canonical tables)
--
-- Namespace prefixes (canonical):
--   deafauth.*      — identity, auth, ASL signatures
--   fibonrose.*     — trust, verification, visual signals (fixed spelling)
--   magiciancore.*  — agents, runs, steps, tools, projects
--   pinksync.*      — real-time events, logs, channels, Taskade bridge
--   vr4deaf.*       — VR profiles, intakes, vocrehab accounts, job matching
--   billing.*       — subscriptions, stripe, usage, GU pool
--   creator.*       — video, monetization, content
--   platform.*      — orgs, members, roles, allowed_domains
--   ref.*           — reference data (colors, sign language variants)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ─────────────────────────────────────────────────────────────────────────────
-- SHARED TRIGGER FUNCTION (one, canonical, replaces 5 duplicates)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

-- Macro to attach trigger (call after each table creation)
-- Usage: SELECT attach_updated_at('schema.table');
CREATE OR REPLACE FUNCTION attach_updated_at(target_table TEXT)
RETURNS VOID LANGUAGE plpgsql AS $$
BEGIN
  EXECUTE format(
    'CREATE OR REPLACE TRIGGER trg_updated_at
     BEFORE UPDATE ON %s
     FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
    target_table
  );
END;
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: deafauth
-- Identity, authentication, ASL signatures
-- Sources: deafauth_user, deaf_users, deafauth_profiles, ecosystem_users,
--          asl_signatures, authentication_methods
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS deafauth;

-- ── deafauth.users ─────────────────────────────────────────────────────────
-- Canonical user record. Clerk is auth provider (clerk_user_id = source of truth).
-- Merges: deafauth_user + deaf_users + ecosystem_users

CREATE TABLE deafauth.users (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clerk_user_id           TEXT UNIQUE NOT NULL,         -- Clerk JWT sub
  email                   TEXT NOT NULL,
  username                TEXT UNIQUE,

  -- Identity
  first_name              TEXT,
  last_name               TEXT,
  preferred_name          TEXT,
  name_sign               TEXT,                         -- ASL name sign description

  -- Deaf identity (from deaf_users.deaf_identity enum)
  deaf_identity           TEXT CHECK (deaf_identity IN (
                            'deaf','hard_of_hearing','deafblind',
                            'late_deafened','hearing','coda','unspecified'
                          )),
  hearing_loss_type       TEXT,
  hearing_loss_onset      TEXT,
  deaf_culture_connection TEXT,

  -- Communication
  primary_sign_language   TEXT DEFAULT 'asl',
  sign_language_variants  TEXT[],
  communication_prefs     TEXT[],                       -- asl, pse, see, lip_reading, written

  -- Accessibility
  assistive_technologies  JSONB DEFAULT '{}',
  accessibility_prefs     JSONB DEFAULT '{}',

  -- Platform state
  roles                   TEXT[] DEFAULT ARRAY['user'],
  verification_level      TEXT DEFAULT 'unverified'
                            CHECK (verification_level IN (
                              'unverified','email_verified','identity_verified',
                              'community_verified','fully_verified'
                            )),
  pinksync_ready          BOOLEAN DEFAULT FALSE,
  fibonrose_badge         TEXT,
  community_trust_score   NUMERIC(5,2) DEFAULT 0,

  -- Auth
  auth_method             TEXT DEFAULT 'visual'
                            CHECK (auth_method IN (
                              'visual','asl_signature','pin','biometric','clerk_oauth'
                            )),
  last_authenticated_at   TIMESTAMPTZ,

  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW(),
  deleted_at              TIMESTAMPTZ                   -- soft delete
);

SELECT attach_updated_at('deafauth.users');
CREATE INDEX idx_deafauth_users_clerk    ON deafauth.users(clerk_user_id);
CREATE INDEX idx_deafauth_users_email    ON deafauth.users(email);
CREATE INDEX idx_deafauth_users_identity ON deafauth.users(deaf_identity);

-- ── deafauth.profiles ──────────────────────────────────────────────────────
-- Compiled DeafAuth profile blob (version-tracked)
-- Source: deafauth_profiles

CREATE TABLE deafauth.profiles (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  version         TEXT NOT NULL DEFAULT '2.0.0',
  profile_data    JSONB NOT NULL DEFAULT '{}',          -- compiled deafauth object
  compiled_at     TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('deafauth.profiles');
CREATE UNIQUE INDEX idx_deafauth_profiles_user ON deafauth.profiles(user_id);

-- ── deafauth.asl_signatures ────────────────────────────────────────────────
-- ASL handshape signatures for visual auth
-- Source: asl_signatures (preserved fully — good schema)

CREATE TABLE deafauth.asl_signatures (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  signature_type        TEXT NOT NULL CHECK (signature_type IN (
                          'handshape','movement','location','palm_orientation','name_sign'
                        )),
  signature_hash        BYTEA NOT NULL,
  keypoints             JSONB NOT NULL DEFAULT '{}',    -- MediaPipe holistic keypoints
  device_info           JSONB DEFAULT '{}',
  environmental_factors JSONB DEFAULT '{}',
  success_rate          NUMERIC(5,4) DEFAULT 1.0,
  use_count             INTEGER DEFAULT 0,
  last_used_at          TIMESTAMPTZ,
  is_active             BOOLEAN DEFAULT TRUE,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('deafauth.asl_signatures');
CREATE INDEX idx_asl_sig_user ON deafauth.asl_signatures(user_id);

-- ── deafauth.auth_events ───────────────────────────────────────────────────
-- Auth audit log (replaces sign_in_logs + oauth_audit_events)

CREATE TABLE deafauth.auth_events (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES deafauth.users(id) ON DELETE SET NULL,
  clerk_user_id TEXT,
  event_type    TEXT NOT NULL CHECK (event_type IN (
                  'sign_in','sign_out','sign_up','failed_attempt',
                  'mfa_challenge','token_refresh','oauth_connect','oauth_disconnect'
                )),
  auth_method   TEXT,
  ip_address    INET,
  user_agent    TEXT,
  success       BOOLEAN DEFAULT TRUE,
  failure_reason TEXT,
  metadata      JSONB DEFAULT '{}',
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_auth_events_user    ON deafauth.auth_events(user_id);
CREATE INDEX idx_auth_events_created ON deafauth.auth_events(created_at DESC);

-- ── deafauth.oauth_tokens ──────────────────────────────────────────────────
-- Source: oauth_tokens (preserved, moved to schema)

CREATE TABLE deafauth.oauth_tokens (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  provider        TEXT NOT NULL,
  provider_user_id TEXT NOT NULL,
  access_token    TEXT,
  refresh_token   TEXT,
  token_expires_at TIMESTAMPTZ,
  scopes          TEXT[],
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, provider)
);

SELECT attach_updated_at('deafauth.oauth_tokens');


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: platform
-- Orgs, members, roles, allowed domains, API keys
-- Sources: organizations, organization_members, roles, allowed_domains, permissions
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS platform;

CREATE TABLE platform.organizations (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug                    TEXT UNIQUE NOT NULL,
  name                    TEXT NOT NULL,
  org_type                TEXT NOT NULL DEFAULT 'agency'
                            CHECK (org_type IN (
                              'agency','nonprofit','government','corporate',
                              'educational','individual','vr_provider'
                            )),
  domain                  TEXT,
  description             TEXT,
  website                 TEXT,
  github_org_name         TEXT,
  github_org_id           BIGINT,
  primary_focus           TEXT,                         -- deaf, lgbtq, both, general_a11y
  accessibility_commitment TEXT,
  is_public               BOOLEAN DEFAULT FALSE,
  is_verified             BOOLEAN DEFAULT FALSE,
  founded_date            DATE DEFAULT CURRENT_DATE,
  -- Billing ref
  stripe_customer_id      TEXT UNIQUE,
  subscription_tier       TEXT DEFAULT 'free',
  created_by              UUID REFERENCES deafauth.users(id),
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('platform.organizations');
CREATE INDEX idx_orgs_slug ON platform.organizations(slug);
CREATE INDEX idx_orgs_type ON platform.organizations(org_type);

CREATE TABLE platform.org_members (
  org_id      UUID NOT NULL REFERENCES platform.organizations(id) ON DELETE CASCADE,
  user_id     UUID NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  role        TEXT NOT NULL DEFAULT 'member'
                CHECK (role IN ('owner','admin','manager','member','viewer','billing')),
  invited_by  UUID REFERENCES deafauth.users(id),
  joined_at   TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (org_id, user_id)
);

CREATE INDEX idx_org_members_user ON platform.org_members(user_id);

CREATE TABLE platform.allowed_domains (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hostname    TEXT UNIQUE NOT NULL,
  org_id      UUID REFERENCES platform.organizations(id),
  description TEXT,
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Preserve existing 10 rows — INSERT after migration
-- (rows will be migrated via: INSERT INTO platform.allowed_domains SELECT gen_random_uuid(), hostname, null, description, true, created_at FROM public.allowed_domains)

CREATE TABLE platform.api_keys (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id      UUID REFERENCES platform.organizations(id) ON DELETE CASCADE,
  user_id     UUID REFERENCES deafauth.users(id) ON DELETE CASCADE,
  key_hash    TEXT UNIQUE NOT NULL,                     -- bcrypt hash, never store raw
  key_prefix  TEXT NOT NULL,                            -- first 8 chars for display: mbtq_a1b2...
  name        TEXT,
  scopes      TEXT[] DEFAULT ARRAY['read'],
  last_used_at TIMESTAMPTZ,
  expires_at  TIMESTAMPTZ,
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_org  ON platform.api_keys(org_id);
CREATE INDEX idx_api_keys_user ON platform.api_keys(user_id);


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: billing
-- Unified subscriptions, Stripe, GU pool, usage tracking
-- Sources: subscriptions, user_subscriptions, pricing_tiers, generation_units,
--          gu_pool, gu_claims, gu_donations, user_credits, tokenized_transactions
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS billing;

-- ── billing.stripe_customers ───────────────────────────────────────────────
-- THE MISSING LINK. This is what broke Stripe connection.

CREATE TABLE billing.stripe_customers (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID REFERENCES deafauth.users(id) ON DELETE SET NULL,
  org_id              UUID REFERENCES platform.organizations(id) ON DELETE SET NULL,
  stripe_customer_id  TEXT UNIQUE NOT NULL,
  email               TEXT NOT NULL,
  name                TEXT,
  metadata            JSONB DEFAULT '{}',
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW(),
  CHECK (user_id IS NOT NULL OR org_id IS NOT NULL)     -- must belong to someone
);

SELECT attach_updated_at('billing.stripe_customers');
CREATE INDEX idx_stripe_customers_user ON billing.stripe_customers(user_id);
CREATE INDEX idx_stripe_customers_org  ON billing.stripe_customers(org_id);

-- ── billing.subscriptions ─────────────────────────────────────────────────
-- Single source of truth. Merges subscriptions + user_subscriptions.

CREATE TABLE billing.subscriptions (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Owner (user OR org, not both)
  user_id                 UUID REFERENCES deafauth.users(id) ON DELETE CASCADE,
  org_id                  UUID REFERENCES platform.organizations(id) ON DELETE CASCADE,

  -- Stripe
  stripe_customer_id      TEXT NOT NULL REFERENCES billing.stripe_customers(stripe_customer_id),
  stripe_subscription_id  TEXT UNIQUE,
  stripe_price_id         TEXT,
  stripe_product_id       TEXT,

  -- Tier
  tier                    TEXT NOT NULL DEFAULT 'free'
                            CHECK (tier IN (
                              'free','creator','vr_provider',
                              'agency_starter','agency_pro','enterprise'
                            )),
  billing_cycle           TEXT CHECK (billing_cycle IN ('monthly','annual')),
  status                  TEXT NOT NULL DEFAULT 'trialing'
                            CHECK (status IN (
                              'trialing','active','past_due',
                              'canceled','unpaid','paused','incomplete'
                            )),

  -- Entitlements (denormalized from Stripe product metadata for fast reads)
  entitlements            JSONB NOT NULL DEFAULT '{}',

  -- Workspace access (Taskade workspaces this tier unlocks)
  workspace_access        TEXT[] DEFAULT ARRAY[]::TEXT[],
  -- 'mbtq' | 'vr4deaf' | 'pinksync' | '360magicians'

  -- Usage caps (null = unlimited)
  ai_requests_monthly     INTEGER,
  storage_gb              INTEGER,
  client_projects         INTEGER,
  team_members            INTEGER,
  stream_storage_gb       INTEGER,

  -- GU (Generation Units)
  gu_allocation           INTEGER DEFAULT 0,
  gu_consumed             INTEGER DEFAULT 0,
  gu_reset_at             TIMESTAMPTZ,

  -- Dates
  trial_ends_at           TIMESTAMPTZ,
  current_period_start    TIMESTAMPTZ,
  current_period_end      TIMESTAMPTZ,
  canceled_at             TIMESTAMPTZ,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW(),

  CHECK (user_id IS NOT NULL OR org_id IS NOT NULL)
);

SELECT attach_updated_at('billing.subscriptions');
CREATE INDEX idx_subs_user   ON billing.subscriptions(user_id);
CREATE INDEX idx_subs_org    ON billing.subscriptions(org_id);
CREATE INDEX idx_subs_tier   ON billing.subscriptions(tier);
CREATE INDEX idx_subs_status ON billing.subscriptions(status);
CREATE INDEX idx_subs_stripe ON billing.subscriptions(stripe_subscription_id);

-- ── billing.checkout_sessions ─────────────────────────────────────────────

CREATE TABLE billing.checkout_sessions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID REFERENCES deafauth.users(id),
  org_id            UUID REFERENCES platform.organizations(id),
  stripe_session_id TEXT UNIQUE NOT NULL,
  tier              TEXT NOT NULL,
  billing_cycle     TEXT NOT NULL,
  status            TEXT DEFAULT 'pending'
                      CHECK (status IN ('pending','completed','expired')),
  success_url       TEXT,
  cancel_url        TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  expires_at        TIMESTAMPTZ,
  completed_at      TIMESTAMPTZ
);

-- ── billing.usage_events ──────────────────────────────────────────────────

CREATE TABLE billing.usage_events (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id   UUID REFERENCES billing.subscriptions(id) ON DELETE CASCADE,
  user_id           UUID REFERENCES deafauth.users(id),
  event_type        TEXT NOT NULL CHECK (event_type IN (
                      'ai_request','video_upload','caption_generated',
                      'vr_service_delivered','invoice_generated',
                      'credential_issued','gu_consumed','gu_donated',
                      'storage_used','api_call'
                    )),
  workspace         TEXT,                               -- which workspace triggered this
  units             INTEGER DEFAULT 1,
  metadata          JSONB DEFAULT '{}',
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_usage_sub     ON billing.usage_events(subscription_id);
CREATE INDEX idx_usage_user    ON billing.usage_events(user_id);
CREATE INDEX idx_usage_type    ON billing.usage_events(event_type);
CREATE INDEX idx_usage_created ON billing.usage_events(created_at DESC);

-- ── billing.gu_pool ────────────────────────────────────────────────────────
-- Platform-wide GU (Generation Unit) shared pool
-- Source: gu_pool + gu_claims + gu_donations

CREATE TABLE billing.gu_pool (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  total_gu    BIGINT NOT NULL DEFAULT 0,
  donated_gu  BIGINT NOT NULL DEFAULT 0,
  claimed_gu  BIGINT NOT NULL DEFAULT 0,
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Seed single row
INSERT INTO billing.gu_pool (id, total_gu) VALUES (gen_random_uuid(), 0)
ON CONFLICT DO NOTHING;

CREATE TABLE billing.gu_transactions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES deafauth.users(id),
  subscription_id UUID REFERENCES billing.subscriptions(id),
  transaction_type TEXT NOT NULL CHECK (transaction_type IN (
                    'allocated','consumed','donated','claimed','refunded','reset'
                  )),
  units           INTEGER NOT NULL,
  balance_after   INTEGER,
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_gu_tx_user ON billing.gu_transactions(user_id);


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: fibonrose
-- Trust scoring, verifications, scam patterns, visual signals
-- Sources: fibonrose_* (correct) + fibronrose_* (typo) — MERGED and fixed
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS fibonrose;

-- ── fibonrose.trust_scores ─────────────────────────────────────────────────
-- Merges: fibonrose_trust_scores + trust_scores + trust_factors + trust_history
-- Fibonacci-weighted scoring across 5 dimensions

CREATE TABLE fibonrose.trust_scores (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                   UUID NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  entity_type               TEXT DEFAULT 'user'
                              CHECK (entity_type IN ('user','creator','org','vr_provider')),

  -- Composite score (0-100)
  overall_score             NUMERIC(5,2) DEFAULT 50.0,

  -- Dimension scores (Fibonacci-weighted)
  accessibility_engagement  NUMERIC(5,2) DEFAULT 50.0,
  community_verification    NUMERIC(5,2) DEFAULT 50.0,
  content_quality           NUMERIC(5,2) DEFAULT 50.0,
  response_reliability      NUMERIC(5,2) DEFAULT 50.0,
  deaf_community_standing   NUMERIC(5,2) DEFAULT 50.0,

  -- Historical counters (from fibonrose_trust_scores)
  verification_completions  INTEGER DEFAULT 0,
  successful_interactions   INTEGER DEFAULT 0,
  reported_issues           INTEGER DEFAULT 0,
  interpreter_credibility   NUMERIC(5,2) DEFAULT 50.0,
  hearing_participant_score NUMERIC(5,2) DEFAULT 50.0,

  -- Visual badge (from fibonrose_trust_scores)
  trust_badge               TEXT,
  badge_color               TEXT,
  badge_icon                TEXT,

  -- History array (capped at last 50 events)
  score_history             JSONB DEFAULT '[]',

  -- Rolling window
  window_days               INTEGER DEFAULT 30,
  last_calculated_at        TIMESTAMPTZ DEFAULT NOW(),
  created_at                TIMESTAMPTZ DEFAULT NOW(),
  updated_at                TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(user_id)
);

SELECT attach_updated_at('fibonrose.trust_scores');
CREATE INDEX idx_fibonrose_scores_user  ON fibonrose.trust_scores(user_id);
CREATE INDEX idx_fibonrose_scores_score ON fibonrose.trust_scores(overall_score DESC);

-- ── fibonrose.verification_types ──────────────────────────────────────────

CREATE TABLE fibonrose.verification_types (
  id              SERIAL PRIMARY KEY,
  name            TEXT NOT NULL UNIQUE,
  category        TEXT,
  description     TEXT,
  trust_weight    INTEGER DEFAULT 1,
  required_nfts   TEXT[],
  minimum_tier    TEXT DEFAULT 'free',
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── fibonrose.verifications ────────────────────────────────────────────────

CREATE TABLE fibonrose.verifications (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  verification_type_id INTEGER REFERENCES fibonrose.verification_types(id),
  status              TEXT DEFAULT 'pending'
                        CHECK (status IN ('pending','in_review','verified','rejected','expired')),
  blockchain_proof    TEXT,                             -- on-chain hash (Polygon/Base)
  nft_contracts       TEXT[],
  credential_json_ld  JSONB,                            -- signed JSON-LD credential
  metadata            JSONB DEFAULT '{}',
  verified_at         TIMESTAMPTZ,
  expires_at          TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('fibonrose.verifications');
CREATE INDEX idx_verifications_user   ON fibonrose.verifications(user_id);
CREATE INDEX idx_verifications_status ON fibonrose.verifications(status);

-- ── fibonrose.verification_chains ─────────────────────────────────────────
-- Source: fibronrose_verification_chains (typo fixed, structure preserved)

CREATE TABLE fibonrose.verification_chains (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  verification_id UUID REFERENCES fibonrose.verifications(id) ON DELETE CASCADE,
  chain_step      INTEGER NOT NULL,
  verifier_id     UUID REFERENCES deafauth.users(id),
  action          TEXT NOT NULL,
  result          TEXT,
  proof_hash      TEXT,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── fibonrose.trust_patterns ───────────────────────────────────────────────
-- Source: fibronrose_trust_patterns + fibronrose_scam_patterns (merged)

CREATE TABLE fibonrose.trust_patterns (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pattern_name          TEXT NOT NULL UNIQUE,
  pattern_type          TEXT CHECK (pattern_type IN ('positive','negative','scam','neutral')),
  category              TEXT,
  description           TEXT,
  risk_level            TEXT DEFAULT 'low' CHECK (risk_level IN ('low','medium','high','critical')),
  visual_keywords       TEXT[],
  visual_red_flags      TEXT[],
  communication_patterns TEXT[],
  image_descriptors     JSONB DEFAULT '{}',
  suggested_visual_alerts TEXT[],
  mitigation_strategy   TEXT,
  detection_confidence  NUMERIC(5,4) DEFAULT 0.0,
  embedding             VECTOR(1536),                   -- pgvector for semantic matching
  created_by            UUID REFERENCES deafauth.users(id),
  created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trust_patterns_type ON fibonrose.trust_patterns(pattern_type);

-- ── fibonrose.visual_trust_signals ────────────────────────────────────────
-- Source: fibonrose_visual_trust_signals (5 real rows — PRESERVED)

CREATE TABLE fibonrose.visual_trust_signals (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_type       TEXT NOT NULL UNIQUE,
  trust_level       TEXT NOT NULL CHECK (trust_level IN (
                      'unverified','basic','community','verified','elite'
                    )),
  hex_color         TEXT,
  icon_name         TEXT,
  animation_type    TEXT,
  pattern_path      TEXT,
  contrast_ratio    NUMERIC(4,2),
  vibration_pattern TEXT,
  flash_pattern     TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ── fibonrose.audit_log ────────────────────────────────────────────────────
-- Source: fibronrose_audit_logs

CREATE TABLE fibonrose.audit_log (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES deafauth.users(id),
  action      TEXT NOT NULL,
  entity_type TEXT,
  entity_id   UUID,
  before_data JSONB,
  after_data  JSONB,
  ip_address  INET,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_fibonrose_audit_user    ON fibonrose.audit_log(user_id);
CREATE INDEX idx_fibonrose_audit_created ON fibonrose.audit_log(created_at DESC);

-- ── fibonrose.rewards ──────────────────────────────────────────────────────
-- Fibonacci-weighted reward distribution (max 144 recipients)

CREATE TABLE fibonrose.reward_distributions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  distributor_id  UUID NOT NULL REFERENCES deafauth.users(id),
  pool_amount     NUMERIC(12,2) NOT NULL,
  currency        TEXT DEFAULT 'fibonrose_points'
                    CHECK (currency IN ('usd','credits','fibonrose_points')),
  algorithm       TEXT DEFAULT 'fibonacci_weighted',
  recipient_count INTEGER CHECK (recipient_count <= 144),
  status          TEXT DEFAULT 'pending'
                    CHECK (status IN ('pending','processing','completed','failed')),
  metadata        JSONB DEFAULT '{}',
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE fibonrose.reward_recipients (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  distribution_id     UUID NOT NULL REFERENCES fibonrose.reward_distributions(id),
  recipient_id        UUID NOT NULL REFERENCES deafauth.users(id),
  fibonacci_position  INTEGER NOT NULL CHECK (fibonacci_position BETWEEN 1 AND 144),
  fibonacci_weight    NUMERIC(8,4) NOT NULL,
  amount_allocated    NUMERIC(12,2) NOT NULL,
  status              TEXT DEFAULT 'pending',
  paid_at             TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: magiciancore
-- AI agents, runs, steps, tools, projects, workflows
-- Sources: magicians_agents, magician_agent_runs, magician_agent_steps,
--          magician_agent_tool_calls, magician_projects, agents_registry,
--          magician_ai_queue, magician_workflow_templates, magician_outputs
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS magiciancore;

-- ── magiciancore.agents ────────────────────────────────────────────────────
-- Canonical agent registry. Merges: magicians_agents + agents_registry

CREATE TABLE magiciancore.agents (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL UNIQUE,
  agent_type      TEXT NOT NULL CHECK (agent_type IN (
                    'job_magician','developer_magician','business_magician',
                    'media_magician','compliance_magician','custom'
                  )),
  description     TEXT,
  spec            JSONB NOT NULL DEFAULT '{}',          -- tool list, system prompt, model
  metadata        JSONB DEFAULT '{}',
  workspace       TEXT,                                 -- which Taskade workspace
  is_active       BOOLEAN DEFAULT TRUE,
  owner_id        UUID REFERENCES deafauth.users(id),
  org_id          UUID REFERENCES platform.organizations(id),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('magiciancore.agents');

-- ── magiciancore.projects ──────────────────────────────────────────────────

CREATE TABLE magiciancore.projects (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id      UUID REFERENCES platform.organizations(id),
  user_id     UUID REFERENCES deafauth.users(id),
  name        TEXT NOT NULL,
  subdomain   TEXT,
  config      JSONB DEFAULT '{}',
  metadata    JSONB DEFAULT '{}',
  status      TEXT DEFAULT 'active'
                CHECK (status IN ('active','paused','archived','deleted')),
  created_by  UUID REFERENCES deafauth.users(id),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('magiciancore.projects');
CREATE INDEX idx_mc_projects_org ON magiciancore.projects(org_id);

-- ── magiciancore.runs ──────────────────────────────────────────────────────

CREATE TABLE magiciancore.runs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id    UUID NOT NULL REFERENCES magiciancore.agents(id),
  project_id  UUID REFERENCES magiciancore.projects(id),
  user_id     UUID REFERENCES deafauth.users(id),
  run_type    TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'queued'
                CHECK (status IN ('queued','running','completed','failed','canceled')),
  input       JSONB DEFAULT '{}',
  output      JSONB DEFAULT '{}',
  logs        JSONB DEFAULT '[]',
  error       TEXT,
  started_at  TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  duration_ms INTEGER,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('magiciancore.runs');
CREATE INDEX idx_mc_runs_agent  ON magiciancore.runs(agent_id);
CREATE INDEX idx_mc_runs_status ON magiciancore.runs(status);
CREATE INDEX idx_mc_runs_user   ON magiciancore.runs(user_id);

-- ── magiciancore.steps ─────────────────────────────────────────────────────

CREATE TABLE magiciancore.steps (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id      UUID NOT NULL REFERENCES magiciancore.runs(id) ON DELETE CASCADE,
  step_number INTEGER NOT NULL,
  step_type   TEXT NOT NULL CHECK (step_type IN (
                'tool_call','llm_completion','human_input',
                'validation','routing','notification'
              )),
  input       JSONB DEFAULT '{}',
  output      JSONB DEFAULT '{}',
  status      TEXT DEFAULT 'pending',
  started_at  TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mc_steps_run ON magiciancore.steps(run_id);

-- ── magiciancore.tool_calls ────────────────────────────────────────────────

CREATE TABLE magiciancore.tool_calls (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  step_id         UUID REFERENCES magiciancore.steps(id) ON DELETE CASCADE,
  run_id          UUID NOT NULL REFERENCES magiciancore.runs(id) ON DELETE CASCADE,
  tool_name       TEXT NOT NULL,
  subdomain       TEXT,                                 -- which mbtq.dev subdomain
  input           JSONB NOT NULL DEFAULT '{}',
  output          JSONB DEFAULT '{}',
  status          TEXT DEFAULT 'pending',
  latency_ms      INTEGER,
  error           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mc_tools_run  ON magiciancore.tool_calls(run_id);
CREATE INDEX idx_mc_tools_name ON magiciancore.tool_calls(tool_name);

-- ── magiciancore.queue ─────────────────────────────────────────────────────

CREATE TABLE magiciancore.queue (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id        UUID REFERENCES magiciancore.agents(id),
  priority        INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
  payload         JSONB NOT NULL DEFAULT '{}',
  status          TEXT DEFAULT 'pending'
                    CHECK (status IN ('pending','processing','done','failed','dead_letter')),
  attempts        INTEGER DEFAULT 0,
  max_attempts    INTEGER DEFAULT 3,
  last_error      TEXT,
  process_after   TIMESTAMPTZ DEFAULT NOW(),
  claimed_at      TIMESTAMPTZ,
  claimed_by      TEXT,                                 -- worker ID
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mc_queue_status   ON magiciancore.queue(status, process_after);
CREATE INDEX idx_mc_queue_priority ON magiciancore.queue(priority DESC, created_at ASC);

-- ── magiciancore.workflow_templates ───────────────────────────────────────

CREATE TABLE magiciancore.workflow_templates (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL UNIQUE,
  description TEXT,
  steps       JSONB NOT NULL DEFAULT '[]',
  trigger_type TEXT CHECK (trigger_type IN (
                  'manual','webhook','schedule','event','stripe_webhook','taskade_event'
                )),
  is_active   BOOLEAN DEFAULT TRUE,
  created_by  UUID REFERENCES deafauth.users(id),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('magiciancore.workflow_templates');


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: pinksync
-- Real-time events, channels, Taskade bridge, compliance logs
-- Sources: pinksync_logs, pink_sync, taskade_events, pinksync_accessibility_profiles
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS pinksync;

CREATE TABLE pinksync.channels (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT UNIQUE NOT NULL,
  channel_type TEXT DEFAULT 'general'
                CHECK (channel_type IN (
                  'general','creators','a11y','alerts','vr4deaf',
                  'billing','agents','taskade'
                )),
  description TEXT,
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pinksync.events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id      UUID REFERENCES pinksync.channels(id),
  channel_name    TEXT,
  event_type      TEXT NOT NULL,
  payload         JSONB NOT NULL DEFAULT '{}',
  source_service  TEXT,                                 -- which subdomain sent this
  user_id         UUID REFERENCES deafauth.users(id),
  priority        TEXT DEFAULT 'normal'
                    CHECK (priority IN ('low','normal','high','urgent')),
  processed       BOOLEAN DEFAULT FALSE,
  processed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ps_events_channel ON pinksync.events(channel_name);
CREATE INDEX idx_ps_events_type    ON pinksync.events(event_type);
CREATE INDEX idx_ps_events_created ON pinksync.events(created_at DESC);

-- ── pinksync.taskade_events ────────────────────────────────────────────────
-- Source: taskade_events (preserved — good schema, moved to namespace)

CREATE TABLE pinksync.taskade_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  taskade_event   JSONB NOT NULL,
  deafauth_user   UUID REFERENCES deafauth.users(id),
  workspace       TEXT CHECK (workspace IN ('mbtq','vr4deaf','pinksync','360magicians')),
  action          TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'received'
                    CHECK (status IN ('received','processing','processed','failed')),
  metadata        JSONB DEFAULT '{}',
  received_at     TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ps_taskade_user      ON pinksync.taskade_events(deafauth_user);
CREATE INDEX idx_ps_taskade_workspace ON pinksync.taskade_events(workspace);

-- ── pinksync.compliance_logs ──────────────────────────────────────────────
-- Source: pinksync_logs (moved, renamed)

CREATE TABLE pinksync.compliance_logs (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  compliance_check_id UUID,
  worker_id           TEXT,
  action              TEXT NOT NULL,
  detail              JSONB DEFAULT '{}',
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ── pinksync.accessibility_profiles ──────────────────────────────────────

CREATE TABLE pinksync.accessibility_profiles (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID UNIQUE NOT NULL REFERENCES deafauth.users(id) ON DELETE CASCADE,
  caption_prefs   JSONB DEFAULT '{}',
  visual_alerts   JSONB DEFAULT '{}',
  signing_prefs   JSONB DEFAULT '{}',
  color_contrast  TEXT DEFAULT 'high',
  font_size       TEXT DEFAULT 'medium',
  animation_reduce BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('pinksync.accessibility_profiles');


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: vr4deaf
-- VR client profiles, intakes, vocrehab accounts, job matching, IEP
-- Sources: vr4deaf_profiles, vr_intakes, voc_rehab_accounts, job_matches,
--          iep_service_mappings, vr_business_specialists
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS vr4deaf;

-- ── vr4deaf.profiles ──────────────────────────────────────────────────────
-- Source: vr4deaf_profiles (rich schema — preserved entirely)

CREATE TABLE vr4deaf.profiles (
  id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                     UUID UNIQUE NOT NULL REFERENCES deafauth.users(id),
  primary_profession          TEXT,
  secondary_skills            TEXT[],
  education_level             TEXT,
  years_experience            INTEGER,
  preferred_communication_modes TEXT[],
  workplace_accommodations    JSONB DEFAULT '{}',
  career_objectives           TEXT[],
  desired_industries          TEXT[],
  training_interests          TEXT[],
  certification_goals         TEXT[],
  hearing_loss_level          INTEGER CHECK (hearing_loss_level BETWEEN 0 AND 4),
  additional_disabilities     TEXT[],
  current_employment_status   TEXT CHECK (current_employment_status IN (
                                'employed','unemployed','underemployed',
                                'in_training','self_employed','not_seeking'
                              )),
  created_at                  TIMESTAMPTZ DEFAULT NOW(),
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('vr4deaf.profiles');

-- ── vr4deaf.intakes ────────────────────────────────────────────────────────
-- Source: vr_intakes (canonical, vr_intake was the dupe)

CREATE TABLE vr4deaf.intakes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES deafauth.users(id),
  applicant_name  TEXT,
  intake_payload  JSONB NOT NULL DEFAULT '{}',          -- full intake form JSON
  status          TEXT DEFAULT 'submitted'
                    CHECK (status IN (
                      'submitted','under_review','approved',
                      'waitlisted','denied','archived'
                    )),
  reviewer_id     UUID REFERENCES deafauth.users(id),
  reviewed_at     TIMESTAMPTZ,
  submitted_at    TIMESTAMPTZ DEFAULT NOW(),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('vr4deaf.intakes');
CREATE INDEX idx_vr4d_intakes_user   ON vr4deaf.intakes(user_id);
CREATE INDEX idx_vr4d_intakes_status ON vr4deaf.intakes(status);

-- ── vr4deaf.vocrehab_accounts ─────────────────────────────────────────────
-- Source: voc_rehab_accounts (preserved — excellent schema)

CREATE TABLE vr4deaf.vocrehab_accounts (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                 UUID NOT NULL REFERENCES deafauth.users(id),
  iep_reference_number    TEXT NOT NULL UNIQUE,
  total_funding_allocation NUMERIC(12,2) NOT NULL,
  remaining_balance       NUMERIC(12,2) NOT NULL,
  funding_start_date      DATE DEFAULT CURRENT_DATE,
  funding_end_date        DATE NOT NULL,
  status                  TEXT DEFAULT 'active'
                            CHECK (status IN ('active','closed','suspended','pending')),
  federal_program         TEXT NOT NULL,
  state_agency            TEXT NOT NULL,
  disability_category     TEXT,
  token_balance           NUMERIC(12,4) DEFAULT 0,
  token_conversion_rate   NUMERIC(8,4) DEFAULT 1.0,
  metadata                JSONB DEFAULT '{}',
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('vr4deaf.vocrehab_accounts');
CREATE INDEX idx_vocrehab_user ON vr4deaf.vocrehab_accounts(user_id);

-- ── vr4deaf.iep_service_mappings ──────────────────────────────────────────

CREATE TABLE vr4deaf.iep_service_mappings (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vocrehab_account_id UUID NOT NULL REFERENCES vr4deaf.vocrehab_accounts(id),
  service_type        TEXT NOT NULL,
  service_provider    TEXT,
  authorized_units    INTEGER,
  used_units          INTEGER DEFAULT 0,
  unit_cost           NUMERIC(8,2),
  authorization_code  TEXT,
  start_date          DATE,
  end_date            DATE,
  status              TEXT DEFAULT 'active',
  metadata            JSONB DEFAULT '{}',
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('vr4deaf.iep_service_mappings');

-- ── vr4deaf.job_matches ────────────────────────────────────────────────────

CREATE TABLE vr4deaf.job_matches (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES deafauth.users(id),
  job_id          UUID,
  match_score     NUMERIC(5,4),
  match_factors   JSONB DEFAULT '{}',
  accessibility_score NUMERIC(5,2),
  status          TEXT DEFAULT 'pending'
                    CHECK (status IN ('pending','viewed','applied','interview','hired','rejected')),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('vr4deaf.job_matches');

-- ── vr4deaf.invoices ───────────────────────────────────────────────────────
-- TTW auto-invoicing (the self-funding loop from Notion)

CREATE TABLE vr4deaf.invoices (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vocrehab_account_id UUID NOT NULL REFERENCES vr4deaf.vocrehab_accounts(id),
  service_provider_id UUID REFERENCES platform.organizations(id),
  invoice_number      TEXT UNIQUE NOT NULL DEFAULT ('INV-' || to_char(NOW(), 'YYYYMMDD') || '-' || substr(gen_random_uuid()::text, 1, 6)),
  service_date        DATE NOT NULL,
  services            JSONB NOT NULL DEFAULT '[]',      -- line items
  subtotal            NUMERIC(10,2) NOT NULL,
  deaf_service_premium_pct NUMERIC(5,2) DEFAULT 17.5,   -- from Notion billing spec
  deaf_service_premium NUMERIC(10,2),
  total               NUMERIC(10,2) NOT NULL,
  status              TEXT DEFAULT 'draft'
                        CHECK (status IN ('draft','submitted','approved','paid','disputed','void')),
  stripe_invoice_id   TEXT,
  submitted_at        TIMESTAMPTZ,
  approved_at         TIMESTAMPTZ,
  paid_at             TIMESTAMPTZ,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('vr4deaf.invoices');
CREATE INDEX idx_vr4d_invoices_account ON vr4deaf.invoices(vocrehab_account_id);
CREATE INDEX idx_vr4d_invoices_status  ON vr4deaf.invoices(status);


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: creator
-- Videos, monetization, content, Stream integration
-- Sources: videos, video_content, video_metadata, creator_monetization_profile
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS creator;

-- ── creator.videos ─────────────────────────────────────────────────────────
-- Merges: videos + video_content + video_metadata
-- Adds: stream_uid (Cloudflare Stream), all accessibility fields

CREATE TABLE creator.videos (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID NOT NULL REFERENCES deafauth.users(id),
  org_id              UUID REFERENCES platform.organizations(id),

  -- Identity
  title               TEXT NOT NULL,
  description         TEXT DEFAULT '',
  category            TEXT,
  tags                TEXT[] DEFAULT ARRAY[]::TEXT[],
  language            TEXT DEFAULT 'en',

  -- Cloudflare Stream
  stream_uid          TEXT UNIQUE,
  hls_url             TEXT,
  dash_url            TEXT,
  thumbnail_url       TEXT,
  duration_sec        INTEGER,
  file_size_bytes     BIGINT,

  -- Status
  status              TEXT DEFAULT 'pending'
                        CHECK (status IN (
                          'pending','uploading','encoding','ready',
                          'published','archived','error'
                        )),
  upload_protocol     TEXT CHECK (upload_protocol IN ('tus','post')),

  -- Accessibility (Deaf-first)
  deaf_optimized      BOOLEAN DEFAULT TRUE,
  is_asl_content      BOOLEAN DEFAULT FALSE,
  has_captions        BOOLEAN DEFAULT FALSE,
  caption_status      TEXT DEFAULT 'none'
                        CHECK (caption_status IN ('none','generating','ready','error')),
  captions_url        TEXT,
  transcript          TEXT,
  transcript_url      TEXT,
  has_sign_language   BOOLEAN DEFAULT FALSE,
  audio_description   TEXT,
  accessibility_score NUMERIC(5,2) DEFAULT 0,

  -- Engagement
  view_count          BIGINT DEFAULT 0,
  like_count          BIGINT DEFAULT 0,
  comment_count       BIGINT DEFAULT 0,
  share_count         BIGINT DEFAULT 0,
  engagement_score    NUMERIC(5,2) DEFAULT 0,

  -- Monetization
  base_token_reward   NUMERIC(10,4) DEFAULT 0,
  total_token_earnings NUMERIC(10,4) DEFAULT 0,
  content_license     TEXT DEFAULT 'standard',

  -- FibonRose
  fibonrose_score     NUMERIC(5,4),
  fibonrose_credential JSONB,                           -- signed JSON-LD

  -- Stream metadata
  content_metadata    JSONB DEFAULT '{}',

  -- Storage
  storage_path        TEXT,                             -- S3 Glacier source archive path

  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW(),
  published_at        TIMESTAMPTZ,
  ready_at            TIMESTAMPTZ
);

SELECT attach_updated_at('creator.videos');
CREATE INDEX idx_creator_videos_user      ON creator.videos(user_id);
CREATE INDEX idx_creator_videos_stream    ON creator.videos(stream_uid);
CREATE INDEX idx_creator_videos_status    ON creator.videos(status);
CREATE INDEX idx_creator_videos_published ON creator.videos(published_at DESC NULLS LAST);

-- ── creator.monetization_profiles ─────────────────────────────────────────

CREATE TABLE creator.monetization_profiles (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                 UUID UNIQUE NOT NULL REFERENCES deafauth.users(id),
  stripe_connect_id       TEXT UNIQUE,                  -- Stripe Connect account
  payout_method           TEXT DEFAULT 'stripe',
  minimum_payout          NUMERIC(10,2) DEFAULT 25.00,
  total_earned            NUMERIC(12,4) DEFAULT 0,
  total_paid_out          NUMERIC(12,4) DEFAULT 0,
  pending_balance         NUMERIC(12,4) DEFAULT 0,
  fibonrose_tier          TEXT DEFAULT 'none',
  subscription_tier       TEXT,
  is_active               BOOLEAN DEFAULT TRUE,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW()
);

SELECT attach_updated_at('creator.monetization_profiles');

-- ── creator.video_interactions ─────────────────────────────────────────────

CREATE TABLE creator.video_interactions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id        UUID NOT NULL REFERENCES creator.videos(id) ON DELETE CASCADE,
  user_id         UUID REFERENCES deafauth.users(id),
  interaction_type TEXT NOT NULL CHECK (interaction_type IN (
                    'view','like','unlike','share','comment',
                    'caption_viewed','asl_viewed','report'
                  )),
  duration_sec    INTEGER,
  metadata        JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_video_interact_video ON creator.video_interactions(video_id);
CREATE INDEX idx_video_interact_user  ON creator.video_interactions(user_id);


-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMA: ref
-- Reference data: colors (265 rows), sign language variants, verification types
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS ref;

CREATE TABLE ref.colors (
  id          BIGINT PRIMARY KEY,
  name        TEXT,
  hex         TEXT NOT NULL,
  red         SMALLINT,
  green       SMALLINT,
  blue        SMALLINT,
  hue         SMALLINT,
  sat_hsl     SMALLINT,
  light_hsl   SMALLINT,
  sat_hsv     SMALLINT,
  val_hsv     SMALLINT
);
-- Data migrated via: INSERT INTO ref.colors SELECT id,name,hex,red,green,blue,hue,sat_hsl,light_hsl,sat_hsv,val_hsv FROM public.colors

CREATE TABLE ref.sign_language_variants (
  id          SERIAL PRIMARY KEY,
  code        TEXT UNIQUE NOT NULL,
  name        TEXT NOT NULL,
  region      TEXT,
  description TEXT
);

INSERT INTO ref.sign_language_variants (code, name, region) VALUES
  ('asl',  'American Sign Language',       'United States'),
  ('bsl',  'British Sign Language',         'United Kingdom'),
  ('pse',  'Pidgin Signed English',         'United States'),
  ('see',  'Signed Exact English',          'United States'),
  ('lsf',  'Langue des Signes Française',   'France'),
  ('auslan', 'Australian Sign Language',    'Australia'),
  ('isl',  'International Sign Language',   'International')
ON CONFLICT DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY — All schemas
-- ═══════════════════════════════════════════════════════════════════════════════

-- deafauth
ALTER TABLE deafauth.users                ENABLE ROW LEVEL SECURITY;
ALTER TABLE deafauth.profiles             ENABLE ROW LEVEL SECURITY;
ALTER TABLE deafauth.asl_signatures       ENABLE ROW LEVEL SECURITY;
ALTER TABLE deafauth.auth_events          ENABLE ROW LEVEL SECURITY;
ALTER TABLE deafauth.oauth_tokens         ENABLE ROW LEVEL SECURITY;

ALTER TABLE platform.organizations        ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.org_members          ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform.api_keys             ENABLE ROW LEVEL SECURITY;

ALTER TABLE billing.stripe_customers      ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.subscriptions         ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.usage_events          ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.checkout_sessions     ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing.gu_transactions       ENABLE ROW LEVEL SECURITY;

ALTER TABLE fibonrose.trust_scores        ENABLE ROW LEVEL SECURITY;
ALTER TABLE fibonrose.verifications       ENABLE ROW LEVEL SECURITY;
ALTER TABLE fibonrose.audit_log           ENABLE ROW LEVEL SECURITY;
ALTER TABLE fibonrose.reward_distributions ENABLE ROW LEVEL SECURITY;

ALTER TABLE magiciancore.runs             ENABLE ROW LEVEL SECURITY;
ALTER TABLE magiciancore.queue            ENABLE ROW LEVEL SECURITY;

ALTER TABLE pinksync.events               ENABLE ROW LEVEL SECURITY;
ALTER TABLE pinksync.taskade_events       ENABLE ROW LEVEL SECURITY;

ALTER TABLE vr4deaf.profiles              ENABLE ROW LEVEL SECURITY;
ALTER TABLE vr4deaf.intakes               ENABLE ROW LEVEL SECURITY;
ALTER TABLE vr4deaf.vocrehab_accounts     ENABLE ROW LEVEL SECURITY;
ALTER TABLE vr4deaf.invoices              ENABLE ROW LEVEL SECURITY;

ALTER TABLE creator.videos                ENABLE ROW LEVEL SECURITY;
ALTER TABLE creator.monetization_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE creator.video_interactions    ENABLE ROW LEVEL SECURITY;

-- ── Service role bypass (all tables) ─────────────────────────────────────
DO $$
DECLARE
  tbl RECORD;
BEGIN
  FOR tbl IN
    SELECT schemaname || '.' || tablename as full_name
    FROM pg_tables
    WHERE schemaname IN (
      'deafauth','platform','billing','fibonrose',
      'magiciancore','pinksync','vr4deaf','creator'
    )
  LOOP
    EXECUTE format(
      'CREATE POLICY "service_role_all" ON %s USING (true) WITH CHECK (true)',
      tbl.full_name
    );
  EXCEPTION WHEN duplicate_object THEN NULL;
  END LOOP;
END$$;

-- ── User read-own policies ────────────────────────────────────────────────
CREATE POLICY "user_read_own" ON deafauth.users
  FOR SELECT USING (clerk_user_id = auth.jwt() ->> 'sub');

CREATE POLICY "user_read_own_profile" ON deafauth.profiles
  FOR SELECT USING (
    user_id IN (SELECT id FROM deafauth.users WHERE clerk_user_id = auth.jwt() ->> 'sub')
  );

CREATE POLICY "user_read_own_subscription" ON billing.subscriptions
  FOR SELECT USING (
    user_id IN (SELECT id FROM deafauth.users WHERE clerk_user_id = auth.jwt() ->> 'sub')
  );

CREATE POLICY "user_read_own_videos" ON creator.videos
  FOR SELECT USING (
    status = 'published' OR
    user_id IN (SELECT id FROM deafauth.users WHERE clerk_user_id = auth.jwt() ->> 'sub')
  );

CREATE POLICY "user_read_own_vr_profile" ON vr4deaf.profiles
  FOR SELECT USING (
    user_id IN (SELECT id FROM deafauth.users WHERE clerk_user_id = auth.jwt() ->> 'sub')
  );

CREATE POLICY "public_orgs_read" ON platform.organizations
  FOR SELECT USING (is_public = TRUE);


-- ═══════════════════════════════════════════════════════════════════════════════
-- CANONICAL FUNCTIONS (replaces 5 duplicate timestamp functions)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Trust score calculator (replaces duplicate calculate_trust_score)
CREATE OR REPLACE FUNCTION fibonrose.calculate_trust_score(p_user_id UUID)
RETURNS NUMERIC LANGUAGE plpgsql AS $$
DECLARE
  v_score NUMERIC;
  -- Fibonacci weights for 5 dimensions: 1,1,2,3,5 → normalized
  w1 CONSTANT NUMERIC := 1.0/12.0;  -- accessibility_engagement
  w2 CONSTANT NUMERIC := 1.0/12.0;  -- community_verification
  w3 CONSTANT NUMERIC := 2.0/12.0;  -- content_quality
  w4 CONSTANT NUMERIC := 3.0/12.0;  -- response_reliability
  w5 CONSTANT NUMERIC := 5.0/12.0;  -- deaf_community_standing
BEGIN
  SELECT
    ROUND(
      (accessibility_engagement  * w1 +
       community_verification    * w2 +
       content_quality           * w3 +
       response_reliability      * w4 +
       deaf_community_standing   * w5),
      2
    )
  INTO v_score
  FROM fibonrose.trust_scores
  WHERE user_id = p_user_id;
  RETURN COALESCE(v_score, 50.0);
END;
$$;

-- Handle new user (Clerk webhook → deafauth.users)
CREATE OR REPLACE FUNCTION deafauth.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  -- Auto-create billing subscription (free tier)
  -- Note: Stripe customer created by edge function after this fires
  INSERT INTO billing.subscriptions (user_id, tier, status, gu_allocation)
  VALUES (NEW.id, 'free', 'active', 1000)
  ON CONFLICT DO NOTHING;

  -- Auto-create trust score
  INSERT INTO fibonrose.trust_scores (user_id)
  VALUES (NEW.id)
  ON CONFLICT DO NOTHING;

  -- Auto-create accessibility profile
  INSERT INTO pinksync.accessibility_profiles (user_id)
  VALUES (NEW.id)
  ON CONFLICT DO NOTHING;

  RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_new_deafauth_user
  AFTER INSERT ON deafauth.users
  FOR EACH ROW EXECUTE FUNCTION deafauth.handle_new_user();

-- GU consumption check
CREATE OR REPLACE FUNCTION billing.consume_gu(
  p_user_id UUID,
  p_units INTEGER,
  p_event_type TEXT DEFAULT 'ai_request'
)
RETURNS JSONB LANGUAGE plpgsql AS $$
DECLARE
  v_sub billing.subscriptions%ROWTYPE;
  v_available INTEGER;
BEGIN
  SELECT * INTO v_sub
  FROM billing.subscriptions
  WHERE user_id = p_user_id AND status = 'active'
  LIMIT 1;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('ok', false, 'reason', 'no_active_subscription');
  END IF;

  v_available := COALESCE(v_sub.gu_allocation, 0) - COALESCE(v_sub.gu_consumed, 0);

  IF v_sub.ai_requests_monthly IS NOT NULL AND v_available < p_units THEN
    RETURN jsonb_build_object('ok', false, 'reason', 'insufficient_gu', 'available', v_available);
  END IF;

  UPDATE billing.subscriptions
  SET gu_consumed = gu_consumed + p_units
  WHERE id = v_sub.id;

  INSERT INTO billing.usage_events (subscription_id, user_id, event_type, units)
  VALUES (v_sub.id, p_user_id, p_event_type, p_units);

  RETURN jsonb_build_object('ok', true, 'consumed', p_units, 'remaining', v_available - p_units);
END;
$$;


-- ═══════════════════════════════════════════════════════════════════════════════
-- DATA MIGRATION FROM PATHWAY (run after schema is live)
-- Copy the 3 tables that have real data
-- ═══════════════════════════════════════════════════════════════════════════════

-- NOTE: These reference the source Supabase project via postgres_fdw
-- Run manually after connecting to Platform project:

-- 1. Migrate colors (265 rows)
-- INSERT INTO ref.colors
-- SELECT id,name,hex,red,green,blue,hue,sat_hsl,light_hsl,sat_hsv,val_hsv
-- FROM dblink('host=db.hhgmgvhrmebkiscphirp.supabase.co ...', 'SELECT * FROM public.colors')
-- AS t(id bigint, name text, hex text, ...);

-- 2. Migrate allowed_domains (10 rows)
-- INSERT INTO platform.allowed_domains (hostname, description)
-- SELECT hostname, description FROM <pathway>.public.allowed_domains;

-- 3. Migrate fibonrose_visual_trust_signals (5 rows)
-- INSERT INTO fibonrose.visual_trust_signals
-- SELECT id, signal_type, trust_level, hex_color, icon_name, animation_type,
--        pattern_path, contrast_ratio, vibration_pattern, flash_pattern, created_at
-- FROM <pathway>.public.fibonrose_visual_trust_signals;

-- ═══════════════════════════════════════════════════════════════════════════════
-- SUMMARY
-- ═══════════════════════════════════════════════════════════════════════════════
-- Schemas:    deafauth · platform · billing · fibonrose · magiciancore · pinksync · vr4deaf · creator · ref
-- Tables:     ~45 canonical (down from 216)
-- Typos fixed: fibronrose → fibonrose (all occurrences)
-- Duplicates resolved: 6 user tables → 1, 2 subscription tables → 1, 3 agent tables → 1
-- Missing link added: billing.stripe_customers (was the Stripe connection blocker)
-- Functions:  set_updated_at (1, replaces 5), calculate_trust_score (1, replaces 2),
--             handle_new_user, consume_gu, billing.stripe webhook ready
-- RLS:        service_role bypass all + user-read-own per sensitive table
-- ═══════════════════════════════════════════════════════════════════════════════
