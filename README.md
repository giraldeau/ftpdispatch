# ftpdispatch

FTP server that automatically dispatches clients to the most recently created directory.

## Features

- Automatically selects the most recently created directory in a base directory
- All FTP client operations are confined to the selected directory
- Configurable via command line or JSON config file
- Cross-platform support (Windows, Linux, macOS)

## Installation

### From Source

```bash
pip install -e .
```

### Windows Standalone Installer

For Windows users who don't want to install Python:

1. **On Windows:**
   ```cmd
   build_windows.bat
   ```

2. **On Linux/macOS (cross-compile):**
   ```bash
   ./build_windows.sh
   ```

This creates `dist/ftpdispatch.exe` - a standalone executable that can run on any Windows machine without Python installed.

## Usage

### Basic Usage

```bash
ftpdispatch --base-dir /path/to/base/directory
```

### With Custom Settings

```bash
ftpdispatch --base-dir /path/to/base/directory --host 0.0.0.0 --port 2121 --user myuser --password mypass
```

### Using Config File

Create a config file (`config.json`):
```json
{
  "base_dir": "/path/to/base/directory",
  "host": "127.0.0.1",
  "port": 2121,
  "user": "user",
  "password": "pass"
}
```

Run with config:
```bash
ftpdispatch --config config.json
```

Generate example config:
```bash
ftpdispatch --create-config config.json
```

### Windows Standalone

```cmd
ftpdispatch.exe --base-dir "C:\path\to\base\directory"
```

## How It Works

1. Server scans the base directory for subdirectories
2. Selects the most recently created subdirectory
3. FTP clients connect and are automatically placed in this directory
4. All file operations happen within the selected directory only

## Development

### Install Development Dependencies

```bash
pip install -e .[dev]
```

### Run Tests

```bash
pytest
```

### Run Linting

```bash
hatch fmt
```

### Build Windows Installer

```bash
# On Windows
build_windows.bat

# On Linux/macOS
./build_windows.sh
```

## License

MIT License - see [LICENSE](LICENSE) for details.