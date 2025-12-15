import unittest
from unittest.mock import MagicMock, patch

import scan_kpop_doxhunter as scan
from requests.exceptions import RequestException
from pathlib import Path


class ScanKpopDoxhunterTests(unittest.TestCase):
    def setUp(self):
        self._api_key = scan.API_KEY
        self._queries = scan.QUERIES
        self._existing_reports = {p.name for p in Path("reports").glob("dox_report_*.csv")}
        scan.API_KEY = "TEST_KEY"
        scan.QUERIES = ["felix maison test"]

    def tearDown(self):
        scan.API_KEY = self._api_key
        scan.QUERIES = self._queries
        current = {p.name for p in Path("reports").glob("dox_report_*.csv")}
        new_files = current - self._existing_reports
        for name in new_files:
            Path("reports", name).unlink(missing_ok=True)

    def _mock_response(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "Felix maison Seoul",
                        "description": "adresse Felix quartier Coree du Sud",
                    },
                }
            ]
        }
        return mock_resp

    @patch("scan_kpop_doxhunter.requests.get")
    def test_ml_dox_hunter_returns_scored_df(self, mock_get):
        mock_get.return_value = self._mock_response()

        df = scan.ml_dox_hunter()

        self.assertFalse(df.empty)
        self.assertIn("dox_score", df.columns)
        self.assertIn("video_id", df.columns)
        self.assertGreaterEqual(df["dox_score"].iloc[0], scan.MIN_DOX_SCORE)

    @patch("scan_kpop_doxhunter.requests.get", side_effect=RequestException("network down"))
    def test_ml_dox_hunter_exits_on_all_failures(self, mock_get):
        scan.API_KEY = "TEST_KEY"
        scan.QUERIES = ["felix maison test"]

        with self.assertRaises(SystemExit):
            scan.ml_dox_hunter()


if __name__ == "__main__":
    unittest.main()
