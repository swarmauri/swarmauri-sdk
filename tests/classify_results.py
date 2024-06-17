import xml.etree.ElementTree as ET
import sys

def parse_junit_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    unit_failures = 0
    integration_failures = 0
    acceptance_failures = 0
    collection_failures = 0
    error_failures = 0

    for testcase in root.findall(".//testcase"):
        for failure in testcase.findall("failure"):
            failure_text = failure.text.lower() if failure.text else ""
            if '@pytest.mark.unit' in failure_text:
                unit_failures += 1
            elif '@pytest.mark.integration' in failure_text:
                integration_failures += 1
            elif '@pytest.mark.acceptance' in failure_text:
                acceptance_failures += 1

        for error in testcase.findall("error"):
            error_message = error.get('message', '').lower()
            error_text = error.text.lower() if error.text else ""
            if 'collection failure' in error_message:
                collection_failures += 1
            else:
                error_failures += 1
    return unit_failures, integration_failures, acceptance_failures, collection_failures, error_failures

if __name__ == "__main__":
    xml_path = sys.argv[1]
    unit_failures, integration_failures, acceptance_failures, collection_failures, error_failures = parse_junit_xml(xml_path)
    print(f"Unit Failures: {unit_failures}")
    print(f"Integration Failures: {integration_failures}")
    print(f"Acceptance Failures: {acceptance_failures}")
    print(f"Collection Failures: {collection_failures}")
    print(f"Other Error Failures: {error_failures}")

    if acceptance_failures > 5:
        sys.exit(1)  # Exit with code 1 to indicate acceptance test failures
    elif integration_failures > 0:
        sys.exit(1)  # Exit with code 1 to indicate integration test failures
    elif unit_failures > 0:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures
    elif collection_failures > 0:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures
    elif error_failures > 0:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures
    else:
        sys.exit(0)  # Exit with code 0 to indicate no failures
