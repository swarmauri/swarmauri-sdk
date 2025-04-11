use pyo3::{prelude::*, types::PyList};
use std::borrow::Cow;

#[pymodule]
fn normalizer(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(lowercase, m)?)?;
    m.add_function(wrap_pyfunction!(remove_punctuation, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_unicode, m)?)?;
    Ok(())
}

#[pyfunction]
fn lowercase<'a>(text: &'a str) -> PyResult<Cow<'a, str>> {
    // Lowercase the input string
    Ok(Cow::from(text.to_lowercase()))
}

#[pyfunction]
fn remove_punctuation<'a>(text: &'a str) -> PyResult<Cow<'a, str>> {
    // Remove punctuation from the input string
    Ok(Cow::from(text.chars().filter(|c|!c.is_punctuation()).collect::<String>()))
}

#[pyfunction]
fn normalize_unicode<'a>(text: &'a str) -> PyResult<Cow<'a, str>> {
    // Normalize the input string to NFC (Normalization Form Compatibility Composition)
    Ok(Cow::from(text.chars().collect::<String>().to_lowercase().nfc().collect::<String>()))
}