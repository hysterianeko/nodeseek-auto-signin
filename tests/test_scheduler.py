import os
import unittest
from unittest.mock import patch

from scheduler import _is_valid_clock, get_run_config


class SchedulerConfigTests(unittest.TestCase):
    def test_valid_clock(self):
        self.assertTrue(_is_valid_clock("00:00"))
        self.assertTrue(_is_valid_clock("23:59"))
        self.assertFalse(_is_valid_clock("24:00"))
        self.assertFalse(_is_valid_clock("8:00"))

    def test_fixed_schedule(self):
        with patch.dict(os.environ, {"RUN_AT": " 09:30 "}):
            self.assertEqual(get_run_config(), ("fixed", "09:30"))

    def test_range_schedule(self):
        with patch.dict(os.environ, {"RUN_AT": "09:00-10:59"}):
            self.assertEqual(get_run_config(), ("range", "09:00-10:59"))

    def test_invalid_schedule_uses_default(self):
        with patch.dict(os.environ, {"RUN_AT": "25:00-26:00"}):
            self.assertEqual(get_run_config(), ("range", "08:00-10:59"))


if __name__ == "__main__":
    unittest.main()
