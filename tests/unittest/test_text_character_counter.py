#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキスト文字数取得ツールのテスト
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from text_character_counter import TextCharacterCounter


class TestTextCharacterCounter(unittest.TestCase):
    """TextCharacterCounterのテストクラス"""
    
    def setUp(self):
        """テストの前準備"""
        self.counter = TextCharacterCounter()
    
    def test_count_all_characters(self):
        """全文字数のカウントテスト"""
        text = "Hello, 世界! 123"
        result = self.counter.count_characters(text, "all")
        self.assertEqual(result["文字数"], len(text))
    
    def test_count_no_spaces(self):
        """空白文字を除くカウントテスト"""
        text = "Hello, 世界! 123"
        result = self.counter.count_characters(text, "no_spaces")
        expected = len(text.replace(' ', ''))
        self.assertEqual(result["文字数（空白除く）"], expected)
    
    def test_count_alphanumeric(self):
        """英数字のみのカウントテスト"""
        text = "Hello, 世界! 123"
        result = self.counter.count_characters(text, "alphanumeric")
        self.assertEqual(result["英数字文字数"], 8)  # Hello123
    
    def test_count_japanese(self):
        """日本語文字のみのカウントテスト"""
        text = "こんにちは カタカナ 漢字"
        result = self.counter.count_characters(text, "japanese")
        # こんにちは(5) + カタカナ(4) + 漢字(2) = 9 (spaces excluded)
        self.assertEqual(result["日本語文字数"], 9)
    
    def test_detailed_count(self):
        """詳細カウントテスト"""
        text = "Hello123 test!"
        result = self.counter.count_characters(text, "detailed")
        
        self.assertEqual(result["総文字数"], len(text))
        self.assertEqual(result["英字"], 9)  # Hello + test = 9
        self.assertEqual(result["数字"], 3)  # 123
        self.assertEqual(result["空白文字"], 1)
        self.assertEqual(result["記号"], 1)  # !
    
    def test_empty_string(self):
        """空文字列のテスト"""
        result = self.counter.count_characters("", "all")
        self.assertEqual(result["文字数"], 0)
    
    def test_invalid_count_type(self):
        """無効なカウント方式のテスト"""
        with self.assertRaises(ValueError):
            self.counter.count_characters("test", "invalid")
    
    def test_non_string_input(self):
        """文字列以外の入力のテスト"""
        with self.assertRaises(TypeError):
            self.counter.count_characters(123, "all")
    
    def test_count_from_file(self):
        """ファイルからのカウントテスト"""
        test_content = "テストファイル\nの内容です。"
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write(test_content)
            temp_file_path = f.name
        
        try:
            result = self.counter.count_from_file(temp_file_path, count_type="all")
            self.assertEqual(result["文字数"], len(test_content))
        finally:
            os.unlink(temp_file_path)
    
    def test_file_not_found(self):
        """存在しないファイルのテスト"""
        with self.assertRaises(Exception):
            self.counter.count_from_file("nonexistent_file.txt")
    
    def test_format_results(self):
        """結果の整形テスト"""
        results = {"文字数": 10, "英字": 5}
        formatted = self.counter.format_results(results)
        
        self.assertIn("=== 文字数カウント結果 ===", formatted)
        self.assertIn("文字数: 10", formatted)
        self.assertIn("英字: 5", formatted)


if __name__ == '__main__':
    unittest.main()