#!/usr/bin/env python3
"""統合CLIツールのテスト

本モジュールは、AGIToolCLIクラスの各機能をテストします。
各ツールの統合動作とコマンドライン引数の処理をテストします。
"""
from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.cli import AGIToolCLI


class TestAGIToolCLI:
    """AGIToolCLIクラスのテストケース"""
    
    @pytest.fixture
    def cli(self):
        """CLIインスタンスを提供するフィクスチャ"""
        return AGIToolCLI()
    
    def test_init(self, cli):
        """初期化テスト"""
        assert cli is not None
        assert cli.parser is not None
        assert hasattr(cli, 'TOOLS')
        assert 'search' in cli.TOOLS
        assert 'analyze' in cli.TOOLS
    
    def test_tools_structure(self, cli):
        """ツール構造のテスト"""
        for tool_name, tool_info in cli.TOOLS.items():
            assert 'description' in tool_info
            assert 'example' in tool_info
            assert isinstance(tool_info['description'], str)
            assert isinstance(tool_info['example'], str)
    
    def test_parser_creation(self, cli):
        """パーサー作成のテスト"""
        parser = cli._create_main_parser()
        assert parser is not None
        
        # ヘルプテキストの確認
        help_text = parser.format_help()
        assert "Claude AGI 統合CLIツール" in help_text
        assert "--list-tools" in help_text
        assert "--interactive" in help_text
    
    def test_help_text_generation(self, cli):
        """ヘルプテキスト生成のテスト"""
        help_text = cli._get_help_text()
        assert "利用可能なツール:" in help_text
        assert "search" in help_text
        assert "analyze" in help_text
        assert "例:" in help_text
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_list_tools(self, mock_stdout, cli):
        """ツール一覧表示のテスト"""
        cli._list_tools()
        output = mock_stdout.getvalue()
        
        assert "=== Claude AGI 利用可能ツール ===" in output
        assert "SEARCH" in output
        assert "ANALYZE" in output
        assert "例:" in output
    
    def test_list_tools_command(self, cli):
        """--list-toolsコマンドのテスト"""
        with patch.object(cli, '_list_tools') as mock_list:
            cli.run(['--list-tools'])
            mock_list.assert_called_once()
    
    @patch('src.cli.BraveSearchClient')
    @patch('src.cli.InteractiveBraveSearch')
    def test_interactive_search_selection(self, mock_interactive, mock_client, cli):
        """インタラクティブモードでの検索選択テスト"""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_interactive_instance = Mock()
        mock_interactive.return_value = mock_interactive_instance
        
        with patch('builtins.input', side_effect=['1', '0']):
            cli._run_interactive()
        
        mock_client.assert_called_once()
        mock_interactive.assert_called_once_with(mock_client_instance)
        mock_interactive_instance.run.assert_called_once()
    
    @patch('src.cli.TextAnalyzer')
    @patch('src.cli.InteractiveTextAnalyzer')
    def test_interactive_analyze_selection(self, mock_interactive, mock_analyzer, cli):
        """インタラクティブモードでの分析選択テスト"""
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_interactive_instance = Mock()
        mock_interactive.return_value = mock_interactive_instance
        
        with patch('builtins.input', side_effect=['2', '0']):
            cli._run_interactive()
        
        mock_analyzer.assert_called_once()
        mock_interactive.assert_called_once_with(mock_analyzer_instance)
        mock_interactive_instance.run.assert_called_once()
    
    def test_search_command_parsing(self, cli):
        """検索コマンドの解析テスト"""
        args = cli.parser.parse_args(['search', 'test query', '--count', '5', '--format', 'json'])
        
        assert args.tool == 'search'
        assert args.query == 'test query'
        assert args.count == 5
        assert args.format == 'json'
    
    def test_analyze_command_parsing(self, cli):
        """分析コマンドの解析テスト"""
        args = cli.parser.parse_args(['analyze', 'test.txt', '--type', 'detailed', '--format', 'csv'])
        
        assert args.tool == 'analyze'
        assert args.file_path == Path('test.txt')
        assert args.type == 'detailed'
        assert args.format == 'csv'
    
    @patch('src.cli.BraveSearchClient')
    def test_run_search(self, mock_client, cli):
        """検索実行のテスト"""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.search.return_value = Mock()
        mock_client_instance.format_results.return_value = "search results"
        
        args = Mock()
        args.query = "test query"
        args.count = 5
        args.format = "text"
        args.output = None
        args.lang = "ja"
        args.country = "JP"
        args.api_key = None
        
        with patch('sys.stderr', new_callable=StringIO):
            with patch('builtins.print') as mock_print:
                cli._run_search(args)
        
        mock_client.assert_called_once_with(api_key=None)
        mock_client_instance.search.assert_called_once()
        mock_print.assert_called_with("search results")
    
    @patch('src.cli.TextAnalyzer')
    def test_run_analyze(self, mock_analyzer, cli):
        """分析実行のテスト"""
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_with_config.return_value = {"文字数": 10}
        mock_analyzer_instance.format_results.return_value = "analysis results"
        
        args = Mock()
        args.text = "test text"
        args.file_path = None
        args.type = "detailed"
        args.format = "text"
        args.output = None
        args.encoding = "utf-8"
        
        with patch('builtins.print') as mock_print:
            cli._run_analyze(args)
        
        mock_analyzer.assert_called_once()
        mock_analyzer_instance.analyze_with_config.assert_called_once()
        mock_print.assert_called_with("analysis results")
    
    def test_version_argument(self, cli):
        """バージョン引数のテスト"""
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['--version'])
    
    def test_no_arguments(self, cli):
        """引数なしのテスト"""
        with patch.object(cli.parser, 'print_help') as mock_help:
            cli.run([])
            mock_help.assert_called_once()
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_keyboard_interrupt(self, mock_stderr, cli):
        """キーボード割り込みのテスト"""
        with patch.object(cli, '_list_tools', side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                cli.run(['--list-tools'])
        
        assert "操作を中断しました" in mock_stderr.getvalue()
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_general_exception(self, mock_stderr, cli):
        """一般的な例外のテスト"""
        with patch.object(cli, '_list_tools', side_effect=Exception("Test error")):
            with pytest.raises(SystemExit):
                cli.run(['--list-tools'])
        
        assert "エラーが発生しました: Test error" in mock_stderr.getvalue()


class TestCLIIntegration:
    """CLI統合テストケース"""
    
    def test_search_subcommand_help(self):
        """検索サブコマンドのヘルプテスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['search', '--help'])
    
    def test_analyze_subcommand_help(self):
        """分析サブコマンドのヘルプテスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['analyze', '--help'])
    
    def test_invalid_subcommand(self):
        """無効なサブコマンドのテスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['invalid'])
    
    def test_search_without_query(self):
        """クエリなしの検索テスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['search'])
    
    def test_analyze_mutual_exclusion(self):
        """分析コマンドの相互排他テスト"""
        cli = AGIToolCLI()
        
        # file_pathとtextの両方を指定
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['analyze', 'file.txt', '--text', 'some text'])


