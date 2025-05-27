#!/usr/bin/env python3
"""Text analysis tool tests

Critical tests for TextAnalyzer functionality.
Focused on essential functionality with minimal test coverage.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.text_analyzer import TextAnalyzer, AnalysisConfig, CountType, OutputFormat


class TestTextAnalyzer:
    """TextAnalyzer class test cases"""
    
    @pytest.fixture
    def analyzer(self):
        """TextAnalyzer instance fixture"""
        return TextAnalyzer()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing fixture"""
        return "Hello, 世界! 123 こんにちは カタカナ 漢字"
    
    @pytest.fixture
    def temp_file(self, sample_text):
        """Temporary file fixture"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write(sample_text)
            temp_path = Path(f.name)
        
        yield temp_path
        
        # Cleanup
        temp_path.unlink()
    
    def test_count_all_characters(self, analyzer, sample_text):
        """Test all character counting"""
        result = analyzer.count_characters(sample_text, CountType.ALL)
        assert "Character count" in result
        assert result["Character count"] == len(sample_text)
    
    def test_count_no_spaces(self, analyzer, sample_text):
        """Test character counting without spaces"""
        result = analyzer.count_characters(sample_text, CountType.NO_SPACES)
        expected_length = len(sample_text.replace(' ', ''))
        assert result["Character count (no spaces)"] == expected_length
    
    def test_count_detailed(self, analyzer, sample_text):
        """Test detailed character counting"""
        result = analyzer.count_characters(sample_text, CountType.DETAILED)
        
        # Check essential keys exist
        assert "Total characters" in result
        assert "English letters" in result
        assert "Numbers" in result
        assert "Hiragana" in result
        assert "Katakana" in result
        assert "Kanji" in result
        
        # Check basic counts
        assert result["Total characters"] == len(sample_text)
        assert result["Numbers"] == 3  # "123"
        assert result["English letters"] == 5  # "Hello"
    
    def test_invalid_text_type(self, analyzer):
        """Test invalid text type handling"""
        with pytest.raises(TypeError):
            analyzer.count_characters(123)
    
    def test_count_from_file(self, analyzer, temp_file):
        """Test counting from file"""
        result = analyzer.count_from_file(temp_file, count_type=CountType.ALL)
        assert "Character count" in result
    
    def test_count_from_nonexistent_file(self, analyzer):
        """Test counting from non-existent file"""
        with pytest.raises(FileNotFoundError):
            analyzer.count_from_file("nonexistent.txt")
    
    def test_format_results_text(self, analyzer):
        """Test text format output"""
        results = {"Total characters": 10, "English letters": 5}
        formatted = analyzer.format_results(results, OutputFormat.TEXT)
        assert "Total characters: 10" in formatted
        assert "English letters: 5" in formatted
    
    def test_format_results_json(self, analyzer):
        """Test JSON format output"""
        results = {"Total characters": 10, "English letters": 5}
        formatted = analyzer.format_results(results, OutputFormat.JSON)
        
        import json
        data = json.loads(formatted)
        assert data["Total characters"] == 10
        assert data["English letters"] == 5
    
    def test_analyze_with_config_text(self, analyzer):
        """Test analysis with configuration using text"""
        config = AnalysisConfig(text="test text", count_type=CountType.ALL)
        result = analyzer.analyze_with_config(config)
        assert "Character count" in result
    
    def test_analyze_with_config_file(self, analyzer, temp_file):
        """Test analysis with configuration using file"""
        config = AnalysisConfig(file_path=temp_file, count_type=CountType.ALL)
        result = analyzer.analyze_with_config(config)
        assert "Character count" in result


class TestAnalysisConfig:
    """AnalysisConfig class test cases"""
    
    def test_config_with_text(self):
        """Test configuration with text"""
        config = AnalysisConfig(text="test")
        assert config.text == "test"
        assert config.file_path is None
    
    def test_config_with_file(self):
        """Test configuration with file"""
        file_path = Path("test.txt")
        config = AnalysisConfig(file_path=file_path)
        assert config.file_path == file_path
        assert config.text is None
    
    def test_config_no_input(self):
        """Test configuration without input"""
        with pytest.raises(ValueError):
            AnalysisConfig()
    
    def test_config_both_inputs(self):
        """Test configuration with both inputs"""
        with pytest.raises(ValueError):
            AnalysisConfig(text="test", file_path=Path("test.txt"))