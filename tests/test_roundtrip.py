"""Round-trip tests: parse -> generate -> parse preserves data."""

import pytest
from zcash_zip321 import (
    Payment,
    TransactionRequest,
    memo_to_base64,
    memo_from_base64,
)

SAPLING_ADDR = "ztestsapling1n65uaftvs2g7075q2x2a04shfk066u3lldzxsrprfrqtzxnhc9ps73v4lhx4l9yfxj46sl0q90k"
SAPLING_ADDR_2 = "ztestsapling10yy2ex5dcqkclhc7z7yrnjq2z6feyjad56ptwlfgmy77dmaqqrl9gyhprdx59qgmsnyfska2kez"


class TestPaymentRoundtrip:
    def test_simple_payment(self):
        p = Payment(recipient_address=SAPLING_ADDR, amount_zatoshis=100_000_000)
        req = TransactionRequest([p])
        uri = req.to_uri()

        req2 = TransactionRequest.from_uri(uri)
        p2 = req2.payments()[0]
        assert p2.recipient_address == SAPLING_ADDR
        assert p2.amount_zatoshis == 100_000_000

    def test_payment_with_memo(self):
        p = Payment(
            recipient_address=SAPLING_ADDR,
            amount_zatoshis=50_000_000,
            memo="Round trip test",
        )
        req = TransactionRequest([p])
        uri = req.to_uri()

        req2 = TransactionRequest.from_uri(uri)
        p2 = req2.payments()[0]
        assert p2.memo_text == "Round trip test"
        assert p2.amount_zatoshis == 50_000_000

    def test_payment_with_all_fields(self):
        p = Payment(
            recipient_address=SAPLING_ADDR,
            amount_zatoshis=200_000_000,
            memo="Full test",
            label="My Label",
            message="My Message",
        )
        req = TransactionRequest([p])
        uri = req.to_uri()

        req2 = TransactionRequest.from_uri(uri)
        p2 = req2.payments()[0]
        assert p2.recipient_address == SAPLING_ADDR
        assert p2.amount_zatoshis == 200_000_000
        assert p2.memo_text == "Full test"
        assert p2.label == "My Label"
        assert p2.message == "My Message"

    def test_multi_payment_roundtrip(self):
        p1 = Payment(recipient_address=SAPLING_ADDR, amount_zatoshis=100_000_000)
        p2 = Payment(recipient_address=SAPLING_ADDR_2, amount_zatoshis=200_000_000)
        req = TransactionRequest([p1, p2])
        uri = req.to_uri()

        req2 = TransactionRequest.from_uri(uri)
        assert len(req2) == 2
        total = req2.total_zatoshis()
        assert total == 300_000_000


class TestMemoBase64Roundtrip:
    def test_text_memo(self):
        original = b"Hello, Zcash!"
        encoded = memo_to_base64(original)
        decoded = memo_from_base64(encoded)
        assert decoded == original

    def test_binary_memo(self):
        original = bytes(range(256))
        encoded = memo_to_base64(original)
        decoded = memo_from_base64(encoded)
        assert decoded == original

    def test_empty_memo(self):
        original = b""
        encoded = memo_to_base64(original)
        decoded = memo_from_base64(encoded)
        assert decoded == original


class TestTotalCalculation:
    def test_total_single(self):
        p = Payment(recipient_address=SAPLING_ADDR, amount_zatoshis=100_000_000)
        req = TransactionRequest([p])
        assert req.total_zatoshis() == 100_000_000
        assert req.total_zec() == pytest.approx(1.0)

    def test_total_multi(self):
        p1 = Payment(recipient_address=SAPLING_ADDR, amount_zatoshis=100_000_000)
        p2 = Payment(recipient_address=SAPLING_ADDR_2, amount_zatoshis=250_000_000)
        req = TransactionRequest([p1, p2])
        assert req.total_zatoshis() == 350_000_000
        assert req.total_zec() == pytest.approx(3.5)

    def test_total_with_none_amount(self):
        p = Payment(recipient_address=SAPLING_ADDR)
        req = TransactionRequest([p])
        assert req.total_zatoshis() is None
        assert req.total_zec() is None