# パフォーマンステスト
class TestCLIPerformance:
    """CLIパフォーマンステストケース"""
    
    def test_parser_creation_performance(self):
        """パーサー作成のパフォーマンステスト"""
        import time
        
        start_time = time.time()
        cli = AGIToolCLI()
        end_time = time.time()
        
        # パーサー作成は1秒以内で完了すべき
        assert (end_time - start_time) < 1.0
    
    def test_help_generation_performance(self):
        """ヘルプ生成のパフォーマンステスト"""
        import time
        
        cli = AGIToolCLI()
        
        start_time = time.time()
        help_text = cli._get_help_text()
        end_time = time.time()
        
        # ヘルプ生成は0.1秒以内で完了すべき
        assert (end_time - start_time) < 0.1
        assert len(help_text) > 0


# エラーハンドリングテスト
class TestCLIErrorHandling:
    """CLIエラーハンドリングテストケース"""
    
    def test_invalid_count_argument(self):
        """無効なcount引数のテスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['search', 'query', '--count', 'invalid'])
    
    def test_invalid_format_argument(self):
        """無効なformat引数のテスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['search', 'query', '--format', 'invalid'])
    
    def test_invalid_type_argument(self):
        """無効なtype引数のテスト"""
        cli = AGIToolCLI()
        
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['analyze', 'file.txt', '--type', 'invalid'])
    
    @patch('src.cli.BraveSearchClient', side_effect=Exception("Init error"))
    def test_search_client_init_error(self, mock_client):
        """検索クライアント初期化エラーのテスト"""
        cli = AGIToolCLI()
        args = Mock()
        args.api_key = None
        
        with pytest.raises(Exception):
            cli._run_search(args)
    
    @patch('src.cli.TextAnalyzer', side_effect=Exception("Init error"))
    def test_analyzer_init_error(self, mock_analyzer):
        """分析ツール初期化エラーのテスト"""
        cli = AGIToolCLI()
        args = Mock()
        
        with pytest.raises(Exception):
            cli._run_analyze(args)