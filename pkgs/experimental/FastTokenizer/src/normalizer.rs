use pyo3::prelude::*;
use std::borrow::Cow;
use unicode_normalization::UnicodeNormalization;

// Add 'pub' keyword to make these functions public
#[pyfunction]
pub fn lowercase<'a>(text: &'a str) -> PyResult<Cow<'a, str>> {
    // Lowercase the input string
    Ok(Cow::from(text.to_lowercase()))
}

#[pyfunction]
pub fn remove_punctuation<'a>(text: &'a str) -> PyResult<Cow<'a, str>> {
    // Remove punctuation from the input string
    Ok(Cow::from(text.chars().filter(|c| !c.is_ascii_punctuation()).collect::<String>()))
}

#[pyfunction]
pub fn normalize_unicode<'a>(text: &'a str) -> PyResult<Cow<'a, str>> {
    // Normalize the input string
    Ok(Cow::from(text.nfc().collect::<String>()))
}

// Create a Normalizer class to expose to Python
#[pyclass]
pub struct Normalizer {}

#[pymethods]
impl Normalizer {
    #[new]
    fn new() -> Self {
        Normalizer {}
    }
    
    fn lowercase(&self, text: &str) -> PyResult<String> {
        Ok(text.to_lowercase())
    }
    
    fn remove_punctuation(&self, text: &str) -> PyResult<String> {
        Ok(text.chars()
            .filter(|c| !c.is_ascii_punctuation())
            .collect::<String>())
    }
    
    fn normalize_unicode(&self, text: &str) -> PyResult<String> {
        Ok(text.to_lowercase().nfc().collect::<String>())
    }
}