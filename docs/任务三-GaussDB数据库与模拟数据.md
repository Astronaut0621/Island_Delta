# 任务三：GaussDB 数据库与模拟数据

## 一、任务目标

设计并创建《孤岛温差》的数据库结构，完成业务数据、统计数据、聊天数据、NLP 预测数据和反馈数据的存储方案。同时准备不少于 300 条模拟情绪数据，支撑开发联调和答辩演示。

## 二、任务范围

本任务负责数据库表结构、初始化 SQL、模拟数据和数据说明文档。不负责后端接口实现、不负责前端页面、不负责 NLP 模型推理。

数据库建议：

```text
Huawei Cloud GaussDB / openGauss 兼容数据库
```

MVP 阶段不强依赖复杂 GIS 扩展，使用以下字段支持附近查询：

```text
latitude
longitude
location_grid
```

## 三、需要完成的具体功能

### 1. 数据库初始化脚本

1. 创建所有核心业务表。
2. 设置主键。
3. 设置必要索引。
4. 设置唯一约束。
5. 设置默认值。
6. 准备表注释或字段说明。

### 2. 用户表 users

用于存储匿名用户和后续可扩展的注册用户。

核心字段：

```text
id
anonymous_id
anonymous_token_hash
nickname
user_type
created_at
last_active_at
status
```

要求：

1. anonymous_id 唯一。
2. 不存储明文 token。
3. status 支持 normal、banned。

### 3. 情绪记录表 emotion_posts

用于存储用户投递的情绪内容。

核心字段：

```text
id
user_id
emotion_type
sentiment
temperature
temperature_bin
content
latitude
longitude
location_grid
location_name
visibility
allow_reaction
model_version
confidence
created_at
updated_at
status
report_count
```

要求：

1. temperature 范围为 -10 到 +10。
2. 只保存模糊化后的 latitude 和 longitude。
3. status 支持 normal、pending、hidden、deleted。
4. 为 location_grid、created_at、emotion_type 建索引。

### 4. 地点表 locations

用于存储校园或城市地点。

核心字段：

```text
id
name
latitude
longitude
category
avg_temperature
post_count
created_at
updated_at
```

建议准备地点：

```text
图书馆
教学楼
食堂
宿舍区
操场
湖边草坪
校门口
地铁站
咖啡馆
自习室
```

### 5. 互动表 reactions

用于存储用户对留言的共鸣互动。

核心字段：

```text
id
post_id
user_id
reaction_type
created_at
```

要求：

1. reaction_type 支持 me_too、hug、light、thanks。
2. 增加唯一约束：

```text
user_id + post_id + reaction_type
```

### 6. 举报表 reports

用于内容举报和后台处理。

核心字段：

```text
id
post_id
user_id
reason
detail
created_at
status
```

status 支持：

```text
pending
handled
ignored
```

### 7. 统计快照表 temperature_snapshots

用于保存每日或每周统计结果。

核心字段：

```text
id
area_name
avg_temperature
post_count
main_emotion
coldest_location
warmest_location
snapshot_date
created_at
```

### 8. 聊天相关表

需要创建：

```text
chat_sessions
chat_messages
```

chat_sessions 用于保存智能体聊天会话。

chat_messages 用于保存用户和智能体消息。

chat_messages 需要支持：

```text
role
content
emotion_type
estimated_temperature
safety_level
status
```

### 9. NLP 相关表

需要创建：

```text
emotion_label_dict
nlp_training_samples
nlp_model_versions
nlp_predictions
ai_feedback_logs
```

emotion_label_dict 第一版建议包含：

```text
lonely   孤独
anxious  焦虑
stressed 压力
tired    疲惫
sad      失落
calm     平静
healed   治愈
safe     安心
happy    快乐
hopeful  希望
```

### 10. 模拟数据

需要准备不少于 300 条 emotion_posts 数据。

模拟数据要求：

1. 覆盖至少 10 个地点。
2. 覆盖至少 10 个情绪标签。
3. 温度覆盖 -10 到 +10。
4. 包含不同时间段，例如早上、中午、下午、晚上、深夜。
5. 包含正向、负向、中性情绪。
6. 内容必须适合公开演示。
7. 数据中应有明显的冷暖地点差异，方便热力图展示。

示例规则：

```text
图书馆：压力、焦虑偏多，温度 -7 到 -2
湖边草坪：平静、治愈偏多，温度 +2 到 +8
宿舍区：疲惫、孤独偏多，温度 -6 到 0
操场：希望、快乐偏多，温度 +1 到 +7
校门口：离别、焦虑偏多，温度 -5 到 +1
```

## 四、交付物

1. `schema.sql`
2. `seed_locations.sql`
3. `seed_emotion_labels.sql`
4. `seed_mock_emotions.sql`
5. 数据库设计说明文档。
6. 模拟数据规则说明文档。

## 五、验收标准

1. 所有 SQL 可以在 GaussDB / openGauss 环境执行。
2. 核心表创建成功。
3. 初始化后至少有 300 条模拟情绪数据。
4. 情绪标签字典完整。
5. 地点数据完整。
6. 后端可以正常查询和写入核心表。
7. 模拟数据能支撑地图点位、热力图、统计报告和地点详情展示。

