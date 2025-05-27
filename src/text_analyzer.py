#!/usr/bin/env python3
"""テキスト分析ツール: 高機能文字数カウンター

本モジュールは、テキストの文字数を様々な方法でカウント・分析するツールです。
CLI、インタラクティブモード、プログラマブルAPIの3つの使用方法に対応しています。

使用例:
    $ python text_analyzer.py sample.txt --type detailed --output results.json
    $ python text_analyzer.py --interactive
    $ from text_analyzer import TextAnalyzer; analyzer = TextAnalyzer()
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union


class CountType(Enum):
    """カウント方式の列挙型"""
    ALL = "all"
    NO_SPACES = "no_spaces"
    ALPHANUMERIC = "alphanumeric"
    JAPANESE = "japanese"
    DETAILED = "detailed"


class OutputFormat(Enum):
    """出力フォーマットの列挙型"""
    TEXT = "text"
    JSON = "json"
    CSV = "csv"


@dataclass(frozen=True)
class AnalysisConfig:
    """分析設定を保持するデータクラス"""
    text: Optional[str] = None
    file_path: Optional[Path] = None
    count_type: CountType = CountType.DETAILED
    output_format: OutputFormat = OutputFormat.TEXT
    output_file: Optional[Path] = None
    encoding: str = "utf-8"

    def __post_init__(self):
        if not self.text and not self.file_path:
            raise ValueError("テキストまたはファイルパスのいずれかを指定する必要があります")
        if self.text and self.file_path:
            raise ValueError("テキストとファイルパスの両方を指定することはできません")


class TextAnalyzer:
    """テキスト分析・文字数カウンタークラス
    
    テキストの文字数を様々な方法でカウントし、詳細な分析結果を提供します。
    日本語文字、英数字、記号の分類カウントにも対応しています。
    """
    
    # 正規表現パターンをクラス変数として定義（効率化）
    _PATTERNS = {
        'english': re.compile(r'[a-zA-Z]'),
        'digits': re.compile(r'[0-9]'),
        'hiragana': re.compile(r'[ひらがな-ゖ]'),
        'katakana': re.compile(r'[カタカナ-ヿ]'),
        'kanji': re.compile(r'[一-龯]'),
        'symbols': re.compile(r'[!-/:-@\[-`{-~]'),
        'whitespace': re.compile(r'\s'),
        'japanese_all': re.compile(r'[ひらがな-ヿカタカナ-ヿ一-龯]'),
        'alphanumeric': re.compile(r'[a-zA-Z0-9]')
    }
    
    def count_characters(self, text: str, count_type: CountType = CountType.ALL) -> Dict[str, int]:
        """テキストの文字数を指定された方式でカウント
        
        Args:
            text: カウント対象のテキスト
            count_type: カウント方式
            
        Returns:
            文字数の結果辞書
            
        Raises:
            TypeError: テキストが文字列でない場合
            ValueError: 無効なカウント方式の場合
        """
        if not isinstance(text, str):
            raise TypeError("テキストは文字列である必要があります")
        
        match count_type:
            case CountType.ALL:
                return {"文字数": len(text)}
            case CountType.NO_SPACES:
                no_space_text = self._PATTERNS['whitespace'].sub('', text)
                return {"文字数（空白除く）": len(no_space_text)}
            case CountType.ALPHANUMERIC:
                alphanumeric_chars = self._PATTERNS['alphanumeric'].findall(text)
                return {"英数字文字数": len(alphanumeric_chars)}
            case CountType.JAPANESE:
                japanese_chars = self._PATTERNS['japanese_all'].findall(text)
                return {"日本語文字数": len(japanese_chars)}
            case CountType.DETAILED:
                return self._detailed_count(text)
            case _:
                raise ValueError(f"無効なカウント方式です: {count_type}")
    
    def _detailed_count(self, text: str) -> Dict[str, int]:
        """文字列の詳細な分類別カウント
        
        Args:
            text: カウント対象のテキスト
            
        Returns:
            詳細な文字数情報の辞書
        """
        result = {
            "総文字数": len(text),
            "英字": len(self._PATTERNS['english'].findall(text)),
            "数字": len(self._PATTERNS['digits'].findall(text)),
            "ひらがな": len(self._PATTERNS['hiragana'].findall(text)),
            "カタカナ": len(self._PATTERNS['katakana'].findall(text)),
            "漢字": len(self._PATTERNS['kanji'].findall(text)),
            "記号": len(self._PATTERNS['symbols'].findall(text)),
            "空白文字": len(self._PATTERNS['whitespace'].findall(text)),
            "改行": text.count('\n'),
            "行数": len(text.splitlines()),
            "単語数": len(text.split()),
            "その他": 0
        }
        
        # その他の文字数を計算
        counted = sum(
            result[key] for key in result 
            if key not in ["総文字数", "その他", "行数", "単語数"]
        )
        result["その他"] = result["総文字数"] - counted
        
        return result
    
    def count_from_file(self, file_path: Union[str, Path], 
                       encoding: str = "utf-8", 
                       count_type: CountType = CountType.ALL) -> Dict[str, int]:
        """ファイルから文字数をカウント
        
        Args:
            file_path: ファイルパス
            encoding: 文字エンコーディング
            count_type: カウント方式
            
        Returns:
            文字数の結果辞書
            
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            IOError: ファイル読み込みエラーの場合
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        try:
            content = file_path.read_text(encoding=encoding)
            return self.count_characters(content, count_type)
        except UnicodeDecodeError as e:
            raise IOError(f"ファイルの文字エンコーディングエラー: {e}") from e
        except Exception as e:
            raise IOError(f"ファイル読み込みエラー: {e}") from e
    
    def format_results(self, results: Dict[str, int], output_format: OutputFormat = OutputFormat.TEXT) -> str:
        """カウント結果を指定されたフォーマットで整形
        
        Args:
            results: カウント結果辞書
            output_format: 出力フォーマット
            
        Returns:
            整形された結果文字列
        """
        match output_format:
            case OutputFormat.JSON:
                return json.dumps(results, ensure_ascii=False, indent=2)
            case OutputFormat.CSV:
                return self._format_csv(results)
            case OutputFormat.TEXT:
                return self._format_text(results)
            case _:
                raise ValueError(f"無効な出力フォーマット: {output_format}")
    
    def _format_text(self, results: Dict[str, int]) -> str:
        """テキストフォーマットで整形"""
        lines = ["=== 文字数分析結果 ==="]
        
        for key, value in results.items():
            lines.append(f"{key}: {value:,}")
        
        return "\n".join(lines)
    
    def _format_csv(self, results: Dict[str, int]) -> str:
        """CSVフォーマットで整形"""
        lines = ["Category,Count"]
        
        for key, value in results.items():
            # CSVのため、カンマを含む可能性のあるキーをエスケープ
            escaped_key = key.replace('"', '""')
            lines.append(f'"{escaped_key}",{value}')
        
        return "\n".join(lines)
    
    def analyze_with_config(self, config: AnalysisConfig) -> Dict[str, int]:
        """設定に基づいてテキストを分析
        
        Args:
            config: 分析設定
            
        Returns:
            分析結果辞書
        """
        if config.text:
            return self.count_characters(config.text, config.count_type)
        elif config.file_path:
            return self.count_from_file(config.file_path, config.encoding, config.count_type)
        else:
            raise ValueError("テキストまたはファイルパスが設定されていません")


