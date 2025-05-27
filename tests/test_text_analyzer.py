#!/usr/bin/env python3
"""テキスト分析ツールのテスト

本モジュールは、TextAnalyzerクラスの各機能をテストします。
pytest形式で統一され、包括的なテストカバレッジを提供します。
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.text_analyzer import (
    TextAnalyzer,
    AnalysisConfig,
    CountType,
    OutputFormat,
    InteractiveTextAnalyzer
)


class TestTextAnalyzer:
    """TextAnalyzerクラスのテストケース"""
    
    @pytest.fixture
    def analyzer(self):
        """TextAnalyzerインスタンスを提供するフィクスチャ"""
        return TextAnalyzer()
    
    @pytest.fixture
    def sample_text(self):
        """テスト用サンプルテキストを提供するフィクスチャ"""
        return "Hello, 世界! 123 こんにちは カタカナ 漢字"
    
    @pytest.fixture
    def temp_file(self, sample_text):
        """一時ファイルを提供するフィクスチャ"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write(sample_text)
            temp_path = Path(f.name)
        
        yield temp_path
        
        # クリーンアップ
        temp_path.unlink()
    
    def test_count_all_characters(self, analyzer, sample_text):
        """全文字数のカウントテスト"""
        result = analyzer.count_characters(sample_text, CountType.ALL)
        assert result["文字数"] == len(sample_text)
    
    def test_count_no_spaces(self, analyzer, sample_text):
        """空白文字を除くカウントテスト"""
        result = analyzer.count_characters(sample_text, CountType.NO_SPACES)
        expected = len(sample_text.replace(' ', ''))
        assert result["文字数（空白除く）"] == expected
    
    def test_count_alphanumeric(self, analyzer, sample_text):
        """英数字のみのカウントテスト"""
        result = analyzer.count_characters(sample_text, CountType.ALPHANUMERIC)
        # Hello123 = 8文字
        assert result["英数字文字数"] == 8
    
    def test_count_japanese(self, analyzer, sample_text):
        """日本語文字のみのカウントテスト"""
        result = analyzer.count_characters(sample_text, CountType.JAPANESE)
        # 世界(2) + こんにちは(5) + カタカナ(4) + 漢字(2) = 13
        assert result["日本語文字数"] == 13
    
    def test_detailed_count(self, analyzer, sample_text):
        """詳細カウントテスト"""
        result = analyzer.count_characters(sample_text, CountType.DETAILED)
        
        assert result["総文字数"] == len(sample_text)
        assert result["英字"] == 5  # Hello
        assert result["数字"] == 3  # 123
        assert result["ひらがな"] == 5  # こんにちは
        assert result["カタカナ"] == 4  # カタカナ
        assert result["漢字"] == 4  # 世界 + 漢字
        assert result["記号"] == 2  # , !
        assert result["空白文字"] == 4
        assert result["改行"] == 0
        assert result["行数"] == 1
        assert result["単語数"] == 6
        assert "その他" in result
    
    def test_empty_string(self, analyzer):
        """空文字列のテスト"""
        result = analyzer.count_characters("", CountType.ALL)
        assert result["文字数"] == 0
    
    def test_invalid_count_type(self, analyzer):
        """無効なカウント方式のテスト"""
        with pytest.raises(ValueError, match="無効なカウント方式"):
            # 直接無効なCountTypeを作ることはできないので、
            # 内部メソッドを使用してテスト
            analyzer.count_characters("test", "invalid")  # type: ignore
    
    def test_non_string_input(self, analyzer):
        """文字列以外の入力のテスト"""
        with pytest.raises(TypeError, match="文字列である必要があります"):
            analyzer.count_characters(123, CountType.ALL)  # type: ignore
    
    def test_count_from_file(self, analyzer, temp_file, sample_text):
        """ファイルからのカウントテスト"""
        result = analyzer.count_from_file(temp_file, count_type=CountType.ALL)
        assert result["文字数"] == len(sample_text)
    
    def test_file_not_found(self, analyzer):
        """存在しないファイルのテスト"""
        with pytest.raises(FileNotFoundError, match="ファイルが見つかりません"):
            analyzer.count_from_file("nonexistent_file.txt")
    
    def test_format_results_text(self, analyzer):
        """テキストフォーマットの結果整形テスト"""
        results = {"文字数": 10, "英字": 5}
        formatted = analyzer.format_results(results, OutputFormat.TEXT)
        
        assert "=== 文字数分析結果 ===" in formatted
        assert "文字数: 10" in formatted
        assert "英字: 5" in formatted
    
    def test_format_results_json(self, analyzer):
        """JSONフォーマットの結果整形テスト"""
        results = {"文字数": 10, "英字": 5}
        formatted = analyzer.format_results(results, OutputFormat.JSON)
        
        # JSONの妥当性をチェック
        import json
        parsed = json.loads(formatted)
        assert parsed["文字数"] == 10
        assert parsed["英字"] == 5
    
    def test_format_results_csv(self, analyzer):
        """CSVフォーマットの結果整形テスト"""
        results = {"文字数": 10, "英字": 5}
        formatted = analyzer.format_results(results, OutputFormat.CSV)
        
        lines = formatted.split('\n')
        assert lines[0] == "Category,Count"
        assert '"文字数",10' in formatted
        assert '"英字",5' in formatted
    
    @pytest.mark.parametrize("count_type,expected_key", [
        (CountType.ALL, "文字数"),
        (CountType.NO_SPACES, "文字数（空白除く）"),
        (CountType.ALPHANUMERIC, "英数字文字数"),
        (CountType.JAPANESE, "日本語文字数"),
        (CountType.DETAILED, "総文字数")
    ])
    def test_count_types_parametrized(self, analyzer, count_type, expected_key):
        """パラメータ化されたカウント方式テスト"""
        text = "Hello 世界"
        result = analyzer.count_characters(text, count_type)
        assert expected_key in result
        assert isinstance(result[expected_key], int)
        assert result[expected_key] >= 0


