"""Claude AGI ツールキット

汎用的で洗練されたAIツールの集合体です。検索、分析、
文字解析などの様々なタスクを効率的に実行できます。

主要モジュール:
    - brave_search: Brave Search APIを使用した検索機能
    - text_analyzer: 文字解析と統計処理機能
    - cli: コマンドライン統合インターフェース

使用例:
    >>> from src.text_analyzer import TextAnalyzer, CountType
    >>> analyzer = TextAnalyzer()
    >>> result = analyzer.count_characters("Hello World", CountType.DETAILED)
    >>> print(result)
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Claude AGI Project"
__description__ = "汎用的なAGIツールキット"

# 主要モジュール
__all__ = [
    "brave_search",
    "text_analyzer", 
    "cli"
]