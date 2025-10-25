# Usage Guide

## Quick Start

### Interactive TUI Mode

The easiest way to use LogKitchen is through the interactive TUI:

```bash
python3 -m logkitchen
```

This will launch a terminal user interface where you can:
1. Select the log type to generate
2. Specify the number of logs
3. Choose output destination (console or file)
4. Set a random seed for reproducibility

### Command Line Mode

For scripting and automation, use the command line interface:

```bash
# Basic usage
python3 -m logkitchen --type syslog --count 100

# Save to file
python3 -m logkitchen --type auditd --count 500 --output logs/audit.log

# Reproducible output with seed
python3 -m logkitchen --type cef --count 1000 --seed 42 --output firewall.log
```

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

## Advanced Usage

### Generate All Log Types

Generate all four log types at once:

```bash
python3 -m logkitchen --all --count 500
```

This creates separate files for each type with timestamps:
- `syslog_20241025_142345.log`
- `auditd_20241025_142345.log`
- `cef_firewall_20241025_142345.log`
- `windows_security_20241025_142345.log`

### Reproducible Output

Use the `--seed` parameter for reproducible random data:

```bash
# Run 1
python3 -m logkitchen --type syslog --count 100 --seed 42 --output run1.log

# Run 2 (will produce identical output)
python3 -m logkitchen --type syslog --count 100 --seed 42 --output run2.log
```

### Direct Generator Usage

Run individual generators directly:

```bash
python3 -m logkitchen.generators.syslog --count 100 --output syslog.log --seed 42
python3 -m logkitchen.generators.auditd --count 50 --output auditd.log
```

## Integration with SIEM Tools

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

## Continuous Log Generation

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

## Configuration Customization

Edit `config/default_config.yaml` to customize generation:

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
```

## Output Formats

### Console Output

Default when no `--output` specified:

```bash
python3 -m logkitchen --type syslog --count 10
```

### File Output

Specify output file:

```bash
python3 -m logkitchen --type syslog --count 1000 --output /var/log/test/syslog.log
```

### Append Mode

Use Python API for append mode:

```python
from logkitchen.generators.syslog import SyslogGenerator

gen = SyslogGenerator(seed=42)
gen.write_logs("syslog.log", count=100, append=True)
```

## Python API

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

## Tips and Best Practices

1. **Start Small**: Test with small counts (10-100) before generating large volumes
2. **Use Seeds**: Use seeds for reproducible test scenarios
3. **Monitor Disk Space**: Large log counts can consume significant disk space
4. **Vary Events**: Adjust event weights in config for realistic distributions
5. **Combine Types**: Mix different log types to simulate real environments
6. **Test Parsers**: Verify your parsers can handle the generated formats
