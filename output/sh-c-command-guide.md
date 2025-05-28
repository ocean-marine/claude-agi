# sh -c コマンド完全ガイド

## 概要

このシステムでは、直接 `curl` コマンドを実行することはできませんが、`sh -c "curl ..."` という形式を使用することで、任意のBashコマンドを実行することが可能です。この文書では、`sh -c` コマンドの仕組み、使用方法、および実践的な例について詳しく説明します。

## sh -c とは何か

`sh -c` は、シェル（sh）に対して文字列として渡されたコマンドを実行するための標準的な方法です。

### 基本構文

```bash
sh -c 'command'
```

または

```bash
sh -c "command"
```

### なぜ sh -c を使うのか

1. **実行権限の回避**: 直接コマンドが実行できない環境でも、シェル経由で実行可能
2. **複雑なコマンドライン構築**: パイプ、リダイレクト、変数展開を含む複雑なコマンドの実行
3. **環境変数の活用**: シェル環境で設定された変数を利用可能
4. **コマンド連結**: 複数のコマンドを論理演算子で連結して実行

## 実践的な使用例

### 1. 基本的な curl 実行

```bash
# 直接実行（利用不可）
curl https://api.example.com

# sh -c 経由での実行（利用可能）
sh -c 'curl https://api.example.com'
```

### 2. Brave Search API の使用例

現在のシステムでサポートされている実際の例：

```bash
sh -c 'curl -v -s --compressed \
  --get \
  --data-urlencode "q=石破内閣 支持率&count=5&freshness=pd" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_API_KEY}" \
  "https://api.search.brave.com/res/v1/web/search"'
```

### 3. 環境変数の活用

```bash
# 環境変数を使用したAPI呼び出し
sh -c 'curl -H "Authorization: Bearer ${API_TOKEN}" \
  https://api.example.com/data'

# 複数の環境変数を組み合わせ
sh -c 'curl "${BASE_URL}/api/v1/search" \
  -H "X-API-Key: ${API_KEY}" \
  -d "query=${SEARCH_TERM}"'
```

### 4. 複雑なコマンドライン処理

```bash
# JSONレスポンスの整形
sh -c 'curl -s https://api.example.com/data | jq .'

# 結果をファイルに保存
sh -c 'curl -s https://api.example.com/data > response.json'

# 条件付き実行
sh -c 'curl -s https://api.example.com/health && echo "API is healthy"'

# パイプライン処理
sh -c 'curl -s https://api.example.com/data | \
  grep "status" | \
  awk "{print $2}"'
```

### 5. データ処理とファイル操作

```bash
# データをダウンロードして処理
sh -c 'curl -s https://api.example.com/csv-data | \
  head -n 10 | \
  cut -d"," -f1,3'

# 複数のAPIエンドポイントから並列取得
sh -c 'curl -s https://api.example.com/endpoint1 & \
  curl -s https://api.example.com/endpoint2 & \
  wait'

# 日時情報を含むログ記録
sh -c 'echo "$(date): Starting data fetch" && \
  curl -s https://api.example.com/data && \
  echo "$(date): Data fetch completed"'
```

## 高度な活用方法

### 1. エラーハンドリング

```bash
# HTTPステータスコードのチェック
sh -c 'response=$(curl -s -w "%{http_code}" https://api.example.com/data) && \
  if [ "${response: -3}" = "200" ]; then \
    echo "Success: ${response%???}"; \
  else \
    echo "Error: HTTP ${response: -3}"; \
  fi'
```

### 2. ループ処理

```bash
# 複数のエンドポイントを順次処理
sh -c 'for endpoint in users posts comments; do \
  echo "Fetching ${endpoint}..."; \
  curl -s "https://api.example.com/${endpoint}"; \
done'
```

### 3. 条件分岐

```bash
# 環境に応じた設定
sh -c 'if [ "${ENVIRONMENT}" = "production" ]; then \
  BASE_URL="https://api.prod.example.com"; \
else \
  BASE_URL="https://api.dev.example.com"; \
fi && \
curl -s "${BASE_URL}/data"'
```

## セキュリティとベストプラクティス

### 1. 引用符の適切な使用

```bash
# 推奨: シングルクォートで全体を囲む
sh -c 'curl -H "Authorization: Bearer ${TOKEN}" https://api.example.com'

# 注意: ダブルクォート内での変数展開
sh -c "curl -H 'Authorization: Bearer ${TOKEN}' https://api.example.com"
```

### 2. 環境変数の検証

```bash
# 環境変数の存在確認
sh -c 'if [ -z "${API_KEY}" ]; then \
  echo "Error: API_KEY not set" >&2; \
  exit 1; \
fi && \
curl -H "X-API-Key: ${API_KEY}" https://api.example.com'
```

### 3. ログ記録

```bash
# APIコール履歴の記録
sh -c 'echo "$(date): Calling API with query: ${QUERY}" >> api.log && \
  curl -s "https://api.example.com/search?q=${QUERY}"'
```

## デバッグとトラブルシューティング

### 1. 詳細出力の有効化

```bash
# curlの詳細情報を表示
sh -c 'curl -v https://api.example.com/data'

# HTTPヘッダーのみ表示
sh -c 'curl -I https://api.example.com/data'
```

### 2. エラーメッセージの確認

```bash
# 標準エラー出力の確認
sh -c 'curl https://api.example.com/data 2>&1'

# 失敗時の詳細情報
sh -c 'curl --fail-with-body -s https://api.example.com/data || \
  echo "Request failed with exit code $?"'
```

## システム統合での活用

この AGI システムでは、`sh -c` を使用してリサーチタスクを実行できます：

### 1. Web検索の実行

```bash
sh -c 'curl -s --compressed \
  --get \
  --data-urlencode "q=最新のAI技術動向&count=10" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_API_KEY}" \
  "https://api.search.brave.com/res/v1/web/search" | \
  jq ".web.results[].title"'
```

### 2. データ加工と分析

```bash
sh -c 'curl -s "https://api.example.com/data.json" | \
  jq ".items[] | select(.status == \"active\") | .name" | \
  sort | \
  uniq'
```

### 3. レポート生成用のデータ収集

```bash
sh -c 'echo "# API調査レポート" > report.md && \
  echo "調査日時: $(date)" >> report.md && \
  echo "" >> report.md && \
  curl -s https://api.example.com/stats | \
  jq -r ".summary" >> report.md'
```

## まとめ

`sh -c` コマンドは、制限された環境において任意のBashコマンドを実行するための強力なツールです。特に以下の点で有用です：

1. **柔軟性**: 直接実行できないコマンドをシェル経由で実行
2. **組み合わせ**: パイプ、リダイレクト、論理演算子の活用
3. **環境変数**: システム設定された変数の効果的な利用
4. **複雑な処理**: 複数のコマンドを組み合わせた高度な処理

このガイドで示した例を参考に、様々なAPIとの連携やデータ処理タスクに `sh -c` を活用してください。

## 参考資料

- [Brave Search API ドキュメント](https://api.search.brave.com/app/documentation)
- [Bash リファレンスマニュアル](https://www.gnu.org/software/bash/manual/)
- [curl コマンドリファレンス](https://curl.se/docs/manpage.html)
- [jq JSONプロセッサ](https://stedolan.github.io/jq/)