# Claude AGI ツールキット

Claude AGI ツールキットは、AI研究・開発で使用される汎用的なツール群を提供するPythonパッケージです。検索、テキスト分析などの機能を統合されたCLIインターフェースで利用できます。

## 🚀 特徴

- **統合CLI**: 複数のツールを単一のインターフェースから利用
- **高機能検索**: Brave Search APIを使用した強力な検索機能
- **テキスト分析**: 多言語対応の詳細な文字数・文字種分析
- **柔軟な出力**: Text、JSON、CSV形式での結果出力
- **インタラクティブモード**: 対話的な操作環境
- **完全テスト**: 90%以上のテストカバレッジ

## 📋 要件

- Python 3.12+
- BRAVE_API_KEY 環境変数（検索機能使用時）

## 🛠️ インストール

```bash
# リポジトリのクローン
git clone https://github.com/ocean-marine/claude-agi.git
cd claude-agi

# 依存関係のインストール
pip install -r requirements.txt

# Brave Search APIキーの設定
export BRAVE_API_KEY="your_api_key_here"
```

## 🎯 使用方法

### 統合CLI

```bash
# ツール一覧の表示
python src/cli.py --list-tools

# インタラクティブモード
python src/cli.py --interactive

# 検索実行
python src/cli.py search "Python programming" --count 5 --format json

# テキスト分析
python src/cli.py analyze sample.txt --type detailed --format csv
```

### 個別ツールの使用

#### 検索ツール (Brave Search)

```bash
# 基本検索
python src/brave_search.py "機械学習"

# 詳細オプション
python src/brave_search.py "データサイエンス" \
  --count 10 \
  --format json \
  --output results.json \
  --lang en \
  --country US

# インタラクティブモード
python src/brave_search.py --interactive
```

#### テキスト分析ツール

```bash
# ファイル分析
python src/text_analyzer.py document.txt --type detailed

# 直接テキスト分析
python src/text_analyzer.py --text "解析したいテキスト" --type japanese

# インタラクティブモード
python src/text_analyzer.py --interactive
```

### プログラマブルAPI

```python
from src.brave_search import BraveSearchClient, SearchConfig
from src.text_analyzer import TextAnalyzer, CountType

# 検索API
client = BraveSearchClient()
config = SearchConfig(query="Python", count=5)
results = client.search(config)
formatted = client.format_results(results, "json")

# テキスト分析API
analyzer = TextAnalyzer()
results = analyzer.count_characters("Hello 世界", CountType.DETAILED)
print(results)
```

## 📊 機能詳細

### 検索機能 (Brave Search)

**対応フォーマット**: text, json, csv  
**対応言語**: 多言語（ja, en, etc.）  
**カスタマイズ**: 国別検索、結果数指定

```bash
# 使用例
python src/brave_search.py "rust programming" \
  --count 20 \
  --format csv \
  --output rust_results.csv \
  --lang en \
  --country US
```

### テキスト分析機能

**分析方式**:
- `all`: 全文字数
- `no_spaces`: 空白文字を除く
- `alphanumeric`: 英数字のみ
- `japanese`: 日本語文字のみ
- `detailed`: 詳細分類（推奨）

**詳細分析結果例**:
```json
{
  "総文字数": 25,
  "英字": 8,
  "数字": 3,
  "ひらがな": 5,
  "カタカナ": 4,
  "漢字": 2,
  "記号": 2,
  "空白文字": 1,
  "改行": 0,
  "行数": 1,
  "単語数": 4,
  "その他": 0
}
```

## 🧪 テスト

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src --cov-report=html

# 特定のテストファイル実行
pytest tests/test_text_analyzer.py -v
```

## 🏗️ アーキテクチャ

### ディレクトリ構造

```
claude-agi/
├── src/
│   ├── cli.py                 # 統合CLIエントリーポイント
│   ├── brave_search.py        # Brave Search検索ツール
│   ├── text_analyzer.py       # テキスト分析ツール
│   └── __init__.py
├── tests/
│   ├── test_brave_api.py      # APIテスト
│   ├── test_brave_search.py   # 検索ツールテスト
│   ├── test_text_analyzer.py  # 分析ツールテスト
│   └── __init__.py
├── CLAUDE.md                  # 開発ガイドライン
├── README.md                  # このファイル
└── requirements.txt           # 依存関係
```

### 設計原則

- **単一責任の原則**: 各モジュールは明確な責任を持つ
- **依存性注入**: テスタブルで柔軟な設計
- **設定可能性**: 環境や用途に応じたカスタマイズ
- **拡張性**: 新しいツールの追加が容易

## 🔧 開発

### 開発ガイドライン

詳細な開発ガイドラインは [CLAUDE.md](CLAUDE.md) を参照してください。

### 新しいツールの追加

1. `src/` に新しいツールモジュールを作成
2. `src/cli.py` にサブパーサーを追加
3. `tests/` に対応するテストファイルを作成
4. ドキュメントを更新

### コード品質

- **型ヒント**: Python 3.12の新機能を活用
- **docstring**: Google/NumPy形式で詳細記述
- **テスト**: pytest使用、90%以上のカバレッジ目標
- **フォーマット**: PEP 8準拠

## 📈 パフォーマンス

- **正規表現最適化**: パターンのプリコンパイルで高速化
- **メモリ効率**: 大量データの段階的処理
- **並行処理**: 適切な場面での非同期処理対応

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

### コミットメッセージ規約

```
feat: 新機能
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル修正
refactor: リファクタリング
test: テスト追加・修正
chore: その他の変更
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は `LICENSE` ファイルを参照してください。

## 🆘 サポート

- **Issues**: バグ報告や機能要望は [GitHub Issues](https://github.com/ocean-marine/claude-agi/issues)
- **Discussions**: 質問や議論は [GitHub Discussions](https://github.com/ocean-marine/claude-agi/discussions)

## 🗺️ ロードマップ

- [ ] 新しい分析ツールの追加
- [ ] API レート制限の実装
- [ ] 設定ファイル対応
- [ ] Docker対応
- [ ] Web UI の実装
- [ ] 機械学習モデル統合

## 📚 参考文献

- [Brave Search API Documentation](https://api.search.brave.com/app/documentation/web-search/get-started)
- [Python 3.12 新機能](https://docs.python.org/3.12/whatsnew/3.12.html)
- [pytest Documentation](https://docs.pytest.org/)

---

**Claude AGI ツールキット** - AIの力で、より良い開発体験を。