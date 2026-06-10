# Database — Island Delta (孤岛温差)

## 概述

本目录包含《孤岛温差》项目的全部数据库资产，目标数据库为 **GaussDB / openGauss** 兼容环境。

MVP 阶段不强依赖 GIS 扩展，使用 `latitude`、`longitude`、`location_grid` 三个字段支持附近查询。

## 文件清单

| 文件 | 说明 |
|------|------|
| `schema.sql` | 核心业务表 DDL（建表、约束、索引、注释） |
| `seeds/seed_emotion_labels.sql` | 情绪标签字典（10 个标签） |
| `seeds/seed_locations.sql` | 地点种子数据（10 个校园地点） |
| `seeds/seed_mock_emotions.sql` | 模拟情绪帖子 315 条 + 15 个模拟用户 |

## 数据库表结构

### 核心业务表

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `users` | 用户表 | anonymous_id(唯一), anonymous_token_hash, nickname, user_type, status |
| `locations` | 地点表 | name, latitude, longitude, category, avg_temperature, post_count |
| `emotion_posts` | 情绪记录表 | emotion_type, sentiment, temperature(-10~+10), content, location_grid, status |
| `reactions` | 互动表 | post_id, user_id, reaction_type(me_too/hug/light/thanks) |
| `reports` | 举报表 | post_id, reason, status(pending/handled/ignored) |
| `temperature_snapshots` | 统计快照表 | area_name, avg_temperature, snapshot_date |

### 聊天相关表

| 表名 | 说明 |
|------|------|
| `chat_sessions` | 聊天会话 |
| `chat_messages` | 聊天消息（支持 role, emotion_type, safety_level） |

### NLP 相关表

| 表名 | 说明 |
|------|------|
| `emotion_label_dict` | 情绪标签字典（lonely, anxious, stressed, tired, sad, calm, healed, safe, happy, hopeful） |
| `nlp_training_samples` | NLP 训练样本 |
| `nlp_model_versions` | NLP 模型版本管理 |
| `nlp_predictions` | NLP 预测记录 |
| `ai_feedback_logs` | AI 反馈日志 |

## 关键约束

- `emotion_posts.temperature` 范围约束 CHECK(-10, +10)
- `reactions` 唯一约束：user_id + post_id + reaction_type
- `users.anonymous_id` 全局唯一
- `emotion_label_dict.code` 全局唯一
- `emotion_posts` 核心索引：location_grid, created_at, emotion_type

## temperature_bin 分档规则

| 分档 | 范围 |
|------|------|
| freezing | ≤ -6 |
| cold | -6 ~ -3 |
| cool | -3 ~ 0 |
| neutral | 0 ~ 3 |
| warm | 3 ~ 6 |
| hot | ≥ 6 |

## 模拟数据规则

各地点的情绪温度分布有明显差异，用于支撑热力图展示：

| 地点 | 主导情绪 | 温度范围 |
|------|----------|----------|
| 图书馆 | 压力、焦虑 | -7 ~ -2 |
| 教学楼 | 焦虑、压力、失落 | -6 ~ -1 |
| 食堂 | 平静、快乐、安心 | 0 ~ +6 |
| 宿舍区 | 疲惫、孤独 | -6 ~ 0 |
| 操场 | 希望、快乐 | +1 ~ +7 |
| 湖边草坪 | 平静、治愈 | +2 ~ +8 |
| 校门口 | 焦虑、失落 | -5 ~ +1 |
| 地铁站 | 疲惫、孤独 | -4 ~ 0 |
| 咖啡馆 | 安心、治愈 | +1 ~ +6 |
| 自习室 | 压力、焦虑 | -7 ~ -1 |

## 执行顺序

```sql
-- 1. 建表
\i schema.sql

-- 2. 种子数据
\i seeds/seed_emotion_labels.sql
\i seeds/seed_locations.sql
\i seeds/seed_mock_emotions.sql
```

## 环境变量

数据库连接信息通过后端 `application.yml` 配置，支持环境变量覆盖：

- 本地开发默认使用 H2 内嵌数据库
- 连接 GaussDB 时使用 `--spring.profiles.active=gaussdb` 并设置环境变量：

```bash
set DB_URL=jdbc:postgresql://<host>:<port>/island_delta
set DB_USER=<username>
set DB_PASS=<password>
mvn spring-boot:run -Dspring-boot.run.profiles=gaussdb
```
