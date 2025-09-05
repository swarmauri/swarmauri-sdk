use pyo3::prelude::*;

#[pyclass]
pub struct WhitespaceTokenizer {}

#[pymethods]
impl WhitespaceTokenizer {
    #[new]
    fn new() -> Self {
        WhitespaceTokenizer {}
    }

    fn tokenize(&self, input: &str) -> PyResult<Vec<String>> {
        let tokens: Vec<String> = input.split_whitespace()
            .map(|s| s.to_string())
            .collect();
        Ok(tokens)
    }
}