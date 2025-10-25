# Quick Start Guide

## Installation (2 minutes)

```bash
# 1. Install dependencies
python3 -m pip install -r requirements.txt

# 2. Verify installation
python3 -c "from logkitchen.generators.syslog import SyslogGenerator; print('Ready to go!')"
```

## Usage Examples

### Launch Interactive TUI

```bash
python3 -m logkitchen
```

Use arrow keys to navigate, Enter to select, and follow the on-screen prompts.

### Generate Logs (Command Line)

```bash
# Syslog - 100 entries to console
python3 -m logkitchen --type syslog --count 100

# Auditd - 500 entries to file
python3 -m logkitchen --type auditd --count 500 --output audit.log

# CEF Firewall - 1000 entries with seed
python3 -m logkitchen --type cef --count 1000 --seed 42 --output firewall.log

# Windows Security - 200 entries
python3 -m logkitchen --type windows --count 200 --output winsec.log

# All types at once
python3 -m logkitchen --all --count 100
```

### Python API

```python
from logkitchen.generators.syslog import SyslogGenerator

# Create generator
gen = SyslogGenerator(seed=42)

# Generate single log
log = gen.generate_log()
print(log)

# Generate 100 logs to file
gen.write_logs("syslog.log", count=100)
```

## Sample Output

All sample outputs are in `examples/sample_outputs/`:
- `syslog_sample.log` - Linux syslog entries
- `auditd_sample.log` - Linux audit daemon logs
- `cef_firewall_sample.log` - CEF firewall logs
- `windows_security_sample.log` - Windows Security Event logs

## Next Steps

- Read `USAGE.md` for detailed usage instructions
- Customize `config/default_config.yaml` for your needs
- Check `INSTALL.md` for troubleshooting
- Integrate with your SIEM tool

## Common Use Cases

**SIEM Testing**
```bash
python3 -m logkitchen --all --count 10000
```

**Detection Rule Development**
```bash
python3 -m logkitchen --type syslog --count 1000 --seed 42
```

**Log Parser Testing**
```bash
python3 -m logkitchen --type cef --count 100 --output test_cef.log
```

## Need Help?

- Check the full `README.md` for project overview
- See `USAGE.md` for detailed examples
- Review `INSTALL.md` for installation issues
- Check sample outputs in `examples/sample_outputs/`
