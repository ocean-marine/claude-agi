#!/usr/bin/env python3
"""Text analysis tool: High-performance character counter

Provides text character counting and analysis functionality.
Simplified interface with essential analysis features.

Usage:
    $ python text_analyzer.py sample.txt
    $ from text_analyzer import TextAnalyzer; analyzer = TextAnalyzer()
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)


class CountType(Enum):
    """Character counting method enumeration"""
    ALL = "all"
    NO_SPACES = "no_spaces"
    DETAILED = "detailed"


class OutputFormat(Enum):
    """Output format enumeration"""
    TEXT = "text"
    JSON = "json"


@dataclass(frozen=True)
class AnalysisConfig:
    """Analysis configuration data class"""
    text: Optional[str] = None
    file_path: Optional[Path] = None
    count_type: CountType = CountType.DETAILED
    output_format: OutputFormat = OutputFormat.TEXT
    output_file: Optional[Path] = None
    encoding: str = "utf-8"

    def __post_init__(self):
        if not self.text and not self.file_path:
            raise ValueError("Either text or file_path must be specified")
        if self.text and self.file_path:
            raise ValueError("Cannot specify both text and file_path")


class TextAnalyzer:
    """Text analysis and character counting class
    
    Provides various methods for text character counting and analysis.
    Supports Japanese characters, alphanumeric, and symbol classification.
    """
    
    # Pre-compiled regex patterns for efficiency
    _PATTERNS = {
        'english': re.compile(r'[a-zA-Z]'),
        'digits': re.compile(r'[0-9]'),
        'hiragana': re.compile(r'[ひらがな-ゖ]'),
        'katakana': re.compile(r'[カタカナ-ヿ]'),
        'kanji': re.compile(r'[一-龯]'),
        'symbols': re.compile(r'[!-/:-@\[-`{-~]'),
        'whitespace': re.compile(r'\s'),
    }
    
    def count_characters(self, text: str, count_type: CountType = CountType.ALL) -> Dict[str, int]:
        """Count text characters using specified method
        
        Args:
            text: Text to count
            count_type: Counting method
            
        Returns:
            Character count result dictionary
            
        Raises:
            TypeError: If text is not a string
            ValueError: For invalid counting method
        """
        if not isinstance(text, str):
            raise TypeError("Text must be a string")
        
        match count_type:
            case CountType.ALL:
                return {"Character count": len(text)}
            case CountType.NO_SPACES:
                no_space_text = self._PATTERNS['whitespace'].sub('', text)
                return {"Character count (no spaces)": len(no_space_text)}
            case CountType.DETAILED:
                return self._detailed_count(text)
            case _:
                raise ValueError(f"Invalid counting method: {count_type}")
    
    def _detailed_count(self, text: str) -> Dict[str, int]:
        """Detailed character classification counting
        
        Args:
            text: Text to count
            
        Returns:
            Detailed character count information dictionary
        """
        result = {
            "Total characters": len(text),
            "English letters": len(self._PATTERNS['english'].findall(text)),
            "Numbers": len(self._PATTERNS['digits'].findall(text)),
            "Hiragana": len(self._PATTERNS['hiragana'].findall(text)),
            "Katakana": len(self._PATTERNS['katakana'].findall(text)),
            "Kanji": len(self._PATTERNS['kanji'].findall(text)),
            "Symbols": len(self._PATTERNS['symbols'].findall(text)),
            "Whitespace": len(self._PATTERNS['whitespace'].findall(text)),
            "Newlines": text.count('\n'),
            "Lines": len(text.splitlines()),
            "Words": len(text.split()),
            "Other": 0
        }
        
        # Calculate other character count
        counted = sum(
            result[key] for key in result 
            if key not in ["Total characters", "Other", "Lines", "Words"]
        )
        result["Other"] = result["Total characters"] - counted
        
        return result
    
    def count_from_file(self, file_path: Union[str, Path], 
                       encoding: str = "utf-8", 
                       count_type: CountType = CountType.ALL) -> Dict[str, int]:
        """Count characters from file
        
        Args:
            file_path: File path
            encoding: Character encoding
            count_type: Counting method
            
        Returns:
            Character count result dictionary
            
        Raises:
            FileNotFoundError: If file not found
            IOError: For file reading errors
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            content = file_path.read_text(encoding=encoding)
            return self.count_characters(content, count_type)
        except UnicodeDecodeError as e:
            raise IOError(f"File character encoding error: {e}") from e
        except Exception as e:
            raise IOError(f"File reading error: {e}") from e
    
    def format_results(self, results: Dict[str, int], output_format: OutputFormat = OutputFormat.TEXT) -> str:
        """Format count results in specified format
        
        Args:
            results: Count result dictionary
            output_format: Output format
            
        Returns:
            Formatted result string
        """
        match output_format:
            case OutputFormat.JSON:
                return json.dumps(results, ensure_ascii=False, indent=2)
            case OutputFormat.TEXT:
                return self._format_text(results)
            case _:
                raise ValueError(f"Invalid output format: {output_format}")
    
    def _format_text(self, results: Dict[str, int]) -> str:
        """Format as text"""
        lines = ["=== Text Analysis Results ==="]
        
        for key, value in results.items():
            lines.append(f"{key}: {value:,}")
        
        return "\n".join(lines)
    
    def analyze_with_config(self, config: AnalysisConfig) -> Dict[str, int]:
        """Analyze text based on configuration
        
        Args:
            config: Analysis configuration
            
        Returns:
            Analysis result dictionary
        """
        if config.text:
            return self.count_characters(config.text, config.count_type)
        elif config.file_path:
            return self.count_from_file(config.file_path, config.encoding, config.count_type)
        else:
            raise ValueError("Text or file_path not configured")


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argparse parser"""
    parser = argparse.ArgumentParser(
        description="High-performance text analysis and character counting tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Count methods:
  all         - All characters (default)
  no_spaces   - Excluding whitespace
  detailed    - Detailed classification (recommended)

Usage examples:
  %(prog)s sample.txt --type detailed --format json
  %(prog)s document.txt --type no_spaces
        """
    )
    
    # Input source
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('file_path', nargs='?', type=Path, help='File path to analyze')
    input_group.add_argument('--text', help='Direct text input')
    
    # Analysis options
    parser.add_argument('-t', '--type', choices=[e.value for e in CountType], default=CountType.DETAILED.value, help='Count method (default: detailed)')
    parser.add_argument('-f', '--format', choices=[e.value for e in OutputFormat], default=OutputFormat.TEXT.value, help='Output format (default: text)')
    parser.add_argument('-o', '--output', type=Path, help='Output file path (prints to stdout if not specified)')
    parser.add_argument('-e', '--encoding', default='utf-8', help='File character encoding (default: utf-8)')
    
    return parser


def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        analyzer = TextAnalyzer()
        
        if not args.file_path and not args.text:
            parser.error("Please specify file_path or --text option.")
        
        config = AnalysisConfig(
            text=args.text,
            file_path=args.file_path,
            count_type=CountType(args.type),
            output_format=OutputFormat(args.format),
            output_file=args.output,
            encoding=args.encoding
        )
        
        results = analyzer.analyze_with_config(config)
        formatted_results = analyzer.format_results(results, config.output_format)
        
        if config.output_file:
            # Output to file
            config.output_file.write_text(formatted_results, encoding='utf-8')
            logger.info(f"Results saved to {config.output_file}")
        else:
            # Output to stdout
            print(formatted_results)
    
    except (ValueError, TypeError, FileNotFoundError, IOError) as e:
        parser.error(str(e))
    except KeyboardInterrupt:
        logger.info("Analysis interrupted.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()