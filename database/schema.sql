-- ============================================================
-- Island Delta (孤岛温差) - Database Schema
-- Target: GaussDB / openGauss compatible
-- ============================================================

-- 清理（开发阶段使用，生产环境请勿执行）
DROP TABLE IF EXISTS ai_feedback_logs;
DROP TABLE IF EXISTS nlp_predictions;
DROP TABLE IF EXISTS nlp_model_versions;
DROP TABLE IF EXISTS nlp_training_samples;
DROP TABLE IF EXISTS emotion_label_dict;
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS temperature_snapshots;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS reactions;
DROP TABLE IF EXISTS emotion_posts;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS users;

-- ============================================================
-- 1. 用户表 users
-- ============================================================
CREATE TABLE users (
    id              BIGSERIAL       PRIMARY KEY,
    anonymous_id    VARCHAR(64)     NOT NULL,
    anonymous_token_hash VARCHAR(128) NOT NULL,
    nickname        VARCHAR(32)     DEFAULT '匿名岛民',
    user_type       VARCHAR(16)     NOT NULL DEFAULT 'anonymous',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    status          VARCHAR(16)     NOT NULL DEFAULT 'normal'
);

COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.id IS '主键';
COMMENT ON COLUMN users.anonymous_id IS '匿名标识，唯一';
COMMENT ON COLUMN users.anonymous_token_hash IS '匿名令牌哈希，不存储明文';
COMMENT ON COLUMN users.nickname IS '昵称';
COMMENT ON COLUMN users.user_type IS '用户类型：anonymous / registered / admin';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.last_active_at IS '最后活跃时间';
COMMENT ON COLUMN users.status IS '状态：normal / banned';

CREATE UNIQUE INDEX uk_users_anonymous_id ON users (anonymous_id);

