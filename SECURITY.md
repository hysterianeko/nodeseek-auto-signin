# Security Policy

## Reporting a vulnerability

请不要在公开 Issue 中发布 Cookie、账号密码、验证码 API Key、Bot Token 或其他凭据。

如果发现会泄露凭据、绕过权限或导致自动任务失控的安全问题，请通过 GitHub 私下联系仓库维护者，并提供：

- 受影响的文件和版本
- 可复现步骤或最小示例
- 可能的影响范围
- 建议的修复方向（如果有）

## Credential hygiene

- 使用 GitHub Secrets、服务器环境变量或受限权限的 `.env` 保存凭据。
- `GH_PAT` 只授予目标仓库所需的 Actions variables 权限。
- Cookie 文件只在本机或容器挂载卷中保存，不要提交到 Git。
- 凭据一旦出现在日志、Issue、截图或提交历史中，应立即撤销并重新生成。
