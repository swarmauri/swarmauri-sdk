"""
h2/hpack.py

Provides stub implementations for HPACK header compression and decompression.
A complete implementation must follow the HPACK specification including dynamic table
management, Huffman coding, and proper indexing.
"""

def hpack_encode(headers):
    """
    Naively encode headers into a bytes object.
    
    WARNING: This implementation is for demonstration purposes only and is not compliant
    with the HPACK specification.
    
    :param headers: dict, header key-value pairs.
    :return: bytes, the encoded header block.
    """
    # For demonstration, simply create a newline-separated list of header lines.
    # Each header is encoded as "key:value".
    header_lines = []
    for key, value in headers.items():
        header_lines.append(f"{key}:{value}")
    header_str = "\n".join(header_lines)
    return header_str.encode("utf-8")

def hpack_decode(data):
    """
    Naively decode a bytes object into header key-value pairs.
    
    WARNING: This implementation is for demonstration purposes only and is not compliant
    with the HPACK specification.
    
    :param data: bytes, the encoded header block.
    :return: dict, the decoded header key-value pairs.
    """
    header_str = data.decode("utf-8")
    headers = {}
    for line in header_str.split("\n"):
        if not line.strip():
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers

if __name__ == "__main__":
    # Example usage:
    sample_headers = {
        "content-type": "application/json",
        "cache-control": "no-cache"
    }
    encoded = hpack_encode(sample_headers)
    print("Encoded headers:", encoded)

    decoded = hpack_decode(encoded)
    print("Decoded headers:", decoded)
