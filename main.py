"""Main entry point for Gemini AI Assistant."""

import sys
import argparse
from typing import Optional

from config import config
from utils import setup_logging


def main():
    """Main entry point with argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="Gemini AI Assistant - AI-powered text generation and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py cli generate --prompt "Write a story about AI"
  python main.py cli chat
  python main.py web
  python main.py api
  python main.py test
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'{config.APP_NAME} v{config.APP_VERSION}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # CLI command
    cli_parser = subparsers.add_parser('cli', help='Run CLI interface')
    cli_parser.add_argument('cli_command', nargs='*', help='CLI command and arguments')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Run Flask web application')
    web_parser.add_argument('--host', default=config.HOST, help='Host to bind to')
    web_parser.add_argument('--port', type=int, default=config.PORT, help='Port to bind to')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Run FastAPI application')
    api_parser.add_argument('--host', default=config.HOST, help='Host to bind to')
    api_parser.add_argument('--port', type=int, default=config.PORT, help='Port to bind to')
    api_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--coverage', action='store_true', help='Run with coverage')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(config.LOG_LEVEL)
    
    # Validate configuration
    if not config.validate() and args.command not in ['config', 'test']:
        print("Error: Invalid configuration. Please check your API key.")
        print("Run 'python main.py config' to see current configuration.")
        sys.exit(1)
    
    if args.command == 'cli':
        run_cli(args.cli_command)
    elif args.command == 'web':
        run_web_app(args.host, args.port, args.debug)
    elif args.command == 'api':
        run_fastapi_app(args.host, args.port, args.reload)
    elif args.command == 'test':
        run_tests(args.coverage, args.verbose)
    elif args.command == 'config':
        show_config()
    else:
        parser.print_help()


def run_cli(cli_args: Optional[list] = None):
    """Run the CLI interface."""
    try:
        from cli import cli
        
        # If no CLI args provided, run interactive mode
        if not cli_args:
            cli_args = []
        
        # Modify sys.argv to pass arguments to click
        original_argv = sys.argv
        sys.argv = ['cli'] + cli_args
        
        try:
            cli(standalone_mode=False)
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv
            
    except ImportError as e:
        print(f"Error importing CLI module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running CLI: {e}")
        sys.exit(1)


def run_web_app(host: str, port: int, debug: bool):
    """Run the Flask web application."""
    try:
        from web_app import app, create_templates
        
        print(f"Starting Flask web application...")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {debug}")
        print(f"URL: http://{host}:{port}")
        
        # Create templates if they don't exist
        create_templates()
        
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        print(f"Error importing web app module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running web app: {e}")
        sys.exit(1)


def run_fastapi_app(host: str, port: int, reload: bool):
    """Run the FastAPI application."""
    try:
        import uvicorn
        
        print(f"Starting FastAPI application...")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Reload: {reload}")
        print(f"URL: http://{host}:{port}")
        print(f"Docs: http://{host}:{port}/docs")
        
        uvicorn.run(
            "fastapi_app:app",
            host=host,
            port=port,
            reload=reload,
            log_level=config.LOG_LEVEL.lower()
        )
        
    except ImportError as e:
        print(f"Error importing FastAPI or uvicorn: {e}")
        print("Please install FastAPI and uvicorn: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"Error running FastAPI app: {e}")
        sys.exit(1)


def run_tests(coverage: bool, verbose: bool):
    """Run the test suite."""
    try:
        import pytest
        
        args = []
        
        if coverage:
            args.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
        
        if verbose:
            args.append('-v')
        
        args.append('tests/')
        
        print("Running tests...")
        exit_code = pytest.main(args)
        
        if coverage:
            print("\nCoverage report generated in htmlcov/")
        
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"Error importing pytest: {e}")
        print("Please install pytest: pip install pytest pytest-cov")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


def show_config():
    """Show current configuration."""
    print(f"\n{config.APP_NAME} Configuration")
    print("=" * 40)
    print(f"App Name: {config.APP_NAME}")
    print(f"Version: {config.APP_VERSION}")
    print(f"Model: {config.MODEL}")
    print(f"API Key: {'*' * 20}...{config.API_KEY[-4:] if config.API_KEY else 'Not set'}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"Log Level: {config.LOG_LEVEL}")
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print(f"Temperature: {config.TEMPERATURE}")
    print(f"Max Tokens: {config.MAX_TOKENS}")
    print(f"Top P: {config.TOP_P}")
    print(f"Top K: {config.TOP_K}")
    
    print("\nValidation:")
    if config.validate():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration is invalid")
        print("  - Check API key configuration")
    
    print(f"\nConfiguration file: .env")
    print(f"Example file: .env.example")


if __name__ == '__main__':
    main()