# RAG Studio

## AI-powered Document Search and Chat Application

SvelteとTailwind CSSで作成されたRAG（Retrieval-Augmented Generation）機能を持つチャットアプリです。

### 機能

- **AI チャット**: OpenAI の Responses API を使用したインテリジェントな会話
- **Vector Store 検索**: ファイルをアップロードして知識ベースとして活用
- **RAG 機能**: 文書検索結果を元にした回答生成
- **会話履歴管理**: チャット履歴の自動保存
- **レスポンシブデザイン**: モバイル対応
- **モダンUI**: ダークテーマ対応

### セットアップ手順

#### 1. 必要な環境

- Node.js 18.0以上
- npm または yarn

#### 2. 依存関係のインストール

```bash
npm install
```

#### 3. 開発サーバーの起動

```bash
npm run dev
```

ブラウザで `http://localhost:5173` を開くと、アプリが表示されます。

#### 4. 本番環境用のビルド

```bash
npm run build
```

このコマンドは `dist` ディレクトリに最適化されたファイルを生成します。

### GitHub Pages への デプロイ

このアプリをGitHub Pagesで公開するには、以下の手順に従ってください。

#### 1. リポジトリ設定

`vite.config.js` の `base` を設定します（既に設定済み）：

```javascript
export default defineConfig({
  plugins: [svelte()],
  base: '/claude-agi/',  // リポジトリ名に置き換え
})
```

#### 2. GitHub Actions設定

`.github/workflows/deploy.yml` を作成してCI/CDパイプラインを設定できます。

または、手動でビルドしてデプロイできます：

```bash
# ビルド
npm run build

# dist ディレクトリを gh-pages ブランチにデプロイ
# gh CLI を使用する場合：
npx gh-pages -d dist
```

#### 3. リポジトリ設定

- GitHub の **Settings** → **Pages** に移動
- **Source** を `gh-pages` ブランチに設定
- 保存すると、`https://username.github.io/claude-agi/` でアクセス可能になります

### プロジェクト構成

```
.
├── src/
│   ├── App.svelte              # メインアプリケーション
│   ├── app.css                 # グローバルスタイル
│   ├── main.js                 # エントリーポイント
│   └── components/
│       ├── ChatContainer.svelte # チャット全体
│       ├── MessageList.svelte   # メッセージ表示
│       ├── Message.svelte       # 単一メッセージ
│       └── ChatInput.svelte     # 入力フォーム
├── index.html                  # HTMLテンプレート
├── vite.config.js              # Viteの設定
├── tailwind.config.js          # Tailwindの設定
├── postcss.config.js           # PostCSSの設定
├── svelte.config.js            # Svelteの設定
└── package.json                # 依存関係定義
```

### 主な技術スタック

- **Svelte 4**: UIフレームワーク
- **Vite**: 高速なビルドツール
- **Tailwind CSS 3**: ユーティリティファーストCSSフレームワーク
- **JavaScript**: 言語

### 使用方法

1. テキストボックスにメッセージを入力
2. 「送信」ボタンをクリックまたはEnterキーで送信
3. アシスタントがランダムな応答を返す
4. チャット履歴はローカルストレージに自動保存される

### カスタマイズ

#### レスポンスの変更

`src/components/ChatContainer.svelte` の `responses` 配列を編集して、アシスタントの応答メッセージをカスタマイズできます。

#### スタイルの変更

Tailwind CSSのクラスを編集してデザインをカスタマイズできます。また、`tailwind.config.js` でテーマを設定できます。

### トラブルシューティング

**ビルドエラー**: 依存関係を再インストールしてください
```bash
rm -rf node_modules package-lock.json
npm install
```

**ローカルストレージがクリアされた**: ブラウザの開発者ツール → Application → Local Storage → サイトを選択して確認できます。

### ライセンス

MIT License
