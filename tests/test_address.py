"""Tests for address validation and inspection utilities."""

import pytest
from zcash_uri import validate_address, is_valid_address, AddressInfo

SAPLING_ADDR = "ztestsapling1n65uaftvs2g7075q2x2a04shfk066u3lldzxsrprfrqtzxnhc9ps73v4lhx4l9yfxj46sl0q90k"
TRANSPARENT_ADDR = "tmEZhbWHTpdKMw5it8YDspUXSMGQyFwovpU"


class TestValidateAddress:
    def test_sapling_address(self):
        info = validate_address(SAPLING_ADDR)
        assert info.is_valid is True
        assert info.address_type == "sapling"
        assert info.can_receive_memo is True
        assert info.pools == ["sapling"]

    def test_transparent_address(self):
        info = validate_address(TRANSPARENT_ADDR)
        assert info.is_valid is True
        assert info.address_type == "transparent"
        assert info.can_receive_memo is False
        assert info.pools == ["transparent"]

    def test_invalid_address(self):
        info = validate_address("not-a-real-address")
        assert info.is_valid is False
        assert info.address_type == "unknown"
        assert info.can_receive_memo is False
        assert info.pools == []

    def test_empty_string(self):
        info = validate_address("")
        assert info.is_valid is False

    def test_repr(self):
        info = validate_address(SAPLING_ADDR)
        r = repr(info)
        assert "AddressInfo" in r
        assert "sapling" in r


class TestIsValidAddress:
    def test_valid_sapling(self):
        assert is_valid_address(SAPLING_ADDR) is True

    def test_valid_transparent(self):
        assert is_valid_address(TRANSPARENT_ADDR) is True

    def test_invalid(self):
        assert is_valid_address("xyz123") is False

    def test_empty(self):
        assert is_valid_address("") is False
