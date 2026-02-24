"""
utils.py

Provides common utility functions for the HTTP client package.
"""

def to_bytes(data, encoding='utf-8'):
    """
    Convert the input data to bytes.

    :param data: A str or bytes object.
    :param encoding: The encoding to use if data is a str.
    :return: Data as bytes.
    :raises TypeError: If data is not a str or bytes.
    """
    if isinstance(data, bytes):
        return data
    elif isinstance(data, str):
        return data.encode(encoding)
    else:
        raise TypeError("Data must be of type str or bytes")


def to_str(data, encoding='utf-8'):
    """
    Convert the input data to a string.

    :param data: A bytes or str object.
    :param encoding: The encoding to use if data is bytes.
    :return: Data as a string.
    :raises TypeError: If data is not a str or bytes.
    """
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode(encoding)
    else:
        raise TypeError("Data must be of type str or bytes")


def merge_headers(*headers):
    """
    Merge multiple header dictionaries into one.

    Later headers override keys from earlier ones.

    :param headers: One or more dictionaries containing header key-value pairs.
    :return: A single dictionary with merged headers.
    """
    merged = {}
    for header in headers:
        if header and isinstance(header, dict):
            merged.update(header)
    return merged


if __name__ == "__main__":
    # Example usage:
    sample_str = "Hello, World!"
    sample_bytes = b"Hello, Bytes!"
    
    print("to_bytes:", to_bytes(sample_str))
    print("to_str:", to_str(sample_bytes))
    
    default_headers = {"Content-Type": "application/json"}
    extra_headers = {"Authorization": "Bearer token", "Content-Type": "text/plain"}
    merged = merge_headers(default_headers, extra_headers)
    print("Merged Headers:", merged)
