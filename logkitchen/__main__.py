"""
Main entry point for LogKitchen
"""

import argparse
import sys
from pathlib import Path

from logkitchen.generators.syslog import SyslogGenerator
from logkitchen.generators.auditd import AuditdGenerator
from logkitchen.generators.cef_firewall import CEFFirewallGenerator
from logkitchen.generators.windows_security import WindowsSecurityGenerator
from logkitchen.utils.helpers import validate_count, validate_seed, get_output_filename


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='LogKitchen - Synthetic Log Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch TUI interface
  python -m logkitchen

  # Generate 100 syslog entries to console
  python -m logkitchen --type syslog --count 100

  # Generate auditd logs to file
  python -m logkitchen --type auditd --count 500 --output audit.log

  # Generate with specific seed for reproducibility
  python -m logkitchen --type cef --count 1000 --seed 12345 --output firewall.log

  # Generate all log types
  python -m logkitchen --all --count 100
        """
    )

    parser.add_argument(
        '--type', '-t',
        choices=['syslog', 'auditd', 'cef', 'windows'],
        help='Type of logs to generate'
    )

    parser.add_argument(
        '--count', '-c',
        type=int,
        default=100,
        help='Number of log entries to generate (default: 100)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file (default: print to console)'
    )

    parser.add_argument(
        '--seed', '-s',
        type=int,
        help='Random seed for reproducible output'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all log types'
    )

    parser.add_argument(
        '--tui',
        action='store_true',
        help='Launch TUI interface (default if no arguments)'
    )

    args = parser.parse_args()

    # If no arguments provided or --tui specified, launch TUI
    if len(sys.argv) == 1 or args.tui:
        from logkitchen.tui.interface import main as tui_main
        tui_main()
        return

    # Generate all log types
    if args.all:
        generators = {
            'syslog': SyslogGenerator,
            'auditd': AuditdGenerator,
            'cef_firewall': CEFFirewallGenerator,
            'windows_security': WindowsSecurityGenerator
        }

        for log_type, generator_class in generators.items():
            print(f"\nGenerating {log_type} logs...")
            generator = generator_class(seed=args.seed)

            if args.output:
                # Add type prefix to filename
                base, ext = args.output.rsplit('.', 1) if '.' in args.output else (args.output, 'log')
                output_file = f"{base}_{log_type}.{ext}"
            else:
                output_file = get_output_filename(log_type)

            generator.write_logs(output_file, count=args.count)
            print(f"Generated {args.count} {log_type} entries to {output_file}")

        return

    # Generate specific log type
    if not args.type:
        parser.print_help()
        print("\nError: Please specify --type or use --all")
        sys.exit(1)

    # Map short names to generator classes
    generators = {
        'syslog': SyslogGenerator,
        'auditd': AuditdGenerator,
        'cef': CEFFirewallGenerator,
        'windows': WindowsSecurityGenerator
    }

    generator_class = generators[args.type]
    generator = generator_class(seed=args.seed)

    if args.output:
        generator.write_logs(args.output, count=args.count)
        print(f"Generated {args.count} {args.type} entries to {args.output}")
    else:
        generator.print_logs(count=args.count)


if __name__ == '__main__':
    main()
