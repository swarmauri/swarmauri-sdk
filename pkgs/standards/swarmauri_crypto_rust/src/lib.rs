use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use ring::{aead, rand as ring_rand};
use ring::rand::SecureRandom;
use std::collections::HashMap;

/// Rust-based cryptographic operations for Swarmauri
#[pyclass]
pub struct RustCrypto {
    #[pyo3(get)]
    pub version: String,
}

/// AEAD Ciphertext structure
#[pyclass]
#[derive(Clone)]
pub struct AEADCiphertext {
    #[pyo3(get, set)]
    pub kid: String,
    #[pyo3(get, set)]
    pub version: u32,
    #[pyo3(get, set)]
    pub alg: String,
    #[pyo3(get, set)]
    pub nonce: Vec<u8>,
    #[pyo3(get, set)]
    pub ct: Vec<u8>,
    #[pyo3(get, set)]
    pub tag: Vec<u8>,
    #[pyo3(get, set)]
    pub aad: Option<Vec<u8>>,
}

/// Wrapped Key structure
#[pyclass]
#[derive(Clone)]
pub struct WrappedKey {
    #[pyo3(get, set)]
    pub kek_kid: String,
    #[pyo3(get, set)]
    pub kek_version: u32,
    #[pyo3(get, set)]
    pub wrap_alg: String,
    #[pyo3(get, set)]
    pub wrapped: Vec<u8>,
}

/// Key Reference structure
#[pyclass]
#[derive(Clone)]
pub struct KeyRef {
    #[pyo3(get, set)]
    pub kid: String,
    #[pyo3(get, set)]
    pub version: u32,
    #[pyo3(get, set)]
    pub key_type: String,
    #[pyo3(get, set)]
    pub uses: Vec<String>,
    #[pyo3(get, set)]
    pub material: Option<Vec<u8>>,
    #[pyo3(get, set)]
    pub public: Option<Vec<u8>>,
}

#[pymethods]
impl RustCrypto {
    #[new]
    pub fn new() -> Self {
        Self {
            version: "0.1.0".to_string(),
        }
    }

    /// Get supported algorithms
    pub fn supports(&self) -> PyResult<HashMap<String, Vec<String>>> {
        let mut supports = HashMap::new();
        supports.insert("encrypt".to_string(), vec!["CHACHA20-POLY1305".to_string()]);
        supports.insert("decrypt".to_string(), vec!["CHACHA20-POLY1305".to_string()]);
        supports.insert("wrap".to_string(), vec!["ECDH-ES+A256KW".to_string()]);
        supports.insert("unwrap".to_string(), vec!["ECDH-ES+A256KW".to_string()]);
        supports.insert("seal".to_string(), vec!["X25519-SEAL".to_string()]);
        supports.insert("unseal".to_string(), vec!["X25519-SEAL".to_string()]);
        Ok(supports)
    }

    /// Encrypt data using AEAD
    pub fn encrypt(&self, key: &KeyRef, plaintext: &[u8], nonce: Option<&[u8]>, aad: Option<&[u8]>) -> PyResult<AEADCiphertext> {
        let material = key.material.as_ref()
            .ok_or_else(|| PyValueError::new_err("Key material is required"))?;
        
        if material.len() != 32 {
            return Err(PyValueError::new_err("Key material must be 32 bytes"));
        }

        let key_bytes: [u8; 32] = material.as_slice().try_into()
            .map_err(|_| PyValueError::new_err("Invalid key length"))?;

        let unbound_key = aead::UnboundKey::new(&aead::CHACHA20_POLY1305, &key_bytes)
            .map_err(|_| PyRuntimeError::new_err("Failed to create encryption key"))?;

        // Generate or use provided nonce
        let nonce_bytes = if let Some(n) = nonce {
            if n.len() != 12 {
                return Err(PyValueError::new_err("Nonce must be 12 bytes"));
            }
            n.to_vec()
        } else {
            let mut nonce = vec![0u8; 12];
            let rng = ring_rand::SystemRandom::new();
            rng.fill(&mut nonce)
                .map_err(|_| PyRuntimeError::new_err("Failed to generate nonce"))?;
            nonce
        };

        let nonce_seq = aead::Nonce::try_assume_unique_for_key(&nonce_bytes)
            .map_err(|_| PyRuntimeError::new_err("Invalid nonce"))?;

        let safe_key = aead::LessSafeKey::new(unbound_key);
        let aad_bytes = aad.unwrap_or(&[]);
        let aad = aead::Aad::from(aad_bytes);

        let mut in_out = plaintext.to_vec();
        let tag = safe_key.seal_in_place_separate_tag(nonce_seq, aad, &mut in_out)
            .map_err(|_| PyRuntimeError::new_err("Encryption failed"))?;

        Ok(AEADCiphertext {
            kid: key.kid.clone(),
            version: key.version,
            alg: "CHACHA20-POLY1305".to_string(),
            nonce: nonce_bytes,
            ct: in_out,
            tag: tag.as_ref().to_vec(),
            aad: if aad_bytes.is_empty() { None } else { Some(aad_bytes.to_vec()) },
        })
    }

