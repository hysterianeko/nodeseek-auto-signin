# Docker Compose 部署

Compose 默认只启动签到容器。验证码可以指向远程 Cloudflyer；本机 Chromium sidecar 用 `--profile local-solver` 按需启动。签到镜像可以继续使用 Docker Hub 上的 `circling0635/nodeseek-signin:v1.0.1`。

## 1. 准备目录

服务器安装并启动 Docker 及 Docker Compose Plugin 后，创建运行目录：

```bash
mkdir -p /opt/nodeseek-signin/cookie
cd /opt/nodeseek-signin
touch .env cookie/NS_COOKIE.txt
chmod 600 .env cookie/NS_COOKIE.txt
```

从仓库复制 `docker-compose.yml` 和 `docker/cloudflyer/` 目录，或直接使用下面的 Compose 内容（Cloudflyer 构建上下文仍需要 `docker/cloudflyer/`）：

```yaml
services:
  cloudflyer:
    profiles: ["local-solver"]
    build:
      context: ./docker/cloudflyer
    image: nodeseek-cloudflyer:latest
    container_name: cloudflyer
    restart: unless-stopped
    environment:
      TZ: Asia/Shanghai
      CLIENTT_KEY: ${CLIENTT_KEY}
    ports:
      - "127.0.0.1:3000:3000"
    shm_size: "256mb"

  nodeseek-signin:
    image: circling0635/nodeseek-signin:v1.0.1
    container_name: nodeseek-signin
    environment:
      - IN_DOCKER=true
    env_file:
      - .env
    volumes:
      - ./cookie:/app/cookie
    restart: always
```

## 2. 配置 `.env`

### 已有 Cookie

如果已有可用 Cookie，在 `.env` 中至少填写：

```env
RUN_AT=08:00-10:59
```

然后将 Cookie 写入：

```text
/opt/nodeseek-signin/cookie/NS_COOKIE.txt
```

多个账户的 Cookie 可以使用 `&` 或换行分隔。当前 Docker 模式从 `cookie/NS_COOKIE.txt` 读取 Cookie；不要只把 `NS_COOKIE` 写入 `.env` 后期待容器自动读取。

### 账号密码

如果没有可用 Cookie，在 `.env` 中填写账号密码和验证码服务配置：

```env
USER1=your_nodeseek_username
PASS1=your_nodeseek_password

SOLVER_TYPE=turnstile
API_BASE_URL=https://challenge.cool.pp.ua
CLIENTT_KEY=same_key_as_remote_cloudflyer

RUN_AT=08:00-10:59
```

登录成功后，程序会将 Cookie 保存到 `cookie/NS_COOKIE.txt`，后续任务会优先读取这个文件。多个账号可以继续配置 `USER2`/`PASS2`、`USER3`/`PASS3` 等变量。

验证码服务只在账号密码登录阶段需要。已有有效 Cookie 时通常不需要配置验证码服务。可选服务和完整参数见 [`docs/configuration/solutions.md`](../configuration/solutions.md)。

### 通知

通知是可选功能。例如 Telegram：

```env
TG_BOT_TOKEN=your_telegram_bot_token
TG_USER_ID=your_telegram_user_id
```

其他通知变量见 [`docs/configuration/config.md`](../configuration/config.md)。

## 3. 拉取并启动

```bash
# 默认只启动签到容器，使用远程 Cloudflyer
docker compose pull
docker compose up -d

# 如果要在本机跑 Chromium sidecar
# docker compose --profile local-solver up -d --build
```

查看日志：

```bash
docker compose logs -f
```

调度器会等待 `RUN_AT` 设置的下一个时间点执行签到，容器启动后不一定立即产生签到日志。

## 4. 管理服务

```bash
# 查看状态
docker compose ps

# 重启容器
docker compose restart

# 停止并删除容器（不会删除 .env 或 cookie 目录）
docker compose down
```

更新镜像后重新创建容器：

```bash
docker compose pull
docker compose up -d
```

## 5. 目录说明

```text
/opt/nodeseek-signin/
├── docker-compose.yml       # Compose 服务配置；本机 sidecar 走 local-solver profile
├── docker/cloudflyer/       # 轻量 Cloudflyer 构建目录
├── .env                     # 账号、验证码、调度和通知配置
└── cookie/
    └── NS_COOKIE.txt        # Cookie 持久化文件
```

`.env` 和 `cookie/NS_COOKIE.txt` 包含敏感信息，不要提交到 Git、Issue 或公开截图中。
