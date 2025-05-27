#!/usr/bin/env python3
"""Brave Search ツール: 高機能検索アプリケーション

本モジュールは、Brave Search APIを使用した検索機能を提供します。
CLI、インタラクティブモード、プログラマブルAPIの3つの使用方法に対応しています。

使用例:
    $ python brave_search.py "Python programming" --count 5 --format json
    $ python brave_search.py --interactive
    $ from brave_search import BraveSearchClient; client = BraveSearchClient()
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from brave import Brave
except ImportError:
    logger.error("Error: brave-search パッケージがインストールされていません。")
    logger.error("pip install brave-search を実行してください。")
    sys.exit(1)


@dataclass(frozen=True)
class SearchConfig:
    """検索設定を保持するデータクラス"""
    query: str
    count: int = 10
    output_format: str = "text"
    output_file: Optional[Path] = None
    search_lang: str = "ja"
    country: str = "JP"

    def __post_init__(self):
        if self.count <= 0:
            raise ValueError("count は正の整数である必要があります")
        if self.output_format not in ["text", "json", "csv"]:
            raise ValueError("output_format は 'text', 'json', 'csv' のいずれかである必要があります")


class BraveSearchClient:
    """Brave Search APIクライアント
    
    Brave Search APIへのアクセスを提供する高レベルインターフェース。
    エラーハンドリング、結果の整形、複数の出力フォーマットに対応。
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """BraveSearchClientの初期化
        
        Args:
            api_key: Brave Search APIキー。Noneの場合は環境変数から取得
            
        Raises:
            ValueError: APIキーが設定されていない場合
            RuntimeError: Brave APIの初期化に失敗した場合
        """
        self._api_key = api_key or os.getenv('BRAVE_API_KEY')
        if not self._api_key:
            raise ValueError(
                "BRAVE_API_KEY環境変数が設定されていないか、api_keyが提供されていません。"
                "Brave Search APIキーを環境変数として設定してください。"
            )
        
        try:
            self.brave = Brave()
        except Exception as e:
            raise RuntimeError(f"Brave Search APIの初期化に失敗しました: {e}") from e
    
    def search(self, config: SearchConfig) -> Optional[dict[str, Any]]:
        """検索を実行
        
        Args:
            config: 検索設定
            
        Returns:
            検索結果辞書。エラーの場合はNone
            
        Raises:
            ValueError: 無効な検索設定の場合
        """
        if not config.query.strip():
            raise ValueError("検索クエリが空です")
        
        try:
            results = self.brave.search(
                q=config.query,
                count=config.count,
                search_lang=config.search_lang,
                country=config.country
            )
            return results
        except Exception as e:
            logger.error(f"検索中にエラーが発生しました: {e}")
            return None
    
    def format_results(self, results: Any, format_type: str = "text") -> str:
        """検索結果を指定されたフォーマットで整形
        
        Args:
            results: Brave Search APIからの検索結果
            format_type: 出力フォーマット ('text', 'json', 'csv')
            
        Returns:
            整形された結果文字列
        """
        if not results or not hasattr(results, 'web_results'):
            return "検索結果が見つかりませんでした。"
        
        web_results = results.web_results
        if not web_results:
            return "ウェブ検索結果が見つかりませんでした。"
        
        if format_type == "json":
            return self._format_json(web_results)
        elif format_type == "csv":
            return self._format_csv(web_results)
        else:  # text
            return self._format_text(web_results)
    
    def _format_text(self, web_results: list[Any]) -> str:
        """テキストフォーマットで整形"""
        lines = [f"=== 検索結果 ({len(web_results)}件) ===\n"]
        
        for i, result in enumerate(web_results, 1):
            lines.append(f"{i}. {result.title}")
            lines.append(f"URL: {result.url}")
            if hasattr(result, 'description') and result.description:
                lines.append(f"説明: {result.description}")
            lines.append("-" * 50)
        
        return "\n".join(lines)
    
    def _format_json(self, web_results: list[Any]) -> str:
        """JSONフォーマットで整形"""
        results_data = []
        for result in web_results:
            result_dict = {
                "title": result.title,
                "url": result.url,
                "description": getattr(result, 'description', '')
            }
            results_data.append(result_dict)
        
        return json.dumps({"results": results_data}, ensure_ascii=False, indent=2)
    
    def _format_csv(self, web_results: list[Any]) -> str:
        """CSVフォーマットで整形"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Title", "URL", "Description"])
        
        for result in web_results:
            title = result.title
            url = result.url
            description = getattr(result, 'description', '')
            writer.writerow([title, url, description])
        
        return output.getvalue()


class InteractiveBraveSearch:
    """インタラクティブな検索セッション"""
    
    def __init__(self, client: BraveSearchClient):
        """初期化
        
        Args:
            client: BraveSearchClientインスタンス
        """
        self.client = client
    
    def run(self):
        """インタラクティブな検索セッションを実行"""
        print("=== Brave Search アプリケーション ===")
        print("検索を開始します。終了するには 'quit' または 'exit' を入力してください。\n")
        
        while True:
            try:
                query = input("検索クエリを入力してください: ").strip()
                
                if query.lower() in ['quit', 'exit', '終了']:
                    print("検索を終了します。")
                    break
                
                if not query:
                    print("検索クエリを入力してください。")
                    continue
                
                # 結果数を入力（オプション）
                count_input = input("取得する結果数を入力してください（デフォルト: 10）: ").strip()
                try:
                    count = int(count_input) if count_input else 10
                    if count <= 0:
                        count = 10
                        print("結果数は正の数である必要があります。デフォルト値 10 を使用します。")
                except ValueError:
                    count = 10
                    print("無効な数値です。デフォルト値 10 を使用します。")
                
                # 出力フォーマットを選択
                format_input = input("出力フォーマットを選択してください (text/json/csv、デフォルト: text): ").strip()
                output_format = format_input if format_input in ["text", "json", "csv"] else "text"
                
                config = SearchConfig(
                    query=query,
                    count=count,
                    output_format=output_format
                )
                
                print(f"\n'{query}' を検索中...")
                results = self.client.search(config)
                
                if results:
                    formatted_results = self.client.format_results(results, output_format)
                    print(formatted_results)
                else:
                    print("検索に失敗しました。")
                
                print("\n" + "="*60)
                
            except KeyboardInterrupt:
                print("\n\n検索を中断しました。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")


def create_parser() -> argparse.ArgumentParser:
    """CLIのargparseパーサーを作成"""
    parser = argparse.ArgumentParser(
        description="Brave Search APIを使用した高機能検索ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s "Python programming" --count 5
  %(prog)s "機械学習" --format json --output results.json
  %(prog)s --interactive
  %(prog)s "データサイエンス" --lang en --country US
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='検索クエリ（インタラクティブモード以外では必須）'
    )
    
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=10,
        help='取得する検索結果数（デフォルト: 10）'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'csv'],
        default='text',
        help='出力フォーマット（デフォルト: text）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='出力ファイルパス（指定しない場合は標準出力）'
    )
    
    parser.add_argument(
        '-l', '--lang',
        default='ja',
        help='検索言語（デフォルト: ja）'
    )
    
    parser.add_argument(
        '--country',
        default='JP',
        help='検索対象国（デフォルト: JP）'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='インタラクティブモードで起動'
    )
    
    parser.add_argument(
        '--api-key',
        help='Brave Search APIキー（環境変数BRAVE_API_KEYでも設定可能）'
    )
    
    return parser


def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # クライアントの初期化
        client = BraveSearchClient(api_key=args.api_key)
        
        if args.interactive:
            # インタラクティブモード
            interactive = InteractiveBraveSearch(client)
            interactive.run()
        else:
            # CLIモード
            if not args.query:
                parser.error("クエリが指定されていません。--interactive を使用するか、検索クエリを指定してください。")
            
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
                    # ファイルに出力
                    config.output_file.write_text(formatted_results, encoding='utf-8')
                    logger.info(f"結果を {config.output_file} に保存しました。")
                else:
                    # 標準出力
                    print(formatted_results)
            else:
                logger.error("検索に失敗しました。")
                sys.exit(1)
    
    except ValueError as e:
        parser.error(str(e))
    except KeyboardInterrupt:
        logger.info("検索を中断しました。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()