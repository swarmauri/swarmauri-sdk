# `FastTokenizer`

## Installation

To install the `FastTokenizer` package, you can use pip:

```bash
pip install fasttokenizer
```

## Usage

You can use the `FastTokenizer` package as follows:

```python
import fasttokenizer

# Load the text from a file
text = fasttokenizer.load_text("example.txt")

# Tokenize the text
tokens = fasttokenizer.tokenize(text)

# Get the regex pattern used for tokenization
pattern = fasttokenizer.get_pattern()

# Save the text to a file
fasttokenizer.save_text("output.txt", text)

# Read the text from a file
read_text = fasttokenizer.read_text("example.txt")

# Tokenize the text again
tokens = fasttokenizer.tokenize(read_text)

# Get the normalized text
normalized_text = fasttokenizer.normalize_unicode(read_text)

# Print the results
print("Tokens:", tokens)
print("Normalized Text:", normalized_text)
```

### Dependencies
#### `FastTokenizer/FastTokenizer/regex_tokenizer.rs`
```rust
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

#[pymodule]
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
```

#### `FastTokenizer/FastTokenizer/whitespace_tokenizer.rs`
```rust
#[cfg(feature = "py_bindings")]
#[pymodule]
fn fasttokenizer {
    #[pyfunction]
    fn whitespace_tokenizer(text: &str) -> Vec<String> {
        let mut result = vec![];
        let mut buffer = String::new();

        for char in text.chars() {
            if char.is_whitespace() {
                buffer.push(char);
                if buffer.ends_with('\n') {
                    buffer.pop();
                }
                if!buffer.is_empty() {
                    result.push(buffer.clone());
                    buffer.clear();
                }
            } else {
                buffer.push(char);
            }
        }

        if!buffer.is_empty() {
            result.push(buffer.clone());
        }

        result
    }
}
```

#### `FastTokenizer/FastTokenizer/normalizer.rs`
```rust
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
```

#### `FastTokenizer/FastTokenizer/tokenizer_io.rs`
```rust
use pyo3::prelude::*;
use std::fs::File;
use std::io::{self, BufReader, Read};

/// Module for tokenizer I/O operations.
#[pymodule]
#[pyo3(name = "tokenizer_io")]
pub mod tokenizer_io {
    /// Loads text from a file.
    ///
    /// Args:
    ///     filename (str): The path to the file.
    ///
    /// Returns:
    ///     str: The content of the file as a string.
    ///
    /// Raises:
    ///     PyIOError: If the file cannot be opened or read.
    #[pyfunction]
    pub fn load_text(filename: &str) -> PyResult<String> {
        // Open the file in read-only mode.
        let file = File::open(filename).map_err(|e| PyIOError::new(e.kind(), e.to_string()))?;
        let mut reader = BufReader::new(file);
        let mut buffer = String::new();

        // Read the entire file content into the buffer.
        reader.read_to_string(&mut buffer).map_err(|e| PyIOError::new(e.kind(), e.to_string()))?;

        Ok(buffer)
    }

    /// Reads text from a string reader.
    ///
    /// Args:
    ///     text (str): The text to read.
    ///
    /// Returns:
    ///     str: The input text.
    #[pyfunction]
    pub fn read_text(text: &str) -> PyResult<String> {
        Ok(text.to_string())
    }

    /// Saves text to a file.
    ///
    /// Args:
    ///     filename (str): The path to the file.
    ///     text (str): The text to save.
    ///
    /// Raises:
    ///     PyIOError: If the file cannot be opened or written.
    #[pyfunction]
    pub fn save_text(filename: &str, text: &str) -> PyResult<()> {
        // Open the file in write mode.
        let file = File::create(filename).map_err(|e| PyIOError::new(e.kind(), e.to_string()))?;
        let mut writer = io::BufWriter::new(file);

        // Write the text to the file.
        writer.write_all(text.as_bytes()).map_err(|e| PyIOError::new(e.kind(), e.to_string()))?;
        writer.flush().map_err(|e| PyIOError::new(e.kind(), e.to_string()))?;

        Ok(())
    }
}
```

#### `FastTokenizer/pyproject.toml`
```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "FastTokenizer"
version = "0.1.0"
description = "A fast tokenizer implemented in Rust"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.8"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
classifiers = [
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Programming Language :: Rust"
]
keywords = ["tokenizer", "nlp", "rust", "fast", "text processing"]

dependencies = [
    "regex", # Example dependency
    "pyo3"  # Example dependency
]

[tool.maturin]
features = ["py_bindings"]
module-name = "fasttokenizer"
python-source = "src"

[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "i9n: Integration tests",
    "r8n: Regression tests",
    "xfail: Expected failures",
    "xpass: Expected passes"
]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s [%(levelname)s] %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
```