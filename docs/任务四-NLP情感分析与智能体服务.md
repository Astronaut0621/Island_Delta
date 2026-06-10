# 任务四：NLP 情感分析与智能体服务

## 一、任务目标

搭建独立的 NLP 与智能体服务，为《孤岛温差》提供情绪分类、情感倾向判断、温度推荐、安全等级识别、留言生成和基础聊天能力。业务后端通过 HTTP / JSON 调用本服务。

## 二、任务范围

本任务负责 FastAPI 服务、PaddleNLP 或规则模型接入、NLP 接口、智能体基础回复和模型预测结果格式。不负责 Spring Boot 业务接口、不负责前端页面、不负责数据库建表。

MVP 阶段可以先使用规则模型或 PaddleNLP Taskflow；时间充足时再进行中文预训练模型微调。

## 三、需要完成的具体功能

### 1. FastAPI 服务搭建

1. 创建 FastAPI 项目。
2. 提供健康检查接口。
3. 定义统一请求和响应格式。
4. 支持跨服务 HTTP 调用。
5. 编写基础接口文档。

接口：

```text
GET /health
```

### 2. 情绪分类

输入用户的一句话内容，输出情绪类型。

第一版支持标签：

```text
lonely
anxious
stressed
tired
sad
calm
healed
safe
happy
hopeful
```

要求：

1. 中文输入可以正常识别。
2. 输出标签必须来自字典。
3. 返回中文名称和英文 code。
4. 返回置信度。

### 3. 情感倾向分析

输出 sentiment：

```text
positive
neutral
negative
```

要求：

1. 负向内容识别为 negative。
2. 正向内容识别为 positive。
3. 情绪不明显时识别为 neutral。

### 4. 温度推荐

根据文本和情绪类型推荐温度值。

范围：

```text
-10 到 +10
```

规则建议：

```text
严重负向：-10 到 -7
一般负向：-6 到 -2
中性：-1 到 +1
一般正向：+2 到 +6
强正向：+7 到 +10
```

### 5. 安全等级识别

输出 safety_level：

```text
normal
warning
crisis
```

要求：

1. 普通情绪表达返回 normal。
2. 明显消极但无紧急风险返回 warning。
3. 涉及自伤、自杀、伤害他人等内容返回 crisis。
4. crisis 内容不能直接推荐公开发布。
5. 返回安全提示文案。

### 6. NLP 分析接口

接口：

```text
POST /nlp/analyze
```

请求示例：

```json
{
  "text": "今天在图书馆复习到很晚，感觉压力很大",
  "location_name": "图书馆"
}
```

响应示例：

```json
{
  "emotion_type": "stressed",
  "emotion_name": "压力",
  "sentiment": "negative",
  "temperature": -6,
  "safety_level": "normal",
  "confidence": 0.82,
  "model_version": "taskflow-mvp-v1",
  "suggested_content": "今天在图书馆待了很久，压力有点重。"
}
```

### 7. 留言生成接口

根据用户原始表达生成更适合公开投递的一句话。

接口：

```text
POST /nlp/generate-post
```

要求：

1. 保留用户原意。
2. 不夸大情绪。
3. 不生成攻击性内容。
4. 不泄露隐私。
5. 输出一句适合地图公开展示的短留言。

### 8. 智能体聊天接口

接口：

```text
POST /chat/message
```

智能体需要支持：

1. 倾听用户表达。
2. 帮用户整理情绪。
3. 推荐情绪标签。
4. 推荐温度。
5. 生成留言草稿。
6. 推荐附近更温暖的地点。

智能体不能做：

1. 医疗诊断。
2. 心理治疗承诺。
3. 鼓励危险行为。
4. 自动替用户发布情绪。
5. 要求用户提供真实身份隐私。

### 9. 模型版本接口

接口：

```text
GET /nlp/model-version
```

返回当前服务使用的模型名称、版本、能力说明。

### 10. 用户反馈接口

接口：

```text
POST /nlp/feedback
```

用于接收用户是否采纳或修正模型推荐结果。

## 四、服务依赖

建议依赖：

1. Python
2. FastAPI
3. Uvicorn
4. PaddleNLP
5. Pydantic

MVP 兜底方案：

1. 如果 PaddleNLP 安装或模型下载困难，先使用关键词规则模型。
2. 规则模型必须返回与正式模型一致的 JSON 格式。
3. 后续替换模型时不影响 Spring Boot 和前端。

## 五、交付物

1. 可运行 FastAPI 服务。
2. NLP 分析接口。
3. 留言生成接口。
4. 智能体聊天接口。
5. 模型版本接口。
6. 用户反馈接口。
7. 测试样例。
8. 模型或规则说明文档。

## 六、验收标准

1. 服务可以正常启动。
2. `/health` 接口返回正常。
3. 输入一句中文留言后可以返回情绪标签、情感倾向、温度、安全等级。
4. 返回 JSON 格式稳定。
5. Spring Boot 可以成功调用本服务。
6. 高风险内容可以被识别并返回 warning 或 crisis。
7. 留言生成结果适合公开展示。
8. 智能体能完成基础情绪整理和留言草稿生成。

