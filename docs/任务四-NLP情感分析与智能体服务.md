# 任务四：NLP 情感分析与智能体服务

## 一、任务目标

搭建独立的 NLP 与智能体服务，为《孤岛温差》提供情绪分类、情感倾向判断、安全等级识别、留言生成和基础聊天能力。业务后端通过 HTTP / JSON 调用本服务。

MVP 优先级调整：

1. 第一阶段优先实现十类主情绪识别，支撑“十种情绪地图”展示。
2. `sentiment` 由主情绪自动派生。
3. `temperature` 暂时作为可选推荐字段保留，不作为第一阶段训练目标，也不要求用户手动确认。
4. 温度热力图可在情绪地图可用后作为增强功能继续推进。

## 二、任务范围

本任务负责 FastAPI 服务、PaddleNLP 或规则模型接入、NLP 接口、智能体基础回复和模型预测结果格式。不负责 Spring Boot 业务接口、不负责前端页面、不负责数据库建表。

MVP 阶段可以先使用规则模型或 PaddleNLP Taskflow；训练阶段优先微调主情绪十分类模型，时间充足时再探索温度推荐。

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
secure
happy
hopeful
```

要求：

1. 中文输入可以正常识别。
2. 输出标签必须来自字典。
3. 返回中文名称和英文 code。
4. 返回置信度。
5. 第一阶段训练集采用单标签标注，每条样本只标一个最主要的 `emotion_type`，不做 multi-label classification。

第一阶段固定标签元数据，前端地图、图例和统计图应复用同一套颜色：

| code | 中文 | sentiment | color |
| --- | --- | --- | --- |
| lonely | 孤独 | negative | `#4f46e5` |
| anxious | 焦虑 | negative | `#7c3aed` |
| stressed | 压力 | negative | `#dc2626` |
| tired | 疲惫 | negative | `#64748b` |
| sad | 失落 | negative | `#2563eb` |
| calm | 平静 | neutral | `#14b8a6` |
| healed | 治愈 | positive | `#22c55e` |
| secure | 安心 | positive | `#0f766e` |
| happy | 快乐 | positive | `#f59e0b` |
| hopeful | 希望 | positive | `#eab308` |

### 2.1 训练数据格式

第一版自建校园情绪数据集使用 CSV：

```csv
id,text,emotion_type,source
1,晚上一个人回宿舍，突然觉得整条路都很安静,lonely,manual
51,明天就要考试了，心里一直发慌,anxious,manual
```

当前初版样本文件：

```text
nlp-service/data/campus_emotion_samples_v1.csv
```

该文件包含 200 条 `ai_generated` 样本，每类主情绪 20 条，用于第一轮人工审核和训练脚本打样。

扩展打样样本文件：

```text
nlp-service/data/campus_emotion_samples_v2.csv
```

该文件包含 500 条 `ai_generated` 样本，每类主情绪 50 条。它可以用于训练脚本、baseline 评估和接口集成测试，但最终模型仍需要人工审核样本和真实校园表达补充。

字段说明：

1. `id`：人工维护的稳定编号。
2. `text`：一句可投递到情绪地图的中文短句。
3. `emotion_type`：十类主情绪之一。
4. `source`：样本来源，固定为 `manual`、`ai_generated`。人工编写和论坛/社交平台人工采集整理都标为 `manual`，AI 批量生成样本标为 `ai_generated`。

初版整理时可以按标签分段编号，方便检查每类数量：

```text
1-50 lonely
51-100 anxious
101-150 stressed
151-200 tired
201-250 sad
251-300 calm
301-350 healed
351-400 secure
401-450 happy
451-500 hopeful
```

训练脚本不能直接按原始顺序切分数据，必须先按 `emotion_type` 分层打乱，再生成 train / dev / test，避免某些标签只出现在单个 split 中。

### 2.2 标注边界规则

细粒度情绪本身存在模糊边界。第一阶段不追求“唯一真理”，而是追求团队标注口径一致。每条样本只标一个 dominant emotion，按下面规则判断：

1. 先看文本最明确的情绪触发源。
2. 如果同时出现多个情绪，选择更具体、更能解释整句话的主情绪。
3. 如果文本只描述场景，没有明显正负波动，标为 `calm`。
4. 不因为地点直接决定标签，例如“图书馆”不必然是 `stressed`，要看文本表达。
5. 不因为强度直接改变标签，强度以后可用于温度增强，不用于 emotion_type。

容易混淆的标签边界：

| 混淆组 | 判定规则 | 示例 |
| --- | --- | --- |
| `anxious` vs `stressed` | 害怕结果、心慌、不确定，标 `anxious`；任务量、考试、DDL、绩点压迫，标 `stressed`。 | “明天考试我怕自己发挥不好” -> `anxious`；“三门作业堆在一起压得喘不过气” -> `stressed` |
| `tired` vs `sad` | 没力气、困、熬夜、撑不动，标 `tired`；委屈、想哭、失去感，标 `sad`。 | “写到凌晨脑子已经转不动了” -> `tired`；“努力了很久还是被否定，想哭” -> `sad` |
| `lonely` vs `sad` | 一个人、没人陪、没人懂、不被看见，标 `lonely`；没有明显孤独关系，只是难过失落，标 `sad`。 | “路上全是人但没人能说话” -> `lonely`；“今天收到结果后整个人很失落” -> `sad` |
| `calm` vs `healed` | 安静、平稳、没有明显被缓解，标 `calm`；被风景、音乐、晚风、阳光等缓解，标 `healed`。 | “湖边很安静，我坐了一会儿” -> `calm`；“湖边晚风吹过来，心里松了一点” -> `healed` |
| `healed` vs `secure` | 外部环境带来缓解和治愈，标 `healed`；踏实、安全、被接住、有人支持，标 `secure`。 | “操场的风让我缓过来” -> `healed`；“朋友说会陪我，我突然安心了” -> `secure` |
| `happy` vs `hopeful` | 当下开心、快乐、兴奋，标 `happy`；面向未来的期待、还能继续，标 `hopeful`。 | “今天和朋友笑了一整晚” -> `happy`；“虽然很累，但感觉明天还能继续” -> `hopeful` |

当一句话仍然难以判断时，优先按以下顺序处理：

```text
明确风险内容交给 safety_level，不靠 emotion_type 解决。
明确任务压迫优先 stressed。
明确未来担心优先 anxious。
明确孤身/无人理解优先 lonely。
明确被环境缓解优先 healed。
明确支持和安全感优先 secure。
其余轻微、稳定、难以归类的内容标 calm。
```

### 3. 情感倾向分析

输出 sentiment：

```text
positive
neutral
negative
```

MVP 第一阶段采用两层情绪口径：

1. 模型优先预测细粒度主情绪 `emotion_type`。
2. `sentiment` 由 `emotion_type` 自动派生，不作为第一阶段独立训练目标。

派生规则：

```text
lonely / anxious / stressed / tired / sad -> negative
calm -> neutral
healed / secure / happy / hopeful -> positive
```

要求：

1. 负向内容识别为 negative。
2. 正向内容识别为 positive。
3. 情绪不明显时识别为 neutral。

### 4. 温度推荐（可选增强）

根据文本和情绪类型推荐温度值。

范围：

```text
-10 到 +10
```

MVP 第一阶段不把温度作为必须训练的模型目标，也不强制用户额外确认温度。服务可以返回一个可解释的推荐值，前端和后端可以暂时主要使用 `emotion_type` 展示十类情绪地图。

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

该接口还需要返回 `label_metadata`，包括每个 `emotion_type` 的中文名、`sentiment`、固定颜色和展示顺序，供前端情绪地图统一使用。

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

