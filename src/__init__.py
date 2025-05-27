"""Claude AGI �����

,�ñ��oAIv��zg(U��N(�j��뤒ЛW~Y
"ƭ���jin_��qU�_���է��g)(gM~Y

;�����:
    - brave_search: Brave Search API�(W_"_�
    - text_analyzer: �_�ƭ�����Wp����
    - cli: q��������է��

(�:
    >>> from src.text_analyzer import TextAnalyzer, CountType
    >>> analyzer = TextAnalyzer()
    >>> result = analyzer.count_characters("Hello L", CountType.DETAILED)
    >>> print(result)
"""
from __future__ import annotations

__version__ = "1.0.0"
__author__ = "Claude AGI Project"
__description__ = "N(�jAGI�����"

# �ñ��n����
__all__ = [
    "brave_search",
    "text_analyzer", 
    "cli"
]