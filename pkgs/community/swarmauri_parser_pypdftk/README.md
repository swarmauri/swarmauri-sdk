![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_parser_pypdftk/">
        <img src="https://static.pepy.tech/badge/swarmauri_parser_pypdftk/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdftk/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_parser_pypdftk.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/pypi/l/swarmauri_parser_pypdftk" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_parser_pypdftk/">
        <img src="https://img.shields.io/pypi/v/swarmauri_parser_pypdftk?label=swarmauri_parser_pypdftk&color=green" alt="PyPI - swarmauri_parser_pypdftk"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Parser PyPDFTK

`swarmauri_parser_pypdftk` is the Swarmauri PDF form-field parser for
extracting AcroForm data through [PyPDFTK](https://pypi.org/project/pypdftk/)
and the native `pdftk` toolchain. It converts structured PDF form fields into a
single Swarmauri `Document` so downstream workflows can index, validate, or
route filled forms.

## Why Use Swarmauri Parser PyPDFTK

- Extract structured PDF field data instead of only free-form text.
- Normalize AcroForm output into a Swarmauri `Document` for ingestion,
  automation, and analysis pipelines.
- Keep form parsing aligned with the same Swarmauri parser interface used by
  other document components.
- Pair form-field extraction with other PDF parsers when both structured fields
  and page text matter.

## FAQ

> **What does this parser extract?**  
> PDF form fields returned by `pypdftk.dump_data_fields`, such as AcroForm
> names and values.

> **Does it parse ordinary PDF text?**  
> No. This package is for structured PDF form fields. Use another parser for
> general page text.

> **Does it need a system binary?**  
> Yes. It depends on the `pdftk` or `pdftk-java` executable being installed and
> available on `PATH`.

> **What happens when the PDF has no form fields?**  
> The parser returns an empty list.

## Features

- Extracts PDF AcroForm fields through PyPDFTK.
- Returns one Swarmauri `Document` with newline-delimited `key: value` content.
- Preserves the input source path in metadata.
- Useful for form ingestion, validation, compliance workflows, and automation.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_parser_pypdftk
```

```bash
pip install swarmauri_parser_pypdftk
```

System requirement:

- Install `pdftk` or `pdftk-java` and make sure the executable is available on
  `PATH`.

## Usage

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
documents = parser.parse("forms/enrollment.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content)
```

## Examples

### Extract form fields from a filled PDF

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
docs = parser.parse("forms/application.pdf")

if docs:
    print(docs[0].content)
```

Example output:

```text
GivenName: John
FamilyName: Doe
BirthDate: 1990-01-01
```

### Detect forms without field data

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
docs = parser.parse("forms/plain.pdf")

if not docs:
    print("No PDF form fields were detected.")
```

## Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [PyPDFTK on PyPI](https://pypi.org/project/pypdftk/)
- [pdftk-java project](https://gitlab.com/pdftk-java/pdftk)

## Best Practices

- Use this parser for PDFs with real AcroForm fields, not for generic PDF page
  text.
- Validate that the `pdftk` binary is installed in deployment targets before
  running pipelines that depend on this package.
- Pair this package with `swarmauri_parser_pypdf2` or
  `swarmauri_parser_fitzpdf` if you also need free-form page text.
- Route scan-only documents through OCR if they are image-based and contain no
  useful form structure.

## License

This project is licensed under the Apache-2.0 License.


