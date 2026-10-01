# NodeSeek Auto Sign-in

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-supported-2088FF?logo=githubactions&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

NodeSeek 自动签到工具，面向个人 VPS、Docker Compose、GitHub Actions 和青龙面板设计。

它把签到任务拆成几个清晰的阶段：优先使用 Cookie 签到，失效后再用账号密码完成 Turnstile 验证并刷新 Cookie，最后查询近期收益并发送通知。请求层还会在遇到 Cloudflare 挑战时自动尝试备用浏览器指纹，减少因单一指纹失效导致的任务中断。

## 功能

- Cookie 优先，Cookie 失效时按账号配置自动重新登录
- 支持多账号，Cookie 与 `USERn`/`PASSn` 可以混合使用
- 支持自建 Cloudflyer、YesCaptcha 和 CapSolver
- 支持 Cloudflare 挑战下的 `curl_cffi` 指纹回退
- 查询最近 30 天签到天数、鸡腿总数和日均收益
- Docker 持久化最新 Cookie，GitHub Actions 可回写仓库变量
- 支持 Telegram、Bark、PushPlus、邮件、Webhook 等通知渠道
- 支持固定时间或时间范围随机调度

## Docker Hub 镜像

已发布镜像：

```text
circling0635/nodeseek-signin:v1.0.0
```

镜像中已经包含 Python 运行环境、项目依赖和签到程序。其他服务器不需要克隆 GitHub 源码，也不需要执行 `docker build`；只需要安装 Docker，准备配置文件和 Cookie 持久化目录即可。

### 直接使用 Docker Run

创建运行目录：

```bash
mkdir -p /opt/nodeseek-signin/cookie
cd /opt/nodeseek-signin
touch .env cookie/NS_COOKIE.txt
chmod 600 .env cookie/NS_COOKIE.txt
```

编辑 `.env`。如果使用已有 Cookie，`.env` 可以先只填写运行时间：

```env
RUN_AT=08:00-10:59
```

然后把 NodeSeek Cookie 写入下面的文件：

```text
/opt/nodeseek-signin/cookie/NS_COOKIE.txt
```

多个 Cookie 可以用 `&` 或换行分隔。

拉取并启动容器：

```bash
docker pull circling0635/nodeseek-signin:v1.0.0

docker run -d \
  --name nodeseek-signin \
  --restart always \
  --env-file .env \
  -e IN_DOCKER=true \
  -v "$(pwd)/cookie:/app/cookie" \
  circling0635/nodeseek-signin:v1.0.0
```

启动参数说明：

| 参数 | 作用 |
| --- | --- |
| `-d` | 后台运行容器 |
| `--name nodeseek-signin` | 设置容器名称，便于查看日志和管理 |
| `--restart always` | Docker 或服务器重启后自动启动 |
| `--env-file .env` | 将 `.env` 中的配置传入容器 |
| `-e IN_DOCKER=true` | 启用 Docker 模式，让程序读写 `/app/cookie/NS_COOKIE.txt` |
| `-v "$(pwd)/cookie:/app/cookie"` | 将 Cookie 保存到宿主机，防止容器重建后丢失 |

### Docker 配置文件

Docker 模式下建议准备以下目录和文件：

```text
/opt/nodeseek-signin/
├── .env
└── cookie/
    └── NS_COOKIE.txt
```

`.env` 用于账号、验证码服务、运行时间和通知配置。`cookie/NS_COOKIE.txt` 用于保存已有 Cookie 和登录成功后自动刷新得到的 Cookie。

当前 Docker 模式会从 `cookie/NS_COOKIE.txt` 读取 Cookie。如果只把 `NS_COOKIE` 写入 `.env` 而没有写入 Cookie 文件，容器不会按 Docker 模式读取该值。

#### Cookie 模式

已有有效 Cookie 时，`.env` 最少可以填写：

```env
RUN_AT=08:00-10:59
```

将 Cookie 填入 `cookie/NS_COOKIE.txt`。这种模式通常不需要验证码服务。

#### 账号密码模式

没有可用 Cookie 时，在 `.env` 中填写账号密码和验证码服务：

