#!/usr/bin/env python3
"""
備蓄米についてのニュースを検索するスクリプト
Brave Search APIを使用して関連ニュースを取得
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any


class StockpiledRiceNewsSearcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
    
    def search_news(self, query: str, count: int = 10) -> Dict[str, Any]:
        """指定されたクエリでニュースを検索"""
        params = {
            "q": query,
            "count": count,
            "search_lang": "jp",
            "country": "JP"
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API呼び出しエラー: {e}")
            return {}
    
    def search_comprehensive_stockpiled_rice_news(self) -> List[Dict[str, Any]]:
        """備蓄米に関する包括的なニュース検索"""
        search_queries = [
            "備蓄米についてのニュース",
            "政府備蓄米",
            "備蓄米 放出",
            "備蓄米 在庫"
        ]
        
        all_results = []
        seen_urls = set()
        
        print("🔍 備蓄米についてのニュースを検索中...")
        print("=" * 60)
        
        for i, query in enumerate(search_queries):
            print(f"検索クエリ {i+1}/{len(search_queries)}: {query}")
            results = self.search_news(query, count=10)
            
            if "web" in results and "results" in results["web"]:
                for result in results["web"]["results"]:
                    url = result.get("url", "")
                    title = result.get("title", "")
                    description = result.get("description", "")
                    
                    # 重複除去
                    if url not in seen_urls and title and description:
                        seen_urls.add(url)
                        all_results.append({
                            "title": title,
                            "url": url,
                            "description": description,
                            "query": query
                        })
                
                print(f"  → {len(results.get('web', {}).get('results', []))} 件見つかりました")
            else:
                print(f"  → 結果が見つかりませんでした")
            
            # レート制限対策として少し待機
            import time
            if i < len(search_queries) - 1:
                time.sleep(2)
        
        print(f"\n📊 合計 {len(all_results)} 件のユニークなニュース記事を発見")
        return all_results
    
    def display_results(self, results: List[Dict[str, Any]]):
        """検索結果を整形して表示"""
        if not results:
            print("❌ ニュース記事が見つかりませんでした。")
            return
        
        print("\n" + "=" * 80)
        print("📰 備蓄米についてのニュース検索結果")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n【{i}】 {result['title']}")
            print(f"📝 {result['description']}")
            print(f"🔗 {result['url']}")
            print(f"🔍 検索クエリ: {result['query']}")
            print("-" * 80)
    
    def save_results_to_file(self, results: List[Dict[str, Any]]):
        """検索結果をファイルに保存"""
        if not results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stockpiled_rice_news_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 検索結果を {filename} に保存しました")
        
        # テキスト版も保存
        txt_filename = f"stockpiled_rice_news_{timestamp}.txt"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("備蓄米についてのニュース検索結果\n")
            f.write("=" * 80 + "\n")
            f.write(f"検索日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"総記事数: {len(results)}\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"【{i}】 {result['title']}\n")
                f.write(f"📝 {result['description']}\n")
                f.write(f"🔗 {result['url']}\n")
                f.write(f"🔍 検索クエリ: {result['query']}\n")
                f.write("-" * 80 + "\n")
        
        print(f"📄 読みやすい形式で {txt_filename} にも保存しました")


def main():
    # 環境変数からAPIキーを取得
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        print("❌ エラー: BRAVE_API_KEY環境変数が設定されていません")
        print("以下のコマンドでAPIキーを設定してください:")
        print("export BRAVE_API_KEY='your_api_key_here'")
        return
    
    print("🚀 備蓄米ニュース検索を開始します...")
    print(f"⏰ 検索開始時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    # 検索実行
    searcher = StockpiledRiceNewsSearcher(api_key)
    results = searcher.search_comprehensive_stockpiled_rice_news()
    
    # 結果表示
    searcher.display_results(results)
    
    # ファイル保存
    searcher.save_results_to_file(results)
    
    print(f"\n✅ 検索完了!")
    print(f"⏰ 検索終了時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")


if __name__ == "__main__":
    main()