"""
Linux Syslog generator
"""

import random
from typing import Optional
from .base import BaseLogGenerator


class SyslogGenerator(BaseLogGenerator):
    """Generate Linux syslog entries"""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed)

        # Common Linux users
        self.users = ['root', 'admin', 'ubuntu', 'centos', 'deploy', 'ansible',
                      'jenkins', 'www-data', 'mysql', 'postgres', 'redis']

        # Facilities and severities
        self.facilities = {
            'auth': 4, 'authpriv': 10, 'cron': 9, 'daemon': 3,
            'kern': 0, 'local0': 16, 'mail': 2, 'syslog': 5, 'user': 1
        }

        self.severities = {
            'emerg': 0, 'alert': 1, 'crit': 2, 'err': 3,
            'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
        }

    def generate_log(self) -> str:
        """Generate a single syslog entry"""
        # Choose event type with weights
        event_generators = {
            self._generate_ssh_event: 0.3,
            self._generate_sudo_event: 0.15,
            self._generate_auth_event: 0.15,
            self._generate_cron_event: 0.1,
            self._generate_systemd_event: 0.15,
            self._generate_kernel_event: 0.05,
            self._generate_network_event: 0.1
        }

        generator = self.weighted_choice(event_generators)
        return generator()

    def _format_syslog(self, timestamp: str, hostname: str,
                       process: str, pid: int, message: str) -> str:
        """Format a syslog message"""
        # Standard syslog format: timestamp hostname process[pid]: message
        return f"{timestamp} {hostname} {process}[{pid}]: {message}"

    def _generate_ssh_event(self) -> str:
        """Generate SSH-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()
        pid = random.randint(1000, 65535)

        events = {
            'accepted': 0.6,
            'failed': 0.3,
            'disconnect': 0.1
        }

        event_type = self.weighted_choice(events)

        if event_type == 'accepted':
            user = random.choice(self.users)
            src_ip = self.generate_ip_address(private=False)
            port = random.randint(40000, 65000)
            messages = [
                f"Accepted password for {user} from {src_ip} port {port} ssh2",
                f"Accepted publickey for {user} from {src_ip} port {port} ssh2: RSA SHA256:{''.join(random.choices('0123456789abcdef', k=43))}",
                f"pam_unix(sshd:session): session opened for user {user} by (uid=0)"
            ]
            message = random.choice(messages)

        elif event_type == 'failed':
            user = random.choice(self.users + ['invalid', 'test', 'guest', 'oracle'])
            src_ip = self.generate_ip_address(private=False)
            port = random.randint(40000, 65000)
            messages = [
                f"Failed password for {user} from {src_ip} port {port} ssh2",
                f"Failed password for invalid user {user} from {src_ip} port {port} ssh2",
                f"Connection closed by authenticating user {user} {src_ip} port {port} [preauth]",
                f"Invalid user {user} from {src_ip} port {port}",
                f"Received disconnect from {src_ip} port {port}:11: Bye Bye [preauth]"
            ]
            message = random.choice(messages)

        else:  # disconnect
            src_ip = self.generate_ip_address(private=False)
            port = random.randint(40000, 65000)
            message = f"Received disconnect from {src_ip} port {port}:11: disconnected by user"

        return self._format_syslog(timestamp, hostname, "sshd", pid, message)

    def _generate_sudo_event(self) -> str:
        """Generate sudo-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()
        pid = random.randint(1000, 65535)

        user = random.choice([u for u in self.users if u != 'root'])
        commands = [
            '/usr/bin/systemctl restart nginx',
            '/usr/bin/systemctl status apache2',
            '/usr/bin/apt update',
            '/usr/bin/yum update',
            '/bin/cat /var/log/syslog',
            '/usr/bin/docker ps',
            '/usr/bin/docker restart webapp',
            '/bin/journalctl -u sshd',
            '/usr/sbin/iptables -L',
            '/usr/bin/vim /etc/nginx/nginx.conf'
        ]
        command = random.choice(commands)

        success = random.random() > 0.1  # 90% success rate

        if success:
            message = f"{user} : TTY=pts/{random.randint(0, 5)} ; PWD=/home/{user} ; USER=root ; COMMAND={command}"
        else:
            message = f"{user} : command not allowed ; TTY=pts/{random.randint(0, 5)} ; PWD=/home/{user} ; USER=root ; COMMAND={command}"

        return self._format_syslog(timestamp, hostname, "sudo", pid, message)

    def _generate_auth_event(self) -> str:
        """Generate authentication-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()
        pid = random.randint(1000, 65535)

        user = random.choice(self.users)
        events = [
            f"pam_unix(cron:session): session opened for user {user} by (uid=0)",
            f"pam_unix(cron:session): session closed for user {user}",
            f"pam_unix(sudo:session): session opened for user root by {user}(uid=0)",
            f"pam_unix(sudo:session): session closed for user root",
            f"New session {random.randint(1, 999)} of user {user}.",
            f"Removed session {random.randint(1, 999)}."
        ]

        message = random.choice(events)
        process = random.choice(['systemd-logind', 'su', 'login'])

        return self._format_syslog(timestamp, hostname, process, pid, message)

    def _generate_cron_event(self) -> str:
        """Generate cron-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()
        pid = random.randint(1000, 65535)

        user = random.choice(self.users)
        commands = [
            '/usr/bin/backup.sh',
            '/usr/local/bin/cleanup.sh',
            '/home/user/scripts/monitor.py',
            '/usr/bin/certbot renew',
            '/usr/bin/updatedb'
        ]

        events = [
            f"({user}) CMD ({random.choice(commands)})",
            f"(CRON) info (No MTA installed, discarding output)",
            f"({user}) CMD (cd /var/www && php artisan schedule:run)"
        ]

        message = random.choice(events)

        return self._format_syslog(timestamp, hostname, "CRON", pid, message)

    def _generate_systemd_event(self) -> str:
        """Generate systemd-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()
        pid = random.randint(1, 2000)

        services = ['nginx.service', 'apache2.service', 'mysql.service',
                   'postgresql.service', 'redis.service', 'docker.service',
                   'sshd.service', 'cron.service', 'ufw.service']

        service = random.choice(services)

        events = [
            f"Started {service}.",
            f"Stopped {service}.",
            f"Reloading {service}.",
            f"Stopping {service}...",
            f"Starting {service}...",
            f"{service}: Succeeded.",
            f"{service}: Main process exited, code=exited, status=0/SUCCESS"
        ]

        message = random.choice(events)

        return self._format_syslog(timestamp, hostname, "systemd", pid, message)

    def _generate_kernel_event(self) -> str:
        """Generate kernel-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()

        events = [
            "Kernel logging (proc) stopped.",
            "Kernel log daemon terminating.",
            f"OUT={random.choice(['eth0', 'eth1', 'ens33', 'enp0s3'])} MAC={self.generate_mac_address()} SRC={self.generate_ip_address()} DST={self.generate_ip_address()}",
            f"[UFW BLOCK] IN={random.choice(['eth0', 'eth1'])} OUT= MAC={self.generate_mac_address()} SRC={self.generate_ip_address(private=False)} DST={self.generate_ip_address()} PROTO=TCP DPT={self.generate_port()}",
            f"usb 1-1: new high-speed USB device number {random.randint(2, 10)} using ehci-pci"
        ]

        message = random.choice(events)

        return f"{timestamp} {hostname} kernel: {message}"

    def _generate_network_event(self) -> str:
        """Generate network-related log entry"""
        timestamp = self.generate_timestamp(format_string="%b %d %H:%M:%S")
        hostname = self.generate_hostname()
        pid = random.randint(1000, 65535)

        events = [
            (f"DHCPACK from {self.generate_ip_address()} (xid=0x{random.randint(10000000, 99999999):x})", "dhclient"),
            (f"Server {self.generate_ip_address()} not responding, still trying", "NetworkManager"),
            (f"link becomes ready", "NetworkManager"),
            (f"Connection 'Wired connection 1' ({random.randint(1000, 9999)}) successfully activated.", "NetworkManager")
        ]

        message, process = random.choice(events)

        return self._format_syslog(timestamp, hostname, process, pid, message)


def main():
    """CLI interface for syslog generator"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate synthetic Linux syslog entries')
    parser.add_argument('--count', type=int, default=10, help='Number of log entries to generate')
    parser.add_argument('--output', type=str, help='Output file (default: print to console)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible output')

    args = parser.parse_args()

    generator = SyslogGenerator(seed=args.seed)

    if args.output:
        generator.write_logs(args.output, count=args.count)
        print(f"Generated {args.count} syslog entries to {args.output}")
    else:
        generator.print_logs(count=args.count)


if __name__ == '__main__':
    main()
