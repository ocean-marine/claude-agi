#!/usr/bin/env python3
"""Brave Search ツールのテスト

本モジュールは、BraveSearchClientクラスの各機能をテストします。
pytest形式で統一され、モックを使用した安全なテスト環境を提供します。
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.brave_search import (
    BraveSearchClient,
    SearchConfig,
    InteractiveBraveSearch
)


class TestSearchConfig:
    """SearchConfigクラスのテストケース"""
    
    def test_default_config(self):
        """デフォルト設定のテスト"""
        config = SearchConfig(query="test query")
        assert config.query == "test query"
        assert config.count == 10
        assert config.output_format == "text"
        assert config.output_file is None
        assert config.search_lang == "ja"
        assert config.country == "JP"
    
    def test_custom_config(self):
        """カスタム設定のテスト"""
        output_file = Path("output.json")
        config = SearchConfig(
            query="custom query",
            count=5,
            output_format="json",
            output_file=output_file,
            search_lang="en",
            country="US"
        )
        assert config.query == "custom query"
        assert config.count == 5
        assert config.output_format == "json"
        assert config.output_file == output_file
        assert config.search_lang == "en"
        assert config.country == "US"
    
    def test_invalid_count(self):
        """無効なカウント数のテスト"""
        with pytest.raises(ValueError, match="正の整数である必要があります"):
            SearchConfig(query="test", count=0)
        
        with pytest.raises(ValueError, match="正の整数である必要があります"):
            SearchConfig(query="test", count=-1)
    
    def test_invalid_output_format(self):
        """無効な出力フォーマットのテスト"""
        with pytest.raises(ValueError, match="'text', 'json', 'csv' のいずれか"):
            SearchConfig(query="test", output_format="invalid")


class TestBraveSearchClient:
    """BraveSearchClientクラスのテストケース"""
    
    @pytest.fixture
    def mock_brave_api(self):
        """Brave APIをモックするフィクスチャ"""
        with patch('src.brave_search.Brave') as mock_brave:
            mock_instance = Mock()
            mock_brave.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def client(self, mock_brave_api):
        """テスト用のBraveSearchClientインスタンスを提供"""
        with patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'}):
            return BraveSearchClient()
    
    @pytest.fixture
    def sample_search_results(self):
        """サンプル検索結果を提供するフィクスチャ"""
        results = Mock()
        results.web_results = [
            Mock(
                title="テストタイトル1",
                url="https://example1.com",
                description="テスト説明1"
            ),
            Mock(
                title="テストタイトル2",
                url="https://example2.com",
                description="テスト説明2"
            )
        ]
        return results
    
    def test_init_with_env_key(self, mock_brave_api):
        """環境変数APIキーでの初期化テスト"""
        with patch.dict('os.environ', {'BRAVE_API_KEY': 'env_test_key'}):
            client = BraveSearchClient()
            assert client._api_key == 'env_test_key'
    
    def test_init_with_provided_key(self, mock_brave_api):
        """提供されたAPIキーでの初期化テスト"""
        client = BraveSearchClient(api_key="provided_key")
        assert client._api_key == "provided_key"
    
    def test_init_no_api_key(self, mock_brave_api):
        """APIキーなしでの初期化テスト"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="BRAVE_API_KEY環境変数が設定されていない"):
                BraveSearchClient()
    
    def test_init_brave_api_failure(self):
        """Brave API初期化失敗のテスト"""
        with patch('src.brave_search.Brave', side_effect=Exception("API init failed")):
            with patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'}):
                with pytest.raises(RuntimeError, match="Brave Search APIの初期化に失敗"):
                    BraveSearchClient()
    
    def test_search_success(self, client, mock_brave_api, sample_search_results):
        """正常な検索のテスト"""
        mock_brave_api.search.return_value = sample_search_results
        config = SearchConfig(query="test query", count=5)
        
        result = client.search(config)
        
        assert result == sample_search_results
        mock_brave_api.search.assert_called_once_with(
            q="test query",
            count=5,
            search_lang="ja",
            country="JP"
        )
    
    def test_search_empty_query(self, client):
        """空のクエリでの検索テスト"""
        config = SearchConfig(query="   ")
        
        with pytest.raises(ValueError, match="検索クエリが空です"):
            client.search(config)
    
    def test_search_api_error(self, client, mock_brave_api):
        """API検索エラーのテスト"""
        mock_brave_api.search.side_effect = Exception("API Error")
        config = SearchConfig(query="test query")
        
        result = client.search(config)
        
        assert result is None
    
    def test_format_results_text(self, client, sample_search_results):
        """テキストフォーマットの結果整形テスト"""
        formatted = client.format_results(sample_search_results, "text")
        
        assert "=== 検索結果 (2件) ===" in formatted
        assert "テストタイトル1" in formatted
        assert "https://example1.com" in formatted
        assert "テスト説明1" in formatted
    
    def test_format_results_json(self, client, sample_search_results):
        """JSONフォーマットの結果整形テスト"""
        formatted = client.format_results(sample_search_results, "json")
        
        # JSONの妥当性をチェック
        parsed = json.loads(formatted)
        assert "results" in parsed
        assert len(parsed["results"]) == 2
        assert parsed["results"][0]["title"] == "テストタイトル1"
        assert parsed["results"][0]["url"] == "https://example1.com"
    
    def test_format_results_csv(self, client, sample_search_results):
        """CSVフォーマットの結果整形テスト"""
        formatted = client.format_results(sample_search_results, "csv")
        
        lines = formatted.split('\n')
        assert lines[0] == "Title,URL,Description"
        assert '"テストタイトル1","https://example1.com","テスト説明1"' in formatted
    
    def test_format_results_no_results(self, client):
        """結果なしの整形テスト"""
        empty_results = Mock()
        empty_results.web_results = []
        
        formatted = client.format_results(empty_results, "text")
        assert "ウェブ検索結果が見つかりませんでした" in formatted
    
    def test_format_results_none(self, client):
        """None結果の整形テスト"""
        formatted = client.format_results(None, "text")
        assert "検索結果が見つかりませんでした" in formatted
    
    def test_csv_escaping(self, client):
        """CSV文字エスケープのテスト"""
        results = Mock()
        results.web_results = [
            Mock(
                title='タイトル"with"quotes',
                url="https://example.com",
                description='説明"with"quotes'
            )
        ]
        
        formatted = client.format_results(results, "csv")
        assert '""with""' in formatted  # ダブルクォートのエスケープ確認


