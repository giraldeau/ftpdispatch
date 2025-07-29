"""Integration tests for the FTP server."""

import socket
import tempfile
import threading
import time
from ftplib import FTP
from pathlib import Path

import pytest
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

from ftpdispatch.server import DirectoryDispatchAuthorizer, FTPServer


def find_free_port():
    """Find a free port to use for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class FTPServerThread:
    """Helper class to run FTP server in a separate thread."""

    def __init__(self, base_directory, host="127.0.0.1", port=None, username="testuser", password="testpass"):
        self.base_directory = base_directory
        self.host = host
        self.port = port or find_free_port()
        self.username = username
        self.password = password
        self.server_thread = None
        self.server_exception = None
        self._stop_event = threading.Event()

    def _server_target(self):
        """Target function for the server thread."""
        try:
            # Patch the server to add a stop condition
            import logging

            # Set up logging
            logging.basicConfig(level=logging.INFO)

            # Set up authorizer
            authorizer = DirectoryDispatchAuthorizer()
            authorizer.add_user(self.username, self.password, self.base_directory, perm="elradfmwMT")

            # Set up handler
            handler = FTPHandler
            handler.authorizer = authorizer
            handler.banner = "Test FTP Server ready."

            # Create server instance
            server = ThreadedFTPServer((self.host, self.port), handler)
            server.base_directory = self.base_directory

            # Run server with stop condition
            while not self._stop_event.is_set():
                server.serve_forever(timeout=0.1, blocking=False)
                time.sleep(0.01)

            server.close_all()

        except Exception as e:
            self.server_exception = e

    def start(self):
        """Start the FTP server in a separate thread."""
        self.server_thread = threading.Thread(target=self._server_target, daemon=True)
        self.server_thread.start()
        # Give the server time to start
        time.sleep(1.0)

    def stop(self):
        """Stop the FTP server."""
        if self.server_thread:
            self._stop_event.set()
            self.server_thread.join(timeout=2.0)

        if self.server_exception:
            raise self.server_exception


@pytest.fixture
def temp_base_with_dirs():
    """Create a temporary directory with two subdirectories of different ages."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)

        # Create two directories with different creation times
        dir_old = base_path / "aaa"
        dir_old.mkdir()
        dir_new = base_path / "bbb"
        dir_new.mkdir()

        yield temp_dir, str(dir_old), str(dir_new)


def test_ftp_server_file_upload_integration(temp_base_with_dirs):
    """Integration test: Start server, connect client, upload file, verify location."""
    base_dir, dir_old, dir_new = temp_base_with_dirs

    # Start FTP server in separate thread
    server = FTPServerThread(base_dir)
    server.start()

    try:
        # Connect FTP client
        ftp = FTP()
        ftp.connect(server.host, server.port)
        ftp.login(server.username, server.password)

        # Create test file content
        test_content = b"Hello from FTP integration test!"
        test_filename = "upload.txt"

        # Upload file using STOR command
        from io import BytesIO

        test_file = BytesIO(test_content)
        ftp.storbinary(f"STOR {test_filename}", test_file)

        # Close FTP connection
        ftp.quit()

        # Verify file was uploaded to the most recent directory (dir_new)
        uploaded_file = Path(dir_new) / test_filename
        assert uploaded_file.exists(), f"File not found in most recent directory: {uploaded_file}"

        # Verify file content
        with open(uploaded_file, "rb") as f:
            content = f.read()
        assert content == test_content, "File content doesn't match"

        # Verify file is NOT in the old directory
        old_file = Path(dir_old) / test_filename
        assert not old_file.exists(), f"File should not be in old directory: {old_file}"

    finally:
        # Always stop the server
        server.stop()


def test_ftp_server_directory_listing_integration(temp_base_with_dirs):
    """Integration test: Verify client sees the most recent directory as root."""
    base_dir, dir_old, dir_new = temp_base_with_dirs

    # Create a file in the old directory (should not be visible)
    old_file = Path(dir_old) / "aaa_file.txt"
    old_file.write_text("This file should NOT be visible")

    # Create a test file in the most recent directory
    test_file = Path(dir_new) / "bbb_file.txt"
    test_file.write_text("This file should be visible")

    # Start FTP server
    server = FTPServerThread(base_dir)
    server.start()

    try:
        # Connect and list directory
        ftp = FTP()
        ftp.connect(server.host, server.port)
        ftp.login(server.username, server.password)

        # List files in root directory (should be contents of most recent dir)
        files = []
        ftp.retrlines("LIST", files.append)

        ftp.quit()

        # Convert list output to just filenames
        filenames = []
        for line in files:
            # Parse LIST output (format varies, but filename is usually last)
            parts = line.split()
            if parts:
                filenames.append(parts[-1])

        # Verify we see the file from the most recent directory
        assert "bbb_file.txt" in filenames, f"Should see file from recent dir, got: {filenames}"

        # Verify we don't see the file from the old directory
        assert "aaa_file.txt" not in filenames, f"Should not see file from old dir, got: {filenames}"

    finally:
        server.stop()
