![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_bulkhead/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_bulkhead" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_bulkhead">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_bulkhead&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri/swarmauri_middleware_bulkhead">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_bulkhead" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/swarmauri_middleware_bulkhead">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_bulkhead" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri/swarmauri_middleware_bulkhead">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_bulkhead?label=swarmauri_middleware_bulkhead&color=green" alt="PyPI - swarmauri_middleware_bulkhead"/></a>
</p>

---

# `swarmauri_middleware_bulkhead`

## Overview

The `swarmauri_middleware_bulkhead` package provides a middleware implementation for controlling concurrency isolation in FastAPI applications. It uses a semaphore-based approach to limit the number of concurrent requests, preventing resource overload and ensuring reliable service operation.

## Features

- **Concurrency Control**: Restricts the maximum number of simultaneous requests
- **Semaphore-based Management**: Efficiently manages request queuing and processing
- **Logging Integration**: Provides detailed logging for request processing and errors
- **Configurable**: Allows customizing the maximum concurrency level
- **Compatibility**: Works seamlessly with FastAPI applications

## Requirements

- Python 3.10+
- FastAPI
- `swarmauri_core` package
- `swarmauri_base` package

## Installation

To install the package, use Poetry or pip: