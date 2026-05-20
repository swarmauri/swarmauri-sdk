![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_standard/">
        <img src="https://static.pepy.tech/badge/swarmauri_standard/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_standard/tests/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_standard/tests.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_standard/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_standard/">
        <img src="https://img.shields.io/pypi/l/swarmauri_standard" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_standard/">
        <img src="https://img.shields.io/pypi/v/swarmauri_standard?label=swarmauri_standard&color=green" alt="PyPI - swarmauri_standard"/></a>
</p>

# Swarmauri-SDK Test Cases
This project demonstrates how to classify pytest errors using GitHub Actions and handle the workflow based on the severity of the failures.

## Test Classification

Tests are classified into three categories:
- Unit tests
- Integration tests
- Acceptance tests


## Running the Tests

The tests can be run locally using pytest:
```sh
pytest --junitxml=results.xml
python classify_test_results.py results.xml
