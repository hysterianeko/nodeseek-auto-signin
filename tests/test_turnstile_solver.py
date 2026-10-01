import unittest
from unittest.mock import Mock, patch

from turnstile_solver import TurnstileSolver, TurnstileSolverError


class TurnstileSolverTests(unittest.TestCase):
    def setUp(self):
        self.solver = TurnstileSolver(
            api_base_url="http://cloudflyer:3000/",
            client_key="test-key",
            max_retries=3,
            retry_interval=0,
            timeout=5,
        )

    def test_strips_trailing_slash(self):
        self.assertEqual(self.solver.create_task_url, "http://cloudflyer:3000/createTask")
        self.assertEqual(self.solver.get_result_url, "http://cloudflyer:3000/getTaskResult")

    def test_requires_client_key(self):
        solver = TurnstileSolver(api_base_url="http://127.0.0.1:3000", client_key="")
        with self.assertRaises(TurnstileSolverError):
            solver.solve("https://www.nodeseek.com/signIn.html", "sitekey")

    @patch("turnstile_solver.requests.post")
    def test_solve_cloudflyer_token(self, post):
        create_resp = Mock()
        create_resp.status_code = 200
        create_resp.json.return_value = {"taskId": "task-1"}

        pending_resp = Mock()
        pending_resp.status_code = 200
        pending_resp.json.return_value = {"status": "processing", "result": None}

        done_resp = Mock()
        done_resp.status_code = 200
        done_resp.json.return_value = {
            "status": "completed",
            "result": {
                "success": True,
                "code": 200,
                "response": {"token": "0.turnstile-token"},
            },
        }
        post.side_effect = [create_resp, pending_resp, done_resp]

        token = self.solver.solve(
            url="https://www.nodeseek.com/signIn.html",
            sitekey="0x4AAAAAAAaNy7leGjewpVyR",
        )
        self.assertEqual(token, "0.turnstile-token")
        self.assertEqual(post.call_count, 3)
        self.assertEqual(post.call_args_list[0].kwargs["json"]["type"], "Turnstile")
        self.assertEqual(post.call_args_list[0].kwargs["json"]["siteKey"], "0x4AAAAAAAaNy7leGjewpVyR")

    @patch("turnstile_solver.requests.post")
    def test_failed_task_raises(self, post):
        create_resp = Mock()
        create_resp.status_code = 200
        create_resp.json.return_value = {"taskId": "task-1"}

        done_resp = Mock()
        done_resp.status_code = 200
        done_resp.json.return_value = {
            "status": "completed",
            "result": {"success": False, "error": "CAPTCHA_FAIL"},
        }
        post.side_effect = [create_resp, done_resp]

        with self.assertRaises(TurnstileSolverError):
            self.solver.solve("https://www.nodeseek.com/signIn.html", "sitekey")


if __name__ == "__main__":
    unittest.main()
