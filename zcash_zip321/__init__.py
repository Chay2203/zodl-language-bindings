"""
zcash-zip321: Python bindings for Zcash ZIP-321 payment request URIs.

Parse and generate Zcash payment URIs per the ZIP-321 specification.
Wraps the reference Rust implementation from librustzcash via PyO3.
"""

from zcash_zip321.zcash_zip321 import (
    # Core classes
    Payment,
    TransactionRequest,
    # Helper functions
    memo_to_base64,
    memo_from_base64,
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
    "memo_to_base64",
    "memo_from_base64",
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
