# Kustainer Quick Reference

## Initial Setup

### 1. Access Kustainer
Open in browser: http://localhost:9002

### 2. Create Persistent Database

```kql
.create database LogAnalysis persist (
  @"/kustodata/dbs/LogAnalysis/md",
  @"/kustodata/dbs/LogAnalysis/data"
)
```

### 3. Select Database

```kql
.database LogAnalysis
```

## Table Schemas by Log Type

### Linux Syslog Table

```kql
.create table SyslogLogs (
  Timestamp:datetime,
  Hostname:string,
  Process:string,
  PID:int,
  Severity:string,
  Facility:string,
  Message:string
)
```

### Linux Auditd Table

```kql
.create table AuditdLogs (
  Timestamp:datetime,
  Type:string,
  RecordNumber:long,
  Message:string,
  User:string,
  UID:int,
  Command:string,
  Result:string
)
```

### CEF Firewall Table

```kql
.create table FirewallLogs (
  Timestamp:datetime,
  DeviceVendor:string,
  DeviceProduct:string,
  DeviceVersion:string,
  SignatureID:string,
  Name:string,
  Severity:int,
  SourceIP:string,
  DestinationIP:string,
  SourcePort:int,
  DestinationPort:int,
  Protocol:string,
  Action:string
)
```

### Windows Security Table

```kql
.create table WindowsSecurityLogs (
  Timestamp:datetime,
  EventID:int,
  Level:string,
  Computer:string,
  Source:string,
  TaskCategory:string,
  User:string,
  Message:string
)
```

## Ingesting Log Files

### From Shared Outputs Folder

Files saved to `outputs/` folder are available at `/logs/` in Kustainer:

```kql
// Ingest syslog
.ingest into table SyslogLogs (@"/logs/logkitchen_syslog_20251025.log")
  with (format="txt")

// Ingest auditd
.ingest into table AuditdLogs (@"/logs/logkitchen_auditd_20251025.log")
  with (format="txt")

// Ingest CEF
.ingest into table FirewallLogs (@"/logs/logkitchen_cef_20251025.log")
  with (format="txt")

// Ingest Windows Security
.ingest into table WindowsSecurityLogs (@"/logs/logkitchen_windows_20251025.log")
  with (format="txt")
```

### Inline Ingestion (Copy/Paste)

```kql
.ingest inline into table SyslogLogs <|
Oct 25 14:30:15 web-42 sshd[1234]: Failed password for root from 192.168.1.100
Oct 25 14:30:16 web-42 sshd[1234]: Connection closed by 192.168.1.100
```

## Common KQL Queries

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
```

### Analysis Queries

```kql
// Count by severity
SyslogLogs
| summarize count() by Severity
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
| summarize FailedAttempts=count() by SourceIP=extract(@"from ([\d.]+)", 1, Message)
| where FailedAttempts > 5
| order by FailedAttempts desc
```

### Security Analysis

```kql
// Suspicious user activity
AuditdLogs
| where Command contains "sudo" or Command contains "su"
| summarize count() by User, Command
| order by count_ desc

// Port scanning detection
FirewallLogs
| where Action == "Deny"
| summarize UniqueDestPorts=dcount(DestinationPort) by SourceIP
| where UniqueDestPorts > 20
| order by UniqueDestPorts desc

// Failed Windows logon attempts
WindowsSecurityLogs
| where EventID == 4625
| summarize FailedLogons=count() by User, Computer
| order by FailedLogons desc
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

### Detach Database (keeps data)

```kql
.detach database LogAnalysis
```

### Re-attach Database

```kql
.attach database LogAnalysis from @"/kustodata/dbs/LogAnalysis"
```

### Drop Table

```kql
.drop table SyslogLogs
```

### Drop Database (permanent!)

```kql
.drop database LogAnalysis
```

## Tips

1. **Always use `persist`** when creating databases to survive container restarts
2. **Shared folder**: Files in `outputs/` are automatically available at `/logs/` in Kustainer
3. **Backup**: Copy the `kustodata/` folder to backup all databases
4. **Memory**: Default 4GB limit - increase in docker-compose.yml if needed
5. **Performance**: Use materialized views for frequently run queries

## Resources

- [KQL Documentation](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Kusto Emulator Guide](https://learn.microsoft.com/en-us/azure/data-explorer/kusto-emulator-install)
- [KQL Quick Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kql-quick-reference)
