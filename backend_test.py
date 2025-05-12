import requests
import unittest
import sys
import uuid
from datetime import datetime

class WalletAITester:
    def __init__(self, base_url="https://3496fde9-0ca4-47c5-a941-c1346434431b.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_wallets = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json() if response.text else {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test the API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_create_ethereum_wallet(self, name=None):
        """Test creating an Ethereum wallet"""
        if name is None:
            name = f"ETH Wallet {uuid.uuid4().hex[:8]}"
        
        success, response = self.run_test(
            "Create Ethereum Wallet",
            "POST",
            "wallets",
            200,
            data={"name": name, "chain_type": "ETH"}
        )
        
        if success:
            self.created_wallets.append(response)
            print(f"Created ETH wallet: {response['name']} with address {response['address']}")
        
        return success, response

    def test_create_solana_wallet(self, name=None):
        """Test creating a Solana wallet"""
        if name is None:
            name = f"SOL Wallet {uuid.uuid4().hex[:8]}"
        
        success, response = self.run_test(
            "Create Solana Wallet",
            "POST",
            "wallets",
            200,
            data={"name": name, "chain_type": "SOL"}
        )
        
        if success:
            self.created_wallets.append(response)
            print(f"Created SOL wallet: {response['name']} with address {response['address']}")
        
        return success, response

    def test_get_wallets(self):
        """Test getting all wallets"""
        success, response = self.run_test(
            "Get All Wallets",
            "GET",
            "wallets",
            200
        )
        
        if success:
            print(f"Found {len(response)} wallets")
        
        return success, response

    def test_get_wallet(self, wallet_id):
        """Test getting a specific wallet"""
        success, response = self.run_test(
            f"Get Wallet {wallet_id}",
            "GET",
            f"wallets/{wallet_id}",
            200
        )
        
        return success, response

    def test_get_wallet_balance(self, wallet_id):
        """Test getting a wallet's balance"""
        success, response = self.run_test(
            f"Get Wallet Balance {wallet_id}",
            "GET",
            f"wallets/{wallet_id}/balance",
            200
        )
        
        if success:
            print(f"Balance: {response['balance']} {response['token_symbol']}")
        
        return success, response

    def test_ai_chat(self, message, wallet_id=None):
        """Test the AI chat functionality"""
        data = {
            "message": message,
            "wallet_id": wallet_id
        }
        
        success, response = self.run_test(
            "AI Chat",
            "POST",
            "ai/chat",
            200,
            data=data
        )
        
        if success:
            print(f"AI Response: {response['response'][:100]}...")
        
        return success, response

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Wallet AI API Tests")
        
        # Test API root
        self.test_api_root()
        
        # Test wallet creation
        eth_success, eth_wallet = self.test_create_ethereum_wallet("Test ETH Wallet")
        sol_success, sol_wallet = self.test_create_solana_wallet("Test SOL Wallet")
        
        # Test getting wallets
        self.test_get_wallets()
        
        # Test getting specific wallets
        if eth_success:
            self.test_get_wallet(eth_wallet["wallet_id"])
            self.test_get_wallet_balance(eth_wallet["wallet_id"])
        
        if sol_success:
            self.test_get_wallet(sol_wallet["wallet_id"])
            self.test_get_wallet_balance(sol_wallet["wallet_id"])
        
        # Test AI chat
        if eth_success:
            self.test_ai_chat("What's my wallet balance?", eth_wallet["wallet_id"])
            self.test_ai_chat("How can I send ETH to another address?", eth_wallet["wallet_id"])
        
        # Test AI chat without wallet
        self.test_ai_chat("How do I create a new wallet?")
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = WalletAITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)