"""
zcash-uri: Python bindings for Zcash ZIP-321 payment request URIs.

Parse and generate Zcash payment URIs per the ZIP-321 specification.
Wraps the reference Rust implementation from librustzcash via PyO3.
"""

from zcash_uri.zcash_uri import (
    # Core classes
    Payment,
    TransactionRequest,
    AddressInfo,
    # Helper functions
    memo_to_base64,
    memo_from_base64,
    # Address utilities
    validate_address,
    is_valid_address,
    # Amount utilities
    zec_to_zatoshis,
    zatoshis_to_zec,
    format_zec,
    # AI-friendly examples
    examples,
    # Exception hierarchy
    Zip321Error,
    ParseError,
    InvalidBase64Error,
    MemoTooLongError,
    TooManyPaymentsError,
    TransparentMemoError,
    RecipientMissingError,
    InvalidPaymentError,
    InvalidAddressError,
    # Version
    __version__,
)

__all__ = [
    "Payment",
    "TransactionRequest",
    "AddressInfo",
    "memo_to_base64",
    "memo_from_base64",
    "validate_address",
    "is_valid_address",
    "zec_to_zatoshis",
    "zatoshis_to_zec",
    "format_zec",
    "examples",
    "Zip321Error",
    "ParseError",
    "InvalidBase64Error",
    "MemoTooLongError",
    "TooManyPaymentsError",
    "TransparentMemoError",
    "RecipientMissingError",
    "InvalidPaymentError",
    "InvalidAddressError",
    "__version__",
]
