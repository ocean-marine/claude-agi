#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキスト文字数取得ツール

このモジュールは文字列の文字数を様々な方法で計算するツールを提供します。
"""

import sys
import re
from typing import Dict, Optional, Union
from pathlib import Path


class TextCharacterCounter:
    """テキストの文字数を取得するためのクラス"""
    
    def __init__(self):
        """TextCharacterCounterの初期化"""
        pass
    
    def count_characters(self, text: str, count_type: str = "all") -> Dict[str, int]:
        """
        テキストの文字数を様々な方法でカウント
        
        Args:
            text (str): カウント対象のテキスト
            count_type (str): カウント方式
                - "all": 全文字（デフォルト）
                - "no_spaces": 空白文字を除く
                - "alphanumeric": 英数字のみ
                - "japanese": ひらがな・カタカナ・漢字のみ
                - "detailed": 詳細な分類別カウント
        
        Returns:
            Dict[str, int]: 文字数の結果
        """
        if not isinstance(text, str):
            raise TypeError("テキストは文字列である必要があります")
        
        if count_type == "all":
            return {"文字数": len(text)}
        
        elif count_type == "no_spaces":
            no_space_text = re.sub(r'\s', '', text)
            return {"文字数（空白除く）": len(no_space_text)}
        
        elif count_type == "alphanumeric":
            alphanumeric_chars = re.findall(r'[a-zA-Z0-9]', text)
            return {"英数字文字数": len(alphanumeric_chars)}
        
        elif count_type == "japanese":
            japanese_chars = re.findall(r'[ひらがな-ヿカタカナ-ヿ一-龯]', text)
            return {"日本語文字数": len(japanese_chars)}
        
        elif count_type == "detailed":
            return self._detailed_count(text)
        
        else:
            raise ValueError(f"無効なカウント方式です: {count_type}")
    
    def _detailed_count(self, text: str) -> Dict[str, int]:
        """
        文字列の詳細な分類別カウント
        
        Args:
            text (str): カウント対象のテキスト
            
        Returns:
            Dict[str, int]: 詳細な文字数情報
        """
        result = {
            "総文字数": len(text),
            "英字": len(re.findall(r'[a-zA-Z]', text)),
            "数字": len(re.findall(r'[0-9]', text)),
            "ひらがな": len(re.findall(r'[ひらがな-ゖ]', text)),
            "カタカナ": len(re.findall(r'[カタカナ-ヿ]', text)),
            "漢字": len(re.findall(r'[一-龯]', text)),
            "記号": len(re.findall(r'[!-/:-@\[-`{-~]', text)),
            "空白文字": len(re.findall(r'\s', text)),
            "改行": text.count('\n'),
            "その他": 0
        }
        
        # その他の文字数を計算
        counted = sum(result[key] for key in result if key not in ["総文字数", "その他"])
        result["その他"] = result["総文字数"] - counted
        
        return result
    
    def count_from_file(self, file_path: Union[str, Path], 
                       encoding: str = "utf-8", 
                       count_type: str = "all") -> Dict[str, int]:
        """
        ファイルから文字数をカウント
        
        Args:
            file_path (Union[str, Path]): ファイルパス
            encoding (str): 文字エンコーディング（デフォルト: utf-8）
            count_type (str): カウント方式
            
        Returns:
            Dict[str, int]: 文字数の結果
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return self.count_characters(content, count_type)
        
        except Exception as e:
            raise Exception(f"ファイル読み込みエラー: {e}")
    
    def format_results(self, results: Dict[str, int]) -> str:
        """
        カウント結果を整形して表示用文字列を生成
        
        Args:
            results (Dict[str, int]): カウント結果
            
        Returns:
            str: 整形された結果文字列
        """
        output_lines = ["=== 文字数カウント結果 ==="]
        
        for key, value in results.items():
            output_lines.append(f"{key}: {value:,}")
        
        return "\n".join(output_lines)


class InteractiveCharacterCounter:
    """インタラクティブな文字数カウンターアプリケーション"""
    
    def __init__(self):
        """InteractiveCharacterCounterの初期化"""
        self.counter = TextCharacterCounter()
    
    def show_menu(self):
        """メニューを表示"""
        print("\n=== 文字数取得ツール ===")
        print("1. 直接テキスト入力")
        print("2. ファイルから読み込み")
        print("3. 終了")
        print("選択してください (1-3): ", end="")
    
    def show_count_type_menu(self):
        """カウント方式選択メニューを表示"""
        print("\n=== カウント方式を選択 ===")
        print("1. 全文字")
        print("2. 空白文字を除く")
        print("3. 英数字のみ")
        print("4. 日本語文字のみ")
        print("5. 詳細分類")
        print("選択してください (1-5): ", end="")
    
    def get_count_type(self, choice: str) -> str:
        """選択番号からカウント方式を取得"""
        count_types = {
            "1": "all",
            "2": "no_spaces", 
            "3": "alphanumeric",
            "4": "japanese",
            "5": "detailed"
        }
        return count_types.get(choice, "all")
    
    def run(self):
        """インタラクティブセッションを実行"""
        print("文字数取得ツールを開始します。")
        
        while True:
            try:
                self.show_menu()
                choice = input().strip()
                
                if choice == "1":
                    self._handle_text_input()
                elif choice == "2":
                    self._handle_file_input()
                elif choice == "3":
                    print("文字数取得ツールを終了します。")
                    break
                else:
                    print("無効な選択です。1-3の数字を入力してください。")
                
            except KeyboardInterrupt:
                print("\n\n処理を中断しました。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    def _handle_text_input(self):
        """直接テキスト入力を処理"""
        print("\nテキストを入力してください（複数行可、終了は空行で Enter）:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        
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
            self.show_count_type_menu()
            count_choice = input().strip()
            count_type = self.get_count_type(count_choice)
            
            results = self.counter.count_from_file(file_path, count_type=count_type)
            formatted_results = self.counter.format_results(results)
            print(f"\n{formatted_results}")
            
        except Exception as e:
            print(f"ファイル処理エラー: {e}")
    
    def _count_and_display(self, text: str):
        """文字数をカウントして表示"""
        self.show_count_type_menu()
        count_choice = input().strip()
        count_type = self.get_count_type(count_choice)
        
        results = self.counter.count_characters(text, count_type)
        formatted_results = self.counter.format_results(results)
        print(f"\n{formatted_results}")


def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        # コマンドライン引数が指定された場合
        if sys.argv[1] in ["-h", "--help"]:
            print_help()
            return
        
        # ファイルパスが指定された場合
        file_path = sys.argv[1]
        count_type = sys.argv[2] if len(sys.argv) > 2 else "detailed"
        
        try:
            counter = TextCharacterCounter()
            results = counter.count_from_file(file_path, count_type=count_type)
            formatted_results = counter.format_results(results)
            print(formatted_results)
        except Exception as e:
            print(f"エラー: {e}")
            sys.exit(1)
    else:
        # インタラクティブモード
        app = InteractiveCharacterCounter()
        app.run()


def print_help():
    """ヘルプメッセージを表示"""
    help_text = """
文字数取得ツール

使用方法:
  python text_character_counter.py [ファイルパス] [カウント方式]
  python text_character_counter.py  # インタラクティブモード

カウント方式:
  all         - 全文字（デフォルト）
  no_spaces   - 空白文字を除く
  alphanumeric- 英数字のみ
  japanese    - 日本語文字のみ
  detailed    - 詳細分類

例:
  python text_character_counter.py sample.txt detailed
  python text_character_counter.py document.txt no_spaces
"""
    print(help_text)


if __name__ == "__main__":
    main()