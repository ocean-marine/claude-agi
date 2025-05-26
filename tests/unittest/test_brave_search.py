import pytest
import os
from unittest.mock import Mock, patch
from src.main import BraveSearchApp


class TestBraveSearchApp:
    """BraveSearchAppクラスのテストケース"""
    
    def test_init_brave_search_app(self):
        """BraveSearchAppクラスの初期化テスト"""
        app = BraveSearchApp()
        assert app is not None
        
    @patch('src.main.Brave')
    def test_search_method_exists(self, mock_brave):
        """検索メソッドが存在することを確認するテスト"""
        app = BraveSearchApp()
        assert hasattr(app, 'search')
        
    @patch('src.main.Brave')
    def test_search_with_query(self, mock_brave):
        """基本的な検索機能のテスト"""
        mock_brave_instance = Mock()
        mock_brave.return_value = mock_brave_instance
        mock_search_results = Mock()
        mock_search_results.web_results = [
            Mock(title="テストタイトル1", url="https://example1.com", description="テスト説明1"),
            Mock(title="テストタイトル2", url="https://example2.com", description="テスト説明2")
        ]
        mock_brave_instance.search.return_value = mock_search_results
        
        app = BraveSearchApp()
        results = app.search("cobalt mining", 5)
        
        assert results is not None
        mock_brave_instance.search.assert_called_once_with(q="cobalt mining", count=5)
        
    @patch('src.main.Brave')
    def test_search_with_custom_count(self, mock_brave):
        """検索結果数の指定テスト"""
        mock_brave_instance = Mock()
        mock_brave.return_value = mock_brave_instance
        mock_search_results = Mock()
        mock_search_results.web_results = []
        mock_brave_instance.search.return_value = mock_search_results
        
        app = BraveSearchApp()
        app.search("test query", 15)
        
        mock_brave_instance.search.assert_called_once_with(q="test query", count=15)
        
    @patch('src.main.Brave')
    def test_format_results_method_exists(self, mock_brave):
        """結果フォーマットメソッドが存在することを確認するテスト"""
        app = BraveSearchApp()
        assert hasattr(app, 'format_results')
        
    def test_run_method_exists(self):
        """runメソッドが存在することを確認するテスト"""
        app = BraveSearchApp()
        assert hasattr(app, 'run')