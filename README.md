# zcash-uri

[![PyPI](https://img.shields.io/pypi/v/zcash-uri)](https://pypi.org/project/zcash-uri/)
[![CI](https://github.com/Chay2203/zodl-language-bindings/actions/workflows/CI.yml/badge.svg)](https://github.com/Chay2203/zodl-language-bindings/actions/workflows/CI.yml)
[![License](https://img.shields.io/pypi/l/zcash-uri)](https://pypi.org/project/zcash-uri/)
[![Python](https://img.shields.io/pypi/pyversions/zcash-uri)](https://pypi.org/project/zcash-uri/)

> **Alpha** -- API may change. Not yet audited for production use.

Python bindings for **Zcash ZIP-321 payment request URIs**, wrapping the
reference Rust implementation from
[librustzcash](https://github.com/zcash/librustzcash) via PyO3.

ZIP-321 defines a standard URI format for Zcash payment requests supporting
single and multi-recipient payments with amounts, memos, labels, and messages.

## Installation

```bash
pip install zcash-uri
```

## Quick Start

### Parse a payment URI

```python
from zcash_uri import TransactionRequest

req = TransactionRequest.from_uri("zcash:zs1...?amount=1.5&memo=VGVzdA")

for idx, payment in req.payments().items():
    print(f"Payment {idx}:")
    print(f"  To:     {payment.recipient_address}")
    print(f"  Amount: {payment.amount_zec} ZEC")
    print(f"  Memo:   {payment.memo_text}")
```

### Build a payment URI

```python
from zcash_uri import Payment, TransactionRequest

payment = Payment(
    recipient_address="zs1...",
    amount_zatoshis=150_000_000,  # 1.5 ZEC
    memo="Thank you!",
)

req = TransactionRequest([payment])
print(req.to_uri())  # zcash:zs1...?amount=1.5&memo=...
```

### Multi-recipient payments

```python
p1 = Payment(recipient_address="zs1abc...", amount_zatoshis=100_000_000)
p2 = Payment(recipient_address="zs1def...", amount_zatoshis=200_000_000)

req = TransactionRequest([p1, p2])
print(req.to_uri())
print(f"Total: {req.total_zec()} ZEC")
```

### Validate addresses

```python
from zcash_uri import validate_address, is_valid_address

info = validate_address("zs1...")
print(info.is_valid)          # True
print(info.address_type)      # "sapling"
print(info.can_receive_memo)  # True
print(info.pools)             # ["sapling"]

is_valid_address("not-valid") # False
```

### Amount utilities

```python
from zcash_uri import zec_to_zatoshis, zatoshis_to_zec, format_zec

zec_to_zatoshis(1.5)       # 150000000
zatoshis_to_zec(150000000)  # 1.5
format_zec(150000000)       # "1.50000000 ZEC"
```

### Serialize to dict

```python
p = Payment("zs1...", amount_zatoshis=100_000_000)
p.to_dict()
# {'recipient_address': 'zs1...', 'amount_zatoshis': 100000000, 'amount_zec': 1.0, ...}

req = TransactionRequest([p])
req.to_dict()
# {'payments': [...], 'total_zatoshis': 100000000, 'total_zec': 1.0}
```

### AI-friendly examples

```python
from zcash_uri import examples
print(examples())  # Prints working code snippets for all features
```

## API Reference

### `Payment`

| Property / Method | Type | Description |
|----------|------|-------------|
| `recipient_address` | `str` | Zcash address |
| `amount_zatoshis` | `int \| None` | Amount in zatoshis |
| `amount_zec` | `float \| None` | Amount in ZEC |
| `memo` | `bytes \| None` | Raw memo bytes |
| `memo_text` | `str \| None` | Memo as UTF-8 text |
| `label` | `str \| None` | Human-readable label |
| `message` | `str \| None` | Human-readable message |
| `.to_dict()` | `dict` | Dict representation |

### `TransactionRequest`

| Method | Returns | Description |
|--------|---------|-------------|
| `TransactionRequest(payments)` | | Create from list of `Payment` |
| `TransactionRequest.from_uri(uri)` | `TransactionRequest` | Parse a ZIP-321 URI |
| `.to_uri()` | `str` | Serialize to URI |
| `.payments()` | `dict[int, Payment]` | All payments |
| `.total_zatoshis()` | `int \| None` | Sum of all amounts |
| `.total_zec()` | `float \| None` | Sum in ZEC |
| `.to_dict()` | `dict` | Dict representation |
| `len(req)` | `int` | Number of payments |

### `AddressInfo`

| Property | Type | Description |
|----------|------|-------------|
| `is_valid` | `bool` | Whether the address is valid |
| `address_type` | `str` | `"transparent"`, `"sapling"`, `"unified"`, or `"unknown"` |
| `can_receive_memo` | `bool` | Whether memos are supported |
| `pools` | `list[str]` | Pool types the address can receive to |

### Helper Functions

- `memo_to_base64(memo: bytes) -> str` -- Encode memo bytes to ZIP-321 base64
- `memo_from_base64(encoded: str) -> bytes` -- Decode base64 memo
- `validate_address(address: str) -> AddressInfo` -- Inspect a Zcash address
- `is_valid_address(address: str) -> bool` -- Quick validity check
- `zec_to_zatoshis(zec: float) -> int` -- Convert ZEC to zatoshis
- `zatoshis_to_zec(zatoshis: int) -> float` -- Convert zatoshis to ZEC
- `format_zec(zatoshis: int) -> str` -- Human-readable ZEC string
- `examples() -> str` -- Working code snippets for all features

### Exceptions

All exceptions inherit from `Zip321Error`:

- `ParseError` -- URI parsing failed
- `InvalidBase64Error` -- Invalid base64 in memo
- `MemoTooLongError` -- Memo exceeds 512 bytes
- `TooManyPaymentsError` -- Too many payments in request
- `TransparentMemoError` -- Memo attached to transparent address
- `RecipientMissingError` -- Payment missing recipient
- `InvalidPaymentError` -- Invalid payment parameters
- `InvalidAddressError` -- Unrecognized address format

## Development

```bash
# Install Rust and maturin
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
pip install maturin[patchelf]

# Build and install in development mode
maturin develop

# Run tests
pip install pytest
pytest tests/ -v

# Build release wheel
maturin build --release
```

## License

Licensed under either of:

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
- MIT License ([LICENSE-MIT](LICENSE-MIT))

at your option.
