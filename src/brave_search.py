#!/usr/bin/env python3
"""Brave Search tool: High-performance search application

Provides search functionality using Brave Search API.
Simplified interface with essential features only.

Usage:
    $ python brave_search.py "Python programming" --count 5
    $ from brave_search import BraveSearchClient; client = BraveSearchClient()
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from brave import Brave
except ImportError:
    logger.error("Error: brave-search package not installed.")
    logger.error("Please run: pip install brave-search")
    sys.exit(1)


@dataclass(frozen=True)
class SearchConfig:
    """Search configuration data class"""
    query: str
    count: int = 10
    output_format: str = "text"
    output_file: Optional[Path] = None

    def __post_init__(self):
        if self.count <= 0:
            raise ValueError("count must be a positive integer")
        if self.output_format not in ["text", "json"]:
            raise ValueError("output_format must be 'text' or 'json'")


class BraveSearchClient:
    """Brave Search API client
    
    High-level interface for Brave Search API access.
    Handles error handling and result formatting.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize BraveSearchClient
        
        Args:
            api_key: Brave Search API key. If None, will get from environment
            
        Raises:
            ValueError: If API key is not set
            RuntimeError: If Brave API initialization fails
        """
        self._api_key = api_key or os.getenv('BRAVE_API_KEY')
        if not self._api_key:
            raise ValueError(
                "BRAVE_API_KEY environment variable not set or api_key not provided. "
                "Please set Brave Search API key as environment variable."
            )
        
        try:
            self.brave = Brave()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Brave Search API: {e}") from e
    
    def search(self, config: SearchConfig) -> Optional[dict[str, Any]]:
        """Execute search
        
        Args:
            config: Search configuration
            
        Returns:
            Search result dictionary. None if error occurs
            
        Raises:
            ValueError: For invalid search configuration
        """
        if not config.query.strip():
            raise ValueError("Search query is empty")
        
        try:
            results = self.brave.search(q=config.query, count=config.count)
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return None
    
    def format_results(self, results: Any, format_type: str = "text") -> str:
        """Format search results in specified format
        
        Args:
            results: Search results from Brave Search API
            format_type: Output format ('text' or 'json')
            
        Returns:
            Formatted result string
        """
        if not results or not hasattr(results, 'web_results'):
            return "No search results found."
        
        web_results = results.web_results
        if not web_results:
            return "No web search results found."
        
        if format_type == "json":
            return self._format_json(web_results)
        else:  # text
            return self._format_text(web_results)
    
    def _format_text(self, web_results: list[Any]) -> str:
        """Format as text"""
        lines = [f"=== Search Results ({len(web_results)} items) ===\n"]
        
        for i, result in enumerate(web_results, 1):
            lines.append(f"{i}. {result.title}")
            lines.append(f"URL: {result.url}")
            if hasattr(result, 'description') and result.description:
                lines.append(f"Description: {result.description}")
            lines.append("-" * 50)
        
        return "\n".join(lines)
    
    def _format_json(self, web_results: list[Any]) -> str:
        """Format as JSON"""
        results_data = []
        for result in web_results:
            result_dict = {
                "title": result.title,
                "url": result.url,
                "description": getattr(result, 'description', '')
            }
            results_data.append(result_dict)
        
        return json.dumps({"results": results_data}, ensure_ascii=False, indent=2)


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argparse parser"""
    parser = argparse.ArgumentParser(
        description="High-performance search tool using Brave Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s "Python programming" --count 5
  %(prog)s "machine learning" --format json
        """
    )
    
    parser.add_argument('query', help='Search query')
    parser.add_argument('-c', '--count', type=int, default=10, help='Number of search results (default: 10)')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='Output format (default: text)')
    parser.add_argument('-o', '--output', type=Path, help='Output file path (prints to stdout if not specified)')
    parser.add_argument('--api-key', help='Brave Search API key (can also use BRAVE_API_KEY env var)')
    
    return parser


def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Initialize client
        client = BraveSearchClient(api_key=args.api_key)
        
        config = SearchConfig(
            query=args.query,
            count=args.count,
            output_format=args.format,
            output_file=args.output
        )
        
        logger.info(f"Searching for '{config.query}'...")
        results = client.search(config)
        
        if results:
            formatted_results = client.format_results(results, config.output_format)
            
            if config.output_file:
                # Output to file
                config.output_file.write_text(formatted_results, encoding='utf-8')
                logger.info(f"Results saved to {config.output_file}")
            else:
                # Output to stdout
                print(formatted_results)
        else:
            logger.error("Search failed.")
            sys.exit(1)
    
    except ValueError as e:
        parser.error(str(e))
    except KeyboardInterrupt:
        logger.info("Search interrupted.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()