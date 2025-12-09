from web3 import Web3
import logging

class PolygonService:
    def __init__(self, rpc):
        self.web3 = Web3(Web3.HTTPProvider(rpc))

    def fetch_tx(self, tx_hash: str):
        try:
            return self.web3.eth.get_transaction(tx_hash)
        except Exception as e:
            logging.error(f"Polygon RPC error: {e}")
            return None

    def fetch_receipt(self, tx_hash: str):
        try:
            return self.web3.eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            logging.error(f"Polygon receipt error: {e}")
            return None

    def get_value_eth(self, tx):
        return Web3.from_wei(tx["value"], "ether")
