import py_compile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_python_files_compile() -> None:
    python_files = list((PROJECT_ROOT / "src").rglob("*.py")) + list((PROJECT_ROOT / "dags").rglob("*.py"))

    assert python_files, "Expected Python files under src/ or dags/."

    for file_path in python_files:
        py_compile.compile(str(file_path), doraise=True)
