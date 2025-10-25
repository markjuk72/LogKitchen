"""
Base log generator class with common functionality
"""

import random
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from faker import Faker


class BaseLogGenerator(ABC):
    """Base class for all log generators"""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the base log generator

        Args:
            seed: Random seed for reproducible output
        """
        self.seed = seed
        if seed:
            random.seed(seed)
            Faker.seed(seed)

        self.faker = Faker()
        self.current_time = datetime.now()

    def generate_timestamp(self,
                          format_string: str = "%Y-%m-%d %H:%M:%S",
                          max_days_past: int = 7) -> str:
        """
        Generate a random timestamp

        Args:
            format_string: strftime format string
            max_days_past: Maximum days in the past for timestamp

        Returns:
            Formatted timestamp string
        """
        seconds_past = random.randint(0, max_days_past * 24 * 3600)
        timestamp = self.current_time - timedelta(seconds=seconds_past)
        return timestamp.strftime(format_string)

    def generate_datetime(self, max_days_past: int = 7) -> datetime:
        """
        Generate a random datetime object

        Args:
            max_days_past: Maximum days in the past

        Returns:
            datetime object
        """
        seconds_past = random.randint(0, max_days_past * 24 * 3600)
        return self.current_time - timedelta(seconds=seconds_past)

    def generate_ip_address(self, private: bool = True) -> str:
        """
        Generate a random IP address

        Args:
            private: If True, generate private IP addresses

        Returns:
            IP address string
        """
        if private:
            # Generate private IP addresses
            subnet = random.choice([
                "10.{}.{}.{}",      # 10.0.0.0/8
                "172.{}.{}.{}",     # 172.16.0.0/12
                "192.168.{}.{}"     # 192.168.0.0/16
            ])

            if subnet.startswith("10"):
                return subnet.format(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(1, 254)
                )
            elif subnet.startswith("172"):
                return subnet.format(
                    random.randint(16, 31),
                    random.randint(0, 255),
                    random.randint(1, 254)
                )
            else:  # 192.168
                return subnet.format(
                    random.randint(0, 255),
                    random.randint(1, 254)
                )
        else:
            return self.faker.ipv4_public()

    def generate_username(self) -> str:
        """Generate a random username"""
        patterns = [
            lambda: self.faker.user_name(),
            lambda: self.faker.first_name().lower(),
            lambda: f"{self.faker.first_name().lower()}.{self.faker.last_name().lower()}",
            lambda: f"{self.faker.first_name()[0].lower()}{self.faker.last_name().lower()}"
        ]
        return random.choice(patterns)()

    def generate_hostname(self, prefix: Optional[str] = None) -> str:
        """
        Generate a random hostname

        Args:
            prefix: Optional prefix for hostname (e.g., 'web', 'db', 'fw')

        Returns:
            Hostname string
        """
        if prefix:
            return f"{prefix}-{random.randint(1, 100)}"

        prefixes = ['web', 'app', 'db', 'mail', 'dns', 'fw', 'proxy', 'dc', 'fs']
        prefix = random.choice(prefixes)
        return f"{prefix}-{random.randint(1, 100)}"

    def generate_process_name(self) -> str:
        """Generate a random process name"""
        processes = [
            'sshd', 'systemd', 'cron', 'sudo', 'su', 'login',
            'apache2', 'nginx', 'mysqld', 'postgres', 'redis',
            'docker', 'containerd', 'kubelet', 'etcd',
            'fail2ban', 'ufw', 'iptables', 'firewalld'
        ]
        return random.choice(processes)

    def generate_port(self, well_known: bool = False) -> int:
        """
        Generate a random port number

        Args:
            well_known: If True, use well-known ports (0-1023)

        Returns:
            Port number
        """
        if well_known:
            common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 8443]
            return random.choice(common_ports)
        return random.randint(1024, 65535)

    def generate_mac_address(self) -> str:
        """Generate a random MAC address"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])

    def generate_user_agent(self) -> str:
        """Generate a random user agent string"""
        return self.faker.user_agent()

    def weighted_choice(self, choices: Dict[Any, float]) -> Any:
        """
        Make a weighted random choice

        Args:
            choices: Dict mapping choice to weight

        Returns:
            Selected choice
        """
        items = list(choices.keys())
        weights = list(choices.values())
        return random.choices(items, weights=weights, k=1)[0]

    @abstractmethod
    def generate_log(self) -> str:
        """
        Generate a single log entry

        Must be implemented by subclasses

        Returns:
            Log entry as string
        """
        pass

    def generate_logs(self, count: int = 10) -> List[str]:
        """
        Generate multiple log entries

        Args:
            count: Number of log entries to generate

        Returns:
            List of log entries
        """
        return [self.generate_log() for _ in range(count)]

    def write_logs(self, filename: str, count: int = 10, append: bool = False):
        """
        Write logs to a file

        Args:
            filename: Output filename
            count: Number of log entries to generate
            append: If True, append to existing file
        """
        mode = 'a' if append else 'w'
        with open(filename, mode) as f:
            for log in self.generate_logs(count):
                f.write(log + '\n')

    def print_logs(self, count: int = 10):
        """
        Print logs to console

        Args:
            count: Number of log entries to generate
        """
        for log in self.generate_logs(count):
            print(log)
