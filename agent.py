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

    def print_banner(self):
        banner_text = """

    +============================================================================================+
    |██████╗ ██████╗  █████╗ ███████╗████████╗    ███╗   ██╗    ██████╗ ██████╗  █████╗ ██╗   ██╗|
    |██╔══██╗██╔══██╗██╔══██╗██╔════╝╚══██╔══╝    ████╗  ██║    ██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝|
    |██║  ██║██████╔╝███████║█████╗     ██║       ██╔██╗ ██║    ██████╔╝██████╔╝███████║ ╚████╔╝ |
    |██║  ██║██╔══██╗██╔══██║██╔══╝     ██║       ██║╚██╗██║    ██╔═══╝ ██╔══██╗██╔══██║  ╚██╔╝  |
    |██████╔╝██║  ██║██║  ██║██║        ██║       ██║ ╚████║    ██║     ██║  ██║██║  ██║   ██║   |
    |╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝       ╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   |
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

    def check_environment(self):
        console.print("🔍 Checking environment configuration...", style="yellow")

        required_vars = ["GOOGLE_API_KEY", "FIRECRAWL_API_KEY"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            console.print(
                f"❌ Missing required environment variables: {', '.join(missing_vars)}",
                style="red",
            )
            console.print(
                "💡 Please create a .env file with the required API keys", style="cyan"
            )
            return False

        console.print("✅ Environment configuration valid", style="green")
        return True

    def initialize_agent(self):
        try:
            with console.status("[bold green]Initializing AI Agent...", spinner="dots"):
                llm = get_model()
                self.agent = create_react_agent(
                    model=llm,
                    tools=TOOLS,
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
                if initialize_vectorstore_with_cv(self.cv_path):
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
• [green]quit[/green], [green]exit[/green], [green]bye[/green] - Exit the application

[bold cyan]Example Queries:[/bold cyan]
• "What are my technical skills?"
• "Tell me about my work experience"
• "Crawl https://example.com and summarize it"
• "What programming languages do I know?"
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


@app.command()
def main():
    """Start the Draft 'n' Pray Agent"""
    agent_cli = AgentCLI()
    agent_cli.run()


@app.command()
def version():
    """Show version information"""
    console.print("[bold blue]Draft 'n' Pray[/bold blue]")
    console.print("[cyan]Write. Send. Hope. Repeat. (Now with AI)[/cyan]")


if __name__ == "__main__":
    app()