class TestAnalysisConfig:
    """AnalysisConfigクラスのテストケース"""
    
    def test_config_with_text(self):
        """テキスト指定の設定テスト"""
        config = AnalysisConfig(text="test text")
        assert config.text == "test text"
        assert config.file_path is None
    
    def test_config_with_file(self):
        """ファイル指定の設定テスト"""
        file_path = Path("test.txt")
        config = AnalysisConfig(file_path=file_path)
        assert config.file_path == file_path
        assert config.text is None
    
    def test_config_validation_no_input(self):
        """入力なしの設定バリデーションテスト"""
        with pytest.raises(ValueError, match="テキストまたはファイルパス"):
            AnalysisConfig()
    
    def test_config_validation_both_inputs(self):
        """両方の入力がある設定バリデーションテスト"""
        with pytest.raises(ValueError, match="両方を指定することはできません"):
            AnalysisConfig(text="test", file_path=Path("test.txt"))


class TestInteractiveTextAnalyzer:
    """InteractiveTextAnalyzerクラスのテストケース"""
    
    def test_init(self):
        """初期化テスト"""
        analyzer = TextAnalyzer()
        interactive = InteractiveTextAnalyzer(analyzer)
        assert interactive.analyzer is analyzer
    
    def test_get_count_type_valid(self):
        """有効な選択番号のカウント方式取得テスト"""
        analyzer = TextAnalyzer()
        interactive = InteractiveTextAnalyzer(analyzer)
        
        assert interactive._get_count_type("1") == CountType.ALL
        assert interactive._get_count_type("2") == CountType.NO_SPACES
        assert interactive._get_count_type("5") == CountType.DETAILED
    
    def test_get_count_type_invalid(self):
        """無効な選択番号のカウント方式取得テスト"""
        analyzer = TextAnalyzer()
        interactive = InteractiveTextAnalyzer(analyzer)
        
        # 無効な選択はデフォルトでDETAILEDを返す
        assert interactive._get_count_type("invalid") == CountType.DETAILED
        assert interactive._get_count_type("99") == CountType.DETAILED


# パフォーマンステスト
class TestPerformance:
    """パフォーマンスに関するテストケース"""
    
    def test_large_text_performance(self):
        """大きなテキストの処理性能テスト"""
        analyzer = TextAnalyzer()
        large_text = "あ" * 10000  # 10,000文字の日本語テキスト
        
        # 処理が正常に完了することを確認
        result = analyzer.count_characters(large_text, CountType.DETAILED)
        assert result["総文字数"] == 10000
        assert result["ひらがな"] == 10000
    
    def test_regex_pattern_reuse(self):
        """正規表現パターンの再利用テスト"""
        analyzer = TextAnalyzer()
        
        # 同じパターンが再利用されていることを確認
        assert hasattr(analyzer, '_PATTERNS')
        assert 'hiragana' in analyzer._PATTERNS
        assert hasattr(analyzer._PATTERNS['hiragana'], 'findall')


# エラーハンドリングテスト
class TestErrorHandling:
    """エラーハンドリングのテストケース"""
    
    def test_file_encoding_error(self):
        """ファイルエンコーディングエラーのテスト"""
        analyzer = TextAnalyzer()
        
        # バイナリファイルを作成
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'\x80\x81\x82')  # 無効なUTF-8バイト
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(IOError, match="文字エンコーディングエラー"):
                analyzer.count_from_file(temp_path, encoding='utf-8')
        finally:
            temp_path.unlink()
    
    def test_analyze_with_config_no_input(self):
        """入力のない設定での分析テスト"""
        analyzer = TextAnalyzer()
        config = AnalysisConfig.__new__(AnalysisConfig)  # バリデーションをスキップ
        config.text = None
        config.file_path = None
        
        with pytest.raises(ValueError, match="テキストまたはファイルパスが設定されていません"):
            analyzer.analyze_with_config(config)