import xml.etree.ElementTree as ET
import sys

def parse_junit_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    minor_failures = 0
    major_failures = 0
    normal_failures = 0

    for testcase in root.findall(".//testcase"):
        for failure in testcase.findall("failure"):
            if 'minor' in testcase.attrib.get('classname', '').lower():
                minor_failures += 1
            elif 'major' in testcase.attrib.get('classname', '').lower():
                major_failures += 1
            else:
                normal_failures += 1

    return minor_failures, major_failures, normal_failures

if __name__ == "__main__":
    xml_path = sys.argv[1]
    minor_failures, major_failures, normal_failures = parse_junit_xml(xml_path)
    print(f"Minor Failures: {minor_failures}")
    print(f"Major Failures: {major_failures}")
    print(f"Normal Failures: {normal_failures}")

    if major_failures > 0:
        sys.exit(1)  # Exit with code 1 to indicate major failures
    else:
        sys.exit(0)  # Exit with code 0 to indicate no major failures