```env
USER1=your_nodeseek_username
PASS1=your_nodeseek_password

SOLVER_TYPE=turnstile
API_BASE_URL=http://cloudflyer:3000
CLIENTT_KEY=change_me_to_a_random_string

RUN_AT=08:00-10:59
```

账号密码登录成功后，程序会把新 Cookie 写入 `cookie/NS_COOKIE.txt`，后续运行会优先使用该文件中的 Cookie。使用多个账号时继续添加 `USER2`/`PASS2`、`USER3`/`PASS3` 等配置。

验证码服务只在账号密码登录阶段使用。推荐使用自建 Cloudflyer（`SOLVER_TYPE=turnstile`）；`yescaptcha` 和 `capsolver` 仍可作为付费备选。完整参数见 [`docs/configuration/solutions.md`](docs/configuration/solutions.md)。

#### 通知配置

通知不是签到运行的必需项。需要通知时，在 `.env` 中增加对应变量，例如 Telegram：

```env
TG_BOT_TOKEN=your_telegram_bot_token
TG_USER_ID=your_telegram_user_id
```

其他通知渠道和变量见 [`docs/configuration/config.md`](docs/configuration/config.md)。

### 查看、停止和更新

```bash
# 查看实时日志
docker logs -f nodeseek-signin

# 查看容器状态
docker ps -a --filter name=nodeseek-signin

# 停止容器
docker stop nodeseek-signin

# 启动已停止的容器
docker start nodeseek-signin
```

更新到新镜像时，先拉取新镜像，再重新创建容器。重新创建时要保留原来的 `.env` 和 `cookie` 目录挂载：

```bash
docker pull circling0635/nodeseek-signin:v1.0.0
docker rm -f nodeseek-signin

docker run -d \
  --name nodeseek-signin \
  --restart always \
  --env-file .env \
  -e IN_DOCKER=true \
  -v "$(pwd)/cookie:/app/cookie" \
  circling0635/nodeseek-signin:v1.0.0
```

### 使用 Docker Compose

如果希望使用 Compose，先准备 `docker-compose.yml`、`.env` 和 `cookie` 目录：

```bash
mkdir -p /opt/nodeseek-signin/cookie
cd /opt/nodeseek-signin
touch .env cookie/NS_COOKIE.txt
```

Compose 文件应使用远程镜像，不要配置 `build: .`：

```yaml
services:
  cloudflyer:
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
    image: circling0635/nodeseek-signin:v1.0.0
    build: .
    container_name: nodeseek-signin
    environment:
      - IN_DOCKER=true
    env_file:
      - .env
    volumes:
      - ./cookie:/app/cookie
    depends_on:
      - cloudflyer
    restart: always
```

启动：

```bash
docker compose up -d --build
docker compose logs -f
```

### 常见问题

- **容器启动但暂时没有签到日志**：`scheduler.py` 会等待 `RUN_AT` 设置的下一个时间点，不一定启动后立即签到。
- **提示没有账号或 Cookie**：检查 `cookie/NS_COOKIE.txt` 是否存在且有内容，或者检查 `.env` 中的 `USER1`/`PASS1` 是否成对填写。
- **账号密码登录失败**：检查 `SOLVER_TYPE`、`API_BASE_URL` 和 `CLIENTT_KEY` 是否与验证码服务匹配。
- **重启后 Cookie 丢失**：确认启动命令包含 `-v "$(pwd)/cookie:/app/cookie"`，Compose 中确认有 `./cookie:/app/cookie`。
- **ARM 服务器无法启动镜像**：当前 `v1.0.0` 发布标签需要先确认目标服务器的 CPU 架构是否受支持；常见的 x86_64/amd64 服务器可优先使用。

## 其他部署方式

### 方式一：从源码使用 Docker Compose

```bash
git clone https://github.com/hysterianeko/nodeseek-auto-signin.git
cd nodeseek-auto-signin
cp .env.example .env
```

编辑 `.env` 后拉取镜像并启动：

```bash
docker compose pull
docker compose up -d
docker compose logs -f
```

### 方式二：GitHub Actions

