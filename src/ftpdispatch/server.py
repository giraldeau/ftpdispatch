"""FTP server implementation with automatic directory selection."""

import logging
import os
from pathlib import Path
from typing import Optional

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class DirectoryDispatchAuthorizer(DummyAuthorizer):
    def __init__(self):
        super().__init__()

    def get_home_dir(self, username):
        base_directory = super().get_home_dir(username)
        homedir = find_most_recent_directory(base_directory)
        return homedir


def find_most_recent_directory(base_path: str) -> Optional[str]:
    """Find the most recently created directory in the base path."""
    base_path = Path(base_path)

    if not base_path.exists() or not base_path.is_dir():
        return None

    directories = [d for d in base_path.iterdir() if d.is_dir()]

    if not directories:
        return None

    # Sort by creation time (most recent first)
    most_recent = max(directories, key=lambda d: d.stat().st_ctime)
    return str(most_recent)


def start_ftp_server(
    base_directory: str, host: str = "127.0.0.1", port: int = 2121, username: str = "user", password: str = "pass"
) -> None:
    """Start the FTP server with directory dispatch functionality."""

    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Validate base directory
    if not os.path.exists(base_directory):
        msg = f"Base directory does not exist: {base_directory}"
        raise ValueError(msg)

    if not os.path.isdir(base_directory):
        msg = f"Base path is not a directory: {base_directory}"
        raise ValueError(msg)

    # Set up authorizer
    authorizer = DirectoryDispatchAuthorizer()

    authorizer.add_user(
        username,
        password,
        base_directory,
        perm="elradfmwMT",  # All permissions within the directory
    )

    # Set up handler
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "FTP Dispatch Server ready."

    # Create server instance and store base directory for handler access
    server = FTPServer((host, port), handler)
    server.base_directory = base_directory

    logging.info(f"Starting FTP server on {host}:{port}")
    logging.info(f"Base directory: {base_directory}")
    logging.info("Press Ctrl+C to stop the server")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        server.close_all()
