# 任务二：Spring Boot 业务后端

## 一、任务目标

搭建《孤岛温差》的核心业务后端，负责用户、情绪、地图、地点、互动、统计、聊天转发、NLP 服务调用和基础安全校验。后端需要为前端提供稳定的 HTTP API。

## 二、任务范围

本任务负责 Spring Boot 业务服务，不负责前端页面开发、不负责数据库模拟数据生产、不负责 PaddleNLP 模型训练。数据库表结构由任务三提供，NLP 服务由任务四提供。

建议分层：

1. Controller：接收 HTTP 请求。
2. Service：处理业务逻辑。
3. Repository / Mapper：访问 GaussDB。
4. Entity：数据库实体。
5. DTO / VO：接口请求和响应对象。
6. Utils：坐标模糊化、距离计算、敏感词检测、时间处理。
7. Client：调用 FastAPI NLP 服务。

## 三、需要完成的具体功能

### 1. 后端项目搭建

1. 创建 Spring Boot 项目。
2. 配置 GaussDB / openGauss 数据源。
3. 配置 MyBatis Plus、JPA 或其他 ORM。
4. 配置统一响应结构。
5. 配置全局异常处理。
6. 配置参数校验。
7. 配置 Swagger / OpenAPI 文档。

### 2. 匿名用户模块

1. 创建匿名用户。
2. 生成 anonymous_id。
3. 生成匿名 token。
4. 只保存 token hash，不保存明文 token。
5. 更新 last_active_at。
6. 支持匿名用户状态校验。

接口：

```text
POST /api/users/anonymous
```

### 3. 情绪发布模块

1. 接收情绪标签、情感倾向、温度、一句话内容、地点信息。
2. 校验温度范围必须在 -10 到 +10。
3. 校验内容长度。
4. 对坐标进行模糊化处理。
5. 生成 location_grid。
6. 判断 temperature_bin。
7. 写入 emotion_posts 表。
8. 如果前端带有 NLP 推荐结果，需要保存 model_version 和 confidence。

接口：

```text
POST /api/emotions
```

### 4. 附近情绪查询模块

1. 根据经纬度和半径查询附近情绪。
2. MVP 阶段可以先用经纬度范围筛选，再在后端计算距离。
3. 只返回 status 为 normal 的公开内容。
4. 支持按情绪类型、温度区间、时间范围筛选。
5. 返回留言、温度、情绪标签、地点名称、共鸣数量。

接口：

```text
GET /api/emotions/nearby
```

### 5. 热力图数据模块

1. 聚合情绪点。
2. 根据温度绝对值、时间衰减和数量生成热力权重。
3. 返回前端热力图需要的经纬度和权重。
4. 支持按情绪类型筛选。

接口：

```text
GET /api/map/heatmap
```

### 6. 地点详情模块

1. 查询地点基础信息。
2. 统计地点平均温度。
3. 统计地点情绪数量。
4. 统计主要情绪。
5. 返回地点附近留言列表。

接口：

```text
GET /api/locations/{id}
```

### 7. 共鸣互动模块

1. 支持用户对留言进行共鸣。
2. 支持互动类型：me_too、hug、light、thanks。
3. 限制同一用户对同一留言的同一互动类型只能提交一次。
4. 返回最新互动数量。

接口：

```text
POST /api/reactions
```

### 8. 统计报告模块

1. 统计今日情绪数量。
2. 统计今日平均温度。
3. 统计最冷地点。
4. 统计最暖地点。
5. 统计主要情绪分布。
6. 返回前端报告页需要的数据结构。

接口：

```text
GET /api/statistics/today
```

### 9. NLP 服务调用模块

1. 调用 FastAPI 的情绪分析接口。
2. 将 NLP 返回结果转成前端需要的格式。
3. 保存模型预测记录。
4. 接收用户修正反馈并写入反馈日志。

接口：

```text
POST /api/nlp/analyze
POST /api/nlp/feedback
GET  /api/nlp/model-version
```

### 10. 智能体聊天转发模块

1. 创建聊天会话。
2. 保存用户消息。
3. 调用智能体服务。
4. 保存智能体回复。
5. 返回聊天消息和推荐情绪结果。

接口：

```text
POST /api/chat/sessions
POST /api/chat/message
```

## 四、数据依赖

依赖任务三提供以下表：

```text
users
emotion_posts
locations
reactions
temperature_snapshots
chat_sessions
chat_messages
nlp_predictions
ai_feedback_logs
```

## 五、交付物

1. 可运行 Spring Boot 后端项目。
2. 完整 API 接口。
3. Swagger / OpenAPI 文档。
4. 数据库连接配置示例。
5. 统一响应结构和错误码。
6. 与前端和 NLP 服务联调完成。

## 六、验收标准

1. 后端服务可以正常启动。
2. 可以连接 GaussDB 并完成读写。
3. 匿名用户、情绪发布、附近查询、热力图、共鸣、统计接口可用。
4. 坐标会被模糊化，不保存原始精准坐标。
5. NLP 分析接口可以成功转发并记录预测结果。
6. Swagger 文档能展示主要接口。
7. 核心接口有基础参数校验和异常处理。

