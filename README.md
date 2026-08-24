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
- 支持自建 Turnstile 服务、YesCaptcha 和 CapSolver
- 支持 Cloudflare 挑战下的 `curl_cffi` 指纹回退
- 查询最近 30 天签到天数、鸡腿总数和日均收益
- Docker 持久化最新 Cookie，GitHub Actions 可回写仓库变量
- 支持 Telegram、Bark、PushPlus、邮件、Webhook 等通知渠道
- 支持固定时间或时间范围随机调度

## 快速开始

### 方式一：Docker Compose

```bash
git clone https://github.com/hysterianeko/nodeseek-auto-signin.git
cd nodeseek-auto-signin
cp .env.example .env
```

编辑 `.env`。如果已经有可用 Cookie，最小配置可以只有：

```env
NS_COOKIE=your_nodeseek_cookie
RUN_AT=08:00-10:59
```

启动并查看日志：

```bash
docker compose up -d --build
docker compose logs -f
```

容器会挂载 `./cookie`，重新登录成功后的 Cookie 会保存到 `cookie/NS_COOKIE.txt`。该文件已被 `.gitignore` 忽略，请不要手动提交。

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
SOLVER_TYPE=capsolver
API_BASE_URL=https://api.capsolver.com
CLIENTT_KEY=your_capsolver_api_key
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
turnstile_solver.py    自建 Turnstile 服务适配器
scheduler.py           Docker 定时调度器
notify.py              通知渠道集合
docker-compose.yml     Docker Compose 配置
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