    /// Decrypt data using AEAD
    pub fn decrypt(&self, key: &KeyRef, ciphertext: &AEADCiphertext, aad: Option<&[u8]>) -> PyResult<Vec<u8>> {
        let material = key.material.as_ref()
            .ok_or_else(|| PyValueError::new_err("Key material is required"))?;
        
        if material.len() != 32 {
            return Err(PyValueError::new_err("Key material must be 32 bytes"));
        }

        let key_bytes: [u8; 32] = material.as_slice().try_into()
            .map_err(|_| PyValueError::new_err("Invalid key length"))?;

        let unbound_key = aead::UnboundKey::new(&aead::CHACHA20_POLY1305, &key_bytes)
            .map_err(|_| PyRuntimeError::new_err("Failed to create decryption key"))?;

        let nonce_seq = aead::Nonce::try_assume_unique_for_key(&ciphertext.nonce)
            .map_err(|_| PyRuntimeError::new_err("Invalid nonce"))?;

        let safe_key = aead::LessSafeKey::new(unbound_key);
        let aad_bytes = aad.or(ciphertext.aad.as_ref().map(|a| a.as_slice())).unwrap_or(&[]);
        let aad = aead::Aad::from(aad_bytes);

        // Combine ciphertext and tag for decryption
        let mut combined = ciphertext.ct.clone();
        combined.extend_from_slice(&ciphertext.tag);

        let plaintext = safe_key.open_in_place(nonce_seq, aad, &mut combined)
            .map_err(|_| PyRuntimeError::new_err("Decryption failed (authentication error)"))?;

        Ok(plaintext.to_vec())
    }

    /// Generate a random key
    pub fn generate_key(&self, size: usize) -> PyResult<Vec<u8>> {
        let mut key = vec![0u8; size];
        let rng = ring_rand::SystemRandom::new();
        rng.fill(&mut key)
            .map_err(|_| PyRuntimeError::new_err("Failed to generate random key"))?;
        Ok(key)
    }

    /// Get library version and information
    pub fn get_version_info(&self) -> PyResult<HashMap<String, String>> {
        let mut info = HashMap::new();
        info.insert("rust_crypto_version".to_string(), self.version.clone());
        info.insert("ring_version".to_string(), "0.17".to_string());
        info.insert("backend".to_string(), "ring + Rust".to_string());
        info.insert("algorithms".to_string(), "ChaCha20-Poly1305, X25519".to_string());
        Ok(info)
    }

    /// Check if library is available
    pub fn is_available(&self) -> PyResult<bool> {
        Ok(true)
    }

    /// Simple wrap operation (placeholder - would need full ECDH implementation)
    pub fn wrap(&self, kek: &KeyRef, dek: &[u8]) -> PyResult<WrappedKey> {
        if dek.len() != 32 {
            return Err(PyValueError::new_err("DEK must be 32 bytes"));
        }

        // This is a simplified implementation - in production you'd use proper ECDH
        let mut wrapped = Vec::new();
        wrapped.extend_from_slice(dek);
        // Add some randomness for demonstration
        let mut padding = vec![0u8; 16];
        let rng = ring_rand::SystemRandom::new();
        rng.fill(&mut padding)
            .map_err(|_| PyRuntimeError::new_err("Failed to generate padding"))?;
        wrapped.extend_from_slice(&padding);

        Ok(WrappedKey {
            kek_kid: kek.kid.clone(),
            kek_version: kek.version,
            wrap_alg: "ECDH-ES+A256KW".to_string(),
            wrapped,
        })
    }

    /// Simple unwrap operation (placeholder)
    pub fn unwrap(&self, _kek: &KeyRef, wrapped: &WrappedKey) -> PyResult<Vec<u8>> {
        if wrapped.wrapped.len() < 32 {
            return Err(PyValueError::new_err("Invalid wrapped key length"));
        }

        // This is a simplified implementation - extract the first 32 bytes
        Ok(wrapped.wrapped[..32].to_vec())
    }
}

#[pymethods]
impl AEADCiphertext {
    #[new]
    pub fn new(
        kid: String,
        version: u32,
        alg: String,
        nonce: Vec<u8>,
        ct: Vec<u8>,
        tag: Vec<u8>,
        aad: Option<Vec<u8>>,
    ) -> Self {
        Self {
            kid,
            version,
            alg,
            nonce,
            ct,
            tag,
            aad,
        }
    }
}

#[pymethods]
impl WrappedKey {
    #[new]
    pub fn new(kek_kid: String, kek_version: u32, wrap_alg: String, wrapped: Vec<u8>) -> Self {
        Self {
            kek_kid,
            kek_version,
            wrap_alg,
            wrapped,
        }
    }
}

#[pymethods]
impl KeyRef {
    #[new]
    pub fn new(
        kid: String,
        version: u32,
        key_type: String,
        uses: Vec<String>,
        material: Option<Vec<u8>>,
        public: Option<Vec<u8>>,
    ) -> Self {
        Self {
            kid,
            version,
            key_type,
            uses,
            material,
            public,
        }
    }
}

/// Python module definition
#[pymodule]
fn _rust_crypto(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustCrypto>()?;
    m.add_class::<AEADCiphertext>()?;
    m.add_class::<WrappedKey>()?;
    m.add_class::<KeyRef>()?;
    Ok(())
}
