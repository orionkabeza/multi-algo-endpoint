import json
import shutil
import tempfile
import unittest
from pathlib import Path

import app as app_module


class SaveEndpointTests(unittest.TestCase):
    def setUp(self):
        self._real_data_dir = app_module.DATA_DIR
        app_module.DATA_DIR = Path(tempfile.mkdtemp())
        self.client = app_module.app.test_client()

    def tearDown(self):
        shutil.rmtree(app_module.DATA_DIR, ignore_errors=True)
        app_module.DATA_DIR = self._real_data_dir

    def test_save_without_name_generates_timestamped_file(self):
        payload = {"algo": "linear_search", "seconds": 0.001}
        resp = self.client.post("/save", json=payload)
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["data"], payload)

        saved_path = Path(body["saved_path"])
        self.assertTrue(saved_path.exists())
        self.assertEqual(json.loads(saved_path.read_text()), payload)
        self.assertTrue(saved_path.name.endswith(".json"))

    def test_save_with_name_uses_that_filename(self):
        resp = self.client.post("/save?name=result", json={"n": 1})
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["filename"], "result.json")
        self.assertTrue((app_module.DATA_DIR / "result.json").exists())

    def test_save_with_name_already_ending_in_json(self):
        resp = self.client.post("/save?name=result.json", json={"n": 1})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["filename"], "result.json")

    def test_path_traversal_in_name_is_sanitized(self):
        resp = self.client.post("/save?name=../../../etc/passwd", json={"n": 1})
        self.assertEqual(resp.status_code, 201)
        saved_path = Path(resp.get_json()["saved_path"])
        # must stay inside the sandboxed data dir, not escape it
        self.assertEqual(saved_path.parent.resolve(), app_module.DATA_DIR.resolve())

    def test_name_that_sanitizes_to_empty_is_rejected(self):
        resp = self.client.post("/save?name=../../..", json={"n": 1})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    def test_missing_json_body_returns_400(self):
        resp = self.client.post("/save", data="not json", content_type="text/plain")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.get_json())

    def test_invalid_json_body_returns_400(self):
        resp = self.client.post("/save", data="{not valid json", content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_get_not_allowed(self):
        resp = self.client.get("/save")
        self.assertEqual(resp.status_code, 405)

    def test_save_accepts_json_array(self):
        payload = [1, 2, 3]
        resp = self.client.post("/save", json=payload)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.get_json()["data"], payload)


if __name__ == "__main__":
    unittest.main()
