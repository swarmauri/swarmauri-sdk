import json
import sys
from collections import defaultdict

def analyze_tags_from_file(file_path):
    try:
        # Load JSON data from the file
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Extract the summary and list of tests
        summary = data.get("summary", {})
        tests = data.get("tests", [])
        
        # Check if the summary and tests exist
        if not summary or not tests:
            print("No test data or summary found in the provided file.")
            return

        # Get total number of tests
        total_tests = summary.get("total", 0)

        # Print summary with percentage
        print("\nTest Results Summary:")
        print(f"{'Category':<15} {'Count':<10} {'Total':<10} {'% of Total':<10}")
        print("-" * 50)
        for category in ["passed", "skipped", "failed"]:
            count = summary.get(category, 0)
            percentage = (count / total_tests) * 100 if total_tests > 0 else 0
            print(f"{category.capitalize():<15} {count:<10} {total_tests:<10} {percentage:<10.2f}")
        print("\n")

        # Group tests by tags
        tag_outcomes = defaultdict(lambda: {"passed": 0, "total": 0})

        for test in tests:
            outcome = test["outcome"]
            for tag in test["keywords"]:
                tag_outcomes[tag]["total"] += 1
                if outcome == "passed":
                    tag_outcomes[tag]["passed"] += 1

        # Print detailed results by tags
        print("Tag-Based Results:")
        print(f"{'Tag':<30} {'Passed':<10} {'Total':<10} {'% Passed':<10}")
        print("-" * 70)
        for tag, outcomes in tag_outcomes.items():
            passed = outcomes["passed"]
            total = outcomes["total"]
            percentage = (passed / total) * 100 if total > 0 else 0
            print(f"{tag:<30} {passed:<10} {total:<10} {percentage:<10.2f}")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from file: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Check if the file path is provided
    if len(sys.argv) != 2:
        print("Usage: python tag_analysis.py <path_to_json_file>")
        sys.exit(1)

    # Get the file path from command-line arguments
    json_file_path = sys.argv[1]

    # Run the analysis
    analyze_tags_from_file(json_file_path)
