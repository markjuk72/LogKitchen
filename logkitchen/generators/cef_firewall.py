"""
CEF (Common Event Format) Firewall log generator
"""

import random
from typing import Optional, Dict, List
from datetime import datetime
from .base import BaseLogGenerator


class CEFFirewallGenerator(BaseLogGenerator):
    """Generate CEF-formatted firewall log entries"""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed)

        # CEF header components
        self.vendors = {
            'Palo Alto Networks': ('PAN-OS', ['9.0.0', '9.1.0', '10.0.0', '10.1.0']),
            'Cisco': ('ASA', ['9.8', '9.12', '9.14']),
            'Fortinet': ('FortiGate', ['6.0.0', '6.2.0', '6.4.0', '7.0.0']),
            'Check Point': ('VPN-1 & FireWall-1', ['R80.40', 'R81', 'R81.10']),
            'pfSense': ('pfSense', ['2.5.0', '2.6.0'])
        }

        # Protocols
        self.protocols = {
            'TCP': 0.5,
            'UDP': 0.3,
            'ICMP': 0.15,
            'GRE': 0.03,
            'ESP': 0.02
        }

        # Common services
        self.services = {
            'http': (80, 'TCP'),
            'https': (443, 'TCP'),
            'ssh': (22, 'TCP'),
            'telnet': (23, 'TCP'),
            'smtp': (25, 'TCP'),
            'dns': (53, 'UDP'),
            'dhcp': (67, 'UDP'),
            'tftp': (69, 'UDP'),
            'pop3': (110, 'TCP'),
            'imap': (143, 'TCP'),
            'snmp': (161, 'UDP'),
            'ldap': (389, 'TCP'),
            'smb': (445, 'TCP'),
            'mysql': (3306, 'TCP'),
            'rdp': (3389, 'TCP'),
            'postgresql': (5432, 'TCP'),
            'mongodb': (27017, 'TCP'),
            'redis': (6379, 'TCP')
        }

        # Event types
        self.event_types = {
            'TRAFFIC': 0.7,
            'THREAT': 0.2,
            'SYSTEM': 0.1
        }

        # Threat categories
        self.threat_categories = [
            'malware', 'spyware', 'vulnerability', 'virus',
            'wildfire', 'url-filtering', 'data-filtering',
            'file-blocking', 'scan', 'flood'
        ]

        # Actions
        self.actions_allow = ['allowed', 'permit', 'accept']
        self.actions_deny = ['denied', 'drop', 'reject', 'block']

    def generate_log(self) -> str:
        """Generate a single CEF firewall log entry"""
        event_type = self.weighted_choice(self.event_types)

        if event_type == 'TRAFFIC':
            return self._generate_traffic_event()
        elif event_type == 'THREAT':
            return self._generate_threat_event()
        else:
            return self._generate_system_event()

    def _format_cef(self, vendor: str, product: str, version: str,
                    event_class_id: str, name: str, severity: int,
                    extensions: Dict[str, str]) -> str:
        """
        Format a CEF log entry

        CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|Extension
        """
        # CEF version is always 0
        cef_version = 0

        # Format extensions
        ext_parts = []
        for key, value in extensions.items():
            # Escape pipes and backslashes in extension values
            escaped_value = str(value).replace('\\', '\\\\').replace('|', '\\|')
            ext_parts.append(f"{key}={escaped_value}")

        extensions_str = " ".join(ext_parts)

        # Build CEF message
        cef_parts = [
            f"CEF:{cef_version}",
            vendor,
            product,
            version,
            event_class_id,
            name,
            str(severity),
            extensions_str
        ]

        return "|".join(cef_parts)

    def _generate_traffic_event(self) -> str:
        """Generate a traffic allow/deny event"""
        # Select vendor and product
        vendor, (product, versions) = random.choice(list(self.vendors.items()))
        version = random.choice(versions)

        # Determine if traffic is allowed or denied
        allowed = random.random() > 0.3  # 70% allowed, 30% denied

        if allowed:
            action = random.choice(self.actions_allow)
            severity = random.choice([1, 2, 3])  # Low severity for allowed
            event_class_id = "TRAFFIC"
            name = "traffic-allowed"
        else:
            action = random.choice(self.actions_deny)
            severity = random.choice([5, 6, 7])  # Higher severity for denied
            event_class_id = "TRAFFIC"
            name = "traffic-denied"

        # Generate source and destination
        src_internal = random.random() > 0.3
        src = self.generate_ip_address(private=src_internal)

        # If source is internal, destination is usually external
        if src_internal:
            dst = self.generate_ip_address(private=False) if random.random() > 0.3 else self.generate_ip_address(private=True)
        else:
            dst = self.generate_ip_address(private=True)

        # Protocol
        proto = self.weighted_choice(self.protocols)

        # Ports
        if proto in ['TCP', 'UDP']:
            # Sometimes use well-known services
            if random.random() > 0.5:
                service, (dpt, service_proto) = random.choice(list(self.services.items()))
                if service_proto == proto:
                    pass  # Use the service port
                else:
                    dpt = self.generate_port(well_known=True)
            else:
                dpt = self.generate_port(well_known=random.random() > 0.7)

            spt = self.generate_port(well_known=False)
        else:
            spt = 0
            dpt = 0

        # Bytes transferred
        out_bytes = random.randint(100, 1000000)
        in_bytes = random.randint(100, 1000000)

        # Timestamp
        dt = self.generate_datetime()
        timestamp = dt.strftime("%b %d %Y %H:%M:%S")

        # Build extensions
        extensions = {
            'rt': timestamp,
            'src': src,
            'dst': dst,
            'spt': spt,
            'dpt': dpt,
            'proto': proto,
            'act': action,
            'out': out_bytes,
            'in': in_bytes,
            'deviceDirection': random.choice(['0', '1']),  # 0=inbound, 1=outbound
            'cn1': random.randint(1, 999999),  # Connection ID
            'cn1Label': 'ConnectionID'
        }

        # Add application info sometimes
        if random.random() > 0.5:
            apps = ['web-browsing', 'ssl', 'dns', 'ssh', 'ftp', 'smtp', 'http', 'smtp', 'ms-rdp']
            extensions['app'] = random.choice(apps)

        # Add source/dest zones
        if random.random() > 0.5:
            zones = ['trust', 'untrust', 'dmz', 'internal', 'external', 'vpn']
            extensions['deviceInboundInterface'] = random.choice(zones)
            extensions['deviceOutboundInterface'] = random.choice(zones)

        return self._format_cef(vendor, product, version, event_class_id, name, severity, extensions)

    def _generate_threat_event(self) -> str:
        """Generate a threat detection event"""
        # Select vendor and product
        vendor, (product, versions) = random.choice(list(self.vendors.items()))
        version = random.choice(versions)

        # Threat details
        threat_category = random.choice(self.threat_categories)
        threat_id = f"{random.randint(10000, 99999)}"

        event_class_id = "THREAT"
        name = f"threat-{threat_category}"
        severity = random.randint(7, 10)  # High severity

        # Generate source (usually external) and destination (usually internal)
        src = self.generate_ip_address(private=False)
        dst = self.generate_ip_address(private=True)

        # Protocol
        proto = random.choice(['TCP', 'UDP', 'ICMP'])

        # Ports
        if proto in ['TCP', 'UDP']:
            dpt = self.generate_port(well_known=True)
            spt = self.generate_port(well_known=False)
        else:
            spt = 0
            dpt = 0

        # Timestamp
        dt = self.generate_datetime()
        timestamp = dt.strftime("%b %d %Y %H:%M:%S")

        # Threat names
        threat_names = [
            'Generic.Malware.Detected',
            'Trojan.Win32.Agent',
            'Exploit.CVE-2021-44228',
            'Malicious.URL.Detected',
            'Suspicious.Network.Traffic',
            'SQL.Injection.Attempt',
            'XSS.Attack.Detected',
            'Brute.Force.Attack',
            'Port.Scan.Detected',
            'DDoS.Attack.Detected'
        ]

        threat_name = random.choice(threat_names)

        # Build extensions
        extensions = {
            'rt': timestamp,
            'src': src,
            'dst': dst,
            'spt': spt,
            'dpt': dpt,
            'proto': proto,
            'act': random.choice(self.actions_deny + ['alert', 'reset-both']),
            'cat': threat_category,
            'cs1': threat_name,
            'cs1Label': 'ThreatName',
            'cn1': threat_id,
            'cn1Label': 'ThreatID',
            'deviceDirection': '0'  # Inbound
        }

        # Add URL for URL filtering
        if 'url' in threat_category or random.random() > 0.7:
            malicious_urls = [
                'http://malicious-site.com/payload.exe',
                'http://phishing-site.net/login.php',
                'http://c2-server.org/beacon',
                'http://exploit-kit.ru/landing'
            ]
            extensions['request'] = random.choice(malicious_urls)

        # Add file info for malware
        if 'malware' in threat_category or 'virus' in threat_category:
            files = ['payload.exe', 'malware.dll', 'trojan.js', 'backdoor.sh']
            extensions['fname'] = random.choice(files)
            extensions['fileHash'] = ''.join(random.choices('0123456789abcdef', k=64))

        return self._format_cef(vendor, product, version, event_class_id, name, severity, extensions)

    def _generate_system_event(self) -> str:
        """Generate a system/administrative event"""
        # Select vendor and product
        vendor, (product, versions) = random.choice(list(self.vendors.items()))
        version = random.choice(versions)

        event_class_id = "SYSTEM"

        # System event types
        system_events = [
            ('admin-login', 'Administrator login', 5),
            ('admin-logout', 'Administrator logout', 3),
            ('config-change', 'Configuration changed', 6),
            ('system-start', 'System started', 4),
            ('system-shutdown', 'System shutdown', 4),
            ('ha-failover', 'HA failover occurred', 8),
            ('license-expire', 'License expiring soon', 7),
            ('disk-space-low', 'Disk space low', 7)
        ]

        event_id, name, severity = random.choice(system_events)

        # Timestamp
        dt = self.generate_datetime()
        timestamp = dt.strftime("%b %d %Y %H:%M:%S")

        # Build extensions
        extensions = {
            'rt': timestamp,
            'dvc': self.generate_ip_address(private=True),
            'dvchost': self.generate_hostname(prefix='fw')
        }

        # Add admin user for login/logout/config events
        if event_id in ['admin-login', 'admin-logout', 'config-change']:
            extensions['suser'] = random.choice(['admin', 'firewall-admin', 'security-admin'])
            extensions['src'] = self.generate_ip_address(private=True)

        # Add message
        messages = {
            'admin-login': 'Administrator logged in from management interface',
            'admin-logout': 'Administrator logged out',
            'config-change': 'Security policy modified',
            'system-start': 'Firewall system started successfully',
            'system-shutdown': 'Firewall system shutting down',
            'ha-failover': 'HA failover to secondary device',
            'license-expire': f'License will expire in {random.randint(1, 30)} days',
            'disk-space-low': f'Disk space at {random.randint(85, 95)}% capacity'
        }

        extensions['msg'] = messages[event_id]

        return self._format_cef(vendor, product, version, event_class_id, name, severity, extensions)


def main():
    """CLI interface for CEF firewall generator"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate synthetic CEF firewall log entries')
    parser.add_argument('--count', type=int, default=10, help='Number of log entries to generate')
    parser.add_argument('--output', type=str, help='Output file (default: print to console)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible output')

    args = parser.parse_args()

    generator = CEFFirewallGenerator(seed=args.seed)

    if args.output:
        generator.write_logs(args.output, count=args.count)
        print(f"Generated {args.count} CEF firewall entries to {args.output}")
    else:
        generator.print_logs(count=args.count)


if __name__ == '__main__':
    main()
