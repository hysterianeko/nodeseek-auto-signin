import time
from typing import Dict, Optional, Union

import requests


class TurnstileSolverError(Exception):
    """Turnstile 解决器错误基类。"""


class TurnstileSolver:
    """
    自建 Turnstile 服务客户端。

    兼容 CloudFreed / Cloudflyer 的 createTask / getTaskResult 接口。
    """

    def __init__(
        self,
        api_base_url: str,
        client_key: str,
        max_retries: int = 20,
        retry_interval: int = 6,
        timeout: int = 60,
    ):
        if not api_base_url:
            raise TurnstileSolverError("未配置 API_BASE_URL")

        self.api_base_url = api_base_url.rstrip("/")
        self.create_task_url = f"{self.api_base_url}/createTask"
        self.get_result_url = f"{self.api_base_url}/getTaskResult"
        self.client_key = client_key
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.timeout = timeout

    def solve(
        self,
        url: str,
        sitekey: str,
        action: Optional[str] = None,
        user_agent: Optional[str] = None,
        proxy: Optional[Dict[str, Union[str, int]]] = None,
        verbose: bool = False,
    ) -> str:
        if not self.client_key:
            raise TurnstileSolverError("未配置 CLIENTT_KEY")

        if verbose:
            print("正在创建 Turnstile 验证任务...")

        task_id = self._create_task(url, sitekey, action, user_agent, proxy, verbose)
        token = self._get_task_result(task_id, verbose)

        if verbose:
            preview = f"{token[:30]}...{token[-10:]}" if len(token) > 40 else token
            print(f"验证码解决成功: {preview}")

        return token

    def _create_task(
        self,
        url: str,
        sitekey: str,
        action: Optional[str],
        user_agent: Optional[str],
        proxy: Optional[Dict[str, Union[str, int]]],
        verbose: bool,
    ) -> str:
        payload = {
            "clientKey": self.client_key,
            "type": "Turnstile",
            "url": url,
            "siteKey": sitekey,
        }
        if action:
            payload["action"] = action
        if user_agent:
            payload["userAgent"] = user_agent
        if proxy:
            payload["proxy"] = proxy

        result = self._post_json(self.create_task_url, payload, "创建验证码任务")
        if verbose:
            print(f"创建任务响应: {result}")

        task_id = result.get("taskId") or result.get("task_id")
        if not task_id:
            raise TurnstileSolverError(f"未能获取到 taskId: {result}")
        return task_id

    def _get_task_result(self, task_id: str, verbose: bool) -> str:
        payload = {
            "clientKey": self.client_key,
            "taskId": task_id,
        }

        for attempt in range(1, self.max_retries + 1):
            if verbose:
                print(f"正在获取 Turnstile 验证结果，尝试 {attempt}/{self.max_retries}...")

            result = self._post_json(self.get_result_url, payload, "获取验证码结果")
            status = (result.get("status") or "").lower()

            if status in {"processing", "idle", "pending"}:
                if attempt < self.max_retries:
                    if verbose:
                        print(f"任务处理中，等待 {self.retry_interval} 秒后重试...")
                    time.sleep(self.retry_interval)
                continue

            if status != "completed":
                if verbose:
                    print(f"获取结果响应内容: {result}")
                raise TurnstileSolverError(f"验证任务返回未知状态: {status or '空'}")

            token = self._extract_token(result)
            if not token:
                raise TurnstileSolverError(f"未找到验证令牌: {result}")
            return token

        raise TurnstileSolverError(f"达到最大重试次数 ({self.max_retries})，验证失败")

    def _post_json(self, endpoint: str, payload: dict, action_name: str) -> dict:
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise TurnstileSolverError(f"{action_name}请求失败: {exc}") from exc

        try:
            result = response.json()
        except ValueError as exc:
            raise TurnstileSolverError(
                f"{action_name}返回了无法解析的响应 ({response.status_code}): {response.text[:300]}"
            ) from exc

        if response.status_code >= 400:
            detail = result.get("detail") or result.get("error") or result
            raise TurnstileSolverError(f"{action_name}失败: {detail}")

        if result.get("errorId"):
            raise TurnstileSolverError(
                f"{action_name}失败: {result.get('errorDescription') or result}"
            )

        return result

    @staticmethod
    def _extract_token(result: dict) -> Optional[str]:
        result_obj = result.get("result") or {}
        if result_obj.get("success") is False:
            error = result_obj.get("error") or result_obj
            raise TurnstileSolverError(f"验证任务失败: {error}")

        response_obj = result_obj.get("response", {})
        if isinstance(response_obj, dict):
            return response_obj.get("token") or response_obj.get("value")
        if isinstance(response_obj, str) and response_obj:
            return response_obj
        return None
