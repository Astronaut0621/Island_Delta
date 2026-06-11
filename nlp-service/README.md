# Island Delta NLP Service

任务四交付的独立 NLP 与智能体服务。Spring Boot 后端通过 HTTP/JSON 调用本服务，后端调用代码不属于本模块主责。

## 功能范围

- `GET /health`
- `POST /nlp/analyze`
- `POST /nlp/generate-post`
- `POST /chat/message`
- `GET /nlp/model-version`
- `POST /nlp/feedback`

当前推理策略：

1. 优先加载本地 PaddleNLP ERNIE 十分类模型。
2. 模型依赖缺失或加载失败时自动 fallback 到关键词规则模型。
3. `sentiment` 由 `emotion_type` 自动派生。
4. `temperature` 是可解释推荐值，不是第一阶段训练目标。
5. `safety_level` 使用规则检测高风险内容，并覆盖发布安全判断。

## 本地启动

从项目根目录安装基础依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\nlp-service
```

启用本地 ERNIE 模型推理：

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".\nlp-service[paddle]"
```

启动服务：

```powershell
cd D:\Island_Delta\nlp-service
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

检查模型是否真实启用：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/nlp/model-version
```

期望看到：

```text
engine: paddle-ernie-local
model_version: emotion-ernie-mini-local-v1
paddle_available: True
fallback_reason: null
```

如果看到 `engine: keyword-rules`，说明服务在规则兜底模式。查看 `fallback_reason` 处理依赖或模型路径问题。

## 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `NLP_EMOTION_MODEL_DIR` | `nlp-service/models/emotion-ernie-mini/best` | 本地 PaddleNLP 模型目录 |
| `NLP_PADDLE_DEVICE` | `auto` | `auto`、`cpu` 或 Paddle 支持的设备名 |
| `NLP_FEEDBACK_LOG_PATH` | `nlp-service/runtime/nlp_feedback.jsonl` | `/nlp/feedback` JSONL 记录路径 |

`runtime/` 是本地运行产物，已被 `.gitignore` 忽略。

## API 示例

### `POST /nlp/analyze`

请求：

```json
{
  "text": "今天在图书馆复习到很晚，感觉压力很大",
  "location_name": "图书馆"
}
```

响应字段：

```json
{
  "emotion_type": "stressed",
  "emotion_name": "压力",
  "sentiment": "negative",
  "temperature": -6,
  "safety_level": "normal",
  "confidence": 0.82,
  "model_version": "emotion-ernie-mini-local-v1",
  "suggested_content": "今天在图书馆复习到很晚，感觉压力很大",
  "safety_message": null
}
```

### `GET /nlp/model-version`

返回当前模型状态、能力列表和 `label_metadata`。前端和后端应复用这里的标签中文名、颜色、sentiment 和展示顺序。

### `POST /nlp/feedback`

请求：

```json
{
  "text": "今天很开心",
  "original_emotion": "happy",
  "corrected_emotion": "hopeful",
  "original_temperature": 7,
  "corrected_temperature": 6,
  "accepted": false
}
```

响应：

```json
{
  "accepted": false,
  "stored": true,
  "model_version": "emotion-ernie-mini-local-v1"
}
```

## 测试

测试不依赖 Paddle 模型，会 monkeypatch 模型状态到规则兜底模式，验证接口 contract。

```powershell
cd D:\Island_Delta\nlp-service
..\.venv\Scripts\python.exe -m unittest discover -s tests
```

评估已保存的 ERNIE 模型：

```powershell
cd D:\Island_Delta\nlp-service
..\.venv\Scripts\python.exe scripts\evaluate_paddlenlp_emotion_classifier.py --dataset data\campus_emotion_samples_v2.csv --model-dir models\emotion-ernie-mini\best --seed 42
```

当前评估记录见 `data/emotion_ernie_evaluation.md`。

模型真实运行验证：

```powershell
cd D:\Island_Delta\nlp-service
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

另开 PowerShell：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/nlp/model-version
Invoke-RestMethod http://127.0.0.1:8000/nlp/analyze `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"湖边晚风吹过来，心里松了一点","location_name":"湖边"}'
```

## 已知限制

- 当前模型训练数据仍以 `ai_generated` 样本为主，需要人工审核和真实校园表达补充。
- 模型可运行不等于模型质量达标，仍需独立的 classification report、confusion matrix 和误判样例分析。
- 附近温暖地点推荐需要后端地点与统计数据支持，本服务当前只返回基础聊天建议和留言草稿。
