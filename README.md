# LogKitchen - Synthetic Log Generator

A Python-based synthetic log generator for SIEM testing, detection rule development, and log parsing practice.

## Features

- **Multiple Log Types**:
  - Linux Syslog
  - Linux Auditd
  - CEF Firewall Logs
  - Windows Security Event Logs

- **Use Cases**:
  - Generate test data for SIEM tools
  - Practice detection rule development
  - Test log parsing and normalization (CEF, OCSF, etc.)
  - Populate lab environments with realistic log data

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### TUI Mode (Interactive)
```bash
python -m logkitchen.tui.interface
```

### Command Line Mode
```bash
# Generate 100 syslog entries
python -m logkitchen.generators.syslog --count 100 --output syslog.log

# Generate auditd logs
python -m logkitchen.generators.auditd --count 50 --output auditd.log

# Generate CEF firewall logs
python -m logkitchen.generators.cef_firewall --count 200 --output firewall.log

# Generate Windows Security logs
python -m logkitchen.generators.windows_security --count 100 --output winsec.log
```

## Configuration

Edit `config/default_config.yaml` to customize:
- Log generation patterns
- IP address ranges
- Usernames and hostnames
- Event type distributions
- Output formats

## Project Structure

```
logkitchen/
├── logkitchen/         # Main package
│   ├── generators/     # Log generator modules
│   ├── config/         # Configuration management
│   ├── tui/           # Terminal UI
│   └── utils/         # Helper utilities
├── config/            # Configuration files
└── examples/          # Sample outputs
```

## Future Plans

- Docker-compose stack with web UI
- Real-time log streaming
- Additional log formats (Apache, Nginx, etc.)
- Anomaly injection for detection testing
- OCSF schema output support
