#!/usr/bin/env python3
"""Claude AGI 統合CLIツール

本モジュールは、複数のAGIツールを統合したコマンドラインインターフェースです。
各ツールを個別に実行することも、統合されたインターフェースから選択することも可能です。

使用例:
    $ python cli.py search "Python programming" --count 5
    $ python cli.py analyze sample.txt --type detailed
    $ python cli.py --list-tools
    $ python cli.py --interactive
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ローカルモジュールのインポート
try:
    from brave_search import BraveSearchClient, SearchConfig, InteractiveBraveSearch
    from text_analyzer import TextAnalyzer, AnalysisConfig, CountType, OutputFormat, InteractiveTextAnalyzer
except ImportError as e:
    logger.error(f"モジュールのインポートエラー: {e}")
    logger.error("必要な依存関係がインストールされていることを確認してください。")
    sys.exit(1)


class AGIToolCLI:
    """AGI統合CLIコントローラー"""
    
    TOOLS = {
        'search': {
            'description': 'Brave Search API を使用した高機能検索',
            'example': 'search "Python programming" --count 5 --format json'
        },
        'analyze': {
            'description': 'テキスト分析・文字数カウンター',
            'example': 'analyze sample.txt --type detailed --format csv'
        }
    }
    
    def __init__(self):
        """初期化"""
        self.parser = self._create_main_parser()
    
    def _create_main_parser(self) -> argparse.ArgumentParser:
        """メインパーサーを作成"""
        parser = argparse.ArgumentParser(
            description="Claude AGI 統合CLIツール",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_help_text()
        )
        
        subparsers = parser.add_subparsers(
            dest='tool',
            help='使用するツール',
            metavar='TOOL'
        )
        
        # 検索ツールのサブパーサー
        self._add_search_parser(subparsers)
        
        # テキスト分析ツールのサブパーサー
        self._add_analyze_parser(subparsers)
        
        # グローバルオプション
        parser.add_argument(
            '-l', '--list-tools',
            action='store_true',
            help='利用可能なツールの一覧を表示'
        )
        
        parser.add_argument(
            '-i', '--interactive',
            action='store_true',
            help='インタラクティブモードで起動'
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='Claude AGI CLI 1.0.0'
        )
        
        return parser
    
    def _add_search_parser(self, subparsers):
        """検索ツールのサブパーサーを追加"""
        search_parser = subparsers.add_parser(
            'search',
            help='Brave Search APIを使用した検索',
            description='Brave Search APIを使用した高機能検索ツール'
        )
        
        search_parser.add_argument(
            'query',
            help='検索クエリ'
        )
        
        search_parser.add_argument(
            '-c', '--count',
            type=int,
            default=10,
            help='取得する検索結果数（デフォルト: 10）'
        )
        
        search_parser.add_argument(
            '-f', '--format',
            choices=['text', 'json', 'csv'],
            default='text',
            help='出力フォーマット（デフォルト: text）'
        )
        
        search_parser.add_argument(
            '-o', '--output',
            type=Path,
            help='出力ファイルパス'
        )
        
        search_parser.add_argument(
            '-l', '--lang',
            default='ja',
            help='検索言語（デフォルト: ja）'
        )
        
        search_parser.add_argument(
            '--country',
            default='JP',
            help='検索対象国（デフォルト: JP）'
        )
        
        search_parser.add_argument(
            '--api-key',
            help='Brave Search APIキー'
        )
    
    def _add_analyze_parser(self, subparsers):
        """テキスト分析ツールのサブパーサーを追加"""
        analyze_parser = subparsers.add_parser(
            'analyze',
            help='テキスト分析・文字数カウンター',
            description='高機能テキスト分析・文字数カウンターツール'
        )
        
        # 入力ソース（互いに排他的）
        input_group = analyze_parser.add_mutually_exclusive_group(required=True)
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
        
        analyze_parser.add_argument(
            '-t', '--type',
            choices=[e.value for e in CountType],
            default=CountType.DETAILED.value,
            help='カウント方式（デフォルト: detailed）'
        )
        
        analyze_parser.add_argument(
            '-f', '--format',
            choices=[e.value for e in OutputFormat],
            default=OutputFormat.TEXT.value,
            help='出力フォーマット（デフォルト: text）'
        )
        
        analyze_parser.add_argument(
            '-o', '--output',
            type=Path,
            help='出力ファイルパス'
        )
        
        analyze_parser.add_argument(
            '-e', '--encoding',
            default='utf-8',
            help='ファイルの文字エンコーディング（デフォルト: utf-8）'
        )
    
    def _get_help_text(self) -> str:
        """ヘルプテキストを生成"""
        lines = ["\n利用可能なツール:"]
        
        for tool_name, tool_info in self.TOOLS.items():
            lines.append(f"  {tool_name:<10} - {tool_info['description']}")
            lines.append(f"             例: {tool_info['example']}")
            lines.append("")
        
        lines.extend([
            "グローバルオプション:",
            "  --list-tools   利用可能なツールの一覧を表示",
            "  --interactive  インタラクティブモードで起動",
            "  --version      バージョン情報を表示",
            "",
            "各ツールの詳細なヘルプ:",
            "  %(prog)s search --help",
            "  %(prog)s analyze --help"
        ])
        
        return "\n".join(lines)
    
    def run(self, args: Optional[List[str]] = None):
        """CLIを実行"""
        parsed_args = self.parser.parse_args(args)
        
        try:
            if parsed_args.list_tools:
                self._list_tools()
            elif parsed_args.interactive:
                self._run_interactive()
            elif parsed_args.tool == 'search':
                self._run_search(parsed_args)
            elif parsed_args.tool == 'analyze':
                self._run_analyze(parsed_args)
            else:
                self.parser.print_help()
        
        except KeyboardInterrupt:
            logger.info("操作を中断しました。")
            sys.exit(1)
        except Exception as e:
            logger.error(f"エラーが発生しました: {e}")
            sys.exit(1)
    
    def _list_tools(self):
        """利用可能なツールの一覧を表示"""
        print("=== Claude AGI 利用可能ツール ===\n")
        
        for tool_name, tool_info in self.TOOLS.items():
            print(f"🔧 {tool_name.upper()}")
            print(f"   {tool_info['description']}")
            print(f"   例: python cli.py {tool_info['example']}")
            print()
    
    def _run_interactive(self):
        """インタラクティブモードを実行"""
        print("=== Claude AGI インタラクティブモード ===")
        print("使用するツールを選択してください。")
        
        while True:
            try:
                print("\n利用可能なツール:")
                for i, (tool_name, tool_info) in enumerate(self.TOOLS.items(), 1):
                    print(f"{i}. {tool_name.upper()} - {tool_info['description']}")
                print("0. 終了")
                
                choice = input("\n選択してください (0-{}): ".format(len(self.TOOLS))).strip()
                
                if choice == "0":
                    print("インタラクティブモードを終了します。")
                    break
                elif choice == "1":
                    # 検索ツール
                    client = BraveSearchClient()
                    interactive = InteractiveBraveSearch(client)
                    interactive.run()
                elif choice == "2":
                    # テキスト分析ツール
                    analyzer = TextAnalyzer()
                    interactive = InteractiveTextAnalyzer(analyzer)
                    interactive.run()
                else:
                    print("無効な選択です。")
            
            except KeyboardInterrupt:
                print("\n\nインタラクティブモードを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    def _run_search(self, args):
        """検索ツールを実行"""
        client = BraveSearchClient(api_key=args.api_key)
        
        config = SearchConfig(
            query=args.query,
            count=args.count,
            output_format=args.format,
            output_file=args.output,
            search_lang=args.lang,
            country=args.country
        )
        
        logger.info(f"'{config.query}' を検索中...")
        results = client.search(config)
        
        if results:
            formatted_results = client.format_results(results, config.output_format)
            
            if config.output_file:
                config.output_file.write_text(formatted_results, encoding='utf-8')
                logger.info(f"結果を {config.output_file} に保存しました。")
            else:
                print(formatted_results)
        else:
            logger.error("検索に失敗しました。")
            sys.exit(1)
    
    def _run_analyze(self, args):
        """テキスト分析ツールを実行"""
        analyzer = TextAnalyzer()
        
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
            config.output_file.write_text(formatted_results, encoding='utf-8')
            logger.info(f"結果を {config.output_file} に保存しました。")
        else:
            print(formatted_results)


def main():
    """メイン関数"""
    cli = AGIToolCLI()
    cli.run()


if __name__ == "__main__":
    main()