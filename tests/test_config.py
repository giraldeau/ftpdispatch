"""Tests for configuration file handling."""

import argparse
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ftpdispatch.config import ConfigFileAction, create_example_config, load_config_file, merge_config_with_args


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config = {
            "base_dir": "/test/base/dir",
            "host": "192.168.1.100",
            "port": 2122,
            "user": "testuser",
            "password": "testpass",
        }
        json.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def invalid_json_file():
    """Create a temporary file with invalid JSON."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json content")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


def test_load_config_file_success(temp_config_file):
    """Test successful loading of config file."""
    config = load_config_file(temp_config_file)

    assert config["base_dir"] == "/test/base/dir"
    assert config["host"] == "192.168.1.100"
    assert config["port"] == 2122
    assert config["user"] == "testuser"
    assert config["password"] == "testpass"


def test_load_config_file_not_found():
    """Test loading non-existent config file."""
    with pytest.raises(FileNotFoundError):
        load_config_file("/nonexistent/config.json")


def test_load_config_file_invalid_json(invalid_json_file):
    """Test loading config file with invalid JSON."""
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_config_file(invalid_json_file)


def test_create_example_config():
    """Test creating example config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "example_config.json"

        with patch("builtins.print"):  # Suppress print output
            create_example_config(str(config_path))

        assert config_path.exists()

        # Verify content
        with open(config_path) as f:
            config = json.load(f)

        assert "base_dir" in config
        assert "host" in config
        assert "port" in config
        assert "user" in config
        assert "password" in config


def test_merge_config_with_args():
    """Test merging config file with command line arguments."""
    config = {"base_dir": "/config/base", "host": "config.host.com", "port": 9999, "user": "configuser"}

    # Create mock args namespace
    args = argparse.Namespace()
    args.base_dir = "/args/base"  # This should override config
    args.host = None  # This should use config value
    args.port = 8888  # This should override config
    args.user = None  # This should use config value
    args.password = "argspass"  # This should be added

    merged = merge_config_with_args(config, args)

    assert merged["base_dir"] == "/args/base"  # Command line wins
    assert merged["host"] == "config.host.com"  # Config value used
    assert merged["port"] == 8888  # Command line wins
    assert merged["user"] == "configuser"  # Config value used
    assert merged["password"] == "argspass"  # Command line value added


def test_config_file_action_success(temp_config_file):
    """Test ConfigFileAction with valid config file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action=ConfigFileAction)
    parser.add_argument("--base-dir")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)

    # Parse with config file
    args = parser.parse_args(["--config", temp_config_file])

    # Check that config values were loaded
    assert args.base_dir == "/test/base/dir"
    assert args.host == "192.168.1.100"
    assert args.port == 2122


def test_config_file_action_override(temp_config_file):
    """Test that command line args override config file values."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action=ConfigFileAction)
    parser.add_argument("--base-dir")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)

    # Parse with config file and command line overrides
    args = parser.parse_args(["--config", temp_config_file, "--host", "override.host.com", "--port", "3333"])

    # Check that command line values override config
    assert args.base_dir == "/test/base/dir"  # From config
    assert args.host == "override.host.com"  # Command line override
    assert args.port == 3333  # Command line override


def test_config_file_action_nonexistent():
    """Test ConfigFileAction with non-existent config file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action=ConfigFileAction)

    with pytest.raises(SystemExit):  # argparse calls parser.error which raises SystemExit
        parser.parse_args(["--config", "/nonexistent/config.json"])


def test_config_file_action_invalid_json(invalid_json_file):
    """Test ConfigFileAction with invalid JSON file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action=ConfigFileAction)

    with pytest.raises(SystemExit):  # argparse calls parser.error which raises SystemExit
        parser.parse_args(["--config", invalid_json_file])
