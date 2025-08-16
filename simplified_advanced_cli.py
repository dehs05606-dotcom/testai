#!/usr/bin/env python3
"""
🚀 SIMPLIFIED ADVANCED CLI
Working version of the most advanced CLI
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from simplified_advanced_engine import SimplifiedAdvancedAIEngine, AIProvider, create_simplified_advanced_ai_engine

console = Console()

class AdvancedCLIContext:
    def __init__(self):
        self.ai_engine = create_simplified_advanced_ai_engine()
        self.current_session = None

@click.group()
@click.version_option(version="2.0.0", prog_name="Advanced AI Assistant")
@click.pass_context
def cli(ctx):
    """🚀 MOST ADVANCED AI ASSISTANT CLI"""
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
@click.option('--session-id', help='Session ID for context')
@click.pass_obj
def generate(ctx: AdvancedCLIContext, prompt, provider, use_rag, session_id):
    """🚀 ADVANCED TEXT GENERATION"""
    
    async def run_generation():
        try:
            current_session_id = session_id
            if not current_session_id:
                current_session_id = await ctx.ai_engine.create_session()
                console.print(f"[green]✅ Created session: {current_session_id}[/green]")
            
            provider_enum = AIProvider(provider)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"🧠 Generating with {provider.upper()}...", total=None)
                
                response = await ctx.ai_engine.enhanced_generate(
                    prompt=prompt,
                    session_id=current_session_id,
                    provider=provider_enum,
                    use_rag=use_rag
                )
                
                progress.remove_task(task)
            
            console.print(Panel(
                response,
                title=f"🚀 {provider.upper()} Response",
                border_style="green"
            ))
            
            # Metadata
            metadata_table = Table(title="📊 Generation Metadata")
            metadata_table.add_column("Metric", style="cyan")
            metadata_table.add_column("Value", style="green")
            
            metadata_table.add_row("Provider", provider.upper())
            metadata_table.add_row("RAG Enabled", "✅" if use_rag else "❌")
            metadata_table.add_row("Session ID", current_session_id)
            metadata_table.add_row("Response Length", str(len(response)))
            
            console.print(metadata_table)
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_generation())

@cli.command()
@click.option('--session-id', help='Session ID')
@click.option('--provider', '-m', type=click.Choice(['gemini', 'openai', 'anthropic']), 
              default='gemini', help='AI provider to use')
@click.pass_obj
def chat(ctx: AdvancedCLIContext, session_id, provider):
    """🚀 ADVANCED INTERACTIVE CHAT"""
    
    async def run_chat():
        try:
            if not session_id:
                session_id = await ctx.ai_engine.create_session()
            
            ctx.current_session = session_id
            provider_enum = AIProvider(provider)
            
            console.print(Panel(
                f"[bold green]🚀 Advanced Chat Session Started[/bold green]\n"
                f"Session ID: {session_id}\n"
                f"Provider: {provider.upper()}\n"
                f"Type 'quit' to exit, '/help' for commands",
                border_style="green"
            ))
            
            while True:
                try:
                    user_input = console.input("\n[bold blue]You:[/bold blue] ")
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    if user_input.startswith('/'):
                        await handle_chat_command(ctx, user_input, session_id)
                        continue
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("🧠 Processing...", total=None)
                        
                        result = await ctx.ai_engine.advanced_chat(
                            message=user_input,
                            session_id=session_id,
                            provider=provider_enum
                        )
                        
                        progress.remove_task(task)
                    
                    console.print(f"\n[bold green]🤖 Assistant:[/bold green] {result['response']}")
                    
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
    """Handle chat commands"""
    
    if command == '/help':
        help_table = Table(title="🚀 Advanced Chat Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/stats", "Show session statistics")
        help_table.add_row("/analytics", "Show analytics dashboard")
        help_table.add_row("/clear", "Clear conversation history")
        
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

@cli.command()
@click.option('--providers', '-p', multiple=True, 
              type=click.Choice(['gemini', 'openai', 'anthropic']),
              default=['gemini'], help='AI providers to use')
@click.option('--prompt', required=True, help='Prompt for all models')
@click.pass_obj
def multi_model(ctx: AdvancedCLIContext, providers, prompt):
    """🚀 MULTI-MODEL GENERATION"""
    
    async def run_multi_model():
        try:
            provider_enums = [AIProvider(p) for p in providers]
            
            console.print(f"[bold blue]🚀 Multi-Model Generation[/bold blue]")
            console.print(f"Providers: {', '.join([p.upper() for p in providers])}")
            console.print("─" * 50)
            
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
                    
                    progress.remove_task(task)
                
                console.print(Panel(
                    response,
                    title=f"🤖 {provider_enum.value.upper()} Response",
                    border_style="green"
                ))
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_multi_model())

@cli.command()
@click.option('--query', '-q', required=True, help='Search query')
@click.option('--k', type=int, default=5, help='Number of results')
@click.pass_obj
def rag_search(ctx: AdvancedCLIContext, query, k):
    """🚀 RAG VECTOR DATABASE SEARCH"""
    
    try:
        results = ctx.ai_engine.vector_db.search(query, k)
        
        console.print(Panel(
            f"[bold blue]🔍 RAG Search Results[/bold blue]\n"
            f"Query: {query}\n"
            f"Found: {len(results)} results",
            border_style="blue"
        ))
        
        if results:
            results_table = Table(title="📊 Search Results")
            results_table.add_column("Score", style="green")
            results_table.add_column("Text", style="white")
            results_table.add_column("Metadata", style="cyan")
            
            for result in results:
                results_table.add_row(
                    f"{result['score']:.3f}",
                    result['text'][:100] + "..." if len(result['text']) > 100 else result['text'],
                    json.dumps(result.get('metadata', {}))[:50] + "..."
                )
            
            console.print(results_table)
        else:
            console.print("[yellow]No results found[/yellow]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

@cli.command()
@click.option('--text', '-t', required=True, help='Text to add')
@click.option('--metadata', '-m', default='{}', help='Metadata as JSON')
@click.pass_obj
def rag_add(ctx: AdvancedCLIContext, text, metadata):
    """🚀 ADD TEXT TO RAG DATABASE"""
    
    try:
        metadata_dict = json.loads(metadata)
        metadata_dict.update({
            "added_at": datetime.now().isoformat(),
            "text_length": len(text)
        })
        
        ctx.ai_engine.vector_db.add_document(text, metadata_dict)
        
        console.print(Panel(
            f"[bold green]✅ Text Added to RAG Database[/bold green]\n"
            f"Text: {text[:100]}{'...' if len(text) > 100 else ''}\n"
            f"Length: {len(text)} characters\n"
            f"Words: {len(text.split())}",
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
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(show_analytics())

@cli.command()
@click.option('--prompt', '-p', required=True, help='Prompt to enhance')
@click.option('--complexity', '-c', type=click.Choice(['basic', 'intermediate', 'advanced', 'expert', 'master']), 
              default='master', help='Target complexity level')
@click.option('--show-analysis/--no-analysis', default=True, help='Show detailed analysis')
@click.pass_obj
def enhance_prompt(ctx: AdvancedCLIContext, prompt, complexity, show_analysis):
    """🚀 ENHANCE PROMPT TO MASTER LEVEL"""
    
    async def run_enhancement():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"🧠 Enhancing to {complexity.upper()} level...", total=None)
                
                result = await ctx.ai_engine.enhance_prompt(
                    prompt=prompt,
                    complexity=complexity
                )
                
                progress.remove_task(task)
            
            # Display original prompt
            console.print(Panel(
                prompt,
                title="📝 Original Prompt",
                border_style="yellow"
            ))
            
            # Display enhanced prompt
            console.print(Panel(
                result["enhanced"],
                title=f"🚀 Enhanced {complexity.upper()} Level Prompt",
                border_style="green"
            ))
            
            # Display scores
            scores_table = Table(title="📊 Enhancement Scores")
            scores_table.add_column("Metric", style="cyan")
            scores_table.add_column("Score", style="green")
            
            scores_table.add_row("Professional Score", f"{result.get('professional_score', 0):.1f}%")
            scores_table.add_row("Complexity Score", f"{result.get('complexity_score', 0):.1f}%")
            scores_table.add_row("Processing Time", f"{result.get('processing_time', 0):.3f}s")
            scores_table.add_row("Enhancement Type", result.get('enhancement_type', 'unknown'))
            
            console.print(scores_table)
            
            # Show analysis if requested
            if show_analysis and 'analysis' in result:
                analysis = result['analysis']
                analysis_table = Table(title="🔍 Prompt Analysis")
                analysis_table.add_column("Aspect", style="cyan")
                analysis_table.add_column("Value", style="white")
                
                analysis_table.add_row("Category", analysis.get('category', 'unknown'))
                analysis_table.add_row("Domain", analysis.get('domain', 'unknown'))
                analysis_table.add_row("Intent", analysis.get('intent', 'unknown'))
                analysis_table.add_row("Tone", analysis.get('tone', 'unknown'))
                analysis_table.add_row("Keywords", ', '.join(analysis.get('keywords', [])[:5]))
                
                console.print(analysis_table)
            
            # Show enhancements applied
            if 'enhancements' in result and result['enhancements']:
                enhancements_table = Table(title="✨ Enhancements Applied")
                enhancements_table.add_column("Enhancement", style="green")
                
                for enhancement in result['enhancements'][:5]:
                    enhancements_table.add_row(enhancement)
                
                console.print(enhancements_table)
            
            # Show metadata
            if 'metadata' in result:
                metadata = result['metadata']
                console.print(f"\n[cyan]📈 Improvement Ratio: {metadata.get('improvement_ratio', 1):.1f}x[/cyan]")
                console.print(f"[cyan]📏 Length: {metadata.get('original_length', 0)} → {metadata.get('enhanced_length', 0)} characters[/cyan]")
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(run_enhancement())

@cli.command()
@click.pass_obj
def health(ctx: AdvancedCLIContext):
    """🚀 COMPREHENSIVE HEALTH CHECK"""
    
    async def check_health():
        try:
            health_data = await ctx.ai_engine.health_check()
            
            status_color = "green" if health_data["status"] == "healthy" else "yellow"
            
            console.print(Panel(
                f"[bold {status_color}]{health_data['status'].upper()}[/bold {status_color}]\n"
                f"Timestamp: {health_data['timestamp']}",
                title="🏥 System Health",
                border_style=status_color
            ))
            
            if 'components' in health_data:
                health_table = Table(title="🔧 Component Status")
                health_table.add_column("Component", style="cyan")
                health_table.add_column("Status", style="white")
                
                for component, status in health_data['components'].items():
                    status_icon = "✅" if status == "healthy" else "❌"
                    health_table.add_row(component.replace('_', ' ').title(), f"{status_icon} {status}")
                
                console.print(health_table)
        
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    
    asyncio.run(check_health())

if __name__ == '__main__':
    cli()