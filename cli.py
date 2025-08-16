"""Command Line Interface for Gemini AI Assistant."""

import click
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.table import Table

from client_factory import get_client
from utils import read_file, write_file, setup_logging, format_response
from config import config

console = Console()
logger = setup_logging(config.LOG_LEVEL)


@click.group()
@click.version_option(version=config.APP_VERSION)
def cli():
    """Gemini AI Assistant - Command Line Interface"""
    if not config.validate():
        console.print("[red]Error: Invalid API key. Please check your configuration.[/red]")
        sys.exit(1)


@cli.command()
@click.option('--prompt', '-p', help='Text prompt to generate from')
@click.option('--file', '-f', help='File to read prompt from')
@click.option('--output', '-o', help='Output file to save response')
@click.option('--temperature', '-t', type=float, help='Temperature for generation (0.0-1.0)')
@click.option('--max-tokens', '-m', type=int, help='Maximum tokens to generate')
def generate(prompt: Optional[str], file: Optional[str], output: Optional[str], 
            temperature: Optional[float], max_tokens: Optional[int]):
    """Generate text using Gemini API."""
    
    if not prompt and not file:
        prompt = Prompt.ask("Enter your prompt")
    
    if file:
        try:
            prompt = read_file(file)
            console.print(f"[green]Loaded prompt from: {file}[/green]")
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return
    
    try:
        client = get_client()
        
        with console.status("[bold green]Generating response..."):
            response = client.generate_text(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        # Display response
        console.print("\n" + "="*50)
        console.print(Panel(Markdown(response.text), title="Generated Response"))
        
        # Show metadata if available
        if response.usage_metadata:
            table = Table(title="Usage Metadata")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in response.usage_metadata.items():
                table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(table)
        
        # Save to file if requested
        if output:
            if write_file(output, response.text):
                console.print(f"[green]Response saved to: {output}[/green]")
            else:
                console.print(f"[red]Failed to save response to: {output}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--system', '-s', help='System prompt for the chat session')
def chat(system: Optional[str]):
    """Start an interactive chat session."""
    
    try:
        client = get_client()
        
        console.print(Panel(
            f"[bold green]{config.APP_NAME}[/bold green]\n"
            f"Interactive Chat Mode\n"
            f"Type 'quit', 'exit', or 'bye' to end the session\n"
            f"Type 'clear' to clear chat history\n"
            f"Type 'history' to view chat history",
            title="Chat Session Started"
        ))
        
        if system:
            console.print(f"[yellow]System prompt set: {system}[/yellow]")
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == 'clear':
                    client.clear_chat_history()
                    console.print("[green]Chat history cleared.[/green]")
                    continue
                
                if user_input.lower() == 'history':
                    history = client.get_chat_history()
                    if not history:
                        console.print("[yellow]No chat history.[/yellow]")
                    else:
                        for i, msg in enumerate(history, 1):
                            role_color = "blue" if msg.role == "user" else "green"
                            console.print(f"[{role_color}]{i}. {msg.role.title()}:[/{role_color}] {msg.content[:100]}...")
                    continue
                
                with console.status("[bold green]Thinking..."):
                    response = client.chat(user_input, system_prompt=system if system and not client.chat_history else None)
                
                console.print(f"\n[bold green]Assistant:[/bold green]")
                console.print(Panel(Markdown(response), border_style="green"))
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Chat interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    except Exception as e:
        console.print(f"[red]Failed to start chat: {e}[/red]")


@cli.command()
@click.argument('file_path')
@click.option('--task', '-t', default='summarize', 
              type=click.Choice(['summarize', 'analyze', 'extract_info', 'questions']),
              help='Task to perform on the file')
@click.option('--output', '-o', help='Output file to save results')
def process_file(file_path: str, task: str, output: Optional[str]):
    """Process a file with AI analysis."""
    
    try:
        content = read_file(file_path)
        console.print(f"[green]Loaded file: {file_path}[/green]")
        
        client = get_client()
        
        with console.status(f"[bold green]Processing file with task: {task}..."):
            result = client.process_file_content(content, task)
        
        console.print(f"\n[bold cyan]Task: {task.title()}[/bold cyan]")
        console.print(Panel(Markdown(result), title=f"Results for {file_path}"))
        
        if output:
            if write_file(output, result):
                console.print(f"[green]Results saved to: {output}[/green]")
            else:
                console.print(f"[red]Failed to save results to: {output}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('text')
@click.option('--type', '-t', default='general',
              type=click.Choice(['general', 'sentiment', 'summary', 'keywords', 'translation']),
              help='Type of analysis to perform')
def analyze(text: str, type: str):
    """Analyze text with specified analysis type."""
    
    try:
        client = get_client()
        
        with console.status(f"[bold green]Analyzing text ({type})..."):
            result = client.analyze_text(text, type)
        
        console.print(f"\n[bold cyan]Analysis Type: {type.title()}[/bold cyan]")
        console.print(Panel(Markdown(result), title="Analysis Results"))
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def config_info():
    """Display current configuration."""
    
    table = Table(title="Configuration Information")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("App Name", config.APP_NAME)
    table.add_row("Version", config.APP_VERSION)
    table.add_row("Model", config.MODEL)
    table.add_row("API Key", f"{'*' * 20}...{config.API_KEY[-4:]}" if config.API_KEY else "Not set")
    table.add_row("Debug Mode", str(config.DEBUG))
    table.add_row("Log Level", config.LOG_LEVEL)
    table.add_row("Host", config.HOST)
    table.add_row("Port", str(config.PORT))
    table.add_row("Temperature", str(config.TEMPERATURE))
    table.add_row("Max Tokens", str(config.MAX_TOKENS))
    
    console.print(table)
    
    # Validation status
    if config.validate():
        console.print("[green]✓ Configuration is valid[/green]")
    else:
        console.print("[red]✗ Configuration is invalid (check API key)[/red]")


if __name__ == '__main__':
    cli()