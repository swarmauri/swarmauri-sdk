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