"""Tests for the FTP server functionality."""

import tempfile
import time
from pathlib import Path

import pytest

from ftpdispatch.server import find_most_recent_directory


@pytest.fixture
def temp_base_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def base_dir_with_subdirs(temp_base_dir):
    """Create a base directory with multiple subdirectories of different ages."""
    base_path = Path(temp_base_dir)

    # Create directories with different creation times using sleep for portability
    dir_old = base_path / "aaa"
    dir_old.mkdir()
    dir_new = base_path / "bbb"
    dir_new.mkdir()

    return temp_base_dir, str(dir_old), str(dir_new)


def test_find_most_recent_directory_empty(temp_base_dir):
    """Test directory selection with no subdirectories."""
    result = find_most_recent_directory(temp_base_dir)
    assert result is None


def test_find_most_recent_directory_single(temp_base_dir):
    """Test directory selection with single subdirectory."""
    test_dir = Path(temp_base_dir) / "single_dir"
    test_dir.mkdir()

    result = find_most_recent_directory(temp_base_dir)
    assert result == str(test_dir)


def test_find_most_recent_directory_multiple(base_dir_with_subdirs):
    """Test directory selection with multiple subdirectories."""
    base_dir, dir_old, dir_new = base_dir_with_subdirs

    result = find_most_recent_directory(base_dir)
    assert result == dir_new


def test_find_most_recent_directory_nonexistent():
    """Test directory selection with nonexistent base directory."""
    result = find_most_recent_directory("/nonexistent/path")
    assert result is None


def test_find_most_recent_directory_file_not_dir(temp_base_dir):
    """Test directory selection when base path is a file, not directory."""
    test_file = Path(temp_base_dir) / "test_file.txt"
    test_file.write_text("test")

    result = find_most_recent_directory(str(test_file))
    assert result is None


def test_find_most_recent_directory_many_dirs(temp_base_dir):
    """Test directory selection with many directories."""
    base_path = Path(temp_base_dir)

    # Create directories in specific order, with the 4th one being most recent
    dir_names = ["dir_0", "dir_1", "dir_2", "dir_3", "dir_4"]

    for i, name in enumerate(dir_names):
        if i > 0:
            time.sleep(0.01)  # Ensure different creation times
        dir_path = base_path / name
        dir_path.mkdir()

    result = find_most_recent_directory(temp_base_dir)

    # Should select the last created directory
    expected = str(base_path / "dir_4")
    assert result == expected


def test_find_most_recent_directory_mixed_files_and_dirs(temp_base_dir):
    """Test directory selection ignores files, only considers directories."""
    base_path = Path(temp_base_dir)

    # Create directories first
    dir_old = base_path / "aaa_dir"
    dir_old.mkdir()
    dir_new = base_path / "bbb_dir"
    dir_new.mkdir()

    # Create files (should be ignored even if more recent)
    file1 = base_path / "recent_file.txt"
    file1.write_text("content")

    result = find_most_recent_directory(temp_base_dir)

    # Should select the most recent directory, not the file
    assert result == str(dir_new)


@pytest.fixture
def base_dir_with_many_subdirs(temp_base_dir):
    """Create a base directory with many subdirectories for stress testing."""
    base_path = Path(temp_base_dir)

    # Create 5 directories with small delays between them
    dirs = []
    for i in range(5):
        if i > 0:
            time.sleep(0.01)  # Small delay between directory creation
        dir_path = base_path / f"test_dir_{i:02d}"
        dir_path.mkdir()
        dirs.append(str(dir_path))

    return temp_base_dir, dirs


def test_find_most_recent_directory_stress_test(base_dir_with_many_subdirs):
    """Test directory selection with many directories."""
    base_dir, dirs = base_dir_with_many_subdirs

    result = find_most_recent_directory(base_dir)

    # Should select the last created directory (test_dir_04)
    expected_dir = dirs[-1]  # Last directory in the list
    assert result == expected_dir
