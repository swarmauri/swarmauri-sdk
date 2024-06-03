import xml.etree.ElementTree as ET
import sys

def parse_junit_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    unit_failures = 0
    integration_failures = 0
    acceptance_failures = 0

    for testcase in root.findall(".//testcase"):
        print(f"TestCase: {testcase}")
        properties = testcase.find('properties')
        if properties:
            for prop in properties.findall('property'):
                if prop.attrib['name'] == 'test':
                    test_type = prop.attrib['value']

                    if 'unit' in test_type:
                        for failure in testcase.findall("failure"):
                            unit_failures += 1

                    if 'integration' in test_type:
                        for failure in testcase.findall("failure"):
                            integration_failures += 1

                    if 'acceptance' in test_type:
                        for failure in testcase.findall("failure"):
                            acceptance_failures += 1

    return unit_failures, integration_failures, acceptance_failures

if __name__ == "__main__":
    xml_path = sys.argv[1]
    unit_failures, integration_failures, acceptance_failures = parse_junit_xml(xml_path)
    print(f"Unit Failures: {unit_failures}")
    print(f"Integration Failures: {integration_failures}")
    print(f"Acceptance Failures: {acceptance_failures}")

    if acceptance_failures > 5:
        sys.exit(1)  # Exit with code 1 to indicate acceptance test failures
    elif integration_failures > 0:
        sys.exit(2)  # Exit with code 2 to indicate integration test failures
    elif unit_failures > 0:
        sys.exit(3)  # Exit with code 3 to indicate unit test failures
    else:
        sys.exit(0)  # Exit with code 0 to indicate no failures
