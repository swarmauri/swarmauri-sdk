use pyo3::prelude::*;
use pyo3::types::PyString;
use regex::Regex;
use log::{info, error};

/// High-speed regex-based tokenizer.
///
/// This class provides an implementation of a Rust-accelerated tokenizer 
/// that leverages optimized regex processing for extremely fast token extraction.
#[pymodule]
pub struct RegexTokenizer {
    /// The regex pattern used for tokenization.
    pattern: Regex,
}

#[pyproto]
impl pyo3::class::PyProto for RegexTokenizer {
    fn __init__(slf: PyRefMut<Self>, pattern: &str) {
        slf.pattern = Regex::new(pattern).unwrap();
    }
}

impl RegexTokenizer {
    /// Tokenize the input string using the provided regex pattern.
    ///
    /// Args:
    ///     input (str): The input string to be tokenized.
    ///
    /// Returns:
    ///     List[str]: A list of extracted tokens.
    #[pyfunction]
    pub fn tokenize(&self, input: &str) -> PyResult<Vec<String>> {
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
    #[pyfunction]
    pub fn get_pattern(&self) -> PyResult<String> {
        Ok(self.pattern.as_str().to_string())
    }
}

#[pymodule]
impl pyo3::class::PyModule for RegexTokenizer {
    fn __name__(&self) -> &str {
        "RegexTokenizer"
    }

    fn __doc__(&self) -> &str {
        "High-speed regex-based tokenizer."
    }
}

/// Define a Python module for the RegexTokenizer class.
#[pymodule]
fn regex_tokenizer(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RegexTokenizer>()?;
    Ok(())
}