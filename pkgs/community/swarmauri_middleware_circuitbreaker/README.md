![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_circuitbreaker/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_circuitbreaker" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_circuitbreaker">
        <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/swarmauri/swarmauri-sdk/pkgs/pkgs/swarmauri_middleware_circuitbreaker&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false" alt="GitHub Hits"/></a>
    <a href="https://pypi.org/project/swarmauri/swarmauri_middleware_circuitbreaker">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_circuitbreaker" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/swarmauri_middleware_circuitbreaker">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_circuitbreaker" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri/swarmauri_middleware_circuitbreaker">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_circuitbreaker?label=swarmauri_middleware_circuitbreaker&color=green" alt="PyPI - swarmauri_middleware_circuitbreaker"/></a>
</p>

---

# `swarmauri_middleware_circuitbreaker`

Circuit Breaker Middleware for protecting downstream services using pybreaker.

## Overview

This middleware implements a circuit breaker pattern to prevent cascading failures in distributed systems. It monitors failed requests and opens the circuit when a specified threshold of consecutive failures is reached, preventing further requests until the service becomes healthy again.

## Installation

To install the package, run: