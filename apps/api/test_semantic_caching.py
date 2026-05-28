import sys
import os
import unittest

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from services.local_db import DB_PATH, get_db_connection

class TestSemanticCaching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use temporary test database for clean runs
        cls.original_db = DB_PATH
        cls.test_db_path = DB_PATH + ".test_rag"
        
        # Override the DB_PATH in local_db module dynamically for testing
        import services.local_db as local_db
        local_db.DB_PATH = cls.test_db_path
        local_db.init_db()
        
        cls.client = TestClient(app)
        cls.test_email = "rag_tester@promptpilot.ai"
        cls.test_password = "securepassword123"

    @classmethod
    def tearDownClass(cls):
        # Remove test database
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception as e:
                print(f"Error removing test database file: {e}")

    def test_01_setup_auth_user(self):
        # Sign up
        payload = {
            "email": self.test_email,
            "password": self.test_password
        }
        res = self.client.post("/api/v1/auth/signup", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)
        self.__class__.session_token = data["token"]

    def test_02_upload_large_context_document(self):
        # Prepare a realistic context document with distinct sections
        context_text = (
            "Section 1: General Account Configurations. "
            "To configure your PromptPilot account, go to console and generate a new key. "
            "Never share this API key with third parties as it authorizes billing calls. "
            "Section 2: Payment Gateways Integration. "
            "We support Stripe payments natively. To set up Stripe Checkout, call billing/checkout endpoint. "
            "To manage active credit cards, subscriptions or download payment invoices, call billing/portal. "
            "Section 3: Stripe Webhook Verifications. "
            "When Stripe triggers a payment checkout success event, it sends a webhook payload to your endpoint. "
            "You must cryptographically verify Stripe Webhooks using your endpoint secret to protect against fraud. "
            "Read the header signature, parse raw bytes, and calculate SHA-256 HMAC hash. "
            "Section 4: LLM Rules Limits. "
            "Pruning algorithms can reduce filler tokens by 30-50% instantly."
        )
        
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        payload = {
            "title": "Payments API Docs",
            "text": context_text
        }
        
        res = self.client.post("/api/v1/context/upload", json=payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("doc_id", data)
        self.assertGreater(data["chunks_count"], 0)

    def test_03_list_contexts_success(self):
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        res = self.client.get("/api/v1/context/list", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Payments API Docs")
        self.assertGreater(data[0]["chunk_count"], 0)

    def test_04_semantic_compress_webhook_query(self):
        headers = {
            "Authorization": f"Bearer {self.session_token}"
        }
        # Sawaal matches Section 3 (Webhook secret verification)
        payload = {
            "prompt": "Please tell me: How do I securely verify Stripe webhooks? Thank you!",
            "context_title": "Payments API Docs",
            "level": 1
        }
        res = self.client.post("/api/v1/context/compress", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["retrieved_chunks_count"], 0)
        self.assertIn("optimized_prompt", data)
        self.assertGreater(data["savings_percent"], 0)
        
        # Verify that the retrieved context actually contains webhook text
        opt_prompt = data["optimized_prompt"].lower()
        self.assertIn("webhook", opt_prompt)
        self.assertIn("stripe", opt_prompt)
        
if __name__ == "__main__":
    unittest.main()
