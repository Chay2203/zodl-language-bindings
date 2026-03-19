use pyo3::prelude::*;
use pyo3::create_exception;
use pyo3::types::PyList;
use std::collections::BTreeMap;

use zcash_address::ZcashAddress;
use zcash_protocol::memo::MemoBytes;
use zcash_protocol::value::Zatoshis;

// ---------------------------------------------------------------------------
// Exception hierarchy: all inherit from Zip321Error
// ---------------------------------------------------------------------------

create_exception!(zcash_uri, Zip321Error, pyo3::exceptions::PyException);
create_exception!(zcash_uri, ParseError, Zip321Error);
create_exception!(zcash_uri, InvalidBase64Error, Zip321Error);
create_exception!(zcash_uri, MemoTooLongError, Zip321Error);
create_exception!(zcash_uri, TooManyPaymentsError, Zip321Error);
create_exception!(zcash_uri, TransparentMemoError, Zip321Error);
create_exception!(zcash_uri, RecipientMissingError, Zip321Error);
create_exception!(zcash_uri, InvalidPaymentError, Zip321Error);
create_exception!(zcash_uri, InvalidAddressError, Zip321Error);

/// Convert a zip321::Zip321Error into the appropriate Python exception.
fn zip321_err_to_py(err: zip321::Zip321Error) -> PyErr {
    use zip321::Zip321Error as E;
    match err {
        E::InvalidBase64(e) => InvalidBase64Error::new_err(format!("{e}")),
        E::MemoBytesError(e) => MemoTooLongError::new_err(format!("{e}")),
        E::TooManyPayments(n) => {
            TooManyPaymentsError::new_err(format!("Too many payments: {n}"))
        }
        E::DuplicateParameter(p, i) => {
            ParseError::new_err(format!("Duplicate parameter {p:?} at index {i}"))
        }
        E::TransparentMemo(i) => {
            TransparentMemoError::new_err(format!(
                "Payment {i} attaches a memo to a transparent address"
            ))
        }
        E::RecipientMissing(i) => {
            RecipientMissingError::new_err(format!("Recipient missing at index {i}"))
        }
        E::ParseError(s) => ParseError::new_err(s),
    }
}

// ---------------------------------------------------------------------------
// Internal data carrier (not exposed to Python)
// ---------------------------------------------------------------------------

const ZEC_COIN: u64 = 100_000_000;
const MAX_MONEY: u64 = 21_000_000 * ZEC_COIN;

#[derive(Clone, Debug)]
struct PaymentData {
    address: String,
    amount: Option<u64>,
    memo: Option<Vec<u8>>,
    label: Option<String>,
    message: Option<String>,
}

impl PaymentData {
    /// Convert to the Rust `zip321::Payment` type.
    fn to_rust_payment(&self) -> PyResult<zip321::Payment> {
        let addr = ZcashAddress::try_from_encoded(&self.address)
            .map_err(|e| InvalidAddressError::new_err(format!("{e}")))?;

        let amount = Zatoshis::from_u64(self.amount.unwrap_or(0))
            .map_err(|_| InvalidPaymentError::new_err(
                format!("Amount {} exceeds maximum ({MAX_MONEY})", self.amount.unwrap_or(0))
            ))?;

        let memo = match &self.memo {
            Some(m) => Some(
                MemoBytes::from_bytes(m)
                    .map_err(|e| MemoTooLongError::new_err(format!("{e}")))?,
            ),
            None => None,
        };

        zip321::Payment::new(
            addr,
            amount,
            memo,
            self.label.clone(),
            self.message.clone(),
            vec![],
        )
        .ok_or_else(|| {
            TransparentMemoError::new_err(
                "Invalid payment: cannot add memo to transparent address",
            )
        })
    }

    /// Build from a Rust `zip321::Payment` (e.g. after parsing a URI).
    fn from_rust_payment(p: &zip321::Payment) -> Self {
        let memo = p.memo().map(|m| {
            let bytes = m.as_slice();
            // Strip trailing null-padding for a cleaner Python experience
            let end = bytes
                .iter()
                .rposition(|&b| b != 0)
                .map(|i| i + 1)
                .unwrap_or(0);
            bytes[..end].to_vec()
        });

        PaymentData {
            address: p.recipient_address().encode(),
            amount: Some(p.amount().into_u64()),
            memo,
            label: p.label().cloned(),
            message: p.message().cloned(),
        }
    }
}

// ---------------------------------------------------------------------------
// Payment (Python class)
// ---------------------------------------------------------------------------

/// A single payment within a ZIP-321 transaction request.
#[pyclass(module = "zcash_uri")]
#[derive(Clone, Debug)]
struct Payment {
    data: PaymentData,
}

