"""
Flask web application for LogKitchen
"""

from flask import Flask, render_template, request, jsonify, send_file
import io
import os
import requests
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

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logkitchen_{log_type}_{timestamp}.log"

            # Save to outputs folder (mounted to /app/outputs in container)
            outputs_dir = '/app/outputs'
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)

            file_path = os.path.join(outputs_dir, filename)

            # Write logs to file
            with open(file_path, 'w') as f:
                for log in logs:
                    f.write(log + '\n')

            return jsonify({
                'success': True,
                'filename': filename,
                'path': file_path,
                'count': len(logs),
                'kusto_path': f'/logs/{filename}',
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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
