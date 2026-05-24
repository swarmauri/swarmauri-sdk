from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PKGS_ROOT = REPO_ROOT / "pkgs"
SWARMAURI_BRAND_URL = (
    "https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/"
    "3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg"
)
TIGRBL_BRAND_URL = (
    "https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/"
    "a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg"
)
PYTHON_BADGE = "3.10%20%7C%203.11%20%7C%203.12"
DISCORD_URL = "https://discord.gg/N4UpBuQv8T"
EXCLUDED_DIR_NAMES = {
    ".venv",
    ".pytest_cache",
    ".benchmarks",
    "__pycache__",
    "tests",
}
ACRONYMS = {
    "acme": "ACME",
    "adcs": "ADCS",
    "adyen": "Adyen",
    "ai21": "AI21",
    "api": "API",
    "args": "Args",
    "asn1": "ASN.1",
    "asgi": "ASGI",
    "aws": "AWS",
    "azure": "Azure",
    "ca": "CA",
    "cades": "CAdES",
    "cfssl": "CFSSL",
    "cli": "CLI",
    "cms": "CMS",
    "cnsa20": "CNSA 2.0",
    "cognito": "Cognito",
    "cose": "COSE",
    "cors": "CORS",
    "cron": "Cron",
    "crl": "CRL",
    "csr": "CSR",
    "csronly": "CSR Only",
    "cwt": "CWT",
    "dpop": "DPoP",
    "dsse": "DSSE",
    "ecdh": "ECDH",
    "ecdsa": "ECDSA",
    "ed25519": "Ed25519",
    "fips": "FIPS",
    "fitzpdf": "FitzPDF",
    "fs": "FS",
    "gcpkms": "GCP KMS",
    "gitea": "Gitea",
    "github": "GitHub",
    "gitlab": "GitLab",
    "gmail": "Gmail",
    "google": "Google",
    "groq": "Groq",
    "gzipcompression": "Gzip Compression",
    "h2": "HTTP/2",
    "h2mux": "HTTP/2 Mux",
    "hamming74": "Hamming (7,4)",
    "hkp": "HKP",
    "hpks": "HPKS",
    "hmac": "HMAC",
    "httploaded": "HTTP Loaded",
    "httpsig": "HTTP Signatures",
    "idp": "IDP",
    "iopub": "IOPub",
    "ipsec": "IPsec",
    "jsonrpc": "JSON-RPC",
    "jupyter": "Jupyter",
    "jwks": "JWKS",
    "jwe": "JWE",
    "jws": "JWS",
    "jwt": "JWT",
    "kms": "KMS",
    "llm": "LLM",
    "llamaguard": "Llama Guard",
    "minio": "MinIO",
    "mlm": "MLM",
    "mock": "Mock",
    "mtlsunicast": "mTLS Unicast",
    "mutualinformation": "Mutual Information",
    "nacl": "NaCl",
    "neo4j": "Neo4j",
    "nmf": "NMF",
    "oauth": "OAuth",
    "ocsp": "OCSP",
    "oidc": "OIDC",
    "okta": "Okta",
    "openai": "OpenAI",
    "openpgp": "OpenPGP",
    "paseto": "PASETO",
    "pades": "PAdES",
    "paypal": "PayPal",
    "paystack": "Paystack",
    "pdf": "PDF",
    "pep458": "PEP 458",
    "pgp": "PGP",
    "pinecone": "Pinecone",
    "pkcs11": "PKCS#11",
    "png": "PNG",
    "pop": "PoP",
    "pypdf2": "PyPDF2",
    "pypdftk": "PyPDFTK",
    "qdrant": "Qdrant",
    "quic": "QUIC",
    "rabbitmq": "RabbitMQ",
    "ratepolicy": "Rate Policy",
    "razorpay": "Razorpay",
    "redis": "Redis",
    "rsa": "RSA",
    "s3fs": "S3FS",
    "salesforce": "Salesforce",
    "scep": "SCEP",
    "sdk": "SDK",
    "secp256k1": "secp256k1",
    "self": "Self",
    "self_signed": "Self Signed",
    "sigstore": "Sigstore",
    "sigv4": "SigV4",
    "smogindex": "SMOG Index",
    "sseoutbound": "SSE Outbound",
    "ssh": "SSH",
    "sshcert": "SSH Cert",
    "sshsig": "SSH Sig",
    "sshtunnel": "SSH Tunnel",
    "stdio": "Stdio",
    "svg": "SVG",
    "tcpunicast": "TCP Unicast",
    "textblob": "TextBlob",
    "tfidf": "TF-IDF",
    "tiff": "TIFF",
    "tigrbl": "Tigrbl",
    "tls": "TLS",
    "tlsboundjwt": "TLS-Bound JWT",
    "tokencountestimator": "Token Count Estimator",
    "toolkit": "Toolkit",
    "uds": "UDS",
    "udp": "UDP",
    "webauthn": "WebAuthn",
    "webhook": "Webhook",
    "webauthn": "WebAuthn",
    "webauthn": "WebAuthn",
    "whisper": "Whisper",
    "wsjsonrpcmux": "WS JSON-RPC Mux",
    "x509": "X.509",
    "x509verify": "X.509 Verify",
    "xmld": "XMLD",
    "xmp": "XMP",
    "yubikey": "YubiKey",
    "zapierhook": "Zapier Hook",
}


