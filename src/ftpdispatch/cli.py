"""Command line interface for ftpdispatch."""

import argparse
import sys

from ftpdispatch.__about__ import __version__
from ftpdispatch.config import ConfigFileAction, create_example_config
from ftpdispatch.server import start_ftp_server


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="ftpdispatch",
        description="FTP server that automatically dispatches clients to the most recently created directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Config file format (JSON):
{
  "base-dir": "/path/to/base/directory",
  "host": "127.0.0.1",
  "port": 2121,
  "user": "user",
  "password": "pass"
}

Command line arguments override config file settings.
        """.strip(),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        action=ConfigFileAction,
        help="Path to JSON configuration file",
    )
    parser.add_argument(
        "--create-config",
        metavar="PATH",
        help="Create an example configuration file at the specified path and exit",
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory to scan for subdirectories",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the FTP server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=2121,
        help="Port to bind the FTP server to (default: 2121)",
    )
    parser.add_argument(
        "--user",
        default="anonymous",
        help="FTP username (default: anonymous)",
    )
    parser.add_argument(
        "--password",
        default="pass",
        help="FTP password (default: pass)",
    )

    args = parser.parse_args()

    # Handle config file creation
    if args.create_config:
        try:
            create_example_config(args.create_config)
            return 0
        except Exception as e:
            print(f"Error creating config file: {e}", file=sys.stderr)  # noqa: T201
            return 1

    # Set defaults for any missing values
    if not hasattr(args, "base_dir") or args.base_dir is None:
        parser.error("--base-dir is required (or specify in config file)")

    try:
        start_ftp_server(
            base_directory=args.base_dir,
            host=args.host,
            port=args.port,
            username=args.user,
            password=args.password,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)  # noqa: T201
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
