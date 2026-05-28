import sys
import os
import unittest
import shutil

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from services.local_db import DB_PATH, get_db_connection

class TestAuthFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We can run tests on a temporary test database to keep promptpilot.db clean
        cls.original_db = DB_PATH
        cls.test_db_path = DB_PATH + ".test"
        
        # Override the DB_PATH in local_db module dynamically for testing
        import services.local_db as local_db
        local_db.DB_PATH = cls.test_db_path
        # Re-initialize the test database
        local_db.init_db()
        
        cls.client = TestClient(app)
        cls.test_email = "tester_auth@promptpilot.ai"
        cls.test_password = "securepassword123"

    @classmethod
    def tearDownClass(cls):
        # Remove test database
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception as e:
                print(f"Error removing test database file: {e}")

    def test_01_signup_success(self):
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        res = self.client.post("/api/v1/auth/signup", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], self.test_email)
        self.assertEqual(data["user"]["plan"], "pro")
        self.assertTrue(data["token"].startswith("pp_session_"))

    def test_02_signup_duplicate_fails(self):
        payload = {
            "email": self.test_email,
            "password": "anotherpassword"
        }
        res = self.client.post("/api/v1/auth/signup", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("detail", data)
        self.assertIn("Duplicate entry", data["detail"])

    def test_03_login_incorrect_password_fails(self):
        payload = {
            "email": self.test_email,
            "password": "wrongpassword"
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertIn("detail", data)
        self.assertIn("Invalid email or password", data["detail"])

    def test_04_login_success(self):
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.assertTrue(data["token"].startswith("pp_session_"))
        
        # Save token for subsequent tests
        self.__class__.session_token = data["token"]

    def test_05_profile_me_success(self):
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        res = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["email"], self.test_email)

    def test_06_compress_prompt_logs_in_sqlite(self):
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        payload = {
            "prompt": "Optimize this: please write a very clean function and thank you in advance!",
            "model": "gpt-4o",
            "level": 1
        }
        res = self.client.post("/api/v1/compress", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("compressed_prompt", data)
        self.assertGreater(data["savings_percent"], 0)

        # Check if the metrics were saved inside our local database
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM compressions").fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row["original_tokens"], data["original_tokens"])

    def test_07_dashboard_stats_success(self):
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        res = self.client.get("/api/v1/auth/dashboard-stats", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("stats", data)
        self.assertIn("recent_logs", data)
        self.assertEqual(data["stats"]["total_audited"], 1)
        self.assertGreater(len(data["recent_logs"]), 0)
        self.assertEqual(data["recent_logs"][0]["original"], 15)  # Exact original tokens count

if __name__ == "__main__":
    unittest.main()
