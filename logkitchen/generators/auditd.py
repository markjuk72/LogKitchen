"""
Linux Auditd log generator
"""

import random
import time
from typing import Optional, Dict
from .base import BaseLogGenerator


class AuditdGenerator(BaseLogGenerator):
    """Generate Linux auditd log entries"""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed)

        self.sequence_counter = random.randint(100, 10000)

        # Common executables
        self.executables = {
            '/bin/ls': ['ls', '-la', '-lh', '-R'],
            '/bin/cat': ['cat', '/etc/passwd', '/var/log/syslog'],
            '/usr/bin/vim': ['vim', '/etc/hosts', '/etc/nginx/nginx.conf'],
            '/usr/bin/sudo': ['sudo', '-i', 'systemctl restart nginx'],
            '/bin/ps': ['ps', 'aux', '-ef'],
            '/usr/bin/netstat': ['netstat', '-tulpn', '-an'],
            '/usr/bin/ssh': ['ssh', 'user@192.168.1.10'],
            '/bin/chmod': ['chmod', '755', '/tmp/script.sh'],
            '/bin/chown': ['chown', 'root:root', '/etc/passwd'],
            '/usr/sbin/useradd': ['useradd', '-m', 'newuser'],
            '/usr/sbin/userdel': ['userdel', 'olduser'],
            '/bin/mount': ['mount', '/dev/sda1', '/mnt'],
            '/bin/systemctl': ['systemctl', 'restart', 'nginx']
        }

        # System call numbers (x86_64)
        self.syscalls = {
            'open': 2, 'close': 3, 'read': 0, 'write': 1,
            'execve': 59, 'fork': 57, 'kill': 62, 'chmod': 90,
            'chown': 92, 'setuid': 105, 'setgid': 106, 'unlink': 87,
            'connect': 42, 'accept': 43, 'bind': 49, 'socket': 41
        }

        # Architecture
        self.arch = 'c000003e'  # x86_64

    def generate_log(self) -> str:
        """Generate a single auditd log entry"""
        event_generators = {
            self._generate_syscall_event: 0.25,
            self._generate_execve_event: 0.25,
            self._generate_user_auth_event: 0.15,
            self._generate_user_cmd_event: 0.15,
            self._generate_cred_event: 0.1,
            self._generate_login_event: 0.1
        }

        generator = self.weighted_choice(event_generators)
        return generator()

    def _get_audit_timestamp(self) -> tuple:
        """Generate audit timestamp and sequence number"""
        dt = self.generate_datetime()
        timestamp = int(dt.timestamp())
        millisec = random.randint(0, 999)
        self.sequence_counter += random.randint(1, 10)

        return f"{timestamp}.{millisec:03d}", self.sequence_counter

    def _generate_syscall_event(self) -> str:
        """Generate a SYSCALL audit event"""
        timestamp, seq = self._get_audit_timestamp()

        syscall_name = random.choice(list(self.syscalls.keys()))
        syscall_num = self.syscalls[syscall_name]

        success = random.choice(['yes', 'yes', 'yes', 'no'])  # 75% success
        exit_code = 0 if success == 'yes' else random.choice([1, 13, 2])  # EPERM, EACCES, ENOENT

        uid = random.choice([0, 1000, 1001, 1002])
        gid = random.choice([0, 1000, 1001, 1002])
        euid = uid
        egid = gid

        pid = random.randint(1000, 65535)
        ppid = random.randint(1, 1000)

        exe = random.choice(list(self.executables.keys()))
        comm = exe.split('/')[-1]

        # Generate syscall arguments (simplified)
        a0 = f"{random.randint(0, 0xffffffff):x}"
        a1 = f"{random.randint(0, 0xffffffff):x}"
        a2 = f"{random.randint(0, 0xffffffff):x}"
        a3 = f"{random.randint(0, 0xffffffff):x}"

        items = random.randint(0, 2)

        parts = [
            f"type=SYSCALL",
            f"msg=audit({timestamp}:{seq}):",
            f"arch={self.arch}",
            f"syscall={syscall_num}",
            f"success={success}",
            f"exit={exit_code}",
            f"a0={a0}",
            f"a1={a1}",
            f"a2={a2}",
            f"a3={a3}",
            f"items={items}",
            f"ppid={ppid}",
            f"pid={pid}",
            f"auid={uid}",
            f"uid={uid}",
            f"gid={gid}",
            f"euid={euid}",
            f"egid={egid}",
            f'comm="{comm}"',
            f'exe="{exe}"',
            f'key="{random.choice(["commands", "access", "modify", "delete", "(null)"])}"'
        ]

        return " ".join(parts)

    def _generate_execve_event(self) -> str:
        """Generate an EXECVE audit event"""
        timestamp, seq = self._get_audit_timestamp()

        exe, args = random.choice(list(self.executables.items()))
        cmd_args = random.sample(args, k=min(len(args), random.randint(1, 3)))

        # Format arguments as auditd does (hex encoded)
        argc = len(cmd_args)

        arg_parts = []
        for i, arg in enumerate(cmd_args):
            arg_parts.append(f'a{i}="{arg}"')

        parts = [
            f"type=EXECVE",
            f"msg=audit({timestamp}:{seq}):",
            f"argc={argc}",
            " ".join(arg_parts)
        ]

        return " ".join(parts)

    def _generate_user_auth_event(self) -> str:
        """Generate a USER_AUTH audit event"""
        timestamp, seq = self._get_audit_timestamp()

        user = self.generate_username()
        terminal = random.choice(['ssh', 'pts/0', 'pts/1', 'tty1', ':0'])
        addr = self.generate_ip_address(private=False) if 'ssh' in terminal else '?'

        success = random.choice(['yes', 'yes', 'yes', 'no'])  # 75% success
        res = 'success' if success == 'yes' else 'failed'

        exe = random.choice(['/usr/sbin/sshd', '/bin/login', '/usr/bin/sudo'])

        parts = [
            f"type=USER_AUTH",
            f"msg=audit({timestamp}:{seq}):",
            f"pid={random.randint(1000, 65535)}",
            f"uid={random.choice([0, 1000])}",
            f"auid={random.randint(1000, 2000)}",
            f'msg=\'op=PAM:authentication grantors=pam_unix acct="{user}" exe="{exe}" hostname={addr} addr={addr} terminal={terminal} res={res}\''
        ]

        return " ".join(parts)

    def _generate_user_cmd_event(self) -> str:
        """Generate a USER_CMD audit event"""
        timestamp, seq = self._get_audit_timestamp()

        user = self.generate_username()
        terminal = f"pts/{random.randint(0, 5)}"

        commands = [
            '/usr/bin/systemctl restart nginx',
            '/usr/bin/apt update',
            '/bin/cat /var/log/syslog',
            '/usr/sbin/iptables -L',
            '/usr/bin/docker ps -a',
            '/bin/journalctl -xe'
        ]

        cmd = random.choice(commands)

        parts = [
            f"type=USER_CMD",
            f"msg=audit({timestamp}:{seq}):",
            f"pid={random.randint(1000, 65535)}",
            f"uid={random.randint(1000, 2000)}",
            f"auid={random.randint(1000, 2000)}",
            f'msg=\'cwd="/home/{user}" cmd="{cmd}" terminal={terminal} res=success\''
        ]

        return " ".join(parts)

    def _generate_cred_event(self) -> str:
        """Generate credential-related audit events (CRED_ACQ, CRED_DISP)"""
        timestamp, seq = self._get_audit_timestamp()

        event_type = random.choice(['CRED_ACQ', 'CRED_DISP', 'CRED_REFR'])
        user = self.generate_username()
        terminal = random.choice([f'pts/{i}' for i in range(6)] + ['ssh', ':0'])

        exe = random.choice(['/usr/bin/sudo', '/usr/sbin/sshd', '/bin/su'])
        res = random.choice(['success', 'success', 'success', 'failed'])

        parts = [
            f"type={event_type}",
            f"msg=audit({timestamp}:{seq}):",
            f"pid={random.randint(1000, 65535)}",
            f"uid={random.choice([0, 1000])}",
            f"auid={random.randint(1000, 2000)}",
            f'msg=\'op=PAM:setcred grantors=pam_unix acct="{user}" exe="{exe}" hostname=? addr=? terminal={terminal} res={res}\''
        ]

        return " ".join(parts)

    def _generate_login_event(self) -> str:
        """Generate LOGIN audit event"""
        timestamp, seq = self._get_audit_timestamp()

        user = self.generate_username()
        uid = random.randint(1000, 2000)
        old_auid = 'unset' if random.random() > 0.5 else str(random.randint(1000, 2000))
        terminal = random.choice([f'pts/{i}' for i in range(6)] + ['/dev/tty1'])
        res = random.choice(['success', 'success', 'failed'])

        parts = [
            f"type=LOGIN",
            f"msg=audit({timestamp}:{seq}):",
            f"pid={random.randint(1000, 65535)}",
            f"uid={uid}",
            f"old-auid={old_auid}",
            f"auid={uid}",
            f"tty={terminal}",
            f"old-ses=unset",
            f"ses={random.randint(1, 999)}",
            f"res={res}"
        ]

        return " ".join(parts)


def main():
    """CLI interface for auditd generator"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate synthetic Linux auditd log entries')
    parser.add_argument('--count', type=int, default=10, help='Number of log entries to generate')
    parser.add_argument('--output', type=str, help='Output file (default: print to console)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible output')

    args = parser.parse_args()

    generator = AuditdGenerator(seed=args.seed)

    if args.output:
        generator.write_logs(args.output, count=args.count)
        print(f"Generated {args.count} auditd entries to {args.output}")
    else:
        generator.print_logs(count=args.count)


if __name__ == '__main__':
    main()