def package_roots() -> list[Path]:
    roots: list[Path] = []
    for pyproject in PKGS_ROOT.rglob("pyproject.toml"):
        if any(part in EXCLUDED_DIR_NAMES for part in pyproject.parts):
            continue
        if ".venv" in pyproject.parts:
            continue
        roots.append(pyproject.parent)
    return sorted(roots)


def read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def prettify_token(token: str) -> str:
    raw = token.strip()
    if not raw:
        return ""
    lowered = raw.lower()
    if lowered in ACRONYMS:
        return ACRONYMS[lowered]
    if any(char.isupper() for char in raw[1:]):
        return raw
    return raw.capitalize()


def title_from_name(project_name: str) -> str:
    tokens = re.split(r"[_\-]+", project_name)
    return " ".join(filter(None, (prettify_token(token) for token in tokens)))


def brand_info(project_name: str, package_root: Path) -> tuple[str, str]:
    joined = f"{project_name} {' '.join(package_root.parts)}".lower()
    if "tigrbl" in joined:
        return "Tigrbl", TIGRBL_BRAND_URL
    return "Swarmauri", SWARMAURI_BRAND_URL


def python_versions(project: dict[str, Any]) -> list[str]:
    versions: list[str] = []
    for classifier in project.get("classifiers", []):
        match = re.search(r"Programming Language :: Python :: (\d+\.\d+)$", classifier)
        if match:
            versions.append(match.group(1))
    ordered = sorted(set(versions))
    if not ordered:
        return ["3.10", "3.11", "3.12"]
    return ordered


def package_lane(package_root: Path) -> str:
    relative = package_root.relative_to(REPO_ROOT).parts
    if len(relative) >= 2:
        return relative[1]
    return "pkgs"


def package_import_targets(pyproject: dict[str, Any], package_root: Path) -> list[str]:
    poetry_packages = pyproject.get("tool", {}).get("poetry", {}).get("packages", [])
    imports: list[str] = []
    for package_entry in poetry_packages:
        include = package_entry.get("include")
        if include:
            imports.append(include)

    candidates = [package_root / "src", package_root]
    for base in candidates:
        if not base.exists():
            continue
        for init_file in base.glob("*/__init__.py"):
            if init_file.parent.name in EXCLUDED_DIR_NAMES:
                continue
            imports.append(init_file.parent.name)

    project_name = pyproject.get("project", {}).get("name")
    if project_name:
        imports.append(project_name.replace("-", "_"))
    return sorted(dict.fromkeys(imports))


def extract_exports(import_targets: list[str], package_root: Path) -> tuple[str | None, list[str]]:
    candidates = []
    for import_name in import_targets:
        candidates.extend(
            [
                package_root / "src" / import_name / "__init__.py",
                package_root / import_name / "__init__.py",
            ]
        )
    init_path = next((candidate for candidate in candidates if candidate.exists()), None)
    if not init_path:
        return (import_targets[0] if import_targets else None, [])

    text = init_path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return (init_path.parent.name, [])

    exports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for element in node.value.elts:
                            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                                exports.append(element.value)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    exports.append(alias.asname or alias.name)

    cleaned = [
        name
        for name in exports
        if name not in {"__version__", "annotations"}
        and not name.startswith("_")
    ]
    return (init_path.parent.name, list(dict.fromkeys(cleaned)))


