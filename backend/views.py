import os
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PaymentVerifySerializer
from .services.solana_service import SolanaService
from .services.polygon_service import PolygonService

# ENVIRONMENT CONFIG
INFURA_KEY = os.getenv("INFURA_KEY")
HELIUS_KEY = os.getenv("HELIUS_KEY")

POLYGON_RECEIVE_WALLET = os.getenv("POLYGON_RECEIVE_WALLET").lower()
SOLANA_RECEIVE_WALLET = os.getenv("SOLANA_RECEIVE_WALLET")

REQUIRED_AMOUNT_POLYGON = Decimal(os.getenv("REQUIRED_AMOUNT_POLYGON", "0.1"))
REQUIRED_AMOUNT_SOL = Decimal(os.getenv("REQUIRED_AMOUNT_SOL", "0.1"))

# RPC URLs
POLYGON_RPC = f"https://polygon-amoy.infura.io/v3/{INFURA_KEY}"
SOLANA_RPC = f"https://devnet.helius-rpc.com/?api-key={HELIUS_KEY}"

# Initialize services
polygon = PolygonService(POLYGON_RPC)
solana = SolanaService(SOLANA_RPC)


class VerifyPayment(APIView):

    def post(self, request):
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        network = serializer.validated_data["network"]
        wallet = serializer.validated_data.get("wallet")
        tx_hash = serializer.validated_data["tx_hash"]

        # -------------------------------
        # POLYGON CHECK
        # -------------------------------
        if network == "polygon":

            tx = polygon.fetch_tx(tx_hash)
            if not tx:
                return Response({"error": "Invalid Polygon transaction"}, status=400)

            receipt = polygon.fetch_receipt(tx_hash)
            if not receipt or receipt.get("status") != 1:
                return Response({"error": "Polygon transaction failed"}, status=400)

            receiver = tx["to"].lower()
            if receiver != POLYGON_RECEIVE_WALLET:
                return Response({"error": "Wrong Polygon receiving wallet"}, status=400)

            value_eth = Decimal(polygon.get_value_eth(tx))
            if value_eth < REQUIRED_AMOUNT_POLYGON:
                return Response({"error": "Insufficient Polygon payment"}, status=400)

            return Response({
                "success": True,
                "network": "polygon",
                "wallet": wallet,
                "tx_hash": tx_hash,
                "amount": str(value_eth),
            }, status=200)

        # -------------------------------
        # SOLANA CHECK
        # -------------------------------
        if network == "solana":

            tx = solana.fetch_tx(tx_hash)
            if not tx:
                return Response({"error": "Invalid or unreachable Solana transaction"}, status=400)

            if tx.value is None:
                return Response({"error": "Invalid or unconfirmed Solana transaction"}, status=400)

            amount_sol = solana.get_balance_change(tx, SOLANA_RECEIVE_WALLET)
            if amount_sol is None:
                return Response({"error": "Wrong Solana receiving wallet"}, status=400)

            if Decimal(str(amount_sol)) < REQUIRED_AMOUNT_SOL:
                return Response({"error": "Insufficient SOL payment"}, status=400)

            return Response({
                "success": True,
                "network": "solana",
                "wallet": wallet,
                "tx_hash": tx_hash,
                "amount": amount_sol,
            }, status=200)

        # Unsupported network
        return Response({"error": "Unsupported network"}, status=400)
