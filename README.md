<p align="center">
  <img src="logo.png" alt="LogKitchen Logo" width="200"/>
</p>

# LogKitchen - Synthetic Log Generator

A Python-based synthetic log generator for SIEM testing, detection rule development, and log parsing practice. Features both a command-line interface and a web-based UI with integrated Azure Data Explorer (Kustainer) support.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Interactive TUI](#interactive-tui)
  - [Command Line](#command-line)
  - [Python API](#python-api)
  - [Docker Deployment](#docker-deployment)
- [Log Types](#log-types)
- [Configuration](#configuration)
- [SIEM Integration](#siem-integration)
- [Use Cases](#use-cases)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## Features

- **Multiple Log Types**:
  - Linux Syslog (SSH, sudo, auth, cron, systemd, kernel, network)
  - Linux Auditd (SYSCALL, EXECVE, USER_AUTH, USER_CMD, CRED_ACQ, LOGIN)
  - CEF Firewall Logs (Palo Alto, Cisco, Fortinet, Check Point, pfSense)
  - Windows Security Events (4624, 4625, 4634, 4672, 4720, 4732, 4740, 4768, 4776, 5140, 5156/5157)
  - Verifone POS Security Logs

- **Multiple Interfaces**:
  - Interactive TUI (Terminal User Interface)
  - Command-line interface
  - Python API
  - Web UI with Kustainer integration

- **Use Cases**:
  - Generate test data for SIEM tools
  - Practice detection rule development
  - Test log parsing and normalization (CEF, OCSF, etc.)
  - Populate lab environments with realistic log data
  - Training and education

## Quick Start

### Python CLI (Fastest)

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "from logkitchen.generators.syslog import SyslogGenerator; print('Ready to go!')"

# Launch interactive TUI
python3 -m logkitchen

# Or generate logs directly
python3 -m logkitchen --type syslog --count 100
```

### Docker (With Web UI)

```bash
# Start both LogKitchen web UI and Kustainer
docker-compose up -d

# Access LogKitchen at http://localhost:9001
# Access Kustainer at http://localhost:9002
```

See the [Docker Deployment](#docker-deployment) section or [KUSTAINER.md](KUSTAINER.md) for full details.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Docker and Docker Compose (for web UI deployment)

### Install Python Dependencies

```bash
# Install from requirements.txt
python3 -m pip install -r requirements.txt

# Or install manually
python3 -m pip install python-dateutil pyyaml rich textual faker flask
```

### Verify Installation

```bash
python3 -c "from logkitchen.generators.syslog import SyslogGenerator; print('Installation successful!')"
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m logkitchen
```

## Usage

### Interactive TUI

The easiest way to use LogKitchen is through the interactive Terminal User Interface:

```bash
python3 -m logkitchen
```

or

```bash
python3 -m logkitchen --tui
```

This launches an interactive menu where you can:
1. Select the log type to generate
2. Specify the number of logs
3. Choose output destination (console or file)
4. Set a random seed for reproducibility

Use arrow keys to navigate, Enter to select, and follow the on-screen prompts.

### Command Line

For scripting and automation, use the command-line interface:

**Basic Usage:**
```bash
# Generate 100 syslog entries to console
python3 -m logkitchen --type syslog --count 100

# Generate logs to file
python3 -m logkitchen --type auditd --count 500 --output audit.log

# Reproducible output with seed
python3 -m logkitchen --type cef --count 1000 --seed 42 --output firewall.log

# Generate Windows Security logs
python3 -m logkitchen --type windows --count 200 --output winsec.log
```

**Advanced Usage:**

```bash
# Generate all log types at once
python3 -m logkitchen --all --count 500

# This creates separate files for each type with timestamps:
# - syslog_20241025_142345.log
# - auditd_20241025_142345.log
# - cef_firewall_20241025_142345.log
# - windows_security_20241025_142345.log
```

**Direct Generator Usage:**

Run individual generators directly:

```bash
python3 -m logkitchen.generators.syslog --count 100 --output syslog.log --seed 42
python3 -m logkitchen.generators.auditd --count 50 --output auditd.log
python3 -m logkitchen.generators.cef_firewall --count 200 --output firewall.log
python3 -m logkitchen.generators.windows_security --count 100 --output winsec.log
```

**Reproducible Output:**

Use the `--seed` parameter for reproducible random data:

```bash
# Run 1
python3 -m logkitchen --type syslog --count 100 --seed 42 --output run1.log

# Run 2 (will produce identical output)
python3 -m logkitchen --type syslog --count 100 --seed 42 --output run2.log
```

### Python API

Use LogKitchen in your Python scripts:

```python
from logkitchen.generators.syslog import SyslogGenerator
from logkitchen.generators.auditd import AuditdGenerator
from logkitchen.generators.cef_firewall import CEFFirewallGenerator
from logkitchen.generators.windows_security import WindowsSecurityGenerator

# Create generators
syslog_gen = SyslogGenerator(seed=42)
auditd_gen = AuditdGenerator(seed=42)
cef_gen = CEFFirewallGenerator(seed=42)
win_gen = WindowsSecurityGenerator(seed=42)

# Generate single log
log = syslog_gen.generate_log()
print(log)

# Generate multiple logs
logs = syslog_gen.generate_logs(count=100)
for log in logs:
    print(log)

# Write to file
syslog_gen.write_logs("output.log", count=1000)

# Append to file
syslog_gen.write_logs("output.log", count=100, append=True)
```

### Docker Deployment

LogKitchen includes a Docker Compose stack with:
- **LogKitchen Web UI** (port 9001) - Generate logs through a web interface
- **Kustainer** (port 9002) - Azure Data Explorer for analyzing logs with KQL

**Quick Start:**

```bash
# Start the stack
docker-compose up -d

# Access the services
# LogKitchen Web UI: http://localhost:9001
# Kustainer: http://localhost:9002
```

**Docker Commands:**

```bash
# Stop the stack
docker-compose down

# View logs
docker-compose logs -f logkitchen

# Rebuild after changes
docker-compose build --no-cache && docker-compose up -d

# Restart containers
docker-compose restart
```

**Directory Structure:**
- `./config/` → Configuration files (mounted to LogKitchen)
- `./outputs/` → Generated log files (shared between LogKitchen & Kustainer)
- `./kustodata/` → Kustainer database persistence (survives restarts)

For complete Docker and Kustainer setup instructions, see [KUSTAINER.md](KUSTAINER.md).

## Log Types

### 1. Linux Syslog

Generates standard Linux syslog entries including:
- SSH login attempts (successful and failed)
- Sudo commands
- Authentication events
- Cron jobs
- Systemd service events
- Kernel messages
- Network events

```bash
python3 -m logkitchen --type syslog --count 1000 --output syslog.log
```

**Example output:**
```
Oct 25 14:23:45 web-42 sshd[23451]: Accepted password for ubuntu from 203.0.113.45 port 52341 ssh2
Oct 25 14:24:12 db-15 sudo[23452]: admin : TTY=pts/0 ; PWD=/home/admin ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx
```

### 2. Linux Auditd

Generates Linux audit daemon logs including:
- System calls (SYSCALL)
- Program executions (EXECVE)
- User authentication (USER_AUTH)
- User commands (USER_CMD)
- Credential events (CRED_ACQ, CRED_DISP)
- Login events (LOGIN)

```bash
python3 -m logkitchen --type auditd --count 500 --output auditd.log
```

**Example output:**
```
type=SYSCALL msg=audit(1698246225.123:1234): arch=c000003e syscall=59 success=yes exit=0 a0=7ffe1234 a1=7ffe5678 a2=7ffe9abc a3=7ffedef0 items=2 ppid=1234 pid=23456 auid=1000 uid=1000 gid=1000 euid=1000 egid=1000 comm="ls" exe="/bin/ls" key="commands"
```

### 3. CEF Firewall Logs

Generates CEF (Common Event Format) firewall logs including:
- Traffic events (allow/deny)
- Threat detection events
- System events
- Multiple vendor formats (Palo Alto, Cisco, Fortinet, Check Point, pfSense)

```bash
python3 -m logkitchen --type cef --count 2000 --output firewall.log
```

**Example output:**
```
CEF:0|Palo Alto Networks|PAN-OS|10.0.0|TRAFFIC|traffic-allowed|2|rt=Oct 25 2024 14:23:45 src=10.50.1.25 dst=8.8.8.8 spt=54321 dpt=53 proto=UDP act=allowed out=512 in=1024
```

### 4. Windows Security Events

Generates Windows Security Event Log entries including:
- Event ID 4624: Successful logon
- Event ID 4625: Failed logon
- Event ID 4634: Logoff
- Event ID 4672: Special privileges assigned
- Event ID 4720: User account created
- Event ID 4732: Member added to security group
- Event ID 4740: Account locked out
- Event ID 4768: Kerberos TGT requested
- Event ID 4776: NTLM authentication
- Event ID 5140: Network share accessed
- Event ID 5156/5157: Windows Filtering Platform

```bash
python3 -m logkitchen --type windows --count 1000 --output winsec.log
```

**Example output:**
```
EventID=4624 Level=Information Computer=WS-042 TimeGenerated=10/25/2024 02:23:45 PM Subject_Account_Name: john.doe; Subject_Account_Domain: CORP; Target_Account_Name: john.doe; Logon_Type: 2 (Interactive)
```

## Configuration

Edit `config/default_config.yaml` to customize log generation:

**Example configuration:**

```yaml
# Adjust event weights
syslog:
  event_weights:
    ssh: 0.40        # More SSH events
    sudo: 0.20       # More sudo events
    auth: 0.10
    cron: 0.10
    systemd: 0.10
    kernel: 0.05
    network: 0.05

# Customize usernames
users:
  linux_users:
    - alice
    - bob
    - charlie
    - deploy_bot

# Customize IP ranges
network:
  internal_ranges:
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16
```

You can customize:
- Log generation patterns
- IP address ranges
- Usernames and hostnames
- Event type distributions
- Output formats
- Windows domains

## SIEM Integration

### Splunk

Ingest generated logs into Splunk:

```bash
# Generate logs
python3 -m logkitchen --type syslog --count 10000 --output syslog.log

# Copy to Splunk monitoring directory
cp syslog.log /opt/splunk/var/spool/splunk/
```

### Elastic Stack

```bash
# Generate logs
python3 -m logkitchen --type auditd --count 5000 --output auditd.log

# Use Filebeat to ship to Elasticsearch
# Configure filebeat.yml to monitor auditd.log
```

### QRadar

```bash
# Generate CEF logs
python3 -m logkitchen --type cef --count 2000 --output firewall_cef.log

# Use QRadar's log file protocol to ingest
```

### Continuous Log Generation

Generate logs continuously for testing:

```bash
# Bash script for continuous generation
while true; do
    python3 -m logkitchen --type syslog --count 100 >> continuous_syslog.log
    sleep 60  # Generate every minute
done
```

## Use Cases

### 1. SIEM Testing

Populate your SIEM with realistic test data:

```bash
python3 -m logkitchen --all --count 10000
```

### 2. Detection Rule Development

Generate specific patterns for testing detection rules:

```bash
# Generate SSH brute force patterns
python3 -m logkitchen --type syslog --count 1000 --seed 42

# Generate failed Windows logons
python3 -m logkitchen --type windows --count 500
```

### 3. Log Parser Testing

Test your log parsers with various formats:

```bash
# CEF parsing
python3 -m logkitchen --type cef --count 100

# Syslog parsing
python3 -m logkitchen --type syslog --count 100
```

### 4. Training and Education

Generate sample logs for training purposes:

```bash
python3 -m logkitchen --all --count 100 --seed 123
```

## Troubleshooting

### Python Issues

**ImportError: No module named 'faker'**

Make sure all dependencies are installed:

```bash
python3 -m pip install -r requirements.txt
```

**Permission Denied**

If you get permission errors, try installing with --user:

```bash
python3 -m pip install --user -r requirements.txt
```

**Python Version Issues**

Check your Python version:

```bash
python3 --version
```

LogKitchen requires Python 3.8 or higher.

### Docker Issues

**Port already in use**

If ports 9001 or 9002 are already in use, edit `docker-compose.yml`:

```yaml
# For LogKitchen
ports:
  - "9003:9001"  # Change 9003 to any available port

# For Kustainer
ports:
  - "9004:8080"  # Change 9004 to any available port
```

**Container won't start**

Check the logs:

```bash
# LogKitchen logs
docker-compose logs logkitchen

# Kustainer logs
docker-compose logs kustainer

# All logs
docker-compose logs
```

**Reset everything**

```bash
docker-compose down -v
docker-compose up -d --build
```

## Project Structure

```
logkitchen/
├── README.md                    # This file
├── KUSTAINER.md                 # Docker + Kustainer integration guide
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker build instructions
├── docker-compose.yml           # Docker Compose configuration
│
├── config/
│   └── default_config.yaml      # Default configuration
│
├── logkitchen/                  # Main package
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   │
│   ├── generators/              # Log generator modules
│   │   ├── __init__.py
│   │   ├── base.py              # Base generator class
│   │   ├── syslog.py            # Linux syslog generator
│   │   ├── auditd.py            # Linux auditd generator
│   │   ├── cef_firewall.py      # CEF firewall log generator
│   │   ├── windows_security.py  # Windows Security Event generator
│   │   └── verifone_pos.py      # Verifone POS generator
│   │
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── config_manager.py    # YAML config loader
│   │
│   ├── tui/                     # Terminal User Interface
│   │   ├── __init__.py
│   │   └── interface.py         # Textual-based TUI
│   │
│   ├── web/                     # Web application (Flask)
│   │   ├── app.py               # Main Flask app
│   │   ├── templates/           # HTML templates
│   │   └── static/              # CSS, JS, images
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── helpers.py           # Helper functions
│
├── outputs/                     # Generated log files (gitignored)
├── kustodata/                   # Kustainer database files (gitignored)
│
└── examples/
    └── sample_outputs/          # Example generated logs
        ├── syslog_sample.log
        ├── auditd_sample.log
        ├── cef_firewall_sample.log
        └── windows_security_sample.log
```

## Tips and Best Practices

1. **Start Small**: Test with small counts (10-100) before generating large volumes
2. **Use Seeds**: Use seeds for reproducible test scenarios
3. **Monitor Disk Space**: Large log counts can consume significant disk space
4. **Vary Events**: Adjust event weights in config for realistic distributions
5. **Combine Types**: Mix different log types to simulate real environments
6. **Test Parsers**: Verify your parsers can handle the generated formats

## Sample Outputs

All sample outputs are in `examples/sample_outputs/`:
- `syslog_sample.log` - Linux syslog entries
- `auditd_sample.log` - Linux audit daemon logs
- `cef_firewall_sample.log` - CEF firewall logs
- `windows_security_sample.log` - Windows Security Event logs

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest features.

## License

This project is open source and available for use in security testing, training, and development environments.
