#!/usr/bin/env python3
"""Unified CLI tool tests

Critical tests for AGIToolCLI functionality.
Focused on essential CLI operations with minimal test coverage.
"""
from __future__ import annotations

import sys
from unittest.mock import Mock, patch

import pytest

from src.cli import AGIToolCLI


class TestAGIToolCLI:
    """AGIToolCLI class test cases"""
    
    @pytest.fixture
    def cli(self):
        """CLI instance fixture"""
        return AGIToolCLI()
    
    def test_init(self, cli):
        """Test initialization"""
        assert cli is not None
        assert cli.parser is not None
    
    def test_parser_creation(self, cli):
        """Test parser creation"""
        parser = cli._create_parser()
        assert parser is not None
        
        # Check help text
        help_text = parser.format_help()
        assert "Claude AGI unified CLI tool" in help_text
    
    @patch('src.cli.BraveSearchClient')
    def test_run_search(self, mock_client_class, cli):
        """Test search command execution"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = {"results": "test"}
        mock_client.format_results.return_value = "formatted results"
        
        with patch('sys.argv', ['cli.py', 'search', 'test query']):
            cli.run(['search', 'test query'])
        
        mock_client_class.assert_called_once()
        mock_client.search.assert_called_once()
    
    @patch('src.cli.TextAnalyzer')
    def test_run_analyze(self, mock_analyzer_class, cli):
        """Test analyze command execution"""
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_with_config.return_value = {"count": 10}
        mock_analyzer.format_results.return_value = "analysis results"
        
        with patch('sys.argv', ['cli.py', 'analyze', 'test.txt']):
            cli.run(['analyze', 'test.txt'])
        
        mock_analyzer_class.assert_called_once()
        mock_analyzer.analyze_with_config.assert_called_once()
    
    def test_run_no_command(self, cli, capsys):
        """Test running without command"""
        with patch('sys.argv', ['cli.py']):
            cli.run([])
        
        captured = capsys.readouterr()
        assert "usage:" in captured.out
    
    @patch('src.cli.logger')
    def test_run_keyboard_interrupt(self, mock_logger, cli):
        """Test keyboard interrupt handling"""
        with patch.object(cli.parser, 'parse_args', side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                cli.run([])
        
        mock_logger.info.assert_called_with("Operation interrupted.")
    
    @patch('src.cli.logger')
    def test_run_exception(self, mock_logger, cli):
        """Test exception handling"""
        with patch.object(cli.parser, 'parse_args', side_effect=Exception("test error")):
            with pytest.raises(SystemExit):
                cli.run([])
        
        mock_logger.error.assert_called_with("Error occurred: test error")