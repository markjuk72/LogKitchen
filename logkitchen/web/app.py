"""
Flask web application for LogKitchen
"""

from flask import Flask, render_template, request, jsonify, send_file
import io
import os
import requests
import csv
import re
from datetime import datetime

from logkitchen.generators.syslog import SyslogGenerator
from logkitchen.generators.auditd import AuditdGenerator
from logkitchen.generators.cef_firewall import CEFFirewallGenerator
from logkitchen.generators.windows_security import WindowsSecurityGenerator
from logkitchen.generators.verifone_pos import VerifonePOSGenerator


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

    # Map log types to generator classes
    GENERATORS = {
        'syslog': SyslogGenerator,
        'auditd': AuditdGenerator,
        'cef': CEFFirewallGenerator,
        'windows': WindowsSecurityGenerator,
        'verifone_pos': VerifonePOSGenerator
    }

    LOG_TYPE_NAMES = {
        'syslog': 'Linux Syslog',
        'auditd': 'Linux Auditd',
        'cef': 'CEF Firewall',
        'windows': 'Windows Security',
        'verifone_pos': 'Verifone POS Security'
    }

    # Kusto table schemas for each log type
    KUSTO_SCHEMAS = {
        'syslog': {
            'table_name': 'SyslogLogs',
            'create_command': '.create table SyslogLogs (Timestamp:datetime, Hostname:string, Process:string, PID:int, Message:string, RawLog:string)',
            'columns': ['Timestamp', 'Hostname', 'Process', 'PID', 'Message', 'RawLog']
        },
        'cef': {
            'table_name': 'CEFFirewallLogs',
            'create_command': '.create table CEFFirewallLogs (Timestamp:datetime, Vendor:string, Product:string, Version:string, EventClassID:string, Name:string, Severity:int, SourceIP:string, DestIP:string, SourcePort:int, DestPort:int, Protocol:string, Action:string, RawLog:string)',
            'columns': ['Timestamp', 'Vendor', 'Product', 'Version', 'EventClassID', 'Name', 'Severity', 'SourceIP', 'DestIP', 'SourcePort', 'DestPort', 'Protocol', 'Action', 'RawLog']
        },
        'windows': {
            'table_name': 'WindowsSecurityLogs',
            'create_command': '.create table WindowsSecurityLogs (Timestamp:datetime, EventID:int, Level:string, Computer:string, AccountName:string, AccountDomain:string, SourceIP:string, LogonType:string, RawLog:string)',
            'columns': ['Timestamp', 'EventID', 'Level', 'Computer', 'AccountName', 'AccountDomain', 'SourceIP', 'LogonType', 'RawLog']
        },
        'auditd': {
            'table_name': 'AuditdLogs',
            'create_command': '.create table AuditdLogs (Timestamp:datetime, RecordType:string, Node:string, Syscall:string, Success:string, User:string, Command:string, RawLog:string)',
            'columns': ['Timestamp', 'RecordType', 'Node', 'Syscall', 'Success', 'User', 'Command', 'RawLog']
        },
        'verifone_pos': {
            'table_name': 'VerifonePOSLogs',
            'create_command': '.create table VerifonePOSLogs (Timestamp:datetime, Severity:string, Component:string, TerminalID:string, TransactionID:string, Message:string, RawLog:string)',
            'columns': ['Timestamp', 'Severity', 'Component', 'TerminalID', 'TransactionID', 'Message', 'RawLog']
        }
    }

    def convert_logs_to_csv(logs: list, log_type: str) -> str:
        """Convert raw log strings to CSV format based on log type"""
        if log_type == 'syslog':
            return _convert_syslog_to_csv(logs)
        elif log_type == 'cef':
            return _convert_cef_to_csv(logs)
        elif log_type == 'windows':
            return _convert_windows_to_csv(logs)
        elif log_type == 'auditd':
            return _convert_auditd_to_csv(logs)
        elif log_type == 'verifone_pos':
            return _convert_verifone_to_csv(logs)
        else:
            # Fallback: simple single column
            return _convert_generic_to_csv(logs)

    def _convert_syslog_to_csv(logs: list) -> str:
        """Convert syslog to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(KUSTO_SCHEMAS['syslog']['columns'])

        for log in logs:
            # Parse syslog format: "Feb 12 14:23:45 hostname process[pid]: message"
            match = re.match(r'(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+?)\[(\d+)\]:\s+(.+)', log)
            if match:
                timestamp, hostname, process, pid, message = match.groups()
                writer.writerow([timestamp, hostname, process, pid, message, log])
            else:
                # Fallback if parsing fails
                writer.writerow(['', '', '', '', '', log])

        return output.getvalue()

    def _convert_cef_to_csv(logs: list) -> str:
        """Convert CEF to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(KUSTO_SCHEMAS['cef']['columns'])

        for log in logs:
            # Parse CEF format: CEF:Version|Vendor|Product|Version|EventClassID|Name|Severity|Extensions
            if log.startswith('CEF:'):
                parts = log.split('|')
                if len(parts) >= 8:
                    vendor = parts[1]
                    product = parts[2]
                    version = parts[3]
                    event_class_id = parts[4]
                    name = parts[5]
                    severity = parts[6]
                    extensions = parts[7]

                    # Parse extensions for key fields
                    ext_dict = {}
                    for item in extensions.split():
                        if '=' in item:
                            key, value = item.split('=', 1)
                            ext_dict[key] = value

                    # Extract timestamp
                    timestamp = ext_dict.get('rt', '')

                    # Extract key fields
                    src_ip = ext_dict.get('src', '')
                    dst_ip = ext_dict.get('dst', '')
                    src_port = ext_dict.get('spt', '0')
                    dst_port = ext_dict.get('dpt', '0')
                    protocol = ext_dict.get('proto', '')
                    action = ext_dict.get('act', '')

                    writer.writerow([timestamp, vendor, product, version, event_class_id, name, severity,
                                   src_ip, dst_ip, src_port, dst_port, protocol, action, log])
                else:
                    writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', log])
            else:
                writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', log])

        return output.getvalue()

    def _convert_windows_to_csv(logs: list) -> str:
        """Convert Windows Security logs to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(KUSTO_SCHEMAS['windows']['columns'])

        for log in logs:
            # Parse Windows log format: EventID=4624 Level=Information Computer=DC-001 TimeGenerated=...
            event_id_match = re.search(r'EventID=(\d+)', log)
            level_match = re.search(r'Level=(\w+)', log)
            computer_match = re.search(r'Computer=(\S+)', log)
            timestamp_match = re.search(r'TimeGenerated=(.*?)(?=\s+[A-Z][A-Za-z_]+:|$)', log)
            account_name_match = re.search(r'(?:Target_Account_Name|Account_Name|Subject_Account_Name):\s*(\S+)', log)
            account_domain_match = re.search(r'(?:Target_Account_Domain|Account_Domain|Subject_Account_Domain):\s*(\S+)', log)
            source_ip_match = re.search(r'(?:Source_Network_Address|Client_Address|Source_Address):\s*(\S+)', log)
            logon_type_match = re.search(r'Logon_Type:\s*([^;]+)', log)

            event_id = event_id_match.group(1) if event_id_match else ''
            level = level_match.group(1) if level_match else ''
            computer = computer_match.group(1) if computer_match else ''
            timestamp = timestamp_match.group(1).strip() if timestamp_match else ''
            account_name = account_name_match.group(1) if account_name_match else ''
            account_domain = account_domain_match.group(1) if account_domain_match else ''
            source_ip = source_ip_match.group(1) if source_ip_match else ''
            logon_type = logon_type_match.group(1).strip() if logon_type_match else ''

            writer.writerow([timestamp, event_id, level, computer, account_name, account_domain,
                           source_ip, logon_type, log])

        return output.getvalue()

    def _convert_auditd_to_csv(logs: list) -> str:
        """Convert Auditd logs to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(KUSTO_SCHEMAS['auditd']['columns'])

        for log in logs:
            # Parse auditd format varies, but generally: type=TYPE ... msg=audit(timestamp): ...
            type_match = re.search(r'type=(\S+)', log)
            node_match = re.search(r'node=(\S+)', log)
            syscall_match = re.search(r'syscall=(\S+)', log)
            success_match = re.search(r'success=(\S+)', log)
            user_match = re.search(r'(?:uid|user)=(\S+)', log)
            cmd_match = re.search(r'(?:cmd|comm)=(\S+)', log)
            timestamp_match = re.search(r'audit\(([^)]+)\)', log)

            record_type = type_match.group(1) if type_match else ''
            node = node_match.group(1) if node_match else ''
            syscall = syscall_match.group(1) if syscall_match else ''
            success = success_match.group(1) if success_match else ''
            user = user_match.group(1) if user_match else ''
            command = cmd_match.group(1) if cmd_match else ''
            timestamp = timestamp_match.group(1) if timestamp_match else ''

            writer.writerow([timestamp, record_type, node, syscall, success, user, command, log])

        return output.getvalue()

    def _convert_verifone_to_csv(logs: list) -> str:
        """Convert Verifone POS logs to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(KUSTO_SCHEMAS['verifone_pos']['columns'])

        for log in logs:
            # Parse Verifone format (varies by implementation)
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', log)
            severity_match = re.search(r'\[(CRITICAL|ERROR|WARNING|INFO|DEBUG)\]', log)
            component_match = re.search(r'\[(\w+)\]', log)
            terminal_match = re.search(r'Terminal[:\s]+(\S+)', log)
            transaction_match = re.search(r'(?:Transaction|TXN)[:\s]+(\S+)', log)

            timestamp = timestamp_match.group(1) if timestamp_match else ''
            severity = severity_match.group(1) if severity_match else ''
            component = component_match.group(1) if component_match else ''
            terminal_id = terminal_match.group(1) if terminal_match else ''
            transaction_id = transaction_match.group(1) if transaction_match else ''

            writer.writerow([timestamp, severity, component, terminal_id, transaction_id, log, log])

        return output.getvalue()

    def _convert_generic_to_csv(logs: list) -> str:
        """Generic fallback CSV conversion"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['RawLog'])

        for log in logs:
            writer.writerow([log])

        return output.getvalue()

    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html', log_types=LOG_TYPE_NAMES)

    @app.route('/generate', methods=['POST'])
    def generate():
        """Generate logs based on user input"""
        try:
            data = request.get_json()

            log_type = data.get('log_type')
            count = int(data.get('count', 100))
            seed = data.get('seed')

            # Validate inputs
            if log_type not in GENERATORS:
                return jsonify({'error': 'Invalid log type'}), 400

            if count < 1 or count > 10000:
                return jsonify({'error': 'Count must be between 1 and 10,000'}), 400

            if seed:
                try:
                    seed = int(seed)
                except ValueError:
                    return jsonify({'error': 'Seed must be a number'}), 400

            # Generate logs
            generator_class = GENERATORS[log_type]
            generator = generator_class(seed=seed)
            logs = generator.generate_logs(count=count)

            return jsonify({
                'success': True,
                'logs': logs,
                'count': len(logs),
                'log_type': log_type,
                'log_type_name': LOG_TYPE_NAMES[log_type]
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/download', methods=['POST'])
    def download():
        """Download generated logs as a file"""
        try:
            data = request.get_json()

            logs = data.get('logs', [])
            log_type = data.get('log_type', 'logs')

            if not logs:
                return jsonify({'error': 'No logs to download'}), 400

            # Create file in memory
            output = io.StringIO()
            for log in logs:
                output.write(log + '\n')

            # Convert to bytes
            output.seek(0)
            bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
            bytes_output.seek(0)

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logkitchen_{log_type}_{timestamp}.log"

            return send_file(
                bytes_output,
                mimetype='text/plain',
                as_attachment=True,
                download_name=filename
            )

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/save_to_outputs', methods=['POST'])
    def save_to_outputs():
        """Save generated logs to the outputs folder for Kustainer ingestion"""
        try:
            data = request.get_json()

            logs = data.get('logs', [])
            log_type = data.get('log_type', 'logs')

            if not logs:
                return jsonify({'error': 'No logs to save'}), 400

            # Convert logs to CSV format
            csv_content = convert_logs_to_csv(logs, log_type)

            # Generate filename with .csv extension
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logkitchen_{log_type}_{timestamp}.csv"

            # Save to outputs folder (mounted to /app/outputs in container)
            outputs_dir = '/app/outputs'
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)

            file_path = os.path.join(outputs_dir, filename)

            # Write CSV to file
            with open(file_path, 'w') as f:
                f.write(csv_content)

            # Get schema info for this log type
            schema_info = KUSTO_SCHEMAS.get(log_type, {})
            table_name = schema_info.get('table_name', 'MyIngestedSample')
            create_command = schema_info.get('create_command', '')

            return jsonify({
                'success': True,
                'filename': filename,
                'path': file_path,
                'count': len(logs),
                'kusto_path': f'/logs/{filename}',
                'table_name': table_name,
                'create_command': create_command,
                'message': f'Saved {len(logs)} logs to {filename}'
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'logkitchen'})

    @app.route('/kusto_status')
    def kusto_status():
        """Check Kusto/Kustainer status"""
        try:
            # Attempt to connect to Kusto management endpoint
            # Use 'kustainer' service name for Docker container networking
            response = requests.post(
                'http://kustainer:8080/v1/rest/mgmt',
                json={'csl': '.show cluster'},
                headers={'Content-Type': 'application/json'},
                timeout=3
            )

            if response.status_code == 200:
                return jsonify({
                    'status': 'online',
                    'message': 'Kusto is running and accessible'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Kusto responded with status code {response.status_code}'
                }), 200

        except requests.exceptions.ConnectionError:
            return jsonify({
                'status': 'offline',
                'message': 'Cannot connect to Kusto container'
            }), 200
        except requests.exceptions.Timeout:
            return jsonify({
                'status': 'timeout',
                'message': 'Kusto connection timed out'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error checking Kusto status: {str(e)}'
            }), 200

    @app.route('/list_log_files')
    def list_log_files():
        """List all log files in the outputs folder"""
        try:
            outputs_dir = '/app/outputs'

            # Create directory if it doesn't exist
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
                return jsonify({'files': []})

            # Get all .log and .csv files
            files = []
            for filename in os.listdir(outputs_dir):
                if filename.endswith(('.log', '.csv')):
                    file_path = os.path.join(outputs_dir, filename)
                    file_stat = os.stat(file_path)

                    # Determine log type from filename
                    log_type = None
                    for lt in ['syslog', 'auditd', 'cef', 'windows', 'verifone_pos']:
                        if lt in filename:
                            log_type = lt
                            break

                    schema_info = KUSTO_SCHEMAS.get(log_type, {}) if log_type else {}

                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'kusto_path': f'/logs/{filename}',
                        'log_type': log_type,
                        'table_name': schema_info.get('table_name', 'MyIngestedSample')
                    })

            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)

            return jsonify({'files': files})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/get_schema/<log_type>')
    def get_schema(log_type):
        """Get Kusto schema information for a specific log type"""
        try:
            schema_info = KUSTO_SCHEMAS.get(log_type, {})
            if not schema_info:
                return jsonify({'error': 'Unknown log type'}), 404

            return jsonify(schema_info)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
