import xml.etree.ElementTree as ET
import sys

def parse_junit_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    results = {}
    results['total_cases'] = 0
    results['unit_failures'] = 0
    results['integration_failures'] = 0
    results['acceptance_failures'] = 0
    results['collection_failures'] = 0
    results['error_failures'] = 0

    for testcase in root.findall(".//testcase"):
        results['total_cases'] += 1
        for failure in testcase.findall("failure"):
            failure_text = failure.text.lower() if failure.text else ""
            if '@pytest.mark.unit' in failure_text:
                results['unit_failures'] += 1
            elif '@pytest.mark.integration' in failure_text:
                results['integration_failures'] += 1
            elif '@pytest.mark.acceptance' in failure_text:
                results['acceptance_failures'] += 1

        for error in testcase.findall("error"):
            error_message = error.get('message', '').lower()
            error_text = error.text.lower() if error.text else ""
            if 'collection failure' in error_message:
                results['collection_failures'] += 1
            else:
                results['error_failures'] += 1
    return results

if __name__ == "__main__":
    xml_path = sys.argv[1]
    results = parse_junit_xml(xml_path)
    print(f"Unit Failures: {results['unit_failures']}/{results['total_cases']}")
    print(f"Integration Failures: {results['integration_failures']}/{results['total_cases']}")
    print(f"Acceptance Failures: {results['acceptance_failures']}/{results['total_cases']}")
    print(f"Collection Failures: {results['collection_failures']}/{results['total_cases']}")
    print(f"Other Error Failures: {results['error_failures']}/{results['total_cases']}")

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