def entry_points(project: dict[str, Any]) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []
    for group, values in project.items():
        if not isinstance(values, dict):
            continue
        if group == "scripts":
            for name, target in values.items():
                results.append(("scripts", name, target))
        elif group == "entry-points":
            for subgroup, entries in values.items():
                if isinstance(entries, dict):
                    for name, target in entries.items():
                        results.append((subgroup, name, target))
    return results


def is_deprecated(project: dict[str, Any], description: str, package_root: Path) -> bool:
    lowered = f"{description} {' '.join(project.get('classifiers', []))} {package_root}".lower()
    return "deprecated" in lowered or "inactive" in lowered or "compatibility shim" in lowered


def wrap_sentence(text: str) -> str:
    stripped = " ".join(text.split())
    if not stripped:
        return ""
    if stripped[-1] not in ".!?":
        return stripped + "."
    return stripped


def feature_lines(
    project_name: str,
    description: str,
    lane: str,
    import_name: str | None,
    exported_names: list[str],
    entry_point_rows: list[tuple[str, str, str]],
    deprecated: bool,
) -> list[str]:
    feature_set: list[str] = []
    summary = wrap_sentence(description or f"{project_name} is a focused package in the Swarmauri SDK workspace.")
    feature_set.append(f"- {summary}")

    if deprecated:
        feature_set.append(
            "- Preserves legacy imports and package boundaries so older integrations can keep running while you migrate to active packages."
        )
    elif entry_point_rows:
        group_names = sorted({row[0] for row in entry_point_rows if row[0] != "scripts"})
        if group_names:
            joined = ", ".join(group_names)
            feature_set.append(
                f"- Exposes discoverable runtime entry points for `{joined}` so the package can be wired into Swarmauri or Tigrbl workflows."
            )
        else:
            feature_set.append(
                "- Ships with a package-local command or integration surface that can be installed independently from the rest of the workspace."
            )
    elif exported_names and import_name:
        joined = ", ".join(f"`{name}`" for name in exported_names[:4])
        feature_set.append(
            f"- Centers its public API around {joined} so downstream code can import the package directly without extra registry glue."
        )
    else:
        feature_set.append(
            "- Keeps the package surface isolated so you can install only the capability you need instead of the full workspace."
        )

    if lane == "plugins":
        feature_set.append(
            "- Supports direct plugin instantiation from application code; avoid `PluginManager` unless a task explicitly requires it."
        )
    elif lane == "experimental":
        feature_set.append(
            "- Provides an experimental workspace surface for early validation before functionality graduates into a more stable package lane."
        )
    elif lane == "community":
        feature_set.append(
            "- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface."
        )
    elif lane == "standards":
        feature_set.append(
            "- Fits the standards package lane so the capability can be added to a project as a focused, separately versioned dependency."
        )
    else:
        feature_set.append(
            "- Aligns with the current workspace packaging model so the package can participate cleanly in larger Swarmauri SDK builds."
        )

    return feature_set


def installation_block(project_name: str) -> str:
    return (
        "## Installation\n\n"
        "Install this package with `uv` or `pip`.\n\n"
        "```bash\n"
        f"uv add {project_name}\n"
        "```\n\n"
        "```bash\n"
        f"pip install {project_name}\n"
        "```\n"
    )


