# NodeSeek 自动签到 Docker 镜像

镜像：

```text
circling0635/nodeseek-signin:v1.0.0
```

镜像已经包含运行所需的 Python、依赖和签到程序。其他服务器只需要安装 Docker，准备 `.env` 和 Cookie 文件即可，不需要克隆源码或执行 `docker build`。

## 快速启动

创建配置目录：

```bash
mkdir -p /opt/nodeseek-signin/cookie
cd /opt/nodeseek-signin
touch .env cookie/NS_COOKIE.txt
chmod 600 .env cookie/NS_COOKIE.txt
```

拉取镜像：

```bash
docker pull circling0635/nodeseek-signin:v1.0.0
```

启动容器：

```bash
docker run -d \
  --name nodeseek-signin \
  --restart always \
  --env-file .env \
  -e IN_DOCKER=true \
  -v "$(pwd)/cookie:/app/cookie" \
  circling0635/nodeseek-signin:v1.0.0
```

启动参数说明：

| 参数 | 说明 |
| --- | --- |
| `--env-file .env` | 将 `.env` 配置传入容器 |
| `-e IN_DOCKER=true` | 启用 Docker 模式 |
| `-v "$(pwd)/cookie:/app/cookie"` | 持久化 Cookie，容器重建后不会丢失 |
| `--restart always` | Docker 或服务器重启后自动启动 |

查看日志：

```bash
docker logs -f nodeseek-signin
```

## 配置文件

目录结构：

```text
/opt/nodeseek-signin/
├── .env
└── cookie/
    └── NS_COOKIE.txt
```

### `.env`

`.env` 用于填写运行时间、账号密码、验证码服务和通知配置。

#### Cookie 模式

如果已经有可用的 NodeSeek Cookie，`.env` 最少填写：

```env
RUN_AT=08:00-10:59
```

然后把 Cookie 写入：

```text
cookie/NS_COOKIE.txt
```

多个 Cookie 可以使用 `&` 或换行分隔。

Docker 模式从 `cookie/NS_COOKIE.txt` 读取 Cookie，不要只把 `NS_COOKIE` 写入 `.env`。Cookie 失效后，如果同时配置了账号密码，程序会尝试重新登录并更新这个文件。

#### 账号密码模式

如果没有可用 Cookie，在 `.env` 中填写：

```env
USER1=your_nodeseek_username
PASS1=your_nodeseek_password

SOLVER_TYPE=capsolver
API_BASE_URL=https://api.capsolver.com
CLIENTT_KEY=your_capsolver_api_key

RUN_AT=08:00-10:59
```

账号密码登录需要验证码服务。已有有效 Cookie 时通常不需要配置 `SOLVER_TYPE`、`API_BASE_URL` 和 `CLIENTT_KEY`。

多个账号依次添加：

```env
USER2=another_username
PASS2=another_password
USER3=third_username
PASS3=third_password
```

`RUN_AT` 支持两种格式：

```env
# 每天固定时间执行
RUN_AT=09:30

# 每天在时间范围内随机执行一次
RUN_AT=08:00-10:59
```

#### 通知（可选）

例如使用 Telegram：

```env
TG_BOT_TOKEN=your_telegram_bot_token
TG_USER_ID=your_telegram_user_id
```

不需要通知时可以不填写任何通知变量。

### `cookie/NS_COOKIE.txt`

这个文件用于保存 NodeSeek Cookie。它可以在启动前手动填写，也会在账号密码登录成功后由程序自动更新。必须挂载宿主机的 `cookie` 目录：

```bash
-v "$(pwd)/cookie:/app/cookie"
```

否则容器删除或重建后，Cookie 可能丢失。

## 常用管理命令

```bash
# 查看状态
docker ps -a --filter name=nodeseek-signin

# 停止
docker stop nodeseek-signin

# 再次启动
docker start nodeseek-signin

# 删除容器（不会删除宿主机上的 .env 和 cookie）
docker rm -f nodeseek-signin
```

更新镜像后重新创建容器：

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

容器启动后，调度器会等待 `RUN_AT` 设置的下一个时间点，不一定会立即签到。

## 安全提示

`.env` 和 `cookie/NS_COOKIE.txt` 包含敏感信息，不要提交到 Git、发布到 Issue 或放入公开截图。账号密码、Cookie、验证码服务 Key 和通知 Token 泄露后应立即更换。
