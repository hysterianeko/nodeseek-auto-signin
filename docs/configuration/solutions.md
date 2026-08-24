#### 自建 Turnstile 服务

适用于 CloudFreed、Cloudflyer 或其他兼容 `createTask` / `getTaskResult` 接口的自建服务。账号密码登录时配置：

```env
SOLVER_TYPE=turnstile
API_BASE_URL=http://127.0.0.1:3000
CLIENTT_KEY=your_client_key
```

请先确认服务端返回的任务状态和令牌格式与 `turnstile_solver.py` 一致。服务地址不可用或未配置时，脚本会跳过登录并保留原有 Cookie。

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

CapSolver 使用 Cloudflare Turnstile 的 `AntiTurnstileTaskProxyLess` 任务类型。若 Docker 当前 `.env` 中仍是 YesCaptcha 配置，需要同时替换 `SOLVER_TYPE`、`API_BASE_URL` 和 `CLIENTT_KEY`，然后重新创建容器。
