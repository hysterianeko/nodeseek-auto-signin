# Repository Guidelines

## Project Structure & Module Organization

- `nodeseek_sign.py`: main sign-in workflow (cookie/login, captcha solving, optional notifications).
- `scheduler.py`: time-window scheduler used by Docker/local runs.
- `notify.py`: notification backends (loaded dynamically by `nodeseek_sign.py`).
- `*_solver.py` (`turnstile_solver.py`, `yescaptcha.py`, `capsolver.py`): captcha integrations. `turnstile_solver.py` talks to self-hosted Cloudflyer/CloudFreed.
- `docs/`: configuration + deployment guides (`docs/configuration/`, `docs/deployment/`).
- `cookie/`: runtime cookie persistence (do not commit real cookies).
- `.github/workflows/blank.yml`: GitHub Actions entrypoint (`python nodeseek_sign.py`).
- `Dockerfile`, `docker-compose.yml`, `docker/cloudflyer/`: containerized execution. Cloudflyer sidecar is optional via Compose profile `local-solver`.

## Build, Test, and Development Commands

- `python3 -m venv .venv && source .venv/bin/activate`: create/activate a local venv.
- `pip install -r requirements.txt`: install runtime deps (`curl_cffi`, `requests`, etc.).
- `cp .env.example .env`: create local config (edit values; keep secrets out of git).
- `python test_run.py`: quick smoke-run to validate config + sign-in + notifications.
- `python nodeseek_sign.py`: run a single sign-in (useful for debugging).
- `docker compose up -d`: start the scheduled sign-in container (remote Cloudflyer by default). Use `--profile local-solver` to also start a local Chromium solver; see logs with `docker compose logs -f`.

## Coding Style & Naming Conventions

- Python: 4-space indentation; prefer type hints; follow existing patterns:
  - constants in `UPPER_SNAKE_CASE` (e.g., `IMPERSONATE_VERSION`)
  - helpers prefixed with `_` (e.g., `_get_env_str`)
  - modules/scripts in `snake_case.py`
- Keep configuration in env vars (`.env` / GitHub Secrets+Vars). Never print or log raw cookies/tokens.

## Testing Guidelines

- This repo currently relies on a runnable smoke script (`test_run.py`) rather than a full unit test suite.
- When changing auth/captcha flow, validate at least:
  - Cookie mode (`NS_COOKIE`) and user/pass mode (`USER1`/`PASS1`)
  - the selected solver (`SOLVER_TYPE`) and notification path (if enabled)

## Commit & Pull Request Guidelines

- Commit messages in history are short and imperative (e.g., `Update ...`, `Add ...`, `Fix ...`; some Chinese messages exist). Match that style and keep commits scoped.
- PRs should include:
  - a clear description of behavior change and how to test locally/Actions
  - docs updates in `docs/` when env vars, deployment, or solvers change
  - redacted logs/screenshots when troubleshooting auth/captcha issues

## Security & Configuration Tips

- Do not commit `.env`, cookies, PATs, or solver keys. Use `.env.example` and GitHub Secrets/Vars.
- If credentials are exposed, rotate them immediately (NodeSeek cookie, `GH_PAT`, solver keys).