Fork 或创建本仓库后，在 `Settings > Secrets and variables > Actions` 中添加配置，再从 `Actions` 页面手动触发一次工作流。工作流文件位于 `.github/workflows/blank.yml`，默认每天按 UTC+8 的时间运行。

至少需要以下两种配置之一：

```text
NS_COOKIE
```

或：

```text
USER1 / PASS1
```

账号密码模式还需要配置验证码服务。若希望登录后自动更新 `NS_COOKIE`，再添加 `GH_PAT`，并授予该 Token 对目标仓库 Actions variables 的读写权限。

### 方式三：青龙面板

```bash
ql repo https://github.com/hysterianeko/nodeseek-auto-signin.git
```

变量配置和定时规则见 [`docs/deployment/qinglong-panel.md`](docs/deployment/qinglong-panel.md)。

## 验证码配置

三种方案的选择只影响“账号密码登录”阶段，已有有效 Cookie 时不需要调用验证码服务。

### CapSolver

```env
USER1=your_username
PASS1=your_password
SOLVER_TYPE=turnstile
API_BASE_URL=http://cloudflyer:3000
CLIENTT_KEY=change_me_to_a_random_string
```

CapSolver 使用 `AntiTurnstileTaskProxyLess` 任务类型。项目沿用历史变量名 `CLIENTT_KEY`，这里填写 CapSolver API Key。

### YesCaptcha

```env
SOLVER_TYPE=yescaptcha
API_BASE_URL=https://api.yescaptcha.com
CLIENTT_KEY=your_yescaptcha_client_key
```

国内网络也可以使用 `https://cn.yescaptcha.com`。详细说明见 [`docs/configuration/solutions.md`](docs/configuration/solutions.md)。

### 自建 Turnstile 服务

```env
SOLVER_TYPE=turnstile
API_BASE_URL=http://127.0.0.1:3000
CLIENTT_KEY=your_client_key
```

完整变量说明见 [`docs/configuration/config.md`](docs/configuration/config.md)。

## 配置与部署文档

| 场景 | 文档 |
| --- | --- |
| 所有环境变量 | [`docs/configuration/config.md`](docs/configuration/config.md) |
| 验证码服务对比 | [`docs/configuration/solutions.md`](docs/configuration/solutions.md) |
| GitHub Actions | [`docs/deployment/github-actions.md`](docs/deployment/github-actions.md) |
| Docker Compose | [`docs/deployment/docker-compose.md`](docs/deployment/docker-compose.md) |
| 青龙面板 | [`docs/deployment/qinglong-panel.md`](docs/deployment/qinglong-panel.md) |
| Cloudflare Worker | [`docs/deployment/cloudflare-worker.md`](docs/deployment/cloudflare-worker.md) |

## 本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
python -m unittest discover -s tests -v
```

真实运行前请确认 `.env` 中的账号、Cookie 和验证码配置已经填写。下面的命令会实际访问 NodeSeek，不适合作为无账号的健康检查：

```bash
python test_run.py
```

## 项目结构

```text
nodeseek_sign.py       主签到、登录、统计和 Cookie 持久化流程
capsolver.py           CapSolver Turnstile 适配器
yescaptcha.py          YesCaptcha 适配器
turnstile_solver.py    自建 Cloudflyer / CloudFreed 适配器
scheduler.py           Docker 定时调度器
notify.py              通知渠道集合
docker-compose.yml     Docker Compose 配置
docker/cloudflyer/     轻量 Cloudflyer 构建文件
tests/                 不需要真实账号的回归测试
docs/                  配置和部署文档
```

## 安全与使用边界

不要把以下内容提交到 Git、Issue、日志或截图中：

- `.env`、Cookie 文件、NodeSeek 账号密码
- 验证码服务 API Key、Telegram Bot Token、`GH_PAT`

如果凭据曾经暴露，应立即撤销并重新生成。本项目仅供个人自动化和学习使用；使用前请遵守 NodeSeek、Cloudflare 以及验证码服务的条款，控制请求频率，不要进行批量滥用。

## 许可证

本项目以 MIT License 发布，详见 [`LICENSE`](LICENSE)。
