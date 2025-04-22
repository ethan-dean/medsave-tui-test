import requests
import os

class PlaidClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv('PLAID_SERVER', 'http://localhost:5000')
        self.token = None

    def authenticate(self, user_id):
        # Fake OAuth exchange to get a token
        resp = requests.post(f"{self.base_url}/auth", json={"user_id": user_id})
        resp.raise_for_status()
        self.token = resp.json().get('access_token')
        return self.token

    def get_accounts(self):
        resp = requests.get(
            f"{self.base_url}/accounts",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        resp.raise_for_status()
        return resp.json().get('accounts', [])

    def sync_hospital_bills(self):
        resp = requests.get(
            f"{self.base_url}/bills",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        resp.raise_for_status()
        return resp.json().get('bills', [])
