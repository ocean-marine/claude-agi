import os
import sys
from brave import Brave


class BraveSearchApp:
    """Brave Search APIを使用した検索アプリケーション"""
    
    def __init__(self):
        """BraveSearchAppの初期化"""
        try:
            self.brave = Brave()
        except Exception as e:
            print(f"Brave Search APIの初期化に失敗しました: {e}")
            sys.exit(1)
    
    def search(self, query: str, count: int = 10):
        """
        指定されたクエリで検索を実行
        
        Args:
            query (str): 検索クエリ
            count (int): 取得する結果数（デフォルト: 10）
            
        Returns:
            検索結果オブジェクト
        """
        try:
            results = self.brave.search(q=query, count=count)
            return results
        except Exception as e:
            print(f"検索中にエラーが発生しました: {e}")
            return None
    
    def format_results(self, results):
        """
        検索結果を日本語で整形して表示
        
        Args:
            results: Brave Search APIからの検索結果
        """
        if not results or not hasattr(results, 'web_results'):
            print("検索結果が見つかりませんでした。")
            return
        
        web_results = results.web_results
        if not web_results:
            print("ウェブ検索結果が見つかりませんでした。")
            return
        
        print(f"\n=== 検索結果 ({len(web_results)}件) ===")
        for i, result in enumerate(web_results, 1):
            print(f"\n{i}. {result.title}")
            print(f"URL: {result.url}")
            if hasattr(result, 'description') and result.description:
                print(f"説明: {result.description}")
            print("-" * 50)
    
    def run(self):
        """
        インタラクティブな検索セッションを実行
        """
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
                
                print(f"\n'{query}' を検索中...")
                results = self.search(query, count)
                
                if results:
                    self.format_results(results)
                else:
                    print("検索に失敗しました。")
                
                print("\n" + "="*60)
                
            except KeyboardInterrupt:
                print("\n\n検索を中断しました。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")


def main():
    """メイン関数"""
    # 環境変数のチェック
    if not os.getenv('BRAVE_API_KEY'):
        print("エラー: BRAVE_API_KEY環境変数が設定されていません。")
        print("Brave Search APIキーを環境変数として設定してください。")
        sys.exit(1)
    
    app = BraveSearchApp()
    app.run()


if __name__ == "__main__":
    main()