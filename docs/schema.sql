-- BEC 商务英语智能学习平台 - schema.sql
-- 版本: 1.0
-- 更新时间: 2026-03-31
-- 说明: MVP 核心建表草案（PostgreSQL 优先）

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(128) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    register_source VARCHAR(32) DEFAULT 'web',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profile (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    target_level VARCHAR(32),
    current_level VARCHAR(32),
    industry_background VARCHAR(128),
    learning_goal VARCHAR(255),
    learning_preference VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content_source (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(32) NOT NULL,
    source_url TEXT,
    source_desc TEXT,
    credibility_score NUMERIC(5,2),
    copyright_note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_content (
    id BIGSERIAL PRIMARY KEY,
    source_id BIGINT REFERENCES content_source(id) ON DELETE SET NULL,
    raw_title VARCHAR(255),
    raw_body TEXT NOT NULL,
    raw_format VARCHAR(32),
    clean_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    struct_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vocab_content (
    id BIGSERIAL PRIMARY KEY,
    raw_content_id BIGINT REFERENCES raw_content(id) ON DELETE SET NULL,
    word VARCHAR(128) NOT NULL,
    phonetic VARCHAR(128),
    part_of_speech VARCHAR(32),
    meaning_zh TEXT NOT NULL,
    business_example TEXT,
    collocation TEXT,
    level VARCHAR(32),
    difficulty VARCHAR(32),
    review_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    publish_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pattern_content (
    id BIGSERIAL PRIMARY KEY,
    raw_content_id BIGINT REFERENCES raw_content(id) ON DELETE SET NULL,
    pattern_text TEXT NOT NULL,
    scene_type VARCHAR(64),
    function_type VARCHAR(64),
    example_text TEXT,
    slot_desc TEXT,
    level VARCHAR(32),
    difficulty VARCHAR(32),
    review_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    publish_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scene_content (
    id BIGSERIAL PRIMARY KEY,
    raw_content_id BIGINT REFERENCES raw_content(id) ON DELETE SET NULL,
    scene_name VARCHAR(255) NOT NULL,
    scene_background TEXT,
    training_goal TEXT,
    user_role VARCHAR(128),
    ai_role VARCHAR(128),
    prompt_template TEXT,
    recommended_expression TEXT,
    level VARCHAR(32),
    difficulty VARCHAR(32),
    review_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    publish_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS question_content (
    id BIGSERIAL PRIMARY KEY,
    raw_content_id BIGINT REFERENCES raw_content(id) ON DELETE SET NULL,
    module_type VARCHAR(32) NOT NULL,
    question_type VARCHAR(32) NOT NULL,
    stem TEXT NOT NULL,
    options_json JSONB,
    correct_answer TEXT,
    explanation TEXT,
    level VARCHAR(32),
    difficulty VARCHAR(32),
    review_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    publish_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content_tag (
    id BIGSERIAL PRIMARY KEY,
    tag_name VARCHAR(128) NOT NULL,
    tag_code VARCHAR(64) NOT NULL UNIQUE,
    tag_type VARCHAR(32) NOT NULL,
    tag_desc TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content_tag_relation (
    id BIGSERIAL PRIMARY KEY,
    content_type VARCHAR(32) NOT NULL,
    content_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL REFERENCES content_tag(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content_review_record (
    id BIGSERIAL PRIMARY KEY,
    content_type VARCHAR(32) NOT NULL,
    content_id BIGINT NOT NULL,
    reviewer_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    review_result VARCHAR(32) NOT NULL,
    review_comment TEXT,
    reviewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_vocab_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vocab_id BIGINT NOT NULL REFERENCES vocab_content(id) ON DELETE CASCADE,
    learn_status VARCHAR(32) NOT NULL DEFAULT 'new',
    learn_count INT NOT NULL DEFAULT 0,
    correct_rate NUMERIC(5,2),
    last_learned_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, vocab_id)
);

CREATE TABLE IF NOT EXISTS user_pattern_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pattern_id BIGINT NOT NULL REFERENCES pattern_content(id) ON DELETE CASCADE,
    learn_status VARCHAR(32) NOT NULL DEFAULT 'new',
    learn_count INT NOT NULL DEFAULT 0,
    familiarity_score NUMERIC(5,2),
    last_learned_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, pattern_id)
);

CREATE TABLE IF NOT EXISTS user_scene_session (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scene_id BIGINT NOT NULL REFERENCES scene_content(id) ON DELETE CASCADE,
    session_status VARCHAR(32) NOT NULL DEFAULT 'started',
    round_count INT NOT NULL DEFAULT 0,
    user_summary TEXT,
    ai_feedback_summary TEXT,
    score NUMERIC(5,2),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS level_test_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_score NUMERIC(6,2),
    result_level VARCHAR(32),
    ability_summary TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'submitted',
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS level_test_answer (
    id BIGSERIAL PRIMARY KEY,
    test_record_id BIGINT NOT NULL REFERENCES level_test_record(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES question_content(id) ON DELETE CASCADE,
    user_answer TEXT,
    is_correct BOOLEAN,
    score NUMERIC(6,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mock_exam_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_score NUMERIC(6,2),
    accuracy_rate NUMERIC(5,2),
    weak_tags TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'submitted',
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mock_exam_answer (
    id BIGSERIAL PRIMARY KEY,
    exam_record_id BIGINT NOT NULL REFERENCES mock_exam_record(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES question_content(id) ON DELETE CASCADE,
    user_answer TEXT,
    is_correct BOOLEAN,
    score NUMERIC(6,2),
    explanation_result TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vocab_word ON vocab_content(word);
CREATE INDEX IF NOT EXISTS idx_pattern_scene_type ON pattern_content(scene_type);
CREATE INDEX IF NOT EXISTS idx_scene_level ON scene_content(level);
CREATE INDEX IF NOT EXISTS idx_question_module_type ON question_content(module_type);
CREATE INDEX IF NOT EXISTS idx_tag_relation_content ON content_tag_relation(content_type, content_id);
CREATE INDEX IF NOT EXISTS idx_user_vocab_progress_user ON user_vocab_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_pattern_progress_user ON user_pattern_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_scene_session_user ON user_scene_session(user_id);
CREATE INDEX IF NOT EXISTS idx_level_test_record_user ON level_test_record(user_id);
CREATE INDEX IF NOT EXISTS idx_mock_exam_record_user ON mock_exam_record(user_id);
