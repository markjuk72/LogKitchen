"""
Terminal User Interface for LogKitchen using Textual
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Input, Select, Label, TextLog, RadioButton, RadioSet
from textual.screen import Screen
from textual import on
from pathlib import Path
import sys

# Add parent directory to path to import generators
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from logkitchen.generators.syslog import SyslogGenerator
from logkitchen.generators.auditd import AuditdGenerator
from logkitchen.generators.cef_firewall import CEFFirewallGenerator
from logkitchen.generators.windows_security import WindowsSecurityGenerator


class WelcomeScreen(Screen):
    """Welcome screen with log type selection"""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $accent;
    }

    #subtitle {
        width: 100%;
        height: 2;
        content-align: center middle;
        color: $text-muted;
    }

    .log-type-container {
        width: 80;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }

    .log-type-button {
        width: 100%;
        margin: 1;
    }

    #config-section {
        width: 80;
        height: auto;
        margin-top: 2;
    }

    Input {
        width: 20;
        margin: 1;
    }

    Label {
        width: 20;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()

        yield Static("LogKitchen", id="title")
        yield Static("Synthetic Log Generator for SIEM Testing", id="subtitle")

        with Container(classes="log-type-container"):
            yield Static("Select Log Type to Generate:", classes="section-header")
            yield Button("Linux Syslog", id="btn-syslog", classes="log-type-button", variant="primary")
            yield Button("Linux Auditd", id="btn-auditd", classes="log-type-button", variant="primary")
            yield Button("CEF Firewall Logs", id="btn-cef", classes="log-type-button", variant="primary")
            yield Button("Windows Security Events", id="btn-windows", classes="log-type-button", variant="primary")

        with Container(id="config-section"):
            with Horizontal():
                yield Label("Log Count:")
                yield Input(placeholder="100", id="input-count")

            with Horizontal():
                yield Label("Output File:")
                yield Input(placeholder="(console output)", id="input-file")

            with Horizontal():
                yield Label("Random Seed:")
                yield Input(placeholder="(random)", id="input-seed")

        yield Footer()

    @on(Button.Pressed, "#btn-syslog")
    def on_syslog_pressed(self) -> None:
        """Handle syslog button press"""
        self.app.push_screen(GeneratorScreen("syslog", self._get_config()))

    @on(Button.Pressed, "#btn-auditd")
    def on_auditd_pressed(self) -> None:
        """Handle auditd button press"""
        self.app.push_screen(GeneratorScreen("auditd", self._get_config()))

    @on(Button.Pressed, "#btn-cef")
    def on_cef_pressed(self) -> None:
        """Handle CEF button press"""
        self.app.push_screen(GeneratorScreen("cef_firewall", self._get_config()))

    @on(Button.Pressed, "#btn-windows")
    def on_windows_pressed(self) -> None:
        """Handle Windows button press"""
        self.app.push_screen(GeneratorScreen("windows_security", self._get_config()))

    def _get_config(self) -> dict:
        """Get configuration from inputs"""
        count_input = self.query_one("#input-count", Input)
        file_input = self.query_one("#input-file", Input)
        seed_input = self.query_one("#input-seed", Input)

        try:
            count = int(count_input.value) if count_input.value else 100
        except ValueError:
            count = 100

        try:
            seed = int(seed_input.value) if seed_input.value else None
        except ValueError:
            seed = None

        output_file = file_input.value if file_input.value else None

        return {
            "count": count,
            "seed": seed,
            "output_file": output_file
        }


class GeneratorScreen(Screen):
    """Screen for generating and displaying logs"""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    GeneratorScreen {
        align: center top;
    }

    #gen-title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $accent;
    }

    #gen-info {
        width: 100%;
        height: 2;
        content-align: center middle;
        color: $text-muted;
    }

    #log-output {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }

    Button {
        margin: 0 2;
    }
    """

    def __init__(self, log_type: str, config: dict):
        super().__init__()
        self.log_type = log_type
        self.config = config
        self.generator = None
        self.logs_generated = False

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()

        log_type_names = {
            "syslog": "Linux Syslog",
            "auditd": "Linux Auditd",
            "cef_firewall": "CEF Firewall Logs",
            "windows_security": "Windows Security Events"
        }

        title = f"Generating {log_type_names.get(self.log_type, self.log_type)}"
        info = f"Count: {self.config['count']} | Seed: {self.config['seed'] or 'Random'}"

        if self.config['output_file']:
            info += f" | Output: {self.config['output_file']}"

        yield Static(title, id="gen-title")
        yield Static(info, id="gen-info")

        yield TextLog(id="log-output", highlight=True, markup=True)

        with Horizontal(id="button-container"):
            yield Button("Generate", id="btn-generate", variant="success")
            yield Button("Clear", id="btn-clear", variant="warning")
            yield Button("Save to File", id="btn-save")
            yield Button("Back", id="btn-back", variant="error")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the generator when screen is mounted"""
        generators = {
            "syslog": SyslogGenerator,
            "auditd": AuditdGenerator,
            "cef_firewall": CEFFirewallGenerator,
            "windows_security": WindowsSecurityGenerator
        }

        generator_class = generators.get(self.log_type)
        if generator_class:
            self.generator = generator_class(seed=self.config['seed'])

    @on(Button.Pressed, "#btn-generate")
    def on_generate_pressed(self) -> None:
        """Handle generate button press"""
        if not self.generator:
            return

        log_output = self.query_one("#log-output", TextLog)
        log_output.clear()

        # Generate logs
        logs = self.generator.generate_logs(count=self.config['count'])

        # Display logs
        for log in logs:
            log_output.write(log)

        self.logs_generated = True

        # If output file specified, save automatically
        if self.config['output_file']:
            self._save_to_file()

    @on(Button.Pressed, "#btn-clear")
    def on_clear_pressed(self) -> None:
        """Handle clear button press"""
        log_output = self.query_one("#log-output", TextLog)
        log_output.clear()
        self.logs_generated = False

    @on(Button.Pressed, "#btn-save")
    def on_save_pressed(self) -> None:
        """Handle save button press"""
        if self.logs_generated:
            self._save_to_file()

    @on(Button.Pressed, "#btn-back")
    def on_back_pressed(self) -> None:
        """Handle back button press"""
        self.app.pop_screen()

    def _save_to_file(self) -> None:
        """Save generated logs to file"""
        if not self.generator:
            return

        # Determine filename
        if self.config['output_file']:
            filename = self.config['output_file']
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.log_type}_{timestamp}.log"

        # Generate and save logs
        self.generator.write_logs(filename, count=self.config['count'])

        # Update info
        info_widget = self.query_one("#gen-info", Static)
        info_widget.update(f"{info_widget.renderable} | Saved to: {filename}")


class LogKitchenApp(App):
    """Main LogKitchen TUI Application"""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def on_mount(self) -> None:
        """Initialize the application"""
        self.push_screen(WelcomeScreen())

    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.dark = not self.dark


def main():
    """Run the LogKitchen TUI"""
    app = LogKitchenApp()
    app.run()


if __name__ == "__main__":
    main()
