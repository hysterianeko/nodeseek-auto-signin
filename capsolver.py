from curl_cffi import requests
import time
from typing import Optional


class CapSolverError(Exception):
    """CapSolver 验证码解决器错误基类。"""


class CapSolverSolver:
    """
    使用 CapSolver API 解决 Cloudflare Turnstile 验证码。

    CapSolver 的 API 使用 createTask/getTaskResult 两个接口，
    任务类型为 AntiTurnstileTaskProxyLess。
    """

    def __init__(
        self,
        api_base_url: str = "https://api.capsolver.com",
        client_key: str = "",
        max_retries: int = 20,
        retry_interval: int = 3,
        timeout: int = 60,
    ):
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
        verbose: bool = False,
    ) -> str:
        """创建 Turnstile 任务并返回验证令牌。"""
        if not self.client_key:
            raise CapSolverError("未配置 CapSolver API Key")

        if verbose:
            print("正在创建 CapSolver 验证任务...")

        task_id = self._create_task(url, sitekey, action, verbose)
        token = self._get_task_result(task_id, verbose)

        if verbose:
            print(f"验证码解决成功: {token[:30]}...{token[-10:] if len(token) > 30 else ''}")

        return token

    def _create_task(
        self,
        url: str,
        sitekey: str,
        action: Optional[str],
        verbose: bool,
    ) -> str:
        task = {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": url,
            "websiteKey": sitekey,
        }
        if action:
            task["metadata"] = {"action": action}

        payload = {
            "clientKey": self.client_key,
            "task": task,
        }

        try:
            response = requests.post(
                self.create_task_url,
                json=payload,
                timeout=self.timeout,
                impersonate="chrome110",
            )
            response.raise_for_status()
            result = response.json()
        except (requests.exceptions.RequestException, ValueError) as exc:
            raise CapSolverError(f"创建验证码任务请求失败: {exc}") from exc

        if result.get("errorId", 0) != 0:
            description = result.get("errorDescription", "未知错误")
            raise CapSolverError(f"创建验证码任务失败: {description}")

        task_id = result.get("taskId")
        if not task_id:
            raise CapSolverError("创建验证码任务失败: 响应中没有 taskId")

        if verbose:
            print(f"成功创建 CapSolver 任务，ID: {task_id}")
        return task_id

    def _get_task_result(self, task_id: str, verbose: bool) -> str:
        payload = {
            "clientKey": self.client_key,
            "taskId": task_id,
        }

        for attempt in range(1, self.max_retries + 1):
            if verbose:
                print(f"尝试获取 CapSolver 任务结果 ({attempt}/{self.max_retries})...")

            try:
                response = requests.post(
                    self.get_result_url,
                    json=payload,
                    timeout=self.timeout,
                    impersonate="chrome110",
                )
                response.raise_for_status()
                result = response.json()
            except (requests.exceptions.RequestException, ValueError) as exc:
                raise CapSolverError(f"获取验证码结果请求失败: {exc}") from exc

            if result.get("errorId", 0) != 0:
                description = result.get("errorDescription", "未知错误")
                raise CapSolverError(f"获取验证码结果失败: {description}")

            status = result.get("status")
            if status == "ready":
                token = result.get("solution", {}).get("token")
                if not token:
                    raise CapSolverError("验证码结果中没有 token")
                return token

            if status != "processing":
                raise CapSolverError(f"CapSolver 返回未知任务状态: {status or '空'}")

            if attempt < self.max_retries:
                if verbose:
                    print(f"任务处理中，等待 {self.retry_interval} 秒后重试...")
                time.sleep(self.retry_interval)

        raise CapSolverError(f"达到最大重试次数 ({self.max_retries})，验证码解决超时")