class TestInteractiveBraveSearch:
    """InteractiveBraveSearchクラスのテストケース"""
    
    @pytest.fixture
    def interactive(self):
        """テスト用のInteractiveBraveSearchインスタンス"""
        mock_client = Mock(spec=BraveSearchClient)
        return InteractiveBraveSearch(mock_client)
    
    def test_init(self, interactive):
        """初期化テスト"""
        assert interactive.client is not None
        assert hasattr(interactive.client, 'search')
    
    def test_client_assignment(self):
        """クライアント割り当てテスト"""
        mock_client = Mock(spec=BraveSearchClient)
        interactive = InteractiveBraveSearch(mock_client)
        assert interactive.client == mock_client


# エラーハンドリングテスト
class TestErrorHandling:
    """エラーハンドリングのテストケース"""
    
    def test_search_with_none_config(self):
        """None設定での検索テスト"""
        with patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'}):
            with patch('src.brave_search.Brave'):
                client = BraveSearchClient()
                
                # Noneを渡すとAttributeErrorが発生するはず
                with pytest.raises(AttributeError):
                    client.search(None)  # type: ignore


# パフォーマンステスト
class TestPerformance:
    """パフォーマンステストケース"""
    
    def test_large_result_formatting(self, client):
        """大量結果の整形性能テスト"""
        # 大量の結果をシミュレート
        large_results = Mock()
        large_results.web_results = [
            Mock(
                title=f"タイトル{i}",
                url=f"https://example{i}.com",
                description=f"説明{i}"
            )
            for i in range(1000)
        ]
        
        # 処理が正常に完了することを確認
        formatted = client.format_results(large_results, "text")
        assert "=== 検索結果 (1000件) ===" in formatted
        
        # JSON形式でも正常に処理されることを確認
        json_formatted = client.format_results(large_results, "json")
        parsed = json.loads(json_formatted)
        assert len(parsed["results"]) == 1000


# 統合テスト
class TestIntegration:
    """統合テストケース"""
    
    @pytest.mark.skipif(
        pytest.skip_without_api_key := True,
        reason="API key not available for integration tests"
    )
    def test_real_api_call(self):
        """実際のAPI呼び出しテスト（API keyが利用可能な場合のみ）"""
        # この テストは実際のAPIキーがある場合のみ実行されます
        # CI/CDで実行する場合は、環境変数にAPIキーを設定する必要があります
        import os
        if not os.getenv('BRAVE_API_KEY'):
            pytest.skip("BRAVE_API_KEY not set")
        
        client = BraveSearchClient()
        config = SearchConfig(query="python programming", count=1)
        
        results = client.search(config)
        
        # 実際のAPIが利用可能であることを確認
        assert results is not None
        # 実際の結果の構造を確認
        if hasattr(results, 'web_results') and results.web_results:
            assert len(results.web_results) >= 1