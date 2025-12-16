import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import scan_kpop_doxhunter as scan
from requests.exceptions import RequestException


class ScanKpopDoxhunterTests(unittest.TestCase):
    def setUp(self):
        self._api_key = os.environ.get("YOUTUBE_API_KEY")
        self._queries = scan.QUERIES
        self._existing_reports = {p.name for p in Path("reports").glob("dox_report_*.csv")}
        os.environ["YOUTUBE_API_KEY"] = "TEST_KEY"
        scan.QUERIES = ["felix maison test"]

    def tearDown(self):
        if self._api_key is None:
            os.environ.pop("YOUTUBE_API_KEY", None)
        else:
            os.environ["YOUTUBE_API_KEY"] = self._api_key
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
        scan.QUERIES = ["felix maison test"]

        with self.assertRaises(SystemExit):
            scan.ml_dox_hunter()

    def _quota_response(self, status_code=403):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.raise_for_status.side_effect = RequestException(response=mock_resp)
        return mock_resp

    @patch("scan_kpop_doxhunter.requests.get")
    def test_ml_dox_hunter_saves_partial_then_exits_on_quota(self, mock_get):
        # First query succeeds, second hits quota and stops after saving partial results
        success = self._mock_response()
        quota = self._quota_response(403)
        mock_get.side_effect = [success, quota]
        scan.QUERIES = ["felix maison test", "felix quota test"]

        before = {p.name for p in Path("reports").glob("dox_report_*.csv")}
        with self.assertRaises(SystemExit):
            scan.ml_dox_hunter()

        after = {p.name for p in Path("reports").glob("dox_report_*.csv")}
        new_files = list(after - before)
        self.assertTrue(new_files, "No report saved before quota exit")
        latest = Path("reports", sorted(new_files)[-1])
        df_saved = pd.read_csv(latest)
        self.assertFalse(df_saved.empty)
        self.assertIn("dox_score", df_saved.columns)

    @patch("scan_kpop_doxhunter.requests.get")
    def test_ml_dox_hunter_ignores_non_dict_json(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = ["not-a-dict"]
        mock_get.return_value = mock_resp
        df = scan.ml_dox_hunter()
        self.assertTrue(df.empty)


if __name__ == "__main__":
    unittest.main()
