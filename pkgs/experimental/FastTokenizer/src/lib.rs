use pyo3::prelude::*;

mod normalizer;
mod regex_tokenizer;
mod tokenizer_io;
mod whitespace_tokenizer;

// Import the specific functions and classes
use normalizer::{lowercase, remove_punctuation, normalize_unicode, Normalizer};
use regex_tokenizer::RegexTokenizer;
use tokenizer_io::TokenizerIO;
use whitespace_tokenizer::WhitespaceTokenizer;

/// A Python module implemented in Rust.
#[pymodule]
fn fasttokenizer(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register classes
    m.add_class::<Normalizer>()?;
    m.add_class::<RegexTokenizer>()?;
    m.add_class::<TokenizerIO>()?;
    m.add_class::<WhitespaceTokenizer>()?;
    
    // Register standalone functions
    m.add_function(wrap_pyfunction!(lowercase, m)?)?;
    m.add_function(wrap_pyfunction!(remove_punctuation, m)?)?;
    m.add_function(wrap_pyfunction!(normalize_unicode, m)?)?;
    
    // Add the module version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    
    Ok(())
}