"""
Generator for Verifone POS Security logs
"""

from datetime import datetime, timedelta
import random
from .base import BaseLogGenerator


class VerifonePOSGenerator(BaseLogGenerator):
    """Generates synthetic Verifone POS Security logs"""

    def __init__(self, seed=None):
        super().__init__(seed)

        # Store IDs (100-800 range)
        self.store_ids = list(range(100, 800))

        # Store IP addresses (private ranges)
        self.store_ips = [
            f"172.{random.randint(17, 25)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            for _ in range(200)
        ]

        # Remote IP addresses (typical internal POS network)
        self.remote_ips = [
            f"192.168.31.{i}" for i in range(100, 210)
        ]

        # Usernames
        self.usernames = [
            'mbsusr', 'proctor', 'pdipos', 'archiver', 'admin', 'cashier',
            'manager', 'supervisor', 'sysadmin', 'posuser', 'backoffice'
        ]

        # API actions
        self.api_actions = [
            'cfdcposrequest', 'vtlogpdlist', 'validate', 'vAppInfo', 'vtransset',
            'vrubyrept', 'vgrouplist', 'vreportpdlist', 'vMovement', 'vsalestotals',
            'vitemlist', 'vtenderlist', 'vauditreport', 'vlogin', 'vlogout'
        ]

        # Authentication actions
        self.auth_actions = [
            'validate', 'vlogin', 'vlogout', 'authenticate', 'authorization'
        ]

        # Register IDs
        self.register_ids = list(range(0, 10))

        # Log level
        self.log_level = 'WARN'
        self.category = 'security'

    def _generate_timestamp(self, base_time):
        """Generate a timestamp in Verifone format"""
        return base_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def _generate_user_auth_log(self, timestamp):
        """Generate a user authentication log entry"""
        store_id = random.choice(self.store_ids)
        store_ip = random.choice(self.store_ips)
        username = random.choice(self.usernames)
        action = random.choice(self.auth_actions)
        register_id = random.choice(self.register_ids)
        remote_ip = random.choice(self.remote_ips)

        # 80% success rate, 20% failure
        if random.random() < 0.8:
            status = 'PASSED'
            message = ''
        else:
            status = 'FAILED'
            message = random.choice([
                ' - Invalid Credentials',
                ' - Account Locked',
                ' - Expired Password',
                ' - Insufficient Privileges',
                ' - Session Timeout'
            ])

        log = (
            f"{self._generate_timestamp(timestamp)}     - "
            f"Store {store_id} - {store_ip} - {self.log_level}  {self.category} - "
            f"USER: {username} - {action} - {status} - HTTP REQUEST - "
            f"Register ID# {register_id} - REMOTE IP# {remote_ip} - {message}\\012"
        )

        return log

    def _generate_api_request_log(self, timestamp):
        """Generate an API request log entry"""
        store_id = random.choice(self.store_ids)
        store_ip = random.choice(self.store_ips)
        action = random.choice(self.api_actions)
        register_id = random.choice(self.register_ids)
        remote_ip = random.choice(self.remote_ips)

        # 95% success rate for API requests
        status = 'PASSED' if random.random() < 0.95 else 'FAILED'

        log = (
            f"{self._generate_timestamp(timestamp)}     - "
            f"Store {store_id} - {store_ip} - {self.log_level}  {self.category} - "
            f"{action} - {status} - HTTP REQUEST - "
            f"Register ID# {register_id} - REMOTE IP# {remote_ip} - \\012"
        )

        return log

    def _generate_api_request_with_user_log(self, timestamp):
        """Generate an API request log entry with user information"""
        store_id = random.choice(self.store_ids)
        store_ip = random.choice(self.store_ips)
        username = random.choice(self.usernames)
        action = random.choice([a for a in self.api_actions if a not in self.auth_actions])
        register_id = random.choice(self.register_ids)
        remote_ip = random.choice(self.remote_ips)
        status = 'PASSED' if random.random() < 0.95 else 'FAILED'

        log = (
            f"{self._generate_timestamp(timestamp)}     - "
            f"Store {store_id} - {store_ip} - {self.log_level}  {self.category} - "
            f"USER: {username} - {action} - {status} - HTTP REQUEST - "
            f"Register ID# {register_id} - REMOTE IP# {remote_ip} - \\012"
        )

        return log

    def _generate_pam_ssh_log(self, timestamp):
        """Generate PAM/SSH system log entries"""
        store_id = random.choice(self.store_ids)
        store_ip = random.choice(self.store_ips)
        username = 'archiver'
        remote_ip = random.choice(self.remote_ips)

        log_types = [
            f"pam_unix(sshd:session): session opened for user {username} by (uid=0)",
            f"pam_unix(sshd:session): session closed for user {username}",
            f"Remote request {remote_ip}: scp -t /cygdrive/d/ftproot/TopazLogs/topaz{random.randint(100,200)}-{datetime.now().strftime('%m-%d')}T09-audit.gz",
            f"Remote request {remote_ip}: scp -t /cygdrive/d/ftproot/TopazLogs/topaz{random.randint(100,200)}-{datetime.now().strftime('%m-%d')}T09-ossec.log.gz",
            f"Remote request {remote_ip}: MKDIR /cygdrive/d/ftproot/TopazLogs",
            f"HISTORY: PID={random.randint(5000,6000)} UID=48 /home/archiver/bin/cmd.sh"
        ]

        message = random.choice(log_types)

        log = (
            f"{self._generate_timestamp(timestamp)}     - "
            f"Store {store_id} - {store_ip} - {message}"
        )

        return log

    def _generate_ssh_error_log(self, timestamp):
        """Generate SSH error log entries"""
        store_id = random.choice(self.store_ids)
        store_ip = random.choice(self.store_ips)

        errors = [
            "error: Could not load host key: /etc/openssh/ssh_host_rsa_key",
            "error: Could not load host certificate: /etc/openssh/ssh_host_rsa_key-cert.pub",
            "error: SSH connection failed - timeout",
            "error: Authentication method not supported"
        ]

        message = random.choice(errors)

        log = (
            f"{self._generate_timestamp(timestamp)}     - "
            f"Store {store_id} - {store_ip} - {message}"
        )

        return log

    def _generate_movement_log(self, timestamp):
        """Generate inventory movement log entries"""
        store_id = random.choice(self.store_ids)
        store_ip = random.choice(self.store_ips)

        log = (
            f"{self._generate_timestamp(timestamp)}     - "
            f"Store {store_id} - {store_ip} - {self.log_level}  {self.category} - "
            f"vMovement - PASSED - HTTP REQUEST - Register ID# 0 - REMOTE IP# 127.0.0.1 - \\012"
        )

        return log

    def generate_log(self):
        """Generate a single Verifone POS Security log entry"""
        # Generate a realistic timestamp
        timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3600))

        # Weight the different log types
        log_type = random.choices(
            [
                self._generate_api_request_log,
                self._generate_user_auth_log,
                self._generate_api_request_with_user_log,
                self._generate_pam_ssh_log,
                self._generate_ssh_error_log,
                self._generate_movement_log
            ],
            weights=[40, 20, 25, 8, 2, 5],  # API requests most common
            k=1
        )[0]

        return log_type(timestamp)

    def generate_logs(self, count=100):
        """Generate multiple Verifone POS Security log entries"""
        logs = []
        base_time = datetime.now()

        for i in range(count):
            # Space out logs realistically (every few seconds)
            timestamp = base_time - timedelta(seconds=(count - i) * random.uniform(0.5, 5))

            # Generate weighted log types
            log_type = random.choices(
                [
                    self._generate_api_request_log,
                    self._generate_user_auth_log,
                    self._generate_api_request_with_user_log,
                    self._generate_pam_ssh_log,
                    self._generate_ssh_error_log,
                    self._generate_movement_log
                ],
                weights=[40, 20, 25, 8, 2, 5],
                k=1
            )[0]

            logs.append(log_type(timestamp))

        # Sort by timestamp (most recent first, matching the sample)
        logs.sort(reverse=True)

        return logs
