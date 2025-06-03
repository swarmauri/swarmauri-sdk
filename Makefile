trivy-scan:
trivy fs . --exit-code 1 --severity CRITICAL,HIGH --no-progress

bandit-scan:
bandit -r src || bandit -r pkgs

sbom:
trivy sbom --format cyclonedx --output sbom.xml .
