import ast
from pathlib import Path
import sys


def gather_classes(package_path: Path):
    """Return list of class names defined within the package."""
    classes = []
    for file in package_path.rglob("*.py"):
        if "tests" in file.parts:
            continue
        try:
            source = file.read_text(encoding="utf-8")
        except Exception:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append((node.name, file))
    return classes


def load_test_files(tests_path: Path):
    files = []
    if not tests_path.exists():
        return files
    for file in tests_path.rglob("*.py"):
        try:
            content = file.read_text(encoding="utf-8")
        except Exception:
            content = ""
        files.append((file, content))
    return files


def class_has_test(class_name: str, test_files):
    for path, content in test_files:
        if class_name in path.stem:
            return True
        if class_name in content:
            return True
    return False


def main(repo_root: Path) -> int:
    pkgs_dir = repo_root / "pkgs"
    missing = []
    for pkg in pkgs_dir.iterdir():
        if not (pkg / "pyproject.toml").exists():
            continue
        classes = gather_classes(pkg)
        tests = load_test_files(pkg / "tests")
        for class_name, file_path in classes:
            if not class_has_test(class_name, tests):
                missing.append((pkg.name, class_name, file_path.relative_to(repo_root)))
    if missing:
        print("Missing test files for the following classes:")
        for pkg_name, class_name, rel_path in missing:
            print(f" - {pkg_name}:{class_name} ({rel_path})")
        return 1
    print("All classes have test files.")
    return 0


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    sys.exit(main(root))
