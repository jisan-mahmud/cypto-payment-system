from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from solders.signature import Signature
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
from .serializers import PaymentVerifySerializer

# Configuration
YOUR_INFURA_KEY = "b504e7f264304a07a4cfb1373bc63bc0"

# EVM (Polygon) RPC
POLYGON_RPC = f"https://polygon-amoy.infura.io/v3/{YOUR_INFURA_KEY}"
web3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

# Solana RPC
solana_client = SolanaClient("https://devnet.helius-rpc.com/?api-key=1a9a9285-2659-492c-8405-19b7f344bb38")

# Receiving Wallets
POLYGON_RECEIVE_WALLET = "0x31454F46ad995d77b0280dcBf06C3E571854Ec20".lower()
SOLANA_RECEIVE_WALLET = "G9hisoeBGMoLLLMWWPY81qgj5UNHN8McDvSJmL14aiea"

# Required Amounts
REQUIRED_AMOUNT_POLYGON = Decimal("0.1")
REQUIRED_AMOUNT_SOL = Decimal("0.1")


class VerifyPayment(APIView):

    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        network = serializer.validated_data["network"]
        wallet = serializer.validated_data.get("wallet")
        tx_hash = serializer.validated_data["tx_hash"]

        if network == "polygon":
            try:
                tx = web3.eth.get_transaction(tx_hash)
            except Exception:
                return Response({"error": "Invalid Polygon transaction"}, status=400)

            receiver = tx["to"].lower()
            value = Web3.from_wei(tx["value"], "ether")

            if receiver != POLYGON_RECEIVE_WALLET:
                return Response({"error": "Sent to wrong Polygon wallet"}, status=400)

            if Decimal(value) < REQUIRED_AMOUNT_POLYGON:
                return Response({"error": "Insufficient Polygon amount"}, status=400)

            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt["status"] != 1:
                return Response({"error": "Polygon transaction failed"}, status=400)

            return Response({
                "success": True,
                "network": "polygon",
                "wallet": wallet,
                "tx_hash": tx_hash,
                "amount": str(value),
            }, status=200)

        # ---------------------------
        # SOLANA PAYMENT CHECK
        # ---------------------------
        if network == "solana":

            # Validate signature
            try:
                sig = Signature.from_string(tx_hash)
            except Exception:
                return Response({"error": "Invalid Solana signature format"}, status=400)

            # Fetch transaction
            try:
                sol_tx = solana_client.get_transaction(
                    sig,
                    commitment="confirmed",
                    max_supported_transaction_version=0
                )
            except Exception as e:
                return Response({"error": f"RPC error: {str(e)}"}, status=400)

            # Check if transaction exists
            if sol_tx.value is None:
                return Response({"error": "Invalid or unconfirmed Solana transaction"}, status=400)

            tx_value = sol_tx.value

            # Correct metadata path
            meta = tx_value.transaction.meta
            if meta is None:
                return Response({"error": "No metadata in Solana transaction"}, status=400)

            pre_balances = list(meta.pre_balances)
            post_balances = list(meta.post_balances)

            # Correct account-keys path
            account_keys = [
                str(k) for k in tx_value.transaction.transaction.message.account_keys
            ]

            if SOLANA_RECEIVE_WALLET not in account_keys:
                return Response({"error": "Wrong Solana wallet"}, status=400)

            receiver_index = account_keys.index(SOLANA_RECEIVE_WALLET)

            diff_lamports = post_balances[receiver_index] - pre_balances[receiver_index]
            diff_sol = diff_lamports / 1e9

            if diff_sol < float(REQUIRED_AMOUNT_SOL):
                return Response({"error": "Insufficient SOL amount"}, status=400)

            return Response({
                "success": True,
                "network": "solana",
                "wallet": wallet,
                "tx_hash": tx_hash,
                "amount": diff_sol,
            }, status=200)

        return Response({"error": "Unsupported network"}, status=400)
