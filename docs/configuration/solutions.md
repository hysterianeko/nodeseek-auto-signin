#### 自建 Cloudflyer 服务（推荐）

适用于 [Cloudflyer](https://github.com/cloudflyer-project/cloudflyer-oss) 以及仍兼容 `createTask` / `getTaskResult` 的 CloudFreed 接口。账号密码登录时配置：

```env
SOLVER_TYPE=turnstile
API_BASE_URL=http://cloudflyer:3000
CLIENTT_KEY=change_me_to_a_random_string
```

`SOLVER_TYPE` 也可以写成 `cloudflyer`。`CLIENTT_KEY` 是签到容器和 Cloudflyer 之间的共享口令，两边必须一致。

小内存签到机可以把 Cloudflyer 放到另一台机器，签到容器只改 API 地址：

```env
SOLVER_TYPE=turnstile
API_BASE_URL=https://challenge.cool.pp.ua
CLIENTT_KEY=same_key_as_remote_cloudflyer
```

本仓库 Compose 默认不再启动本机 Chromium。如果要在本机跑 sidecar：

```bash
docker compose --profile local-solver up -d
```

然后把 `API_BASE_URL` 改回 `http://cloudflyer:3000`。

- 远程求解器：`https://challenge.cool.pp.ua`
- 本机 sidecar 内部地址：`http://cloudflyer:3000`
- 本机宿主机调试地址：`http://127.0.0.1:3000`

首次启动会构建 Chromium 环境，并常驻一个浏览器实例。服务地址不可用或未配置时，脚本会跳过登录并保留原有 Cookie。

建议配置：

| 场景 | 内存 | 说明 |
| --- | --- | --- |
| 只跑 Cookie 签到 | 256MB+ | 不需要启动 Cloudflyer |
| 账号密码 + 轻量 Cloudflyer | 2GB RAM（可用 1GB 加 1-2GB swap） | 本仓库默认方案，常驻 Chromium 约 400-800MB |
| 官方 `jackzzs/cloudflyer` 桌面镜像 | 4GB+ | 带 VNC 桌面，不适合小内存 VPS |

可以部署到任意能跑 Docker 的 x86_64 Linux 机器。1 核 2G 的小 VPS 足够；这台 1.7G 机器需要开 swap 才能稳住 Chromium。

#### YesCaptcha 商业服务

1. 访问 [YesCaptcha](https://yescaptcha.com/i/k2Hy3Q) 注册账号
2. 注册后联系客服可免费获得余额（约可使用60次登录）
3. 配置以下环境变量：

| 变量名称 | 说明 |
| :------: | :--- |
| `CLIENTT_KEY` | YesCaptcha 的 API 密钥 |
| `USER1`/`USER2`... | NodeSeek 论坛用户名 |
| `PASS1`/`PASS2`... | NodeSeek 论坛密码 |
| `SOLVER_TYPE` | 设置为 `yescaptcha` |

> **提示**：YesCaptcha 提供两个服务节点，可根据网络情况选择：
> - 国际节点：`https://api.yescaptcha.com`（默认）
> - 国内节点：`https://cn.yescaptcha.com`

#### CapSolver 商业服务

1. 访问 [CapSolver](https://www.capsolver.com/) 注册并充值
2. 在控制台获取 API Key
3. 配置以下环境变量：

| 变量名称 | 说明 |
| :------: | :--- |
| `CLIENTT_KEY` | CapSolver API Key（项目沿用该变量名） |
| `API_BASE_URL` | CapSolver API 地址，填写 `https://api.capsolver.com` |
| `USER1`/`USER2`... | NodeSeek 论坛用户名 |
| `PASS1`/`PASS2`... | NodeSeek 论坛密码 |
| `SOLVER_TYPE` | 设置为 `capsolver` |

CapSolver 使用 Cloudflare Turnstile 的 `AntiTurnstileTaskProxyLess` 任务类型。这是付费备选方案；日常推荐使用上面的自建 Cloudflyer。
