#!/usr/bin/env python3
"""Future Research tool: AI development research application

Provides research functionality for AI tools evolution analysis.
Specialized tool for investigating Claude Code Action, Jules, and Codex development.

Usage:
    $ python future_research.py --topics "Claude Code Action" "Jules" "Codex"
    $ from future_research import FutureResearchTool; tool = FutureResearchTool()
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from brave_search import BraveSearchClient, SearchConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResearchConfig:
    """Research configuration data class"""
    topics: list[str]
    max_results_per_topic: int = 5
    output_format: str = "text"
    output_file: Optional[Path] = None

    def __post_init__(self):
        if not self.topics:
            raise ValueError("topics must not be empty")
        if self.max_results_per_topic <= 0:
            raise ValueError("max_results_per_topic must be a positive integer")
        if self.output_format not in ["text", "json"]:
            raise ValueError("output_format must be 'text' or 'json'")


class FutureResearchTool:
    """AI Development Research Tool
    
    High-level interface for researching AI tools evolution.
    Specializes in Claude Code Action, Jules, and Codex analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize FutureResearchTool
        
        Args:
            api_key: Brave Search API key. If None, will get from environment
            
        Raises:
            ValueError: If API key is not set
            RuntimeError: If search client initialization fails
        """
        try:
            self.search_client = BraveSearchClient(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize search client: {e}") from e
    
    def research(self, config: ResearchConfig) -> dict[str, list[dict[str, Any]]]:
        """Execute research for specified topics
        
        Args:
            config: Research configuration
            
        Returns:
            Dictionary mapping topics to search results
        """
        results = {}
        
        for topic in config.topics:
            logger.info(f"Researching topic: {topic}")
            
            # Create enhanced search query for future/evolution focus
            enhanced_query = f"{topic} future development evolution roadmap 2024 2025"
            
            search_config = SearchConfig(
                query=enhanced_query,
                count=config.max_results_per_topic
            )
            
            search_results = self.search_client.search(search_config)
            
            if search_results and hasattr(search_results, 'web_results'):
                # Convert search results to structured format
                topic_results = []
                for result in search_results.web_results:
                    topic_results.append({
                        "title": result.title,
                        "url": result.url,
                        "description": getattr(result, 'description', '')
                    })
                results[topic] = topic_results
            else:
                # No results found for this topic
                results[topic] = []
                logger.warning(f"No results found for topic: {topic}")
        
        return results
    
    def format_results(self, results: dict[str, list[dict[str, Any]]], format_type: str = "text") -> str:
        """Format research results in specified format
        
        Args:
            results: Research results dictionary
            format_type: Output format ('text' or 'json')
            
        Returns:
            Formatted result string
        """
        if format_type == "json":
            return json.dumps(results, ensure_ascii=False, indent=2)
        else:  # text format
            return self._format_text_results(results)
    
    def _format_text_results(self, results: dict[str, list[dict[str, Any]]]) -> str:
        """Format results as text"""
        lines = ["=== AI Development Research Results ===\n"]
        
        for topic, topic_results in results.items():
            lines.append(f"## {topic}")
            lines.append(f"Found {len(topic_results)} results\n")
            
            if not topic_results:
                lines.append("No results found for this topic.\n")
                continue
            
            for i, result in enumerate(topic_results, 1):
                lines.append(f"{i}. {result['title']}")
                lines.append(f"   URL: {result['url']}")
                if result['description']:
                    lines.append(f"   Description: {result['description']}")
                lines.append("")  # Empty line for readability
            
            lines.append("-" * 60)
            lines.append("")
        
        return "\n".join(lines)


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argparse parser"""
    parser = argparse.ArgumentParser(
        description="AI Development Research Tool using Brave Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s --topics "Claude Code Action" "Jules" "Codex"
  %(prog)s --topics "Claude Code Action" --format json --output research_results.json
        """
    )
    
    parser.add_argument(
        '--topics',
        nargs='+',
        default=["Claude Code Action", "Jules", "Codex"],
        help='Research topics (default: Claude Code Action, Jules, Codex)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=5,
        help='Maximum results per topic (default: 5)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (prints to stdout if not specified)'
    )
    parser.add_argument(
        '--api-key',
        help='Brave Search API key (can also use BRAVE_API_KEY env var)'
    )
    
    return parser


def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Initialize research tool
        tool = FutureResearchTool(api_key=args.api_key)
        
        config = ResearchConfig(
            topics=args.topics,
            max_results_per_topic=args.max_results,
            output_format=args.format,
            output_file=args.output
        )
        
        logger.info(f"Starting research for topics: {', '.join(config.topics)}")
        results = tool.research(config)
        
        # Format and output results
        formatted_results = tool.format_results(results, config.output_format)
        
        if config.output_file:
            # Output to file
            config.output_file.write_text(formatted_results, encoding='utf-8')
            logger.info(f"Results saved to {config.output_file}")
        else:
            # Output to stdout
            print(formatted_results)
    
    except ValueError as e:
        parser.error(str(e))
    except KeyboardInterrupt:
        logger.info("Research interrupted.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()