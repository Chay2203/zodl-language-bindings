# zcash-zip321

> **Alpha** -- API may change. Not yet audited for production use.

Python bindings for **Zcash ZIP-321 payment request URIs**, wrapping the
reference Rust implementation from
[librustzcash](https://github.com/zcash/librustzcash) via PyO3.

ZIP-321 defines a standard URI format for Zcash payment requests supporting
single and multi-recipient payments with amounts, memos, labels, and messages.

## Installation

```bash
pip install zcash-zip321
```

## Quick Start

### Parse a payment URI

```python
from zcash_zip321 import TransactionRequest

req = TransactionRequest.from_uri("zcash:zs1...?amount=1.5&memo=VGVzdA")

for idx, payment in req.payments().items():
    print(f"Payment {idx}:")
    print(f"  To:     {payment.recipient_address}")
    print(f"  Amount: {payment.amount_zec} ZEC")
    print(f"  Memo:   {payment.memo_text}")
```

### Build a payment URI

```python
from zcash_zip321 import Payment, TransactionRequest

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

## API Reference

### `Payment`

| Property | Type | Description |
|----------|------|-------------|
| `recipient_address` | `str` | Zcash address |
| `amount_zatoshis` | `int \| None` | Amount in zatoshis |
| `amount_zec` | `float \| None` | Amount in ZEC |
| `memo` | `bytes \| None` | Raw memo bytes |
| `memo_text` | `str \| None` | Memo as UTF-8 text |
| `label` | `str \| None` | Human-readable label |
| `message` | `str \| None` | Human-readable message |

### `TransactionRequest`

| Method | Returns | Description |
|--------|---------|-------------|
| `TransactionRequest(payments)` | | Create from list of `Payment` |
| `TransactionRequest.from_uri(uri)` | `TransactionRequest` | Parse a ZIP-321 URI |
| `.to_uri()` | `str` | Serialize to URI |
| `.payments()` | `dict[int, Payment]` | All payments |
| `.total_zatoshis()` | `int \| None` | Sum of all amounts |
| `.total_zec()` | `float \| None` | Sum in ZEC |
| `len(req)` | `int` | Number of payments |

### Helper Functions

- `memo_to_base64(memo: bytes) -> str` -- Encode memo bytes to ZIP-321 base64
- `memo_from_base64(encoded: str) -> bytes` -- Decode base64 memo

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
