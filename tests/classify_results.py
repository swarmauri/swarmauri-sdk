import xml.etree.ElementTree as ET
import sys

def parse_junit_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    unit_failures = 0
    integration_failures = 0
    acceptance_failures = 0

    for testcase in root.findall(".//testcase"):
        for failure in testcase.findall("failure"):
            if 'unit' in testcase.attrib.get('classname', '').lower():
                unit_failures += 1
            elif 'integration' in testcase.attrib.get('classname', '').lower():
                integration_failures += 1
            elif 'acceptance' in testcase.attrib.get('classname', '').lower():
                acceptance_failures += 1

    return unit_failures, integration_failures, acceptance_failures

if __name__ == "__main__":
    xml_path = sys.argv[1]
    unit_failures, integration_failures, acceptance_failures = parse_junit_xml(xml_path)
    print(f"Unit Failures: {unit_failures}")
    print(f"Integration Failures: {integration_failures}")
    print(f"Acceptance Failures: {acceptance_failures}")

    if unit_failures + integration_failures > 0:
        sys.exit(1)  # Exit with code 1 to indicate acceptance test failures
    else:
        sys.exit(0)  # Exit with code 0 to indicate no acceptance test failures
