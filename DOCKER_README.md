# LogKitchen - Docker Setup

Web-based synthetic log generator running in a Docker container, integrated with Azure Data Explorer (Kustainer) for log analysis.

## Quick Start

### 1. Build and Start the Stack

```bash
docker-compose up -d
```

This will start **two services**:
- **LogKitchen** - Synthetic log generator (port 9001)
- **Kustainer** - Azure Data Explorer for log analysis (port 9002)

### 2. Access the Services

**LogKitchen Web UI:**
```
http://localhost:9001
```

**Kustainer (Azure Data Explorer):**
```
http://localhost:9002
```

### 3. Complete Workflow (LogKitchen → Kustainer)

**Generate Logs:**
1. Open LogKitchen at http://localhost:9001
2. Select a log type (Syslog, Auditd, CEF Firewall, or Windows Security)
3. Choose the number of logs to generate (1-10,000)
4. Optionally set a random seed for reproducible output
5. Click "Generate Logs"
6. Download the generated logs as a file

**Analyze in Kustainer (with Persistent Storage):**
1. Open Kustainer at http://localhost:9002
2. Create a **persistent** database (survives container restarts):
   ```kql
   .create database LogAnalysis persist (
     @"/kustodata/dbs/LogAnalysis/md",
     @"/kustodata/dbs/LogAnalysis/data"
   )
   ```
3. Select the database: `.database LogAnalysis`
4. Create a table for your logs:
   ```kql
   .create table Logs (
     Timestamp:datetime,
     Level:string,
     Message:string,
     Host:string,
     Source:string
   )
   ```
5. Ingest logs from the shared folder:
   ```kql
   // Files saved to outputs/ folder are accessible at /logs/ in Kustainer
   .ingest into table Logs (@"/logs/logkitchen_syslog_20251025.log")
     with (format="csv", ignoreFirstRecord=false)
   ```
6. Query with KQL (Kusto Query Language)

**Example KQL Queries:**
```kql
// Count logs by type
Logs | summarize count() by LogLevel

// Show recent errors
Logs | where LogLevel == "error" | top 10 by Timestamp desc

// Time series analysis
Logs | summarize count() by bin(Timestamp, 1h) | render timechart
```

## Docker Commands

### Start the container
```bash
docker-compose up -d
```

### Stop the container
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f logkitchen
```

### Rebuild after changes
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Restart the container
```bash
docker-compose restart
```

## Services Overview

### LogKitchen (Port 9001)
- **Container:** `logkitchen-web`
- **Purpose:** Generate synthetic logs for SIEM testing
- **Memory:** Default Docker allocation
- **Features:** Web UI, API, file downloads

### Kustainer (Port 9002)
- **Container:** `kustainer-adx`
- **Purpose:** Azure Data Explorer for log analysis with KQL
- **Memory:** 4GB limit
- **Features:** KQL queries, data ingestion, time-series analysis

Both services run on the same Docker network (`logkitchen-network`) and can communicate with each other.

## Directory Structure

```
logkitchen/
├── config/               # Configuration files (mounted to LogKitchen)
├── outputs/              # Generated log files (shared between LogKitchen & Kustainer)
├── kustodata/            # Kustainer database persistence (survives restarts)
├── logkitchen/
│   ├── web/             # Flask web application
│   │   ├── app.py       # Main Flask app
│   │   └── templates/   # HTML templates
│   └── generators/      # Log generators
├── Dockerfile           # Docker build instructions for LogKitchen
└── docker-compose.yml   # Docker Compose configuration (both services)
```

## Volume Mounts

### LogKitchen Volumes
1. **./config** → `/app/config` (read-only)
   - Custom configuration files for log generators

2. **./outputs** → `/app/outputs` (read-write)
   - Generated log files are saved here
   - Downloads from web UI save to this folder

### Kustainer Volumes
1. **./kustodata** → `/kustodata` (read-write)
   - **Database persistence** - databases created with `persist` survive container restarts
   - Stores metadata and data files
   - Example: `/kustodata/dbs/LogAnalysis/md` and `/kustodata/dbs/LogAnalysis/data`

2. **./outputs** → `/logs` (read-only)
   - **Shared folder** with LogKitchen for log file ingestion
   - Access generated logs for ingestion: `.ingest into table Logs (@"/logs/yourfile.log")`
   - No need to manually copy files - automatically available to Kustainer

## Environment Variables

### LogKitchen
You can customize the following environment variables in `docker-compose.yml`:

- `FLASK_ENV`: Set to `production` (default) or `development`
- `PORT`: Internal port (default: 9001)

### Kustainer
- `ACCEPT_EULA`: Must be set to `Y` to accept Microsoft EULA
- `mem_limit`: Memory limit (default: 4GB) - increase if needed for large datasets

## Database Persistence

### Creating Persistent Databases
**Important:** Always use the `persist` syntax to ensure databases survive container restarts:

```kql
.create database <DatabaseName> persist (
  @"/kustodata/dbs/<DatabaseName>/md",
  @"/kustodata/dbs/<DatabaseName>/data"
)
```

**Without `persist`:** Data is stored only in container memory and will be lost on restart.

### Database Management Commands

**List all databases:**
```kql
.show databases
```

**Detach database (keeps data, stops using it):**
```kql
.detach database <DatabaseName>
```

**Re-attach existing database:**
```kql
.attach database <DatabaseName> from @"/kustodata/dbs/<DatabaseName>"
```

**Drop database (permanently deletes):**
```kql
.drop database <DatabaseName>
```

### File Ingestion from Shared Folder

Log files generated by LogKitchen and saved to `./outputs/` are automatically available in Kustainer at `/logs/`:

```kql
// Ingest a specific file
.ingest into table Logs (@"/logs/logkitchen_syslog_20251025_120000.log")
  with (format="csv")

// Ingest with custom format
.ingest into table Logs (@"/logs/mydata.log")
  with (format="txt", ignoreFirstRecord=true)
```

## Health Checks

Both containers include health checks that run every 30 seconds:

**LogKitchen:**
```bash
docker inspect logkitchen-web --format='{{.State.Health.Status}}'
```

**Kustainer:**
```bash
docker inspect kustainer-adx --format='{{.State.Health.Status}}'
```

## Troubleshooting

### Port already in use
If ports 9001 or 9002 are already in use, edit `docker-compose.yml`:

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

### Container won't start
Check the logs for specific service:
```bash
# LogKitchen logs
docker-compose logs logkitchen

# Kustainer logs
docker-compose logs kustainer

# All logs
docker-compose logs
```

### Kustainer needs more memory
If Kustainer runs out of memory, edit `docker-compose.yml`:
```yaml
mem_limit: 8g  # Increase from 4g to 8g
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
```

## Log Types Supported

1. **Linux Syslog** - Standard Linux system logs
2. **Linux Auditd** - Linux audit daemon logs
3. **CEF Firewall** - Common Event Format firewall logs
4. **Windows Security** - Windows Security Event logs

## API Endpoints

The web application exposes the following endpoints:

- `GET /` - Web UI
- `POST /generate` - Generate logs (JSON API)
- `POST /download` - Download logs as file
- `GET /health` - Health check endpoint

## Development

To run in development mode, edit `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=development
```

This enables:
- Debug mode
- Auto-reload on code changes
- Detailed error pages

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

### Security Considerations
- Both services are exposed on localhost only by default
- To expose externally, update port bindings in docker-compose.yml
- Kustainer EULA must be accepted (ACCEPT_EULA=Y)
- No authentication configured by default - add reverse proxy if exposing publicly
