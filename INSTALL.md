# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

Or install manually:

```bash
python3 -m pip install python-dateutil pyyaml rich textual faker
```

### 2. Verify Installation

Test that all modules can be imported:

```bash
python3 -c "from logkitchen.generators.syslog import SyslogGenerator; print('Installation successful!')"
```

### 3. Run the Application

#### Option A: Launch TUI (Interactive Mode)

```bash
python3 -m logkitchen
```

or

```bash
python3 -m logkitchen --tui
```

#### Option B: Command Line Mode

Generate specific log types:

```bash
# Generate 100 syslog entries
python3 -m logkitchen --type syslog --count 100

# Generate auditd logs to file
python3 -m logkitchen --type auditd --count 500 --output audit.log

# Generate CEF firewall logs with seed
python3 -m logkitchen --type cef --count 1000 --seed 12345 --output firewall.log

# Generate Windows Security Events
python3 -m logkitchen --type windows --count 200 --output winsec.log
```

#### Option C: Generate All Log Types

```bash
python3 -m logkitchen --all --count 100
```

This will create separate files for each log type.

## Direct Module Usage

You can also run individual generators directly:

```bash
# Syslog
python3 -m logkitchen.generators.syslog --count 100 --output syslog.log

# Auditd
python3 -m logkitchen.generators.auditd --count 50 --output auditd.log

# CEF Firewall
python3 -m logkitchen.generators.cef_firewall --count 200 --output firewall.log

# Windows Security
python3 -m logkitchen.generators.windows_security --count 100 --output winsec.log
```

## Configuration

Edit `config/default_config.yaml` to customize:

- Event type distributions
- IP address ranges
- Usernames and hostnames
- Windows domains
- Output settings

## Troubleshooting

### ImportError: No module named 'faker'

Make sure all dependencies are installed:

```bash
python3 -m pip install -r requirements.txt
```

### Permission Denied

If you get permission errors, try installing with --user:

```bash
python3 -m pip install --user -r requirements.txt
```

### Python Version Issues

Check your Python version:

```bash
python3 --version
```

LogKitchen requires Python 3.8 or higher.

## Virtual Environment (Recommended)

For a clean installation, use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
python -m pip install -r requirements.txt

# Run the application
python -m logkitchen
```

## Docker Installation (Coming Soon)

Docker support with web UI is planned for future releases.
