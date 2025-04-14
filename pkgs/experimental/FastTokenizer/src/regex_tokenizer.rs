use pyo3::prelude::*;
use pyo3::types::PyType;
use regex::Regex;
use log::info;

/// High-speed regex-based tokenizer.
///
/// This class provides an implementation of a Rust-accelerated tokenizer 
/// that leverages optimized regex processing for extremely fast token extraction.
#[pyclass]
pub struct RegexTokenizer {
    /// The regex pattern used for tokenization.
    pattern: Regex,
}

#[pymethods]
impl RegexTokenizer {
    /// Create a new RegexTokenizer with the given pattern
    #[new]
    fn new(pattern: &str) -> PyResult<Self> {
        match Regex::new(pattern) {
            Ok(regex) => Ok(RegexTokenizer { pattern: regex }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid regex pattern: {}", e)
            ))
        }
    }

    /// Tokenize the input string using the provided regex pattern.
    ///
    /// Args:
    ///     input (str): The input string to be tokenized.
    ///
    /// Returns:
    ///     List[str]: A list of extracted tokens.
    fn tokenize(&self, input: &str) -> PyResult<Vec<String>> {
        info!("Tokenizing input string...");
        let tokens: Vec<String> = self.pattern.find_iter(input)
           .map(|m| m.as_str().to_string())
           .collect();
        Ok(tokens)
    }

    /// Get the regex pattern used for tokenization.
    ///
    /// Returns:
    ///     str: The regex pattern as a string.
    fn get_pattern(&self) -> PyResult<String> {
        Ok(self.pattern.as_str().to_string())
    }
    
    /// Class documentation for Python
    #[classattr]
    fn __doc__() -> &'static str {
        "High-speed regex-based tokenizer."
    }
}