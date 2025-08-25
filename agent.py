#!/usr/bin/env python3
"""
Draft 'n' Pray - Write. Send. Hope. Repeat. (Now with AI)
"""

import os
import sys
from pathlib import Path
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from system_prompt import system_prompt
from model import get_model
from tools import TOOLS, initialize_vectorstore_with_cv
import colorama
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.align import Align
from rich.markdown import Markdown
import typer
import uuid
import getpass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize colorama for cross-platform color support
colorama.init(autoreset=True)

# Rich console for beautiful output
console = Console()

# Typer app for CLI
app = typer.Typer(
    name="Draft 'n' Pray",
    help="🤖 Write. Send. Hope. Repeat. (Now with AI)",
    add_completion=False,
    rich_markup_mode="rich",
)

checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": str(uuid.uuid4())}}


class AgentCLI:
    def __init__(self):
        self.agent = None
        self.cv_loaded = False
        self.cv_path = None
        self.api_keys = {}

    def print_banner(self):
        banner_text = """

    +============================================================================================+
    |██████╗ ██████╗  █████╗ ███████╗████████╗    ███╗   ██╗    ██████╗ ██████╗  █████╗ ██╗   ██╗|
    |██╔══██╗██╔══██╗██╔══██╗██╔════╝╚══██╔══╝    ████╗  ██║    ██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝|
    |██║  ██║██████╔╝███████║█████╗     ██║       ██╔██╗ ██║    ██████╔╝██████╔╝███████║ ╚████╔╝ |
    |██║  ██║██╔══██╗██╔══██║██╔══╝     ██║       ██║╚██╗██║    ██╔═══╝ ██╔══██╗██╔══██║  ╚██╔╝  |
    |██████╔╝██║  ██║██║  ██║██║        ██║       ██║ ╚████║    ██║     ██║  ██║██║  ██║   ██║   |
    |╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝       ╚═╝  ╚═══╝   ═╝    ═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   |
    +============================================================================================+

        """
        banner = Text(banner_text, style="bold yellow", justify="center")
        subtitle = Text(
            "Write. Send. Hope. Repeat. (Now with AI)",
            style="italic cyan",
            justify="center",
        )

        panel = Panel(
            Align.center(banner + "\n" + subtitle), border_style="cyan", padding=(1, 2)
        )
        console.print(panel)

    def print_header(self):
        header = Table.grid(padding=1)
        header.add_column(style="bold cyan", justify="left")
        header.add_column(style="cyan", justify="left")
        header.add_row("[bold cyan]Made by Fahim Muntasir[/bold cyan]")
        header.add_row("[bold cyan][Email] muntasirfahim.niloy@gmail.com[/bold cyan]")
        console.print(header)
        console.print()

    def get_api_key_interactively(self, key_name: str, description: str = "") -> str:
        """Securely get API key from user input"""
        console.print(f"\n🔑 [bold yellow]API Key Required: {key_name}[/bold yellow]")
        if description:
            console.print(f"💡 {description}")

        # Try to get from environment first
        env_value = os.getenv(key_name)
        if env_value:
            console.print(f"✅ Found {key_name} in environment", style="green")
            if Confirm.ask(f"🔄 Would you like to update the existing {key_name}?"):
                # User wants to update, continue to input
                pass
            else:
                return env_value

        # Ask user to input the key
        while True:
            try:
                # Use getpass for secure input (hidden on most terminals)
                api_key = getpass.getpass(f"🔐 Enter your {key_name}: ")
                if api_key.strip():
                    # Store in memory for this session
                    self.api_keys[key_name] = api_key.strip()
                    # Set as environment variable for this session
                    os.environ[key_name] = api_key.strip()
                    console.print(f"✅ {key_name} set successfully", style="green")
                    return api_key.strip()
                else:
                    console.print("❌ API key cannot be empty", style="red")
            except Exception as e:
                console.print(f"❌ Error reading API key: {str(e)}", style="yellow")
                # Fallback to regular input if getpass fails
                api_key = Prompt.ask(f"🔐 Enter your {key_name}")
                if api_key.strip():
                    self.api_keys[key_name] = api_key.strip()
                    os.environ[key_name] = api_key.strip()
                    console.print(f"✅ {key_name} set successfully", style="green")
                    return api_key.strip()

    def check_and_setup_environment(self):
        """Check environment and setup missing API keys interactively"""
        console.print("🔍 Checking environment configuration...", style="yellow")

        # Define required API keys with descriptions
        required_keys = {
            "GOOGLE_API_KEY": "Required for Google AI services (Gemini, etc.)",
            "FIRECRAWL_API_KEY": "Required for web crawling functionality",
        }

        missing_keys = []

        # Check which keys are missing
        for key_name, description in required_keys.items():
            if not os.getenv(key_name):
                missing_keys.append((key_name, description))

        if missing_keys:
            console.print(
                f"\n⚠️  [yellow]Missing {len(missing_keys)} required API key(s):[/yellow]"
            )

            # Ask user if they want to input keys interactively
            if Confirm.ask("\n🔑 Would you like to input the missing API keys now?"):
                console.print("\n[bold cyan]Setting up API keys...[/bold cyan]")

                for key_name, description in missing_keys:
                    self.get_api_key_interactively(key_name, description)

                console.print("\n✅ All required API keys have been set", style="green")
            else:
                console.print(
                    "\n❌ [red]API keys are required to run the application[/red]"
                )
                console.print("💡 You can:")
                console.print("   • Create a .env file with your API keys")
                console.print("   • Set them as environment variables")
                console.print(
                    "   • Run the application again and input them interactively"
                )
                return False
        else:
            console.print(
                "✅ All required API keys found in environment", style="green"
            )

        # Verify all keys are now available
        for key_name in required_keys.keys():
            if not os.getenv(key_name):
                console.print(f"❌ [red]Failed to set {key_name}[/red]")
                return False

        console.print("✅ Environment configuration complete", style="green")
        return True

    def save_api_keys_to_env_file(self):
        """Offer to save API keys to .env file for future use"""
        if not self.api_keys:
            return

        if Confirm.ask(
            "\n💾 Would you like to save these API keys to a .env file for future use?"
        ):
            try:
                env_content = []

                # Read existing .env file if it exists
                if Path(".env").exists():
                    with open(".env", "r") as f:
                        existing_lines = f.readlines()
                        existing_keys = set()

                        for line in existing_lines:
                            if "=" in line and not line.strip().startswith("#"):
                                key = line.split("=")[0].strip()
                                existing_keys.add(key)

                        # Add existing keys that weren't updated
                        for line in existing_lines:
                            if "=" in line and not line.strip().startswith("#"):
                                key = line.split("=")[0].strip()
                                if key not in self.api_keys:
                                    env_content.append(line)

                # Add new/updated API keys
                for key_name, key_value in self.api_keys.items():
                    env_content.append(f"{key_name}={key_value}\n")

                # Write to .env file
                with open(".env", "w") as f:
                    f.writelines(env_content)

                console.print("✅ API keys saved to .env file", style="green")
                console.print(
                    "💡 [yellow]Note: Keep your .env file secure and don't commit it to version control[/yellow]"
                )

            except Exception as e:
                console.print(
                    f"⚠️  Failed to save to .env file: {str(e)}", style="yellow"
                )

    def check_environment(self):
        """Legacy method - now calls the new setup method"""
        return self.check_and_setup_environment()

    def initialize_agent(self):
        try:
            with console.status("[bold green]Initializing AI Agent...", spinner="dots"):
                # Get the required API keys
                google_api_key = os.getenv("GOOGLE_API_KEY")
                firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

                if not google_api_key:
                    console.print("❌ GOOGLE_API_KEY not found", style="red")
                    return False

                if not firecrawl_api_key:
                    console.print("❌ FIRECRAWL_API_KEY not found", style="red")
                    return False

                # Create tools with proper API keys
                from tools import create_tools_with_api_keys

                tools = create_tools_with_api_keys(google_api_key, firecrawl_api_key)

                llm = get_model(api_key=google_api_key)
                self.agent = create_react_agent(
                    model=llm,
                    tools=tools,
                    prompt=system_prompt,
                    checkpointer=checkpointer,
                )
            console.print("✅ AI Agent initialized successfully", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Failed to initialize AI Agent: {str(e)}", style="red")
            return False

    def initialize_cv_knowledge_base(self):
        self.cv_path = os.getenv("CV_PATH")

        if not self.cv_path:
            console.print("⚠️  No CV_PATH specified in environment", style="yellow")
            self.cv_path = Prompt.ask("📁 Enter path to your CV file", default="cv.pdf")

        if not Path(self.cv_path).exists():
            console.print(f"❌ CV file not found: {self.cv_path}", style="red")
            return False

        console.print(f"📖 Loading CV from: [bold blue]{self.cv_path}[/bold blue]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing CV...", total=None)

            try:
                # Get the Google API key for embeddings
                google_api_key = os.getenv("GOOGLE_API_KEY")
                if not google_api_key:
                    console.print(
                        "❌ GOOGLE_API_KEY not found for CV processing", style="red"
                    )
                    return False

                if initialize_vectorstore_with_cv(self.cv_path, api_key=google_api_key):
                    progress.update(task, description="✅ CV loaded successfully!")
                    self.cv_loaded = True
                    return True
                else:
                    progress.update(task, description="❌ Failed to load CV")
                    return False
            except Exception as e:
                progress.update(task, description=f"❌ Error: {str(e)}")
                return False

    def print_tools_info(self):
        """Display available tools in a beautiful table"""
        tools_table = Table(
            title="🛠️  Available Tools", show_header=True, header_style="bold magenta"
        )
        tools_table.add_column("Tool", style="cyan", no_wrap=True)
        tools_table.add_column("Description", style="white")
        tools_table.add_column("Usage", style="yellow")

        tools_info = [
            (
                "kb_tool",
                "Search your CV for relevant information",
                "Ask about your skills, experience, etc.",
            ),
            ("crawl_website", "Crawl websites for content", "Provide a URL to crawl"),
            (
                "initialize_vectorstore_with_cv",
                "Re-initialize CV knowledge base",
                "Use if CV changes",
            ),
        ]

        for tool, desc, usage in tools_info:
            tools_table.add_row(tool, desc, usage)

        console.print(tools_table)
        console.print()

    def print_help(self):
        """Display help information"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]
• [green]help[/green] - Show this help message
• [green]tools[/green] - Show available tools
• [green]cv[/green] - Show CV status
• [green]apikeys[/green] - Show API key status
• [green]quit[/green], [green]exit[/green], [green]bye[/green] - Exit the application

[bold cyan]CLI Commands:[/bold cyan]
• [green]python agent.py[/green] - Start the main application
• [green]python agent.py setup-keys[/green] - Setup API keys interactively
• [green]python agent.py --help[/green] - Show CLI help

[bold cyan]Example Queries:[/bold cyan]
• "What are my technical skills?"
• "Tell me about my work experience"
• "Crawl https://example.com and summarize it"
• "What programming languages do I know?"

[bold cyan]API Key Management:[/bold cyan]
• Set GOOGLE_API_KEY and FIRECRAWL_API_KEY in .env file
• Or run [green]python agent.py setup-keys[/green] for interactive setup
• API keys are stored securely and can be saved for future use
        """

        panel = Panel(help_text, title="📚 Help", border_style="cyan")
        console.print(panel)

    def show_cv_status(self):
        """Display CV status information"""
        status = "✅ Loaded" if self.cv_loaded else "❌ Not Loaded"
        status_color = "green" if self.cv_loaded else "red"

        status_info = f"""
[bold]CV Status:[/bold] [{status_color}]{status}[/{status_color}]
[bold]CV Path:[/bold] {self.cv_path or "Not specified"}
[bold]Knowledge Base:[/bold] {"Ready" if self.cv_loaded else "Not available"}
        """

        panel = Panel(status_info, title="📄 CV Information", border_style="blue")
        console.print(panel)

    def show_api_keys_status(self):
        """Display API key status information"""
        required_keys = {
            "GOOGLE_API_KEY": "Required for Google AI services (Gemini, etc.)",
            "FIRECRAWL_API_KEY": "Required for web crawling functionality",
        }

        status_table = Table(
            title="🔑 API Key Status", show_header=True, header_style="bold magenta"
        )
        status_table.add_column("API Key", style="cyan", no_wrap=True)
        status_table.add_column("Status", style="white")
        status_table.add_column("Description", style="yellow")

        for key_name, description in required_keys.items():
            status = "✅ Set" if os.getenv(key_name) else "❌ Missing"
            status_style = "green" if os.getenv(key_name) else "red"
            status_table.add_row(
                key_name, f"[{status_style}]{status}[/{status_style}]", description
            )

        console.print(status_table)

        # Show additional info
        if self.api_keys:
            console.print(
                f"\n💡 [cyan]Session API keys: {len(self.api_keys)} key(s) loaded[/cyan]"
            )
        else:
            console.print("\n💡 [cyan]No session API keys loaded[/cyan]")

    def render_markdown_response(self, markdown_text: str):
        """Render markdown response with proper formatting"""
        try:
            # Create a markdown renderer
            markdown = Markdown(markdown_text)

            # Display in a beautiful panel
            response_panel = Panel(
                markdown,
                title="🤖 AI Agent Response",
                border_style="green",
                padding=(1, 2),
                expand=False,
            )
            console.print(response_panel)

        except Exception as e:
            # Fallback to plain text if markdown rendering fails
            console.print(f"⚠️  Markdown rendering failed: {str(e)}", style="yellow")
            response_panel = Panel(
                markdown_text,
                title="🤖 AI Agent Response (Plain Text)",
                border_style="green",
                padding=(1, 2),
            )
            console.print(response_panel)

    def chat_loop(self):
        """Main chat loop with beautiful formatting"""
        console.print(
            "\n[bold green]💬 Chat session started! Type 'help' for commands or start asking questions.[/bold green]"
        )
        console.print("=" * 80)

        while True:
            try:
                # Get user input with rich prompt
                message = Prompt.ask("\n[bold cyan]🤠 You[/bold cyan]")

                # Handle commands
                if message.lower() in ["quit", "exit", "bye"]:
                    console.print(
                        "\n👋 [bold green]Goodbye![/bold green] Thanks for using Draft 'n' Pray! Hope your mail got seen 👀"
                    )
                    break
                elif message.lower() == "help":
                    self.print_help()
                    continue
                elif message.lower() == "tools":
                    self.print_tools_info()
                    continue
                elif message.lower() == "cv":
                    self.show_cv_status()
                    continue
                elif message.lower() == "apikeys":
                    self.show_api_keys_status()
                    continue
                elif not message.strip():
                    continue

                # Process with AI agent
                console.print("\n🤖 [bold yellow]Agent is thinking...[/bold yellow]")

                with console.status("[bold green]Processing...", spinner="dots"):
                    response = self.agent.invoke(
                        {"messages": [{"role": "user", "content": message}]},
                        config=config,
                    )
                    agent_response = response["messages"][-1].content

                # Render the response as markdown
                self.render_markdown_response(agent_response)

            except KeyboardInterrupt:
                console.print("\n\n⚠️  [yellow]Interrupted by user[/yellow]")
                if Confirm.ask("Do you want to exit?"):
                    break
                continue
            except Exception as e:
                error_panel = Panel(
                    f"❌ Error: {str(e)}",
                    title="Error",
                    border_style="red",
                    padding=(1, 2),
                )
                console.print(error_panel)
                continue

    def run(self):
        """Main application runner"""
        try:
            # Display banner and header
            self.print_banner()
            self.print_header()

            # Check environment
            if not self.check_environment():
                console.print(
                    "\n❌ [bold red]Environment check failed. Please fix the issues above.[/bold red]"
                )
                sys.exit(1)

            # Initialize agent
            if not self.initialize_agent():
                console.print(
                    "\n❌ [bold red]Failed to initialize AI Agent. Exiting.[/bold red]"
                )
                sys.exit(1)

            # Initialize CV knowledge base
            if not self.initialize_cv_knowledge_base():
                console.print(
                    "\n⚠️  [yellow]CV knowledge base not available. Agent will work without CV access.[/yellow]"
                )

            # Show tools information
            self.print_tools_info()

            # Start chat loop
            self.chat_loop()

        except Exception as e:
            console.print(f"\n❌ [bold red]Fatal error: {str(e)}[/bold red]")
            sys.exit(1)
        finally:
            # Offer to save API keys to .env file
            self.save_api_keys_to_env_file()


@app.command()
def main():
    """Start the Draft 'n' Pray Agent"""
    agent_cli = AgentCLI()
    agent_cli.run()


@app.command()
def setup_keys():
    """Setup API keys interactively"""
    agent_cli = AgentCLI()
    console.print("[bold cyan]🔑 API Key Setup[/bold cyan]")
    console.print("This will help you configure your API keys for the application.\n")

    if agent_cli.check_and_setup_environment():
        agent_cli.save_api_keys_to_env_file()
        console.print(
            "\n✅ [bold green]API key setup completed successfully![/bold green]"
        )
        console.print(
            "💡 You can now run the main application with: [cyan]python agent.py[/cyan]"
        )
    else:
        console.print("\n❌ [bold red]API key setup failed.[/bold red]")
        sys.exit(1)


@app.command()
def check_keys():
    """Check current API key status"""
    agent_cli = AgentCLI()
    console.print("[bold cyan]🔍 API Key Status Check[/bold cyan]\n")
    agent_cli.show_api_keys_status()


@app.command()
def version():
    """Show version information"""
    console.print("[bold blue]Draft 'n' Pray[/bold blue]")
    console.print("[cyan]Write. Send. Hope. Repeat. (Now with AI)[/cyan]")


if __name__ == "__main__":
    app()
