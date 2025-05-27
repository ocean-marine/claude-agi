#!/usr/bin/env python3
"""
Brave Search APIの基本テスト
"""

import os
import requests
import json


def test_brave_api():
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        print("❌ BRAVE_API_KEY環境変数が設定されていません")
        return
    
    print(f"✅ APIキーが設定されています (長さ: {len(api_key)} 文字)")
    
    # シンプルなテスト検索
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    
    # 英語での簡単なテスト
    params = {
        "q": "rice news Japan",
        "count": 5
    }
    
    print("🔍 英語での基本テストを実行中...")
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "web" in data and "results" in data["web"]:
                results = data["web"]["results"]
                print(f"✅ 成功! {len(results)} 件の結果を取得")
                
                for i, result in enumerate(results[:3], 1):
                    print(f"  {i}. {result.get('title', 'No title')}")
                    print(f"     {result.get('url', 'No URL')}")
            else:
                print("❌ 検索結果の構造が予期されたものと異なります")
                print(json.dumps(data, indent=2))
        else:
            print(f"❌ エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
    
    # 日本語での検索テスト
    print("\n🔍 日本語での検索テストを実行中...")
    params_jp = {
        "q": "米",
        "count": 5,
        "search_lang": "ja",
        "country": "JP"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params_jp)
        print(f"ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "web" in data and "results" in data["web"]:
                results = data["web"]["results"]
                print(f"✅ 成功! {len(results)} 件の結果を取得")
                
                for i, result in enumerate(results[:3], 1):
                    print(f"  {i}. {result.get('title', 'No title')}")
                    print(f"     {result.get('url', 'No URL')}")
            else:
                print("❌ 検索結果の構造が予期されたものと異なります")
        else:
            print(f"❌ エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")


if __name__ == "__main__":
    test_brave_api()