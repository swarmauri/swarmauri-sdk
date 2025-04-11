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
                if !buffer.is_empty() {
                    result.push(buffer.clone());
                    buffer.clear();
                }
            } else {
                buffer.push(char);
            }
        }

        if !buffer.is_empty() {
            result.push(buffer.clone());
        }

        result
    }
}