#[pymethods]
impl Payment {
    /// Create a new Payment.
    ///
    /// Args:
    ///     recipient_address: Zcash address string (shielded or transparent).
    ///     amount_zatoshis: Amount in zatoshis (1 ZEC = 100_000_000 zatoshis).
    ///     memo: Optional memo as ``str`` (UTF-8) or ``bytes`` (max 512 bytes).
    ///     label: Optional human-readable label for the payment.
    ///     message: Optional human-readable message.
    #[new]
    #[pyo3(signature = (recipient_address, amount_zatoshis=None, memo=None, label=None, message=None))]
    fn new(
        recipient_address: String,
        amount_zatoshis: Option<u64>,
        memo: Option<Bound<'_, PyAny>>,
        label: Option<String>,
        message: Option<String>,
    ) -> PyResult<Self> {
        // Validate address
        let addr = ZcashAddress::try_from_encoded(&recipient_address)
            .map_err(|e| InvalidAddressError::new_err(format!("{e}")))?;

        // Validate amount
        if let Some(a) = amount_zatoshis {
            Zatoshis::from_u64(a).map_err(|_| {
                InvalidPaymentError::new_err(format!(
                    "Amount {a} exceeds maximum ({MAX_MONEY})"
                ))
            })?;
        }

        // Convert memo (accept str or bytes)
        let memo_bytes: Option<Vec<u8>> = match memo {
            None => None,
            Some(obj) => {
                let bytes: Vec<u8> = if let Ok(s) = obj.extract::<String>() {
                    s.into_bytes()
                } else if let Ok(b) = obj.extract::<Vec<u8>>() {
                    b
                } else {
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "memo must be str or bytes",
                    ));
                };
                if bytes.len() > 512 {
                    return Err(MemoTooLongError::new_err(format!(
                        "Memo is {} bytes, maximum is 512",
                        bytes.len()
                    )));
                }
                Some(bytes)
            }
        };

        // Transparent address + memo check
        if memo_bytes.is_some() && !addr.can_receive_memo() {
            return Err(TransparentMemoError::new_err(
                "Cannot attach a memo to a transparent address",
            ));
        }

        Ok(Payment {
            data: PaymentData {
                address: recipient_address,
                amount: amount_zatoshis,
                memo: memo_bytes,
                label,
                message,
            },
        })
    }

    /// The recipient Zcash address.
    #[getter]
    fn recipient_address(&self) -> &str {
        &self.data.address
    }

    /// Amount in zatoshis, or ``None`` if unspecified.
    #[getter]
    fn amount_zatoshis(&self) -> Option<u64> {
        self.data.amount
    }

    /// Convenience: amount in ZEC as a float, or ``None``.
    #[getter]
    fn amount_zec(&self) -> Option<f64> {
        self.data.amount.map(|a| a as f64 / ZEC_COIN as f64)
    }

    /// Raw memo bytes (without null-padding), or ``None``.
    #[getter]
    fn memo(&self) -> Option<&[u8]> {
        self.data.memo.as_deref()
    }

    /// Memo decoded as UTF-8, or ``None`` if absent / not valid UTF-8.
    #[getter]
    fn memo_text(&self) -> Option<String> {
        self.data
            .memo
            .as_ref()
            .and_then(|m| std::str::from_utf8(m).ok().map(String::from))
    }

    /// Human-readable label, or ``None``.
    #[getter]
    fn label(&self) -> Option<&str> {
        self.data.label.as_deref()
    }

    /// Human-readable message, or ``None``.
    #[getter]
    fn message(&self) -> Option<&str> {
        self.data.message.as_deref()
    }

    fn __repr__(&self) -> String {
        let amt = match self.data.amount {
            Some(a) => format!("{a}"),
            None => "None".to_string(),
        };
        format!(
            "Payment(recipient_address={:?}, amount_zatoshis={})",
            self.data.address, amt
        )
    }

    fn __eq__(&self, other: &Payment) -> bool {
        self.data.address == other.data.address
            && self.data.amount == other.data.amount
            && self.data.memo == other.data.memo
            && self.data.label == other.data.label
            && self.data.message == other.data.message
    }
}

// ---------------------------------------------------------------------------
// TransactionRequest (Python class)
// ---------------------------------------------------------------------------

/// A ZIP-321 transaction request containing one or more payments.
#[pyclass(module = "zcash_uri")]
#[derive(Clone, Debug)]
struct TransactionRequest {
    payment_data: BTreeMap<usize, PaymentData>,
}

#[pymethods]
impl TransactionRequest {
    /// Create a TransactionRequest from a list of ``Payment`` objects.
    #[new]
    fn new(payments: Bound<'_, PyList>) -> PyResult<Self> {
        let mut payment_data = BTreeMap::new();
        let mut rust_payments = Vec::new();

        for (i, item) in payments.iter().enumerate() {
            let p: PyRef<Payment> = item.extract()?;
            payment_data.insert(i, p.data.clone());
            rust_payments.push(p.data.to_rust_payment()?);
        }

        // Validate through the Rust library
        zip321::TransactionRequest::new(rust_payments).map_err(zip321_err_to_py)?;

        Ok(TransactionRequest { payment_data })
    }

