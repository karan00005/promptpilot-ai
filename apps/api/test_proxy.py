import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from services.local_db import DB_PATH

class TestProxyGateway(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = DB_PATH + ".test_proxy"
        
        # Remove any leftover test database from previous interrupted runs
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass
                
        # Override the DB_PATH dynamically for clean run
        import services.local_db as local_db
        local_db.DB_PATH = cls.test_db_path
        local_db.init_db()
        
        cls.client = TestClient(app)
        
        # Create a test user to get authenticated session
        payload = {
            "email": "proxy_tester@promptpilot.ai",
            "password": "securepassword123"
        }
        res = cls.client.post("/api/v1/auth/signup", json=payload)
        assert res.status_code == 201, f"Signup failed with {res.status_code}: {res.text}"
        data = res.json()
        cls.session_token = data["token"]

    @classmethod
    def tearDownClass(cls):
        # Remove test database
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception as e:
                print(f"Error removing test database file: {e}")

    def test_01_proxy_chat_completions_offline(self):
        """
        Verify that the chat completions endpoint returns the optimized prompt
        and payload correctly when no OpenAI API key is present (offline mode fallback).
        """
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        
        # Standard OpenAI chat completions request payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are a helpful programming assistant."},
                {"role": "user", "content": "Hello! Could you please help me write a Python script? Thanks in advance!"}
            ],
            "temperature": 0.7
        }
        
        res = self.client.post("/api/v1/chat/completions", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertTrue(data["success"])
        self.assertIn("optimized_payload", data)
        self.assertGreater(data["savings_percent"], 0)
        
        # Verify prompt compression actually happened by stripping polite phrases in last message
        optimized_messages = data["optimized_payload"]["messages"]
        self.assertEqual(len(optimized_messages), 2)
        
        original_last_content = payload["messages"][-1]["content"]
        optimized_last_content = optimized_messages[-1]["content"]
        
        self.assertNotEqual(original_last_content, optimized_last_content)
        self.assertNotIn("please", optimized_last_content.lower())
        self.assertNotIn("thanks in advance", optimized_last_content.lower())

if __name__ == "__main__":
    unittest.main()
