#!/usr/bin/env python3
"""
🚀 MOST ADVANCED CLI - Multi-model AI, RAG, Real-time, Analytics
Enterprise-grade command line interface with advanced features
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import websockets

from advanced_ai_engine import AdvancedAIEngine, AIProvider, create_advanced_ai_engine

console = Console()

# 🚀 ADVANCED CLI CONTEXT
class AdvancedCLIContext:
    def __init__(self):
        self.ai_engine = create_advanced_ai_engine()
        self.current_session = None
        self.websocket = None
        self.config = {}

@click.group()
@click.version_option(version="2.0.0", prog_name="Advanced AI Assistant")
@click.pass_context
def cli(ctx):
    """🚀 MOST ADVANCED AI ASSISTANT CLI
    
    Enterprise-grade AI with Multi-model support, RAG, Real-time streaming, and Advanced Analytics
    """
    ctx.ensure_object(dict)
    ctx.obj = AdvancedCLIContext()
    
    console.print(Panel.fit(
        "[bold blue]🚀 MOST ADVANCED AI ASSISTANT CLI[/bold blue]\n"
        "[green]Multi-model • RAG • Real-time • Analytics[/green]",
        border_style="blue"
    ))

@cli.command()
@click.option('--prompt', '-p', required=True, help='Text prompt for generation')
@click.option('--provider', '-m', type=click.Choice(['gemini', 'openai', 'anthropic']), 
              default='gemini', help='AI provider to use')
@click.option('--use-rag/--no-rag', default=True, help='Use RAG enhancement')
@click.option('--stream/--no-stream', default=False, help='Stream response')
@click.option('--temperature', '-t', type=float, default=0.7, help='Creativity level (0.0-1.0)')
@click.option('--max-tokens', type=int, default=8192, help='Maximum tokens')
@click.option('--session-id', help='Session ID for context')
@click.pass_obj
def generate(ctx: AdvancedCLIContext, prompt, provider, use_rag, stream, temperature, max_tokens, session_id):
    """🚀 ADVANCED TEXT GENERATION with Multi-model and RAG"""
    
    async def run_generation():
        try:
            # Create session if not provided
            if not session_id:
                session_id = await ctx.ai_engine.create_session()
                console.print(f"[green]✅ Created session: {session_id}[/green]")
            
            provider_enum = AIProvider(provider)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"🧠 Generating with {provider.upper()}...", total=None)
                
                if stream:
                    console.print(f"\n[bold blue]🚀 Streaming Response:[/bold blue]")
                    console.print("─" * 50)
                    
                    async for chunk in ctx.ai_engine.enhanced_generate(
                        prompt=prompt,
                        session_id=session_id,
                        provider=provider_enum,
                        use_rag=use_rag,
                        stream=True,
                        temperature=temperature,
                        max_tokens=max_tokens
                    ):
                        console.print(chunk, end="")
                    
                    console.print("\n" + "─" * 50)
                else:
                    response = await ctx.ai_engine.enhanced_generate(
                        prompt=prompt,
                        session_id=session_id,
                        provider=provider_enum,
                        use_rag=use_rag,
                        stream=False,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    progress.remove_task(task)
                    
                    # Display response
                    console.print(Panel(
                        response,
                        title=f"🚀 {provider.upper()} Response",
                        border_style="green"
                    ))
                    
                    # Display metadata
                    metadata_table = Table(title="📊 Generation Metadata")
                    metadata_table.add_column("Metric", style="cyan")
                    metadata_table.add_column("Value", style="green")
                    
                    metadata_table.add_row("Provider", provider.upper())
                    metadata_table.add_row("RAG Enabled", "✅" if use_rag else "❌")
                    metadata_table.add_row("Temperature", str(temperature))
                    metadata_table.add_row("Max Tokens", str(max_tokens))
                    metadata_table.add_row("Session ID", session_id)
                    metadata_table.add_row("Response Length", str(len(response)))
                    
                    console.print(metadata_table)
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_generation())

@cli.command()
@click.option('--session-id', help='Session ID (will create new if not provided)')
@click.option('--provider', '-m', type=click.Choice(['gemini', 'openai', 'anthropic']), 
              default='gemini', help='AI provider to use')
@click.option('--use-memory/--no-memory', default=True, help='Use conversation memory')
@click.pass_obj
def chat(ctx: AdvancedCLIContext, session_id, provider, use_memory):
    """🚀 ADVANCED INTERACTIVE CHAT with memory and analytics"""
    
    async def run_chat():
        try:
            # Create session if not provided
            if not session_id:
                session_id = await ctx.ai_engine.create_session()
            
            ctx.current_session = session_id
            provider_enum = AIProvider(provider)
            
            console.print(Panel(
                f"[bold green]🚀 Advanced Chat Session Started[/bold green]\n"
                f"Session ID: {session_id}\n"
                f"Provider: {provider.upper()}\n"
                f"Memory: {'✅ Enabled' if use_memory else '❌ Disabled'}\n"
                f"Type 'quit' to exit, '/help' for commands",
                border_style="green"
            ))
            
            while True:
                try:
                    # Get user input
                    user_input = console.input("\n[bold blue]You:[/bold blue] ")
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if user_input.startswith('/'):
                        await handle_chat_command(ctx, user_input, session_id)
                        continue
                    
                    # Process chat message
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("🧠 Processing...", total=None)
                        
                        result = await ctx.ai_engine.advanced_chat(
                            message=user_input,
                            session_id=session_id,
                            provider=provider_enum,
                            use_memory=use_memory
                        )
                        
                        progress.remove_task(task)
                    
                    # Display response
                    console.print(f"\n[bold green]🤖 Assistant:[/bold green] {result['response']}")
                    
                    # Display analytics
                    if result.get('sentiment') is not None:
                        sentiment_color = "green" if result['sentiment'] > 0 else "red" if result['sentiment'] < 0 else "yellow"
                        console.print(f"[{sentiment_color}]📊 Sentiment: {result['sentiment']:.2f}[/{sentiment_color}]")
                    
                    if result.get('topics'):
                        console.print(f"[cyan]🏷️  Topics: {', '.join(result['topics'])}[/cyan]")
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Chat interrupted by user[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]❌ Chat error: {e}[/red]")
            
            console.print("[green]👋 Chat session ended[/green]")
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_chat())

async def handle_chat_command(ctx: AdvancedCLIContext, command: str, session_id: str):
    """Handle special chat commands"""
    
    if command == '/help':
        help_table = Table(title="🚀 Advanced Chat Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/stats", "Show session statistics")
        help_table.add_row("/analytics", "Show analytics dashboard")
        help_table.add_row("/clear", "Clear conversation history")
        help_table.add_row("/export", "Export conversation")
        help_table.add_row("/switch <provider>", "Switch AI provider")
        
        console.print(help_table)
    
    elif command == '/stats':
        context = ctx.ai_engine.conversations.get(session_id)
        if context:
            stats_table = Table(title="📊 Session Statistics")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            
            stats_table.add_row("Messages", str(len(context.messages)))
            stats_table.add_row("Created", context.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            stats_table.add_row("Updated", context.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            stats_table.add_row("Topics", str(len(set(context.topics))))
            
            if context.sentiment_history:
                avg_sentiment = sum(context.sentiment_history) / len(context.sentiment_history)
                stats_table.add_row("Avg Sentiment", f"{avg_sentiment:.2f}")
            
            console.print(stats_table)
    
    elif command == '/analytics':
        dashboard = await ctx.ai_engine.get_analytics_dashboard()
        console.print(Panel(
            json.dumps(dashboard, indent=2),
            title="📊 Analytics Dashboard",
            border_style="blue"
        ))
    
    elif command == '/clear':
        context = ctx.ai_engine.conversations.get(session_id)
        if context:
            context.messages.clear()
            context.sentiment_history.clear()
            context.topics.clear()
            console.print("[green]✅ Conversation history cleared[/green]")
    
    elif command.startswith('/switch'):
        parts = command.split()
        if len(parts) > 1:
            new_provider = parts[1]
            console.print(f"[green]✅ Switched to {new_provider.upper()}[/green]")
        else:
            console.print("[red]❌ Usage: /switch <provider>[/red]")

@cli.command()
@click.option('--providers', '-p', multiple=True, 
              type=click.Choice(['gemini', 'openai', 'anthropic']),
              default=['gemini'], help='AI providers to use')
@click.option('--prompt', required=True, help='Prompt for all models')
@click.option('--consensus/--no-consensus', default=False, help='Generate consensus response')
@click.pass_obj
def multi_model(ctx: AdvancedCLIContext, providers, prompt, consensus):
    """🚀 MULTI-MODEL GENERATION with consensus"""
    
    async def run_multi_model():
        try:
            provider_enums = [AIProvider(p) for p in providers]
            results = {}
            
            console.print(f"[bold blue]🚀 Multi-Model Generation[/bold blue]")
            console.print(f"Providers: {', '.join([p.upper() for p in providers])}")
            console.print(f"Consensus: {'✅ Enabled' if consensus else '❌ Disabled'}")
            console.print("─" * 50)
            
            # Generate from each provider
            for provider_enum in provider_enums:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(f"🧠 {provider_enum.value.upper()}...", total=None)
                    
                    response = await ctx.ai_engine.enhanced_generate(
                        prompt=prompt,
                        provider=provider_enum,
                        use_rag=True
                    )
                    
                    results[provider_enum.value] = response
                    progress.remove_task(task)
                
                console.print(Panel(
                    response,
                    title=f"🤖 {provider_enum.value.upper()} Response",
                    border_style="green"
                ))
            
            # Generate consensus if requested
            if consensus and len(results) > 1:
                console.print("\n[bold yellow]🧠 Generating Consensus...[/bold yellow]")
                
                consensus_prompt = f"Based on these responses: {json.dumps(results)}, provide a consensus answer to: {prompt}"
                consensus_response = await ctx.ai_engine.enhanced_generate(consensus_prompt)
                
                console.print(Panel(
                    consensus_response,
                    title="🎯 Consensus Response",
                    border_style="yellow"
                ))
            
            # Summary table
            summary_table = Table(title="📊 Multi-Model Summary")
            summary_table.add_column("Provider", style="cyan")
            summary_table.add_column("Response Length", style="green")
            summary_table.add_column("Status", style="yellow")
            
            for provider, response in results.items():
                summary_table.add_row(
                    provider.upper(),
                    str(len(response)),
                    "✅ Success"
                )
            
            console.print(summary_table)
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_multi_model())

@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--k', type=int, default=5, help='Number of results')
@click.option('--threshold', type=float, default=0.5, help='Similarity threshold')
@click.pass_obj
def rag_search(ctx: AdvancedCLIContext, query, k, threshold):
    """🚀 RAG VECTOR DATABASE SEARCH"""
    
    try:
        results = ctx.ai_engine.vector_db.search(query, k)
        
        # Filter by threshold
        filtered_results = [r for r in results if r["score"] >= threshold]
        
        console.print(Panel(
            f"[bold blue]🔍 RAG Search Results[/bold blue]\n"
            f"Query: {query}\n"
            f"Found: {len(results)} total, {len(filtered_results)} above threshold",
            border_style="blue"
        ))
        
        if filtered_results:
            results_table = Table(title="📊 Search Results")
            results_table.add_column("Score", style="green")
            results_table.add_column("Text", style="white")
            results_table.add_column("Metadata", style="cyan")
            
            for result in filtered_results:
                results_table.add_row(
                    f"{result['score']:.3f}",
                    result['text'][:100] + "..." if len(result['text']) > 100 else result['text'],
                    json.dumps(result.get('metadata', {}))[:50] + "..."
                )
            
            console.print(results_table)
        else:
            console.print("[yellow]No results found above threshold[/yellow]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

@cli.command()
@click.option('--file-path', '-f', required=True, type=click.Path(exists=True), help='File to add')
@click.option('--metadata', '-m', default='{}', help='Metadata as JSON string')
@click.pass_obj
def rag_add(ctx: AdvancedCLIContext, file_path, metadata):
    """🚀 ADD DOCUMENT TO RAG DATABASE"""
    
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse metadata
        metadata_dict = json.loads(metadata)
        metadata_dict.update({
            "file_path": str(file_path),
            "added_at": datetime.now().isoformat(),
            "file_size": len(content)
        })
        
        # Add to RAG database
        ctx.ai_engine.vector_db.add_document(content, metadata_dict)
        
        console.print(Panel(
            f"[bold green]✅ Document Added to RAG Database[/bold green]\n"
            f"File: {file_path}\n"
            f"Size: {len(content)} characters\n"
            f"Lines: {content.count(chr(10)) + 1}\n"
            f"Words: {len(content.split())}",
            border_style="green"
        ))
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

@cli.command()
@click.pass_obj
def analytics(ctx: AdvancedCLIContext):
    """🚀 ADVANCED ANALYTICS DASHBOARD"""
    
    async def show_analytics():
        try:
            dashboard = await ctx.ai_engine.get_analytics_dashboard()
            
            # System metrics
            if 'system_metrics' in dashboard:
                metrics_table = Table(title="📊 System Metrics")
                metrics_table.add_column("Metric", style="cyan")
                metrics_table.add_column("Value", style="green")
                
                for key, value in dashboard['system_metrics'].items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            metrics_table.add_row(f"{key}.{sub_key}", str(sub_value))
                    else:
                        metrics_table.add_row(key, str(value))
                
                console.print(metrics_table)
            
            # Session stats
            if 'session_stats' in dashboard:
                session_table = Table(title="👥 Session Statistics")
                session_table.add_column("Metric", style="cyan")
                session_table.add_column("Value", style="green")
                
                for key, value in dashboard['session_stats'].items():
                    session_table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(session_table)
            
            # Vector DB stats
            if 'vector_db_stats' in dashboard:
                vector_table = Table(title="🗄️ Vector Database")
                vector_table.add_column("Metric", style="cyan")
                vector_table.add_column("Value", style="green")
                
                for key, value in dashboard['vector_db_stats'].items():
                    vector_table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(vector_table)
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(show_analytics())

@cli.command()
@click.pass_obj
def health(ctx: AdvancedCLIContext):
    """🚀 COMPREHENSIVE HEALTH CHECK"""
    
    async def check_health():
        try:
            health_data = await ctx.ai_engine.health_check()
            
            # Overall status
            status_color = "green" if health_data["status"] == "healthy" else "yellow" if health_data["status"] == "degraded" else "red"
            
            console.print(Panel(
                f"[bold {status_color}]{health_data['status'].upper()}[/bold {status_color}]\n"
                f"Timestamp: {health_data['timestamp']}",
                title="🏥 System Health",
                border_style=status_color
            ))
            
            # Component status
            if 'components' in health_data:
                health_table = Table(title="🔧 Component Status")
                health_table.add_column("Component", style="cyan")
                health_table.add_column("Status", style="white")
                
                for component, status in health_data['components'].items():
                    status_icon = "✅" if status == "healthy" else "⚠️" if "degraded" in status else "❌"
                    health_table.add_row(component.replace('_', ' ').title(), f"{status_icon} {status}")
                
                console.print(health_table)
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(check_health())

@cli.command()
@click.option('--host', default='localhost', help='WebSocket host')
@click.option('--port', default=12000, help='WebSocket port')
@click.option('--session-id', help='Session ID')
@click.pass_obj
def realtime(ctx: AdvancedCLIContext, host, port, session_id):
    """🚀 REAL-TIME WEBSOCKET COMMUNICATION"""
    
    async def connect_websocket():
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            uri = f"ws://{host}:{port}/ws/{session_id}"
            
            console.print(Panel(
                f"[bold blue]🌐 Connecting to Real-time WebSocket[/bold blue]\n"
                f"URI: {uri}\n"
                f"Session: {session_id}\n"
                f"Type 'quit' to exit",
                border_style="blue"
            ))
            
            async with websockets.connect(uri) as websocket:
                console.print("[green]✅ Connected to WebSocket[/green]")
                
                # Start receiving messages
                async def receive_messages():
                    try:
                        async for message in websocket:
                            data = json.loads(message)
                            
                            if data["type"] == "chat_chunk":
                                console.print(data["chunk"], end="")
                            elif data["type"] == "chat_complete":
                                console.print("\n[green]✅ Response complete[/green]")
                            elif data["type"] == "analytics_update":
                                console.print(f"[cyan]📊 Analytics update received[/cyan]")
                    except Exception as e:
                        console.print(f"[red]❌ Receive error: {e}[/red]")
                
                # Start background task for receiving
                receive_task = asyncio.create_task(receive_messages())
                
                # Main input loop
                while True:
                    try:
                        user_input = await asyncio.get_event_loop().run_in_executor(
                            None, console.input, "\n[bold blue]You:[/bold blue] "
                        )
                        
                        if user_input.lower() in ['quit', 'exit', 'q']:
                            break
                        
                        # Send message
                        message = {
                            "type": "chat",
                            "message": user_input,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        await websocket.send(json.dumps(message))
                        console.print("[yellow]🚀 Message sent, waiting for response...[/yellow]")
                    
                    except KeyboardInterrupt:
                        break
                
                receive_task.cancel()
                console.print("[green]👋 WebSocket connection closed[/green]")
        
        except Exception as e:
            console.print(f"[red]❌ WebSocket error: {e}[/red]")
    
    asyncio.run(connect_websocket())

if __name__ == '__main__':
    cli()