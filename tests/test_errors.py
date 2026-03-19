"""Tests for error handling and exception hierarchy."""

import pytest
from zcash_uri import (
    Payment,
    TransactionRequest,
    Zip321Error,
    ParseError,
    MemoTooLongError,
    TransparentMemoError,
    InvalidPaymentError,
    InvalidAddressError,
)

SAPLING_ADDR = "ztestsapling1n65uaftvs2g7075q2x2a04shfk066u3lldzxsrprfrqtzxnhc9ps73v4lhx4l9yfxj46sl0q90k"
TRANSPARENT_ADDR = "tmEZhbWHTpdKMw5it8YDspUXSMGQyFwovpU"


class TestExceptionHierarchy:
    def test_parse_error_is_zip321_error(self):
        assert issubclass(ParseError, Zip321Error)

    def test_memo_too_long_is_zip321_error(self):
        assert issubclass(MemoTooLongError, Zip321Error)

    def test_transparent_memo_is_zip321_error(self):
        assert issubclass(TransparentMemoError, Zip321Error)

    def test_invalid_address_is_zip321_error(self):
        assert issubclass(InvalidAddressError, Zip321Error)

    def test_invalid_payment_is_zip321_error(self):
        assert issubclass(InvalidPaymentError, Zip321Error)

    def test_catch_all_zip321_errors(self):
        """All specific errors should be catchable as Zip321Error."""
        with pytest.raises(Zip321Error):
            Payment(recipient_address="not-a-valid-address")


class TestInvalidAddress:
    def test_garbage_address(self):
        with pytest.raises(InvalidAddressError):
            Payment(recipient_address="not-a-valid-address")

    def test_empty_address(self):
        with pytest.raises(InvalidAddressError):
            Payment(recipient_address="")


class TestMemoErrors:
    def test_memo_too_long(self):
        with pytest.raises(MemoTooLongError):
            Payment(
                recipient_address=SAPLING_ADDR,
                amount_zatoshis=100_000_000,
                memo=b"x" * 513,
            )

    def test_transparent_address_with_memo(self):
        with pytest.raises(TransparentMemoError):
            Payment(
                recipient_address=TRANSPARENT_ADDR,
                amount_zatoshis=100_000_000,
                memo="Hello",
            )


class TestAmountErrors:
    def test_amount_overflow(self):
        with pytest.raises((InvalidPaymentError, OverflowError)):
            Payment(
                recipient_address=SAPLING_ADDR,
                amount_zatoshis=21_000_001 * 100_000_000,
            )


class TestParseErrors:
    def test_invalid_uri(self):
        with pytest.raises(ParseError):
            TransactionRequest.from_uri("not-a-uri")

    def test_invalid_base64_memo(self):
        with pytest.raises((Zip321Error, Exception)):
            TransactionRequest.from_uri(
                f"zcash:{SAPLING_ADDR}?amount=1&memo=!!!invalid!!!"
            )
