"""
Multi-chain Wallet Manager for Admin Back Office

- Generates and manages wallet addresses for multiple blockchains (Ethereum, BSC, Polygon, etc.)
- Securely stores private keys (for demo: in-memory, for production: use a vault)
- Provides functions to get addresses, check balances, and sign/send transactions
- Simple profit holding ledger (in-memory for demo)
"""

import os
from typing import Dict
from eth_account import Account
from web3 import Web3

# Supported chains (add more as needed)
SUPPORTED_CHAINS = {
    "ethereum": {
        "rpc": os.getenv("ETHEREUM_RPC", "https://mainnet.infura.io/v3/YOUR_INFURA_ID"),
        "symbol": "ETH"
    },
    "bsc": {
        "rpc": os.getenv("BSC_RPC", "https://bsc-dataseed.binance.org/"),
        "symbol": "BNB"
    },
    "polygon": {
        "rpc": os.getenv("POLYGON_RPC", "https://polygon-rpc.com/"),
        "symbol": "MATIC"
    }
}

class WalletManager:
    def __init__(self):
        # In-memory storage for demo (replace with secure storage in production)
        self.wallets: Dict[str, Dict[str, str]] = {}  # {chain: {address, private_key}}
        self.profit_ledger: Dict[str, float] = {}     # {chain: profit_balance}

    def create_wallet(self, chain: str):
        if chain not in SUPPORTED_CHAINS:
            raise ValueError("Unsupported chain")
        acct = Account.create()
        self.wallets[chain] = {
            "address": acct.address,
            "private_key": acct.key.hex()
        }
        self.profit_ledger[chain] = 0.0
        return self.wallets[chain]["address"]

    def get_wallet(self, chain: str):
        return self.wallets.get(chain, None)

    def get_balance(self, chain: str):
        if chain not in self.wallets:
            return None
        w3 = Web3(Web3.HTTPProvider(SUPPORTED_CHAINS[chain]["rpc"]))
        address = self.wallets[chain]["address"]
        balance = w3.eth.get_balance(address)
        return w3.fromWei(balance, 'ether')

    def add_profit(self, chain: str, amount: float):
        if chain not in self.profit_ledger:
            self.profit_ledger[chain] = 0.0
        self.profit_ledger[chain] += amount

    def withdraw_profit(self, chain: str, to_address: str, amount: float):
        if self.profit_ledger.get(chain, 0.0) < amount:
            raise ValueError("Insufficient profit balance")
        # For demo: just deduct, in production: sign/send transaction
        self.profit_ledger[chain] -= amount
        return True

wallet_manager = WalletManager()