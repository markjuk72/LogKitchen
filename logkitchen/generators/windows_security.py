"""
Windows Security Event Log generator
"""

import random
from typing import Optional, Dict, List
from .base import BaseLogGenerator


class WindowsSecurityGenerator(BaseLogGenerator):
    """Generate Windows Security Event log entries"""

    def __init__(self, seed: Optional[int] = None):
        super().__init__(seed)

        # Windows domain and computer names
        self.domains = ['CORP', 'ENTERPRISE', 'DOMAIN', 'CONTOSO']
        self.computer_prefixes = ['DC', 'WS', 'SRV', 'FS', 'EXCH', 'SQL', 'APP']

        # Windows usernames
        self.windows_users = [
            'Administrator', 'admin', 'john.doe', 'jane.smith',
            'service_account', 'backup_admin', 'sql_service',
            'iis_apppool', 'system', 'network_service'
        ]

        # Logon types
        self.logon_types = {
            2: 'Interactive',           # Local logon
            3: 'Network',               # Network logon
            4: 'Batch',                 # Scheduled task
            5: 'Service',               # Service startup
            7: 'Unlock',                # Workstation unlock
            8: 'NetworkCleartext',      # IIS basic auth
            10: 'RemoteInteractive',    # RDP
            11: 'CachedInteractive'     # Cached credentials
        }

        # Security groups
        self.security_groups = [
            'Domain Admins',
            'Enterprise Admins',
            'Administrators',
            'Remote Desktop Users',
            'Backup Operators',
            'Account Operators',
            'Server Operators'
        ]

        # Failure reasons
        self.failure_reasons = [
            'Unknown user name or bad password',
            'Account currently disabled',
            'Account logon time restriction violation',
            'User not allowed to logon at this computer',
            'Password has expired',
            'Account locked out'
        ]

        # Event weights
        self.event_weights = {
            4624: 0.35,  # Successful logon
            4625: 0.15,  # Failed logon
            4634: 0.20,  # Logoff
            4672: 0.05,  # Special privileges
            4720: 0.02,  # User created
            4732: 0.03,  # Member added to group
            4740: 0.02,  # Account locked
            4768: 0.05,  # Kerberos TGT
            4776: 0.05,  # NTLM auth
            5140: 0.05,  # Share access
            5156: 0.02,  # FW allowed
            5157: 0.01   # FW blocked
        }

    def generate_log(self) -> str:
        """Generate a single Windows Security Event log entry"""
        event_id = self.weighted_choice(self.event_weights)

        event_generators = {
            4624: self._generate_4624_successful_logon,
            4625: self._generate_4625_failed_logon,
            4634: self._generate_4634_logoff,
            4672: self._generate_4672_special_privileges,
            4720: self._generate_4720_user_created,
            4732: self._generate_4732_member_added,
            4740: self._generate_4740_account_locked,
            4768: self._generate_4768_kerberos_tgt,
            4776: self._generate_4776_ntlm_auth,
            5140: self._generate_5140_share_access,
            5156: self._generate_5156_fw_allowed,
            5157: self._generate_5157_fw_blocked
        }

        return event_generators[event_id]()

    def _get_windows_timestamp(self) -> str:
        """Generate Windows event log timestamp"""
        dt = self.generate_datetime()
        return dt.strftime("%m/%d/%Y %I:%M:%S %p")

    def _get_domain_user(self) -> tuple:
        """Generate domain and username"""
        domain = random.choice(self.domains)
        user = random.choice(self.windows_users)
        return domain, user

    def _get_computer_name(self) -> str:
        """Generate Windows computer name"""
        prefix = random.choice(self.computer_prefixes)
        return f"{prefix}-{random.randint(1, 100):03d}"

    def _format_event(self, event_id: int, level: str, computer: str,
                      timestamp: str, fields: Dict[str, str]) -> str:
        """Format a Windows event log entry"""
        # Build field string
        field_parts = []
        for key, value in fields.items():
            field_parts.append(f"{key}: {value}")

        fields_str = "; ".join(field_parts)

        return f"EventID={event_id} Level={level} Computer={computer} TimeGenerated={timestamp} {fields_str}"

    def _generate_4624_successful_logon(self) -> str:
        """Generate Event ID 4624: An account was successfully logged on"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        # Choose logon type
        logon_type = self.weighted_choice({
            2: 0.2,   # Interactive
            3: 0.3,   # Network
            10: 0.3,  # RDP
            5: 0.1,   # Service
            4: 0.1    # Batch
        })

        logon_type_name = self.logon_types[logon_type]

        # Source info
        src_ip = self.generate_ip_address(private=random.random() > 0.3)
        src_computer = self._get_computer_name() if random.random() > 0.5 else '-'

        # Session ID
        logon_id = f"0x{random.randint(0x100000, 0xFFFFFF):X}"

        fields = {
            'Subject_Account_Name': random.choice(['SYSTEM', 'LOCAL SERVICE', user]),
            'Subject_Account_Domain': domain,
            'Subject_Logon_ID': f"0x{random.randint(0x1000, 0xFFFF):X}",
            'Target_Account_Name': user,
            'Target_Account_Domain': domain,
            'Target_Logon_ID': logon_id,
            'Logon_Type': f"{logon_type} ({logon_type_name})",
            'Source_Network_Address': src_ip,
            'Source_Port': random.randint(49152, 65535),
            'Workstation_Name': src_computer,
            'Authentication_Package': random.choice(['Kerberos', 'NTLM', 'Negotiate'])
        }

        return self._format_event(4624, 'Information', computer, timestamp, fields)

    def _generate_4625_failed_logon(self) -> str:
        """Generate Event ID 4625: An account failed to log on"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        # Sometimes use invalid usernames
        if random.random() > 0.7:
            user = random.choice(['admin', 'test', 'guest', 'user', 'sqlserver'])

        logon_type = self.weighted_choice({
            2: 0.2,   # Interactive
            3: 0.4,   # Network
            10: 0.4   # RDP
        })

        logon_type_name = self.logon_types[logon_type]
        failure_reason = random.choice(self.failure_reasons)

        # Status and sub-status codes
        status_codes = {
            'Unknown user name or bad password': ('0xC000006D', '0xC000006A'),
            'Account currently disabled': ('0xC0000072', '0x0'),
            'Account logon time restriction violation': ('0xC000006F', '0x0'),
            'User not allowed to logon at this computer': ('0xC0000070', '0x0'),
            'Password has expired': ('0xC0000071', '0x0'),
            'Account locked out': ('0xC0000234', '0xC0000234')
        }

        status, sub_status = status_codes[failure_reason]

        src_ip = self.generate_ip_address(private=False)

        fields = {
            'Target_Account_Name': user,
            'Target_Account_Domain': domain,
            'Failure_Reason': failure_reason,
            'Status': status,
            'Sub_Status': sub_status,
            'Logon_Type': f"{logon_type} ({logon_type_name})",
            'Source_Network_Address': src_ip,
            'Source_Port': random.randint(49152, 65535),
            'Workstation_Name': self._get_computer_name()
        }

        return self._format_event(4625, 'Information', computer, timestamp, fields)

    def _generate_4634_logoff(self) -> str:
        """Generate Event ID 4634: An account was logged off"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        logon_type = random.choice([2, 3, 10])
        logon_type_name = self.logon_types[logon_type]

        fields = {
            'Account_Name': user,
            'Account_Domain': domain,
            'Logon_ID': f"0x{random.randint(0x100000, 0xFFFFFF):X}",
            'Logon_Type': f"{logon_type} ({logon_type_name})"
        }

        return self._format_event(4634, 'Information', computer, timestamp, fields)

    def _generate_4672_special_privileges(self) -> str:
        """Generate Event ID 4672: Special privileges assigned to new logon"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        # Usually admin accounts
        if random.random() > 0.5:
            user = 'Administrator'

        privileges = [
            'SeSecurityPrivilege',
            'SeBackupPrivilege',
            'SeRestorePrivilege',
            'SeTakeOwnershipPrivilege',
            'SeDebugPrivilege',
            'SeSystemEnvironmentPrivilege',
            'SeLoadDriverPrivilege',
            'SeImpersonatePrivilege'
        ]

        selected_privs = random.sample(privileges, k=random.randint(3, 6))

        fields = {
            'Account_Name': user,
            'Account_Domain': domain,
            'Logon_ID': f"0x{random.randint(0x100000, 0xFFFFFF):X}",
            'Privileges': ', '.join(selected_privs)
        }

        return self._format_event(4672, 'Information', computer, timestamp, fields)

    def _generate_4720_user_created(self) -> str:
        """Generate Event ID 4720: A user account was created"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, _ = self._get_domain_user()

        creator_user = random.choice(['Administrator', 'admin', 'hr_admin'])
        new_user = f"{self.faker.first_name().lower()}.{self.faker.last_name().lower()}"

        fields = {
            'Subject_Account_Name': creator_user,
            'Subject_Account_Domain': domain,
            'Target_Account_Name': new_user,
            'Target_Account_Domain': domain,
            'Target_Security_ID': f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(100000, 999999)}-{random.randint(100000, 999999)}-{random.randint(1000, 9999)}"
        }

        return self._format_event(4720, 'Information', computer, timestamp, fields)

    def _generate_4732_member_added(self) -> str:
        """Generate Event ID 4732: A member was added to a security-enabled local group"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        admin_user = random.choice(['Administrator', 'admin'])
        group = random.choice(self.security_groups)

        fields = {
            'Subject_Account_Name': admin_user,
            'Subject_Account_Domain': domain,
            'Member_Name': f"{domain}\\{user}",
            'Target_Group_Name': group,
            'Target_Group_Domain': domain
        }

        return self._format_event(4732, 'Information', computer, timestamp, fields)

    def _generate_4740_account_locked(self) -> str:
        """Generate Event ID 4740: A user account was locked out"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        src_computer = self._get_computer_name()

        fields = {
            'Target_Account_Name': user,
            'Target_Account_Domain': domain,
            'Caller_Computer_Name': src_computer
        }

        return self._format_event(4740, 'Warning', computer, timestamp, fields)

    def _generate_4768_kerberos_tgt(self) -> str:
        """Generate Event ID 4768: A Kerberos authentication ticket (TGT) was requested"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        success = random.random() > 0.1  # 90% success

        fields = {
            'Account_Name': user,
            'Account_Domain': domain,
            'Client_Address': self.generate_ip_address(private=True),
            'Ticket_Options': '0x40810010',
            'Result_Code': '0x0' if success else random.choice(['0x6', '0x12', '0x17', '0x18']),
            'Ticket_Encryption_Type': random.choice(['0x12', '0x17', '0x18'])  # AES256, RC4, AES128
        }

        return self._format_event(4768, 'Information', computer, timestamp, fields)

    def _generate_4776_ntlm_auth(self) -> str:
        """Generate Event ID 4776: The domain controller attempted to validate credentials"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        success = random.random() > 0.15  # 85% success

        fields = {
            'Authentication_Package': 'MICROSOFT_AUTHENTICATION_PACKAGE_V1_0',
            'Logon_Account': user,
            'Source_Workstation': self._get_computer_name(),
            'Error_Code': '0x0' if success else random.choice(['0xC0000064', '0xC000006A', '0xC0000234'])
        }

        return self._format_event(4776, 'Information', computer, timestamp, fields)

    def _generate_5140_share_access(self) -> str:
        """Generate Event ID 5140: A network share object was accessed"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()
        domain, user = self._get_domain_user()

        shares = ['\\\\*\\C$', '\\\\*\\ADMIN$', '\\\\*\\IPC$', '\\\\*\\SYSVOL',
                  '\\\\*\\NETLOGON', '\\\\*\\Shared', '\\\\*\\Users']

        fields = {
            'Subject_Account_Name': user,
            'Subject_Account_Domain': domain,
            'Source_Address': self.generate_ip_address(private=True),
            'Source_Port': random.randint(49152, 65535),
            'Share_Name': random.choice(shares),
            'Access_Mask': random.choice(['0x1', '0x2', '0x3'])  # Read, Write, Read+Write
        }

        return self._format_event(5140, 'Information', computer, timestamp, fields)

    def _generate_5156_fw_allowed(self) -> str:
        """Generate Event ID 5156: Windows Filtering Platform allowed a connection"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()

        protocol = random.choice([6, 17])  # TCP or UDP
        app_paths = [
            '\\device\\harddiskvolume2\\windows\\system32\\svchost.exe',
            '\\device\\harddiskvolume2\\program files\\microsoft sql server\\mssql\\binn\\sqlservr.exe',
            '\\device\\harddiskvolume2\\windows\\system32\\dns.exe',
            '\\device\\harddiskvolume2\\windows\\explorer.exe'
        ]

        fields = {
            'Application': random.choice(app_paths),
            'Direction': random.choice(['Inbound', 'Outbound']),
            'Source_Address': self.generate_ip_address(private=True),
            'Source_Port': random.randint(1024, 65535),
            'Destination_Address': self.generate_ip_address(private=random.random() > 0.5),
            'Destination_Port': self.generate_port(well_known=True),
            'Protocol': protocol
        }

        return self._format_event(5156, 'Information', computer, timestamp, fields)

    def _generate_5157_fw_blocked(self) -> str:
        """Generate Event ID 5157: Windows Filtering Platform blocked a connection"""
        timestamp = self._get_windows_timestamp()
        computer = self._get_computer_name()

        protocol = random.choice([6, 17])  # TCP or UDP

        fields = {
            'Application': 'System',
            'Direction': 'Inbound',
            'Source_Address': self.generate_ip_address(private=False),
            'Source_Port': random.randint(1024, 65535),
            'Destination_Address': self.generate_ip_address(private=True),
            'Destination_Port': self.generate_port(well_known=True),
            'Protocol': protocol
        }

        return self._format_event(5157, 'Information', computer, timestamp, fields)


def main():
    """CLI interface for Windows Security Event generator"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate synthetic Windows Security Event log entries')
    parser.add_argument('--count', type=int, default=10, help='Number of log entries to generate')
    parser.add_argument('--output', type=str, help='Output file (default: print to console)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible output')

    args = parser.parse_args()

    generator = WindowsSecurityGenerator(seed=args.seed)

    if args.output:
        generator.write_logs(args.output, count=args.count)
        print(f"Generated {args.count} Windows Security Event entries to {args.output}")
    else:
        generator.print_logs(count=args.count)


if __name__ == '__main__':
    main()
