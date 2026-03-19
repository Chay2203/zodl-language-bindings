"""Tests for parsing ZIP-321 payment URIs."""

import pytest
from zcash_uri import TransactionRequest, Payment, ParseError

# Valid test addresses from ZIP-321 spec / librustzcash tests
SAPLING_ADDR = "ztestsapling1n65uaftvs2g7075q2x2a04shfk066u3lldzxsrprfrqtzxnhc9ps73v4lhx4l9yfxj46sl0q90k"
SAPLING_ADDR_2 = "ztestsapling10yy2ex5dcqkclhc7z7yrnjq2z6feyjad56ptwlfgmy77dmaqqrl9gyhprdx59qgmsnyfska2kez"
TRANSPARENT_ADDR = "tmEZhbWHTpdKMw5it8YDspUXSMGQyFwovpU"


class TestParseSimple:
    def test_parse_with_amount(self):
        uri = f"zcash:{SAPLING_ADDR}?amount=1.5"
        req = TransactionRequest.from_uri(uri)
        p = req.payments()[0]
        assert p.amount_zatoshis == 150_000_000
        assert p.amount_zec == pytest.approx(1.5)

    def test_parse_with_label(self):
        uri = f"zcash:{SAPLING_ADDR}?amount=0.01&label=Coffee"
        req = TransactionRequest.from_uri(uri)
        p = req.payments()[0]
        assert p.label == "Coffee"
        assert p.amount_zatoshis == 1_000_000

    def test_parse_with_message(self):
        uri = f"zcash:{SAPLING_ADDR}?amount=1&message=Thanks"
        req = TransactionRequest.from_uri(uri)
        p = req.payments()[0]
        assert p.message == "Thanks"

    def test_parse_with_memo(self):
        # "Test" in base64 is "VGVzdA"
        uri = f"zcash:{SAPLING_ADDR}?amount=1&memo=VGVzdA"
        req = TransactionRequest.from_uri(uri)
        p = req.payments()[0]
        assert p.memo is not None
        assert p.memo_text == "Test"

    def test_parse_address_and_amount(self):
        uri = f"zcash:{SAPLING_ADDR}?amount=0.0001"
        req = TransactionRequest.from_uri(uri)
        assert len(req) == 1
        p = req.payments()[0]
        assert p.recipient_address == SAPLING_ADDR
        assert p.amount_zatoshis == 10_000


class TestParseMultiPayment:
    def test_two_payments(self):
        uri = (
            f"zcash:{SAPLING_ADDR}?amount=1"
            f"&address.1={SAPLING_ADDR_2}&amount.1=2"
        )
        req = TransactionRequest.from_uri(uri)
        assert len(req) == 2
        payments = req.payments()
        assert payments[0].amount_zatoshis == 100_000_000
        assert payments[1].amount_zatoshis == 200_000_000


class TestParseErrors:
    def test_invalid_scheme(self):
        with pytest.raises(ParseError):
            TransactionRequest.from_uri("bitcoin:addr123")

    def test_empty_string(self):
        with pytest.raises(ParseError):
            TransactionRequest.from_uri("")

    def test_missing_address(self):
        with pytest.raises((ParseError, Exception)):
            TransactionRequest.from_uri("zcash:?amount=1")
