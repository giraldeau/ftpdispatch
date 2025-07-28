"""Configuration file handling for ftpdispatch."""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict


class ConfigFileAction(argparse.Action):
    """Custom argparse action to load config from JSON file."""

    def __call__(self, parser, namespace, values, _option_string=None):
        """Load config file and set defaults in namespace."""
        config_path = Path(values)

        if not config_path.exists():
            parser.error(f"Config file not found: {config_path}")

        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            parser.error(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            parser.error(f"Error reading config file {config_path}: {e}")

        # Set config values as defaults (will be overridden by command line args)
        for key, value in config.items():
            # Convert hyphens to underscores for argparse compatibility
            attr_name = key.replace("-", "_")

            # Only set if not already set by command line
            if not hasattr(namespace, attr_name) or getattr(namespace, attr_name) is None:
                setattr(namespace, attr_name, value)


def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    config_path = Path(config_path)

    if not config_path.exists():
        msg = f"Config file not found: {config_path}"
        raise FileNotFoundError(msg)

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON in config file: {e}"
        raise ValueError(msg) from e

    return config


def create_example_config(output_path: str) -> None:
    """Create an example configuration file."""
    example_config = {
        "base_dir": "/path/to/your/base/directory",
        "host": "127.0.0.1",
        "port": 2121,
        "user": "user",
        "password": "pass",
    }

    config_path = Path(output_path)
    with open(config_path, "w") as f:
        json.dump(example_config, f, indent=2)

    logging.info("Example config file created at: %s", config_path)


def merge_config_with_args(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Merge config file values with command line arguments.

    Command line arguments take precedence over config file values.
    """
    merged = config.copy()

    # Command line args override config file values
    for key, value in vars(args).items():
        if value is not None:
            merged[key] = value

    return merged