-- ============================================================
-- 2. 地点表 locations
-- ============================================================
CREATE TABLE locations (
    id              BIGSERIAL       PRIMARY KEY,
    name            VARCHAR(64)     NOT NULL,
    latitude        DECIMAL(9,6)    NOT NULL,
    longitude       DECIMAL(9,6)    NOT NULL,
    category        VARCHAR(32)     DEFAULT 'campus',
    avg_temperature DECIMAL(4,1)    DEFAULT 0,
    post_count      INT             DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE locations IS '地点表';
COMMENT ON COLUMN locations.id IS '主键';
COMMENT ON COLUMN locations.name IS '地点名称';
COMMENT ON COLUMN locations.latitude IS '纬度';
COMMENT ON COLUMN locations.longitude IS '经度';
COMMENT ON COLUMN locations.category IS '分类：campus / city / transport / leisure';
COMMENT ON COLUMN locations.avg_temperature IS '平均温度';
COMMENT ON COLUMN locations.post_count IS '关联情绪帖子数';
COMMENT ON COLUMN locations.created_at IS '创建时间';
COMMENT ON COLUMN locations.updated_at IS '更新时间';

-- ============================================================
-- 3. 情绪记录表 emotion_posts
-- ============================================================
CREATE TABLE emotion_posts (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL,
    emotion_type    VARCHAR(32)     NOT NULL,
    sentiment       VARCHAR(16)     NOT NULL DEFAULT 'neutral',
    temperature     DECIMAL(4,1)    NOT NULL DEFAULT 0,
    temperature_bin VARCHAR(8)      NOT NULL DEFAULT 'neutral',
    content         TEXT            NOT NULL DEFAULT '',
    latitude        DECIMAL(9,6)    DEFAULT NULL,
    longitude       DECIMAL(9,6)    DEFAULT NULL,
    location_grid   VARCHAR(16)     DEFAULT NULL,
    location_name   VARCHAR(64)     DEFAULT NULL,
    visibility      VARCHAR(16)     NOT NULL DEFAULT 'public',
    allow_reaction  BOOLEAN         NOT NULL DEFAULT TRUE,
    model_version   VARCHAR(32)     DEFAULT NULL,
    confidence      DECIMAL(3,2)    DEFAULT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    status          VARCHAR(16)     NOT NULL DEFAULT 'normal',
    report_count    INT             NOT NULL DEFAULT 0
);

COMMENT ON TABLE emotion_posts IS '情绪记录表';
COMMENT ON COLUMN emotion_posts.id IS '主键';
COMMENT ON COLUMN emotion_posts.user_id IS '用户ID';
COMMENT ON COLUMN emotion_posts.emotion_type IS '情绪类型，关联emotion_label_dict';
COMMENT ON COLUMN emotion_posts.sentiment IS '情感倾向：positive / negative / neutral';
COMMENT ON COLUMN emotion_posts.temperature IS '情绪温度，范围-10到+10';
COMMENT ON COLUMN emotion_posts.temperature_bin IS '温度分档：freezing / cold / cool / neutral / warm / hot';
COMMENT ON COLUMN emotion_posts.content IS '留言内容';
COMMENT ON COLUMN emotion_posts.latitude IS '模糊化后的纬度';
COMMENT ON COLUMN emotion_posts.longitude IS '模糊化后的经度';
COMMENT ON COLUMN emotion_posts.location_grid IS '网格编码，用于附近查询';
COMMENT ON COLUMN emotion_posts.location_name IS '地点名称';
COMMENT ON COLUMN emotion_posts.visibility IS '可见性：public / private';
COMMENT ON COLUMN emotion_posts.allow_reaction IS '是否允许共鸣互动';
COMMENT ON COLUMN emotion_posts.model_version IS 'NLP模型版本';
COMMENT ON COLUMN emotion_posts.confidence IS '模型置信度0~1';
COMMENT ON COLUMN emotion_posts.created_at IS '创建时间';
COMMENT ON COLUMN emotion_posts.updated_at IS '更新时间';
COMMENT ON COLUMN emotion_posts.status IS '状态：normal / pending / hidden / deleted';
COMMENT ON COLUMN emotion_posts.report_count IS '被举报次数';

-- 温度范围约束
ALTER TABLE emotion_posts ADD CONSTRAINT ck_temperature_range
    CHECK (temperature >= -10 AND temperature <= 10);

-- 核心索引
CREATE INDEX idx_emotion_posts_location_grid ON emotion_posts (location_grid);
CREATE INDEX idx_emotion_posts_created_at ON emotion_posts (created_at);
CREATE INDEX idx_emotion_posts_emotion_type ON emotion_posts (emotion_type);
CREATE INDEX idx_emotion_posts_status ON emotion_posts (status);
CREATE INDEX idx_emotion_posts_user_id ON emotion_posts (user_id);

-- ============================================================
-- 4. 互动表 reactions
-- ============================================================
CREATE TABLE reactions (
    id              BIGSERIAL       PRIMARY KEY,
    post_id         BIGINT          NOT NULL,
    user_id         BIGINT          NOT NULL,
    reaction_type   VARCHAR(16)     NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE reactions IS '互动表';
COMMENT ON COLUMN reactions.id IS '主键';
COMMENT ON COLUMN reactions.post_id IS '情绪帖子ID';
COMMENT ON COLUMN reactions.user_id IS '用户ID';
COMMENT ON COLUMN reactions.reaction_type IS '互动类型：me_too / hug / light / thanks';
COMMENT ON COLUMN reactions.created_at IS '创建时间';

-- 唯一约束：同一用户对同一帖子同一类型只能互动一次
CREATE UNIQUE INDEX uk_reactions_user_post_type
    ON reactions (user_id, post_id, reaction_type);

CREATE INDEX idx_reactions_post_id ON reactions (post_id);

-- ============================================================
-- 5. 举报表 reports
-- ============================================================
CREATE TABLE reports (
    id              BIGSERIAL       PRIMARY KEY,
    post_id         BIGINT          NOT NULL,
    user_id         BIGINT          NOT NULL,
    reason          VARCHAR(32)     NOT NULL,
    detail          TEXT            DEFAULT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    status          VARCHAR(16)     NOT NULL DEFAULT 'pending'
);

COMMENT ON TABLE reports IS '举报表';
COMMENT ON COLUMN reports.id IS '主键';
COMMENT ON COLUMN reports.post_id IS '被举报的帖子ID';
COMMENT ON COLUMN reports.user_id IS '举报用户ID';
COMMENT ON COLUMN reports.reason IS '举报原因：spam / abuse / inappropriate / other';
COMMENT ON COLUMN reports.detail IS '举报详情';
COMMENT ON COLUMN reports.created_at IS '创建时间';
COMMENT ON COLUMN reports.status IS '处理状态：pending / handled / ignored';

CREATE INDEX idx_reports_status ON reports (status);

-- ============================================================
-- 6. 统计快照表 temperature_snapshots
-- ============================================================
CREATE TABLE temperature_snapshots (
    id              BIGSERIAL       PRIMARY KEY,
    area_name       VARCHAR(64)     NOT NULL,
    avg_temperature DECIMAL(4,1)    NOT NULL DEFAULT 0,
    post_count      INT             NOT NULL DEFAULT 0,
    main_emotion    VARCHAR(32)     DEFAULT NULL,
    coldest_location VARCHAR(64)    DEFAULT NULL,
    warmest_location VARCHAR(64)    DEFAULT NULL,
    snapshot_date   DATE            NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE temperature_snapshots IS '统计快照表';
COMMENT ON COLUMN temperature_snapshots.id IS '主键';
COMMENT ON COLUMN temperature_snapshots.area_name IS '区域名称';
COMMENT ON COLUMN temperature_snapshots.avg_temperature IS '平均温度';
COMMENT ON COLUMN temperature_snapshots.post_count IS '帖子数量';
COMMENT ON COLUMN temperature_snapshots.main_emotion IS '主要情绪';
COMMENT ON COLUMN temperature_snapshots.coldest_location IS '最冷地点';
COMMENT ON COLUMN temperature_snapshots.warmest_location IS '最暖地点';
COMMENT ON COLUMN temperature_snapshots.snapshot_date IS '快照日期';
COMMENT ON COLUMN temperature_snapshots.created_at IS '创建时间';

CREATE INDEX idx_snapshots_date ON temperature_snapshots (snapshot_date);

-- ============================================================
-- 7. 聊天会话表 chat_sessions
-- ============================================================
CREATE TABLE chat_sessions (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         BIGINT          NOT NULL,
    status          VARCHAR(16)     NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE chat_sessions IS '聊天会话表';
COMMENT ON COLUMN chat_sessions.id IS '主键';
COMMENT ON COLUMN chat_sessions.user_id IS '用户ID';
COMMENT ON COLUMN chat_sessions.status IS '会话状态：active / closed';
COMMENT ON COLUMN chat_sessions.created_at IS '创建时间';
COMMENT ON COLUMN chat_sessions.updated_at IS '更新时间';

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions (user_id);

-- ============================================================
-- 8. 聊天消息表 chat_messages
-- ============================================================
CREATE TABLE chat_messages (
    id                      BIGSERIAL       PRIMARY KEY,
    session_id              BIGINT          NOT NULL,
    role                    VARCHAR(16)     NOT NULL,
    content                 TEXT            NOT NULL DEFAULT '',
    emotion_type            VARCHAR(32)     DEFAULT NULL,
    estimated_temperature   DECIMAL(4,1)    DEFAULT NULL,
    safety_level            VARCHAR(16)     DEFAULT 'safe',
    status                  VARCHAR(16)     NOT NULL DEFAULT 'normal',
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE chat_messages IS '聊天消息表';
COMMENT ON COLUMN chat_messages.id IS '主键';
COMMENT ON COLUMN chat_messages.session_id IS '会话ID';
COMMENT ON COLUMN chat_messages.role IS '角色：user / assistant / system';
COMMENT ON COLUMN chat_messages.content IS '消息内容';
COMMENT ON COLUMN chat_messages.emotion_type IS '情绪类型';
COMMENT ON COLUMN chat_messages.estimated_temperature IS '估计温度';
COMMENT ON COLUMN chat_messages.safety_level IS '安全级别：safe / warning / crisis';
COMMENT ON COLUMN chat_messages.status IS '状态：normal / hidden / deleted';
COMMENT ON COLUMN chat_messages.created_at IS '创建时间';

CREATE INDEX idx_chat_messages_session_id ON chat_messages (session_id);

-- ============================================================
-- 9. 情绪标签字典表 emotion_label_dict
-- ============================================================
CREATE TABLE emotion_label_dict (
    id              SERIAL          PRIMARY KEY,
    code            VARCHAR(32)     NOT NULL,
    name_zh         VARCHAR(16)     NOT NULL,
    sentiment       VARCHAR(16)     NOT NULL DEFAULT 'neutral',
    temperature_hint DECIMAL(4,1)   DEFAULT 0,
    sort_order      INT             NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE emotion_label_dict IS '情绪标签字典';
COMMENT ON COLUMN emotion_label_dict.id IS '主键';
COMMENT ON COLUMN emotion_label_dict.code IS '标签编码，如lonely';
COMMENT ON COLUMN emotion_label_dict.name_zh IS '中文名称，如孤独';
COMMENT ON COLUMN emotion_label_dict.sentiment IS '情感倾向：positive / negative / neutral';
COMMENT ON COLUMN emotion_label_dict.temperature_hint IS '建议温度参考值';
COMMENT ON COLUMN emotion_label_dict.sort_order IS '排序序号';
COMMENT ON COLUMN emotion_label_dict.is_active IS '是否启用';
COMMENT ON COLUMN emotion_label_dict.created_at IS '创建时间';

CREATE UNIQUE INDEX uk_emotion_label_code ON emotion_label_dict (code);

-- ============================================================
-- 10. NLP 训练样本表 nlp_training_samples
-- ============================================================
CREATE TABLE nlp_training_samples (
    id              BIGSERIAL       PRIMARY KEY,
    content         TEXT            NOT NULL,
    emotion_type    VARCHAR(32)     NOT NULL,
    sentiment       VARCHAR(16)     NOT NULL,
    temperature     DECIMAL(4,1)    NOT NULL DEFAULT 0,
    source          VARCHAR(32)     NOT NULL DEFAULT 'manual',
    is_verified     BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE nlp_training_samples IS 'NLP训练样本表';
COMMENT ON COLUMN nlp_training_samples.id IS '主键';
COMMENT ON COLUMN nlp_training_samples.content IS '文本内容';
COMMENT ON COLUMN nlp_training_samples.emotion_type IS '情绪类型';
COMMENT ON COLUMN nlp_training_samples.sentiment IS '情感倾向';
COMMENT ON COLUMN nlp_training_samples.temperature IS '温度标注';
COMMENT ON COLUMN nlp_training_samples.source IS '来源：manual / user_post / synthetic';
COMMENT ON COLUMN nlp_training_samples.is_verified IS '是否已验证';
COMMENT ON COLUMN nlp_training_samples.created_at IS '创建时间';

CREATE INDEX idx_nlp_training_emotion ON nlp_training_samples (emotion_type);

-- ============================================================
-- 11. NLP 模型版本表 nlp_model_versions
-- ============================================================
CREATE TABLE nlp_model_versions (
    id              SERIAL          PRIMARY KEY,
    version         VARCHAR(32)     NOT NULL,
    description     TEXT            DEFAULT NULL,
    accuracy        DECIMAL(5,4)    DEFAULT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT FALSE,
    trained_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE nlp_model_versions IS 'NLP模型版本表';
COMMENT ON COLUMN nlp_model_versions.id IS '主键';
COMMENT ON COLUMN nlp_model_versions.version IS '版本号';
COMMENT ON COLUMN nlp_model_versions.description IS '版本描述';
COMMENT ON COLUMN nlp_model_versions.accuracy IS '准确率';
COMMENT ON COLUMN nlp_model_versions.is_active IS '是否为当前使用版本';
COMMENT ON COLUMN nlp_model_versions.trained_at IS '训练时间';

CREATE UNIQUE INDEX uk_model_version ON nlp_model_versions (version);

-- ============================================================
-- 12. NLP 预测记录表 nlp_predictions
-- ============================================================
CREATE TABLE nlp_predictions (
    id              BIGSERIAL       PRIMARY KEY,
    post_id         BIGINT          DEFAULT NULL,
    session_id      BIGINT          DEFAULT NULL,
    input_text      TEXT            NOT NULL,
    predicted_emotion VARCHAR(32)   NOT NULL,
    predicted_sentiment VARCHAR(16) NOT NULL,
    predicted_temperature DECIMAL(4,1) NOT NULL DEFAULT 0,
    confidence      DECIMAL(3,2)    NOT NULL DEFAULT 0,
    model_version   VARCHAR(32)     NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE nlp_predictions IS 'NLP预测记录表';
COMMENT ON COLUMN nlp_predictions.id IS '主键';
COMMENT ON COLUMN nlp_predictions.post_id IS '关联帖子ID';
COMMENT ON COLUMN nlp_predictions.session_id IS '关联会话ID';
COMMENT ON COLUMN nlp_predictions.input_text IS '输入文本';
COMMENT ON COLUMN nlp_predictions.predicted_emotion IS '预测情绪类型';
COMMENT ON COLUMN nlp_predictions.predicted_sentiment IS '预测情感倾向';
COMMENT ON COLUMN nlp_predictions.predicted_temperature IS '预测温度';
COMMENT ON COLUMN nlp_predictions.confidence IS '置信度0~1';
COMMENT ON COLUMN nlp_predictions.model_version IS '使用模型版本';
COMMENT ON COLUMN nlp_predictions.created_at IS '创建时间';

CREATE INDEX idx_nlp_predictions_post ON nlp_predictions (post_id);

-- ============================================================
-- 13. AI 反馈日志表 ai_feedback_logs
-- ============================================================
CREATE TABLE ai_feedback_logs (
    id              BIGSERIAL       PRIMARY KEY,
    session_id      BIGINT          DEFAULT NULL,
    message_id      BIGINT          DEFAULT NULL,
    user_id         BIGINT          DEFAULT NULL,
    trigger_type    VARCHAR(32)     NOT NULL,
    input_summary   TEXT            DEFAULT NULL,
    output_summary  TEXT            DEFAULT NULL,
    safety_flag     VARCHAR(16)     DEFAULT 'safe',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ai_feedback_logs IS 'AI反馈日志表';
COMMENT ON COLUMN ai_feedback_logs.id IS '主键';
COMMENT ON COLUMN ai_feedback_logs.session_id IS '会话ID';
COMMENT ON COLUMN ai_feedback_logs.message_id IS '消息ID';
COMMENT ON COLUMN ai_feedback_logs.user_id IS '用户ID';
COMMENT ON COLUMN ai_feedback_logs.trigger_type IS '触发类型：chat / post_analysis / crisis_detect';
COMMENT ON COLUMN ai_feedback_logs.input_summary IS '输入摘要';
COMMENT ON COLUMN ai_feedback_logs.output_summary IS '输出摘要';
COMMENT ON COLUMN ai_feedback_logs.safety_flag IS '安全标记：safe / warning / crisis';
COMMENT ON COLUMN ai_feedback_logs.created_at IS '创建时间';

CREATE INDEX idx_ai_feedback_safety ON ai_feedback_logs (safety_flag);

-- ============================================================
-- 完成
-- ============================================================