def usage_block(
    project_name: str,
    lane: str,
    import_name: str | None,
    exported_names: list[str],
    scripts: list[tuple[str, str, str]],
    deprecated: bool,
) -> str:
    lines = ["## Usage", ""]

    if deprecated:
        lines.append(
            "Use this package only as a compatibility bridge while moving callers onto active packages in the workspace."
        )
    elif lane == "plugins":
        lines.append(
            "Instantiate the exported plugin classes directly in your application or test harness. Do not route plugin setup through `PluginManager` unless you were explicitly asked to do so."
        )
    elif "tigrbl" in project_name.lower():
        lines.append(
            "Import the exported types and wire them into the Tigrbl application or runtime where this package is needed."
        )
    else:
        lines.append(
            "Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it."
        )
    lines.append("")

    if import_name and exported_names:
        names = ", ".join(exported_names[:4])
        lines.extend(
            [
                "```python",
                f"from {import_name} import {names}",
                "",
                f"exports = [{', '.join(repr(name) for name in exported_names[:4])}]",
                "print(exports)",
                "```",
            ]
        )
    elif import_name:
        lines.extend(
            [
                "```python",
                f"import {import_name}",
                "",
                f"print({import_name}.__name__)",
                "```",
            ]
        )
    elif scripts:
        script_name = scripts[0][1]
        lines.extend(
            [
                "```bash",
                f"{script_name} --help",
                "```",
            ]
        )
    else:
        lines.extend(
            [
                "```python",
                f"import {project_name.replace('-', '_')}",
                "```",
            ]
        )
    lines.append("")

    if scripts:
        script_names = ", ".join(f"`{row[1]}`" for row in scripts)
        lines.append(f"Installed command-line entry points: {script_names}.")
    elif deprecated:
        lines.append(
            "Expect legacy imports to continue working, but plan migration work because the package is retained for compatibility rather than long-term growth."
        )
    else:
        lines.append(
            "After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details."
        )
    return "\n".join(lines) + "\n"


def make_readme(package_root: Path) -> str:
    pyproject = read_toml(package_root / "pyproject.toml")
    project = pyproject.get("project", {})
    project_name = project["name"]
    description = project.get("description", "").strip()
    lane = package_lane(package_root)
    readme_path = package_root / "README.md"
    title = title_from_name(project_name)
    brand_name, brand_url = brand_info(project_name, package_root)
    versions = python_versions(project)
    imports = package_import_targets(pyproject, package_root)
    import_name, exported_names = extract_exports(imports, package_root)
    entry_point_rows = entry_points(project)
    script_rows = [row for row in entry_point_rows if row[0] == "scripts"]
    deprecated = is_deprecated(project, description, package_root)
    rel_path = package_root.relative_to(REPO_ROOT).as_posix()

    version_badge = project_name
    header = [
        f"![{brand_name} Logo]({brand_url})",
        "",
        '<p align="center">',
        f'    <a href="https://pepy.tech/project/{project_name}/">',
        f'        <img src="https://static.pepy.tech/badge/{project_name}/month" alt="PyPI - Downloads"/></a>',
        f'    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/{rel_path}/">',
        f'        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/{rel_path}.svg"/></a>',
        f'    <a href="https://pypi.org/project/{project_name}/">',
        f'        <img src="https://img.shields.io/badge/python-{PYTHON_BADGE}-blue" alt="Supported Python Versions"/></a>',
        f'    <a href="https://pypi.org/project/{project_name}/">',
        f'        <img src="https://img.shields.io/pypi/l/{project_name}" alt="License"/></a>',
        f'    <a href="https://pypi.org/project/{project_name}/">',
        f'        <img src="https://img.shields.io/pypi/v/{project_name}?label={version_badge}&color=green" alt="Release Version"/></a>',
        f'    <a href="{DISCORD_URL}">',
        '        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>',
        "</p>",
        "",
        f"# {title}",
        "",
        wrap_sentence(description or f"{title} is a package in the Swarmauri SDK workspace."),
        "",
        "## Features",
        "",
    ]

    features = feature_lines(
        project_name=project_name,
        description=description,
        lane=lane,
        import_name=import_name,
        exported_names=exported_names,
        entry_point_rows=entry_point_rows,
        deprecated=deprecated,
    )
    body = "\n".join(header + features) + "\n\n"
    body += installation_block(project_name) + "\n"
    body += usage_block(
        project_name=project_name,
        lane=lane,
        import_name=import_name,
        exported_names=exported_names,
        scripts=script_rows,
        deprecated=deprecated,
    )
    body += "\nLicense: Apache-2.0. See `LICENSE`.\n"
    return body


def main() -> None:
    for package_root in package_roots():
        readme_path = package_root / "README.md"
        readme_path.write_text(make_readme(package_root), encoding="utf-8", newline="\n")
        print(readme_path.relative_to(REPO_ROOT).as_posix())


if __name__ == "__main__":
    main()
