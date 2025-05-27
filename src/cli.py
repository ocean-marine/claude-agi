#!/usr/bin/env python3
"""Claude AGI unified CLI tool

Provides integrated command line interface for AGI tools.
Basic search and text analysis functionality with minimal configuration.

Usage:
    $ python cli.py search "Python programming"
    $ python cli.py analyze sample.txt
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import local modules
try:
    from brave_search import BraveSearchClient, SearchConfig
    from text_analyzer import TextAnalyzer, AnalysisConfig, CountType
except ImportError as e:
    logger.error(f"Module import error: {e}")
    logger.error("Please ensure all dependencies are installed.")
    sys.exit(1)


class AGIToolCLI:
    """AGI unified CLI controller"""
    
    def __init__(self):
        """Initialize CLI"""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create main parser with subcommands"""
        parser = argparse.ArgumentParser(
            description="Claude AGI unified CLI tool",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(
            dest='tool',
            help='Available tools',
            metavar='TOOL'
        )
        
        # Search tool
        search_parser = subparsers.add_parser(
            'search',
            help='Search using Brave Search API'
        )
        search_parser.add_argument('query', help='Search query')
        search_parser.add_argument('-c', '--count', type=int, default=10, help='Number of results')
        
        # Analysis tool
        analyze_parser = subparsers.add_parser(
            'analyze',
            help='Text analysis and character counting'
        )
        analyze_parser.add_argument('file_path', type=Path, help='File to analyze')
        
        return parser
    
    def run(self, args=None):
        """Execute CLI"""
        parsed_args = self.parser.parse_args(args)
        
        try:
            if parsed_args.tool == 'search':
                self._run_search(parsed_args)
            elif parsed_args.tool == 'analyze':
                self._run_analyze(parsed_args)
            else:
                self.parser.print_help()
        
        except KeyboardInterrupt:
            logger.info("Operation interrupted.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            sys.exit(1)
    
    def _run_search(self, args):
        """Execute search tool"""
        client = BraveSearchClient()
        config = SearchConfig(query=args.query, count=args.count)
        
        logger.info(f"Searching for '{config.query}'...")
        results = client.search(config)
        
        if results:
            formatted_results = client.format_results(results, "text")
            print(formatted_results)
        else:
            logger.error("Search failed.")
            sys.exit(1)
    
    def _run_analyze(self, args):
        """Execute text analysis tool"""
        analyzer = TextAnalyzer()
        config = AnalysisConfig(file_path=args.file_path, count_type=CountType.DETAILED)
        
        results = analyzer.analyze_with_config(config)
        formatted_results = analyzer.format_results(results)
        print(formatted_results)


def main():
    """Main function"""
    cli = AGIToolCLI()
    cli.run()


if __name__ == "__main__":
    main()