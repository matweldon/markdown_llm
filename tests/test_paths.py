import pytest
import tempfile
import os
from pathlib import Path
from llm_tool.paths import validate_file_path
"""
For the `validate_file_path` function, you should test the following properties:

1. It correctly identifies existing files
2. It correctly identifies new files
3. It raises a ValueError for non-existent directories
4. It raises a ValueError for directories without write permission
5. It raises a ValueError for filenames with invalid characters
6. It handles both absolute and relative paths
7. It handles paths that are just filenames
"""
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def existing_file(temp_dir):
    file_path = temp_dir / "existing_file.txt"
    file_path.touch()
    yield file_path

def test_existing_and_new_files(temp_dir, existing_file):
    assert validate_file_path(existing_file) == "exists"
    assert validate_file_path(temp_dir / "new_file.txt") == "new"

def test_non_existent_directory():
    with pytest.raises(ValueError, match="Directory does not exist"):
        validate_file_path("/non/existent/path/file.txt")

def test_no_write_permission(temp_dir):
    os.chmod(temp_dir, 0o555)  # Remove write permissions
    try:
        with pytest.raises(ValueError, match="No write permission in the directory"):
            validate_file_path(temp_dir / "test.txt")
    finally:
        os.chmod(temp_dir, 0o755)  # Restore permissions

def test_invalid_filename(temp_dir):
    with pytest.raises(ValueError, match="Invalid characters in filename"):
        validate_file_path(temp_dir / "invalid<>file.txt")

def test_absolute_and_relative_paths(temp_dir, existing_file):
    assert validate_file_path(existing_file.absolute()) == "exists"
    assert validate_file_path(existing_file.name) == "new"

def test_filename_only():
    assert validate_file_path("just_filename.txt") == "new"
