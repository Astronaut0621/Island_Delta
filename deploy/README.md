# 《孤岛温差》部署说明

## 环境要求

| 组件 | 版本要求 |
|------|---------|
| JDK | 17+ |
| Node.js | 18+ |
| Python | 3.10+ |
| Maven | 3.8+ |
| GaussDB / openGauss | 兼容 PostgreSQL 协议 |

## 1. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`

管理后台入口: `http://127.0.0.1:5173/admin/login`

默认管理员账号: `admin` / `admin123`

## 2. Spring Boot 后端启动

```bash
cd backend
mvn spring-boot:run
```

后端默认运行在 `http://127.0.0.1:8080`

### 环境变量配置

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DB_URL` | 数据库连接URL | `jdbc:h2:file:./data/islanddelta;AUTO_SERVER=TRUE` |
| `DB_USERNAME` | 数据库用户名 | `sa` |
| `DB_PASSWORD` | 数据库密码 | 空 |
| `DB_DRIVER` | 数据库驱动类 | `org.h2.Driver` |
| `NLP_SERVICE_URL` | NLP服务地址 | `http://127.0.0.1:8000` |
| `ADMIN_JWT_SECRET` | 管理员JWT密钥 | `island-delta-admin-secret-key-2026` |

### 连接 GaussDB / openGauss

使用 `gaussdb` profile 启动：

```bash
set DB_URL=jdbc:postgresql://<host>:<port>/island_delta
set DB_USER=<username>
set DB_PASS=<password>
mvn spring-boot:run -Dspring-boot.run.profiles=gaussdb
```

### H2 控制台（本地开发）

本地开发模式使用 H2 内嵌数据库，可通过浏览器访问：

`http://127.0.0.1:8080/h2-console`

JDBC URL: `jdbc:h2:file:./data/islanddelta;AUTO_SERVER=TRUE`

## 3. FastAPI NLP 服务启动

```bash
cd nlp-service
pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

NLP 服务默认运行在 `http://127.0.0.1:8000`

## 4. GaussDB 数据库初始化

### 使用 schema.sql 初始化

```bash
# GaussDB / openGauss 使用 gsql 客户端
gsql -d islanddelta -f database/schema.sql

# PostgreSQL 兼容模式使用 psql
psql -d islanddelta -f database/schema.sql
```

### 导入种子数据

```bash
gsql -d islanddelta -f database/seeds/seed_emotion_labels.sql
gsql -d islanddelta -f database/seeds/seed_locations.sql
gsql -d islanddelta -f database/seeds/seed_mock_emotions.sql
```

### 自动建表（开发模式）

使用 H2 本地开发时，JPA 的 `ddl-auto: update` 会自动根据实体类创建表结构，并自动创建默认管理员账号（admin/admin123）。

## 5. 完整启动顺序

1. 启动 GaussDB / openGauss 数据库（或使用 H2 本地开发）
2. 启动 Spring Boot 后端（端口 8080）
3. 启动 FastAPI NLP 服务（端口 8000）
4. 启动前端开发服务器（端口 5173）
5. 浏览器访问 `http://127.0.0.1:5173`

## 6. 验证服务是否正常

```bash
# 检查后端健康状态
curl http://127.0.0.1:8080/api/admin/login -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# 检查 NLP 服务
curl http://127.0.0.1:8000/docs

# 检查前端
curl http://127.0.0.1:5173
```

## 7. 生产部署建议

- 前端执行 `npm run build` 后将 `dist/` 目录部署到 Nginx
- 后端使用 `mvn package` 打包为 JAR，使用 `java -jar` 运行
- NLP 服务使用 `uvicorn` 或 Gunicorn 部署
- 数据库使用 GaussDB 云服务或 openGauss
- 配置 HTTPS 和反向代理
