"""Tests for generating ZIP-321 payment URIs."""

import pytest
from zcash_zip321 import Payment, TransactionRequest

# Valid test addresses from librustzcash
SAPLING_ADDR = "ztestsapling1n65uaftvs2g7075q2x2a04shfk066u3lldzxsrprfrqtzxnhc9ps73v4lhx4l9yfxj46sl0q90k"
SAPLING_ADDR_2 = "ztestsapling10yy2ex5dcqkclhc7z7yrnjq2z6feyjad56ptwlfgmy77dmaqqrl9gyhprdx59qgmsnyfska2kez"


class TestGenerateSingle:
    def test_with_amount(self):
        p = Payment(recipient_address=SAPLING_ADDR, amount_zatoshis=150_000_000)
        req = TransactionRequest([p])
        uri = req.to_uri()
        assert uri.startswith("zcash:")
        assert "amount=1.5" in uri

    def test_with_memo_string(self):
        p = Payment(
            recipient_address=SAPLING_ADDR,
            amount_zatoshis=100_000_000,
            memo="Test",
        )
        req = TransactionRequest([p])
        uri = req.to_uri()
        assert "memo=" in uri

    def test_with_memo_bytes(self):
        p = Payment(
            recipient_address=SAPLING_ADDR,
            amount_zatoshis=100_000_000,
            memo=b"Test",
        )
        req = TransactionRequest([p])
        uri = req.to_uri()
        assert "memo=" in uri

    def test_with_label_and_message(self):
        p = Payment(
            recipient_address=SAPLING_ADDR,
            amount_zatoshis=100_000_000,
            label="Coffee",
            message="Thanks!",
        )
        req = TransactionRequest([p])
        uri = req.to_uri()
        assert "label=" in uri
        assert "message=" in uri


class TestGenerateMulti:
    def test_two_payments(self):
        p1 = Payment(recipient_address=SAPLING_ADDR, amount_zatoshis=100_000_000)
        p2 = Payment(recipient_address=SAPLING_ADDR_2, amount_zatoshis=200_000_000)
        req = TransactionRequest([p1, p2])
        uri = req.to_uri()
        assert "address.1=" in uri or "amount.1=" in uri
        assert len(req) == 2