    /// Parse a ZIP-321 URI string into a ``TransactionRequest``.
    #[staticmethod]
    fn from_uri(uri: &str) -> PyResult<Self> {
        let req = zip321::TransactionRequest::from_uri(uri).map_err(zip321_err_to_py)?;
        let payment_data = req
            .payments()
            .iter()
            .map(|(&idx, p)| (idx, PaymentData::from_rust_payment(p)))
            .collect();
        Ok(TransactionRequest { payment_data })
    }

    /// Serialize this request to a ZIP-321 URI string.
    fn to_uri(&self) -> PyResult<String> {
        let rust_payments: Vec<zip321::Payment> = self
            .payment_data
            .values()
            .map(|d| d.to_rust_payment())
            .collect::<PyResult<Vec<_>>>()?;
        let req = zip321::TransactionRequest::new(rust_payments).map_err(zip321_err_to_py)?;
        Ok(req.to_uri())
    }

    /// Return all payments as ``dict[int, Payment]``.
    fn payments(&self) -> BTreeMap<usize, Payment> {
        self.payment_data
            .iter()
            .map(|(&idx, d)| (idx, Payment { data: d.clone() }))
            .collect()
    }

    /// Total amount in zatoshis across all payments, or ``None`` if any
    /// payment omits the amount.
    fn total_zatoshis(&self) -> PyResult<Option<u64>> {
        let mut total: u64 = 0;
        for d in self.payment_data.values() {
            match d.amount {
                None => return Ok(None),
                Some(a) => {
                    total = total.checked_add(a).ok_or_else(|| {
                        InvalidPaymentError::new_err("Total amount overflow")
                    })?;
                    if total > MAX_MONEY {
                        return Err(InvalidPaymentError::new_err(format!(
                            "Total {total} exceeds maximum ({MAX_MONEY})"
                        )));
                    }
                }
            }
        }
        Ok(Some(total))
    }

    /// Total amount in ZEC (float), or ``None``.
    fn total_zec(&self) -> PyResult<Option<f64>> {
        self.total_zatoshis()
            .map(|opt| opt.map(|z| z as f64 / ZEC_COIN as f64))
    }

    fn __len__(&self) -> usize {
        self.payment_data.len()
    }

    fn __repr__(&self) -> String {
        format!("TransactionRequest(payments={})", self.payment_data.len())
    }
}

// ---------------------------------------------------------------------------
// Module-level helpers
// ---------------------------------------------------------------------------

/// Encode raw memo bytes to the base64 format used in ZIP-321 URIs.
#[pyfunction]
fn memo_to_base64(memo: &[u8]) -> PyResult<String> {
    let memo_bytes =
        MemoBytes::from_bytes(memo).map_err(|e| MemoTooLongError::new_err(format!("{e}")))?;
    Ok(zip321::memo_to_base64(&memo_bytes))
}

/// Decode a ZIP-321 base64-encoded memo back to raw bytes.
#[pyfunction]
fn memo_from_base64(encoded: &str) -> PyResult<Vec<u8>> {
    let memo_bytes = zip321::memo_from_base64(encoded).map_err(zip321_err_to_py)?;
    let bytes = memo_bytes.as_slice();
    let end = bytes
        .iter()
        .rposition(|&b| b != 0)
        .map(|i| i + 1)
        .unwrap_or(0);
    Ok(bytes[..end].to_vec())
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

#[pymodule]
fn zcash_uri(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Classes
    m.add_class::<Payment>()?;
    m.add_class::<TransactionRequest>()?;

    // Functions
    m.add_function(wrap_pyfunction!(memo_to_base64, m)?)?;
    m.add_function(wrap_pyfunction!(memo_from_base64, m)?)?;

    // Exceptions
    m.add("Zip321Error", m.py().get_type::<Zip321Error>())?;
    m.add("ParseError", m.py().get_type::<ParseError>())?;
    m.add("InvalidBase64Error", m.py().get_type::<InvalidBase64Error>())?;
    m.add("MemoTooLongError", m.py().get_type::<MemoTooLongError>())?;
    m.add("TooManyPaymentsError", m.py().get_type::<TooManyPaymentsError>())?;
    m.add("TransparentMemoError", m.py().get_type::<TransparentMemoError>())?;
    m.add("RecipientMissingError", m.py().get_type::<RecipientMissingError>())?;
    m.add("InvalidPaymentError", m.py().get_type::<InvalidPaymentError>())?;
    m.add("InvalidAddressError", m.py().get_type::<InvalidAddressError>())?;

    // Version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}
