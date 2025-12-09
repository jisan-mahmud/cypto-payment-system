from solders.signature import Signature
from solana.rpc.api import Client
import logging

class SolanaService:
    def __init__(self, rpc_url: str):
        self.client = Client(rpc_url)

    def fetch_tx(self, signature: str):
        try:
            sig = Signature.from_string(signature)
            return self.client.get_transaction(
                sig,
                commitment="confirmed",
                max_supported_transaction_version=0
            )
        except Exception as e:
            logging.error(f"Solana RPC error: {e}")
            return None

    def get_balance_change(self, tx, receive_wallet: str):
        value = tx.value
        if not value:
            return None

        meta = value.transaction.meta
        if not meta:
            return None

        pre_balances = list(meta.pre_balances)
        post_balances = list(meta.post_balances)

        account_keys = [str(k) for k in value.transaction.transaction.message.account_keys]

        if receive_wallet not in account_keys:
            return None

        index = account_keys.index(receive_wallet)

        diff_lamports = post_balances[index] - pre_balances[index]
        return diff_lamports / 1e9  # convert to SOL
