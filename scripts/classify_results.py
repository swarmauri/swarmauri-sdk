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
    results['experimental_failures'] = 0
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

            elif '@pytest.mark.experimental' in failure_text: 
                results['experimental_failures'] += 1

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
    failures = 0
    failures += results['unit_failures'] 
    failures += results['integration_failures']
    failures += results['acceptance_failures']
    failures += results['experimental_failures']
    failures += results['collection_failures']
    failures += results['error_failures']

    print(f"Unit Failures: {results['unit_failures']}/{results['total_cases']}")
    print(f"Integration Failures: {results['integration_failures']}/{results['total_cases']}")
    print(f"Acceptance Failures: {results['acceptance_failures']}/{results['total_cases']}")
    print(f"Experimental Failures: {results['experimental_failures']}/{results['total_cases']}")
    print(f"Collection Failures: {results['collection_failures']}/{results['total_cases']}")
    print(f"Other Error Failures: {results['error_failures']}/{results['total_cases']}")

    print()
    print(f"Failures: {failures}/{results['total_cases']}")
    print(f"Passing: {results['total_cases'] - failures}/{results['total_cases']}")
    try:
        print(f"Pass Rate: {(1 - int(failures) / int(results['total_cases'])) * 100:.2f}%")
    except ZeroDivisionError:
        print(f"Pass Rate: 0 out of 0")

    if results['unit_failures'] > 0:
        sys.exit(1)  # Exit with code 1 to indicate acceptance test failures

    elif results['integration_failures'] > 0:
        sys.exit(1)  # Exit with code 1 to indicate integration test failures

    elif results['acceptance_failures'] > 10:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures

    elif results['experimental_failures'] > 10:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures

    elif results['collection_failures'] > 0:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures

    elif results['error_failures'] > 0:
        sys.exit(1)  # Exit with code 1 to indicate unit test failures

    else:
        sys.exit(0)  # Exit with code 0 to indicate no failures