class InteractiveTextAnalyzer:
    """インタラクティブなテキスト分析セッション"""
    
    def __init__(self, analyzer: TextAnalyzer):
        """初期化
        
        Args:
            analyzer: TextAnalyzerインスタンス
        """
        self.analyzer = analyzer
    
    def run(self):
        """インタラクティブセッションを実行"""
        print("=== テキスト分析ツール ===")
        print("テキストの文字数分析を開始します。")
        
        while True:
            try:
                self._show_menu()
                choice = input().strip()
                
                match choice:
                    case "1":
                        self._handle_text_input()
                    case "2":
                        self._handle_file_input()
                    case "3":
                        print("テキスト分析ツールを終了します。")
                        break
                    case _:
                        print("無効な選択です。1-3の数字を入力してください。")
                
            except KeyboardInterrupt:
                print("\n\n処理を中断しました。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    def _show_menu(self):
        """メニューを表示"""
        print("\n=== メニュー ===")
        print("1. 直接テキスト入力")
        print("2. ファイルから読み込み")
        print("3. 終了")
        print("選択してください (1-3): ", end="")
    
    def _show_count_type_menu(self):
        """カウント方式選択メニューを表示"""
        print("\n=== カウント方式を選択 ===")
        print("1. 全文字")
        print("2. 空白文字を除く")
        print("3. 英数字のみ")
        print("4. 日本語文字のみ")
        print("5. 詳細分類")
        print("選択してください (1-5): ", end="")
    
    def _get_count_type(self, choice: str) -> CountType:
        """選択番号からカウント方式を取得"""
        count_types = {
            "1": CountType.ALL,
            "2": CountType.NO_SPACES,
            "3": CountType.ALPHANUMERIC,
            "4": CountType.JAPANESE,
            "5": CountType.DETAILED
        }
        return count_types.get(choice, CountType.DETAILED)
    
    def _handle_text_input(self):
        """直接テキスト入力を処理"""
        print("\nテキストを入力してください（複数行可、終了は空行で Enter）:")
        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    break
                lines.append(line)
            except EOFError:
                break
        
        text = "\n".join(lines)
        if not text.strip():
            print("テキストが入力されていません。")
            return
        
        self._count_and_display(text)
    
    def _handle_file_input(self):
        """ファイル入力を処理"""
        file_path = input("ファイルパスを入力してください: ").strip()
        if not file_path:
            print("ファイルパスが入力されていません。")
            return
        
        try:
            self._show_count_type_menu()
            count_choice = input().strip()
            count_type = self._get_count_type(count_choice)
            
            results = self.analyzer.count_from_file(file_path, count_type=count_type)
            formatted_results = self.analyzer.format_results(results)
            print(f"\n{formatted_results}")
            
        except Exception as e:
            print(f"ファイル処理エラー: {e}")
    
    def _count_and_display(self, text: str):
        """文字数をカウントして表示"""
        self._show_count_type_menu()
        count_choice = input().strip()
        count_type = self._get_count_type(count_choice)
        
        results = self.analyzer.count_characters(text, count_type)
        formatted_results = self.analyzer.format_results(results)
        print(f"\n{formatted_results}")


def create_parser() -> argparse.ArgumentParser:
    """CLIのargparseパーサーを作成"""
    parser = argparse.ArgumentParser(
        description="高機能テキスト分析・文字数カウンターツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
カウント方式:
  all         - 全文字（デフォルト）
  no_spaces   - 空白文字を除く
  alphanumeric- 英数字のみ
  japanese    - 日本語文字のみ
  detailed    - 詳細分類（推奨）

使用例:
  %(prog)s sample.txt --type detailed --format json
  %(prog)s document.txt --type no_spaces --output result.csv
  %(prog)s --interactive
  %(prog)s --text "解析したいテキスト" --type detailed
        """
    )
    
    # 入力ソース（互いに排他的）
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        'file_path',
        nargs='?',
        type=Path,
        help='分析対象のファイルパス'
    )
    input_group.add_argument(
        '--text',
        help='直接指定するテキスト'
    )
    
    # 分析オプション
    parser.add_argument(
        '-t', '--type',
        choices=[e.value for e in CountType],
        default=CountType.DETAILED.value,
        help='カウント方式（デフォルト: detailed）'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=[e.value for e in OutputFormat],
        default=OutputFormat.TEXT.value,
        help='出力フォーマット（デフォルト: text）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='出力ファイルパス（指定しない場合は標準出力）'
    )
    
    parser.add_argument(
        '-e', '--encoding',
        default='utf-8',
        help='ファイルの文字エンコーディング（デフォルト: utf-8）'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='インタラクティブモードで起動'
    )
    
    return parser


def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        analyzer = TextAnalyzer()
        
        if args.interactive:
            # インタラクティブモード
            interactive = InteractiveTextAnalyzer(analyzer)
            interactive.run()
        else:
            # CLIモード
            if not args.file_path and not args.text:
                parser.error("ファイルパスまたは--textオプション、もしくは--interactiveを指定してください。")
            
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
                # ファイルに出力
                config.output_file.write_text(formatted_results, encoding='utf-8')
                print(f"結果を {config.output_file} に保存しました。", file=sys.stderr)
            else:
                # 標準出力
                print(formatted_results)
    
    except (ValueError, TypeError, FileNotFoundError, IOError) as e:
        parser.error(str(e))
    except KeyboardInterrupt:
        print("\n分析を中断しました。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()