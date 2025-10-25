<p align="center">
  <img src="logo.png" alt="LogKitchen Logo" width="200"/>
</p>

# Kustainer Integration Guide

Complete guide for deploying LogKitchen with Kustainer (Azure Data Explorer) for log analysis using KQL.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Docker Setup](#docker-setup)
- [Complete Workflow](#complete-workflow)
- [Database Management](#database-management)
- [Table Schemas](#table-schemas)
- [Ingesting Logs](#ingesting-logs)
- [KQL Queries](#kql-queries)
- [Docker Configuration](#docker-configuration)
- [Troubleshooting](#troubleshooting)
- [Tips & Best Practices](#tips--best-practices)

## Overview

This guide covers the Docker Compose stack that includes:

- **LogKitchen Web UI** (port 9001) - Generate synthetic logs through a web interface
- **Kustainer** (port 9002) - Local Azure Data Explorer instance for analyzing logs with KQL

Both services run on the same Docker network and share a volume (`./outputs/`) for seamless log file ingestion.

## Quick Start

### 1. Start the Stack

```bash
docker-compose up -d
```

This starts both services:
- LogKitchen at http://localhost:9001
- Kustainer at http://localhost:9002

### 2. Generate Logs

1. Open LogKitchen at http://localhost:9001
2. Select a log type (Syslog, Auditd, CEF Firewall, Windows Security, or Verifone POS)
3. Choose the number of logs to generate (1-10,000)
4. Click "Generate Logs"
5. Click "Save to Outputs Folder" - logs are saved as CSV files

### 3. Create Database in Kustainer

Open Kustainer at http://localhost:9002 and run:

```kql
.create database LogAnalysis persist (
  @"/kustodata/dbs/LogAnalysis/md",
  @"/kustodata/dbs/LogAnalysis/data"
)
```

**Important:** Always use the `persist` syntax to ensure databases survive container restarts.

### 4. Select Database

```kql
.database LogAnalysis
```

### 5. Create Tables and Ingest

The web UI provides copy-paste commands for table creation and ingestion after you save logs.

## Docker Setup

### Services Overview

#### LogKitchen (Port 9001)
- **Container:** `logkitchen-web`
- **Purpose:** Generate synthetic logs for SIEM testing
- **Memory:** Default Docker allocation
- **Features:** Web UI, REST API, CSV export

#### Kustainer (Port 9002)
- **Container:** `kustainer-adx`
- **Purpose:** Azure Data Explorer for log analysis with KQL
- **Memory:** 4GB limit (configurable)
- **Features:** KQL queries, data ingestion, time-series analysis, persistent storage

Both services run on the same Docker network (`logkitchen-network`) and can communicate with each other.

### Directory Structure

```
logkitchen/
├── config/               # Configuration files (mounted to LogKitchen)
├── outputs/              # Generated log files (shared between services)
├── kustodata/            # Kustainer database persistence (survives restarts)
├── logkitchen/
│   ├── web/             # Flask web application
│   │   ├── app.py       # Main Flask app
│   │   └── templates/   # HTML templates
│   └── generators/      # Log generators
├── Dockerfile           # Docker build instructions for LogKitchen
└── docker-compose.yml   # Docker Compose configuration (both services)
```

### Volume Mounts

#### LogKitchen Volumes
1. **./config** → `/app/config` (read-only)
   - Custom configuration files for log generators

2. **./outputs** → `/app/outputs` (read-write)
   - Generated log files are saved here
   - Downloads from web UI save to this folder

#### Kustainer Volumes
1. **./kustodata** → `/kustodata` (read-write)
   - **Database persistence** - databases created with `persist` survive container restarts
   - Stores metadata and data files
   - Example paths: `/kustodata/dbs/LogAnalysis/md` and `/kustodata/dbs/LogAnalysis/data`

2. **./outputs** → `/logs` (read-only)
   - **Shared folder** with LogKitchen for log file ingestion
   - Access generated logs: `.ingest into table Logs (@"/logs/yourfile.csv")`
   - No need to manually copy files - automatically available to Kustainer

### Docker Commands

```bash
# Start the stack
docker-compose up -d

# Stop the stack
docker-compose down

# View logs
docker-compose logs -f logkitchen
docker-compose logs -f kustainer

# Rebuild after changes
docker-compose build --no-cache
docker-compose up -d

# Restart containers
docker-compose restart

# Check health status
docker inspect logkitchen-web --format='{{.State.Health.Status}}'
docker inspect kustainer-adx --format='{{.State.Health.Status}}'
```

## Complete Workflow

### Step 1: Generate Logs in LogKitchen

1. Open http://localhost:9001
2. Select log type from dropdown
3. Set count (1-10,000)
4. Optional: Set a random seed for reproducible output
5. Click "Generate Logs"
6. Review the generated logs in the display
7. Click "Save to Outputs Folder"

### Step 2: Create Persistent Database

In Kustainer (http://localhost:9002), run:

```kql
.create database LogAnalysis persist (
  @"/kustodata/dbs/LogAnalysis/md",
  @"/kustodata/dbs/LogAnalysis/data"
)
```

**Why persist?** Without `persist`, data is stored only in container memory and will be lost on restart.

### Step 3: Select the Database

```kql
.database LogAnalysis
```

### Step 4: Create Tables

Copy the table creation command from the LogKitchen web UI success message, or use the schemas below:

**Syslog:**
```kql
.create table SyslogLogs (Timestamp:datetime, Hostname:string, Process:string, PID:int, Message:string, RawLog:string)
```

**Auditd:**
```kql
.create table AuditdLogs (Timestamp:datetime, RecordType:string, Node:string, Syscall:string, Success:string, User:string, Command:string, RawLog:string)
```

**CEF Firewall:**
```kql
.create table CEFFirewallLogs (Timestamp:datetime, Vendor:string, Product:string, Version:string, EventClassID:string, Name:string, Severity:int, SourceIP:string, DestIP:string, SourcePort:int, DestPort:int, Protocol:string, Action:string, RawLog:string)
```

**Windows Security:**
```kql
.create table WindowsSecurityLogs (Timestamp:datetime, EventID:int, Level:string, Computer:string, AccountName:string, AccountDomain:string, SourceIP:string, LogonType:string, RawLog:string)
```

**Verifone POS:**
```kql
.create table VerifonePOSLogs (Timestamp:datetime, Severity:string, Component:string, TerminalID:string, TransactionID:string, Message:string, RawLog:string)
```

### Step 5: Ingest Data

Copy the ingest command from the LogKitchen web UI, or use this format:

```kql
.ingest into table SyslogLogs (@"/logs/logkitchen_syslog_20251025_143022.csv")
  with (format="csv", ignoreFirstRecord=true)
```

Files saved in `./outputs/` are automatically available at `/logs/` in Kustainer.

### Step 6: Query with KQL

Now analyze your logs:

```kql
// Count total logs
SyslogLogs | count

// Show first 10 rows
SyslogLogs | take 10

// Recent logs
SyslogLogs
| where Timestamp > ago(1h)
| order by Timestamp desc
```

## Database Management

### List Databases

```kql
.show databases
```

### Show Tables

```kql
.show tables
```

### Show Table Row Count

```kql
.show table SyslogLogs extents
| summarize sum(RowCount)
```

### Detach Database (keeps data, stops using it)

```kql
.detach database LogAnalysis
```

### Re-attach Existing Database

```kql
.attach database LogAnalysis from @"/kustodata/dbs/LogAnalysis"
```

### Drop Table

```kql
.drop table SyslogLogs
```

### Drop Database (permanently deletes!)

```kql
.drop database LogAnalysis
```

## Table Schemas

### Linux Syslog Table

```kql
.create table SyslogLogs (
  Timestamp:datetime,
  Hostname:string,
  Process:string,
  PID:int,
  Message:string,
  RawLog:string
)
```

### Linux Auditd Table

```kql
.create table AuditdLogs (
  Timestamp:datetime,
  RecordType:string,
  Node:string,
  Syscall:string,
  Success:string,
  User:string,
  Command:string,
  RawLog:string
)
```

### CEF Firewall Table

```kql
.create table CEFFirewallLogs (
  Timestamp:datetime,
  Vendor:string,
  Product:string,
  Version:string,
  EventClassID:string,
  Name:string,
  Severity:int,
  SourceIP:string,
  DestIP:string,
  SourcePort:int,
  DestPort:int,
  Protocol:string,
  Action:string,
  RawLog:string
)
```

### Windows Security Table

```kql
.create table WindowsSecurityLogs (
  Timestamp:datetime,
  EventID:int,
  Level:string,
  Computer:string,
  AccountName:string,
  AccountDomain:string,
  SourceIP:string,
  LogonType:string,
  RawLog:string
)
```

### Verifone POS Table

```kql
.create table VerifonePOSLogs (
  Timestamp:datetime,
  Severity:string,
  Component:string,
  TerminalID:string,
  TransactionID:string,
  Message:string,
  RawLog:string
)
```

## Ingesting Logs

### From Shared Outputs Folder

Files saved to `./outputs/` folder are available at `/logs/` in Kustainer:

```kql
// Ingest syslog
.ingest into table SyslogLogs (@"/logs/logkitchen_syslog_20251025.csv")
  with (format="csv", ignoreFirstRecord=true)

// Ingest auditd
.ingest into table AuditdLogs (@"/logs/logkitchen_auditd_20251025.csv")
  with (format="csv", ignoreFirstRecord=true)

// Ingest CEF
.ingest into table CEFFirewallLogs (@"/logs/logkitchen_cef_20251025.csv")
  with (format="csv", ignoreFirstRecord=true)

// Ingest Windows Security
.ingest into table WindowsSecurityLogs (@"/logs/logkitchen_windows_20251025.csv")
  with (format="csv", ignoreFirstRecord=true)
```

### Inline Ingestion (Copy/Paste)

```kql
.ingest inline into table SyslogLogs <|
Oct 25 14:30:15,web-42,sshd,1234,Failed password for root from 192.168.1.100,Oct 25 14:30:15 web-42 sshd[1234]: Failed password for root from 192.168.1.100
Oct 25 14:30:16,web-42,sshd,1234,Connection closed by 192.168.1.100,Oct 25 14:30:16 web-42 sshd[1234]: Connection closed by 192.168.1.100
```

## KQL Queries

### Basic Queries

```kql
// Show first 10 rows
SyslogLogs | take 10

// Count total logs
SyslogLogs | count

// Show schema
SyslogLogs | getschema

// Recent logs
SyslogLogs
| where Timestamp > ago(1h)
| order by Timestamp desc
| take 100

// Search for specific text
SyslogLogs
| where RawLog contains "Failed password"
| take 50
```

### Analysis Queries

```kql
// Count by process
SyslogLogs
| summarize count() by Process
| order by count_ desc

// Top hosts by log volume
SyslogLogs
| summarize LogCount=count() by Hostname
| top 10 by LogCount

// Time series analysis (logs per hour)
SyslogLogs
| summarize count() by bin(Timestamp, 1h)
| render timechart

// Failed login attempts
SyslogLogs
| where Message contains "Failed password"
| summarize FailedAttempts=count() by Hostname
| where FailedAttempts > 5
| order by FailedAttempts desc
```

### Security Analysis

```kql
// Suspicious user activity (Auditd)
AuditdLogs
| where Command contains "sudo" or Command contains "su"
| summarize count() by User, Command
| order by count_ desc

// Port scanning detection (Firewall)
CEFFirewallLogs
| where Action == "Deny"
| summarize UniqueDestPorts=dcount(DestPort) by SourceIP
| where UniqueDestPorts > 20
| order by UniqueDestPorts desc

// Failed Windows logon attempts
WindowsSecurityLogs
| where EventID == 4625
| summarize FailedLogons=count() by AccountName, Computer
| order by FailedLogons desc

// Privilege escalation detection
WindowsSecurityLogs
| where EventID == 4672
| summarize PrivilegeCount=count() by AccountName
| order by PrivilegeCount desc
```

### Advanced Queries

```kql
// Join logs from multiple sources
SyslogLogs
| where Process == "sshd"
| join kind=inner (
    AuditdLogs
    | where RecordType == "USER_AUTH"
) on $left.Hostname == $right.Node
| project Timestamp, Hostname, Process, Message, User

// Detect anomalies using time-based patterns
SyslogLogs
| where Process == "sshd"
| summarize Count=count() by bin(Timestamp, 5m), Hostname
| where Count > 10  // More than 10 SSH events in 5 minutes

// Create materialized view for performance
.create materialized-view SshFailures on table SyslogLogs
{
    SyslogLogs
    | where Message contains "Failed password"
    | summarize count() by bin(Timestamp, 1h), Hostname
}
```

## Docker Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

**LogKitchen:**
```yaml
environment:
  - FLASK_ENV=production  # or 'development'
  - PORT=9001
```

**Kustainer:**
```yaml
environment:
  - ACCEPT_EULA=Y  # Required to accept Microsoft EULA
mem_limit: 4g  # Adjust memory limit as needed
```

### Port Configuration

If ports 9001 or 9002 are already in use:

**LogKitchen:**
```yaml
ports:
  - "9003:9001"  # Change 9003 to any available port
```

**Kustainer:**
```yaml
ports:
  - "9004:8080"  # Change 9004 to any available port
```

### Memory Limits

If Kustainer needs more memory for large datasets:

```yaml
mem_limit: 8g  # Increase from 4g to 8g
```

### Development Mode

Enable Flask development mode for auto-reload:

```yaml
environment:
  - FLASK_ENV=development
```

This enables:
- Debug mode
- Auto-reload on code changes
- Detailed error pages

## Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:9001 failed: port is already allocated`

**Solution:** Edit `docker-compose.yml` and change the port mapping:

```yaml
ports:
  - "9003:9001"  # Use different external port
```

### Container Won't Start

**Check the logs:**

```bash
# LogKitchen logs
docker-compose logs logkitchen

# Kustainer logs
docker-compose logs kustainer

# All logs
docker-compose logs
```

**Common issues:**
- Insufficient disk space
- Memory constraints
- Port conflicts
- Missing environment variables

### Kustainer Out of Memory

**Symptoms:**
- Container keeps restarting
- Queries fail with timeout errors
- Ingestion fails

**Solution:** Increase memory limit in `docker-compose.yml`:

```yaml
mem_limit: 8g  # or higher depending on dataset size
```

### Database Not Persisting

**Problem:** Database disappears after container restart

**Cause:** Database was created without `persist` syntax

**Solution:** Always create databases with persistence:

```kql
.create database LogAnalysis persist (
  @"/kustodata/dbs/LogAnalysis/md",
  @"/kustodata/dbs/LogAnalysis/data"
)
```

### Files Not Showing in Kustainer

**Problem:** Log files saved in LogKitchen are not accessible in Kustainer

**Checks:**
1. Verify files exist in `./outputs/` directory on host
2. Check volume mount in `docker-compose.yml`
3. Try absolute path: `.show database storage`
4. Verify file permissions

**Solution:**
```bash
# Check if outputs directory exists
ls -la ./outputs/

# Verify volume mounts
docker inspect kustainer-adx | grep Mounts -A 10
```

### Web UI Not Loading

**Problem:** LogKitchen web UI at http://localhost:9001 doesn't load

**Checks:**
1. Container is running: `docker ps`
2. No port conflicts: `netstat -tuln | grep 9001`
3. Check health: `docker inspect logkitchen-web --format='{{.State.Health.Status}}'`

**Solution:**
```bash
# Restart container
docker-compose restart logkitchen

# Check logs for errors
docker-compose logs logkitchen
```

### Reset Everything

If all else fails, completely reset the stack:

```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove persistent data (WARNING: deletes all data!)
rm -rf ./kustodata/*
rm -rf ./outputs/*

# Rebuild and start fresh
docker-compose build --no-cache
docker-compose up -d
```

## Tips & Best Practices

### Database Management

1. **Always use `persist`** when creating databases to survive container restarts
2. **Backup regularly:** Copy the `./kustodata/` folder to backup all databases
3. **Monitor disk usage:** Kustainer databases can grow large with extensive data
4. **Use `.show database storage`** to check database size

### Performance

1. **Memory:** Default 4GB limit is suitable for testing; increase for production
2. **Materialized views:** Use for frequently run queries to improve performance
3. **Partitioning:** Consider partitioning large tables by time for better query performance
4. **Indexing:** Use `.alter table` commands to add indexes on frequently queried columns

### Data Ingestion

1. **Batch ingestion:** Ingest larger files less frequently rather than many small files
2. **CSV format:** LogKitchen saves CSV files which are optimal for Kusto ingestion
3. **Shared folder:** Files in `outputs/` are automatically available at `/logs/`
4. **Verify ingestion:** Always check row count after ingestion with `.show table extents`

### Security

1. **Localhost only:** Both services are exposed on localhost by default
2. **External access:** To expose externally, update port bindings but add authentication
3. **EULA acceptance:** Kustainer requires `ACCEPT_EULA=Y` in environment
4. **No auth by default:** Add reverse proxy (nginx, traefik) if exposing publicly

### Query Best Practices

1. **Time filters:** Always add time filters to queries for better performance
2. **Limit results:** Use `take` or `top` to limit large result sets
3. **Test on samples:** Test queries on small datasets first
4. **Use explain:** Add `| explain` to understand query execution plans

## API Endpoints

The LogKitchen web application exposes the following REST API endpoints:

- `GET /` - Web UI
- `POST /generate` - Generate logs (JSON API)
- `POST /download` - Download logs to browser
- `POST /save_to_outputs` - Save logs to outputs folder (for Kustainer)
- `GET /health` - Health check endpoint
- `GET /kusto_status` - Check Kustainer connectivity
- `GET /list_log_files` - List all log files in outputs folder
- `GET /get_schema/<log_type>` - Get Kusto schema for log type

## Resources

- [KQL Documentation](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Kusto Emulator Guide](https://learn.microsoft.com/en-us/azure/data-explorer/kusto-emulator-install)
- [KQL Quick Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kql-quick-reference)
- [Azure Data Explorer Documentation](https://learn.microsoft.com/en-us/azure/data-explorer/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Production Notes

### LogKitchen
- Logs are limited to 10,000 entries per generation
- Health checks ensure the service is always running
- The container restarts automatically unless stopped manually
- Flask runs in production mode by default

### Kustainer
- Memory limited to 4GB (increase for production workloads)
- **Data persistence enabled** via `./kustodata` volume mount
- Databases created with `persist` syntax survive container restarts
- Shared `./outputs` folder allows seamless file ingestion from LogKitchen
- Suitable for testing and development; use Azure Data Explorer for production
- **Backup:** Simply copy `./kustodata/` folder to backup all databases

## Need Help?

- Check the main [README.md](README.md) for general LogKitchen usage
- Review Docker Compose logs: `docker-compose logs`
- Check Kustainer documentation at Microsoft Learn
- Verify volume mounts and permissions
- Ensure sufficient disk space and memory
