"""Tests for amount conversion utilities, examples(), and to_dict()."""

import pytest
from zcash_uri import (
    zec_to_zatoshis,
    zatoshis_to_zec,
    format_zec,
    examples,
    Payment,
    TransactionRequest,
    InvalidPaymentError,
)

SAPLING_ADDR = "ztestsapling1n65uaftvs2g7075q2x2a04shfk066u3lldzxsrprfrqtzxnhc9ps73v4lhx4l9yfxj46sl0q90k"


class TestZecToZatoshis:
    def test_one_zec(self):
        assert zec_to_zatoshis(1.0) == 100_000_000

    def test_fractional(self):
        assert zec_to_zatoshis(1.5) == 150_000_000

    def test_zero(self):
        assert zec_to_zatoshis(0.0) == 0

    def test_max_money(self):
        assert zec_to_zatoshis(21_000_000.0) == 2_100_000_000_000_000

    def test_negative_raises(self):
        with pytest.raises(InvalidPaymentError):
            zec_to_zatoshis(-1.0)

    def test_over_max_raises(self):
        with pytest.raises(InvalidPaymentError):
            zec_to_zatoshis(21_000_001.0)


class TestZatoshisToZec:
    def test_one_zec(self):
        assert zatoshis_to_zec(100_000_000) == 1.0

    def test_zero(self):
        assert zatoshis_to_zec(0) == 0.0

    def test_over_max_raises(self):
        with pytest.raises(InvalidPaymentError):
            zatoshis_to_zec(2_100_000_000_000_001)


class TestRoundtrip:
    def test_roundtrip(self):
        for zec in [0.0, 0.00000001, 1.0, 1.5, 21_000_000.0]:
            assert zatoshis_to_zec(zec_to_zatoshis(zec)) == zec


class TestFormatZec:
    def test_whole(self):
        assert format_zec(100_000_000) == "1.00000000 ZEC"

    def test_fractional(self):
        assert format_zec(150_000_000) == "1.50000000 ZEC"

    def test_zero(self):
        assert format_zec(0) == "0.00000000 ZEC"

    def test_small(self):
        assert format_zec(1) == "0.00000001 ZEC"

    def test_over_max_raises(self):
        with pytest.raises(InvalidPaymentError):
            format_zec(2_100_000_000_000_001)


class TestExamples:
    def test_returns_string(self):
        result = examples()
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_key_sections(self):
        result = examples()
        assert "Parse" in result
        assert "validate_address" in result
        assert "zec_to_zatoshis" in result
        assert "to_dict" in result


class TestPaymentToDict:
    def test_basic(self):
        p = Payment(SAPLING_ADDR, amount_zatoshis=100_000_000)
        d = p.to_dict()
        assert d["recipient_address"] == SAPLING_ADDR
        assert d["amount_zatoshis"] == 100_000_000
        assert d["amount_zec"] == 1.0
        assert d["memo"] is None
        assert d["label"] is None
        assert d["message"] is None

    def test_with_memo(self):
        p = Payment(SAPLING_ADDR, amount_zatoshis=50_000_000, memo="Hello")
        d = p.to_dict()
        assert d["memo"] == "Hello"
        assert d["amount_zec"] == 0.5

    def test_with_all_fields(self):
        p = Payment(
            SAPLING_ADDR,
            amount_zatoshis=200_000_000,
            memo="Test",
            label="Alice",
            message="For lunch",
        )
        d = p.to_dict()
        assert d["label"] == "Alice"
        assert d["message"] == "For lunch"


class TestTransactionRequestToDict:
    def test_single_payment(self):
        p = Payment(SAPLING_ADDR, amount_zatoshis=100_000_000)
        req = TransactionRequest([p])
        d = req.to_dict()
        assert len(d["payments"]) == 1
        assert d["total_zatoshis"] == 100_000_000
        assert d["total_zec"] == 1.0

    def test_multi_payment(self):
        p1 = Payment(SAPLING_ADDR, amount_zatoshis=100_000_000)
        p2 = Payment(SAPLING_ADDR, amount_zatoshis=200_000_000)
        req = TransactionRequest([p1, p2])
        d = req.to_dict()
        assert len(d["payments"]) == 2
        assert d["total_zatoshis"] == 300_000_000
        assert d["total_zec"] == 3.0
