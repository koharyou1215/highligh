# 📱 iPhoneでアプリを開く手順

## 📋 必要なファイル一覧

以下のファイルがGitHubリポジトリに含まれていることを確認してください：

### 🔧 メインファイル
- `app.py` - メインアプリケーション
- `requirements.txt` - Pythonパッケージ依存関係
- `packages.txt` - システムパッケージ依存関係（NEW）
- `runtime.txt` - Pythonバージョン指定（NEW）

### ⚙️ 設定ファイル
- `.streamlit/config.toml` - Streamlit設定（NEW）
- `.gitignore` - Git除外設定

### 📦 モジュールファイル
- `character_manager.py` - キャラクター管理
- `gemini_chatbot.py` - Gemini API連携
- `stable_diffusion_api.py` - 画像生成API
- `voice_manager.py` - 音声合成
- `conversation_manager.py` - 会話履歴管理
- `emotion_analyzer.py` - 感情分析
- `theme_manager.py` - テーマ管理

### 👥 キャラクターデータ
- `characters/` フォルダ内の全JSONファイル

### 📚 ドキュメント
- `README.md` - プロジェクト説明
- `DEPLOY_GUIDE.md` - このファイル

## 🚀 Streamlit Cloudでデプロイ

### 1️⃣ GitHubにアップロード

1. **GitHub.com**にログイン
2. **New repository**をクリック
3. Repository name: 任意の名前（例：`highligh`、`ai-character-chatbot`等）
4. **Public**を選択（無料でデプロイするため）
5. **Create repository**をクリック

### 2️⃣ コードをアップロード

コマンドプロンプトで以下を実行：

```bash
cd "c:\Users\kohar\Desktop\script\chat"
git remote add origin https://github.com/YOUR_USERNAME/ai-character-chatbot.git
git branch -M main
git push -u origin main
```

※ `YOUR_USERNAME`を実際のGitHubユーザー名に変更

### 3️⃣ Streamlit Cloudでデプロイ

1. **https://share.streamlit.io** にアクセス
2. **GitHubアカウントでログイン**
3. **New app**をクリック
4. Repository: あなたのリポジトリを選択（例：`koharyou1215/highligh`）
5. Branch: `main`
6. Main file path: `app.py`
7. **Deploy!**をクリック

### 4️⃣ 環境変数の設定

1. デプロイ後、アプリのSettings → **Secrets**
2. **Add secret**をクリック
3. Key: `GEMINI_API_KEY`
4. Value: あなたのGemini APIキー
5. **Save**をクリック

### 5️⃣ iPhoneでアクセス

1. **Safari**を開く
2. 生成されたURL（例：https://your-app.streamlit.app）にアクセス
3. **ホーム画面に追加**で、アプリのように使用可能！

## 🖥️ ローカル環境での簡単起動

### バッチファイルの使用

プロジェクトには2つのバッチファイルが含まれています：

#### 1. `start_app.bat` - アプリ全体の起動
```bash
# エクスプローラーでダブルクリック、または
start_app.bat
```

**機能：**
- 仮想環境の自動セットアップ
- 依存関係の自動インストール
- Stable Diffusion WebUIの自動起動（インストール済みの場合）
- Streamlitアプリの起動

#### 2. `start_sd.bat` - Stable Diffusion WebUI専用
```bash
# エクスプローラーでダブルクリック、または
start_sd.bat
```

**機能：**
- Stable Diffusion WebUIのみを起動
- パスの自動確認
- エラーハンドリング

### バッチファイルのカスタマイズ

Stable Diffusion WebUIのインストールパスが異なる場合：

1. `start_app.bat`または`start_sd.bat`をメモ帳で開く
2. 以下の行を編集：
```batch
set "SD_DIR=C:\Users\kohar\Downloads\stable-diffusion-webui-1.10.1"
```
3. 実際のインストールパスに変更して保存

### iPhone/モバイルからの操作手順

#### 🖥️ PCでの準備
1. **バッチファイル実行**
   - `start_app.bat`をダブルクリック
   - 自動的にブラウザが開く（http://localhost:8501）

2. **IPアドレス確認**
   - コマンドプロンプトで`ipconfig`実行
   - IPv4アドレスをメモ（例：192.168.1.100）

#### 📱 iPhoneからのアクセス
1. **同じWi-Fiネットワークに接続**
2. **Safariで以下にアクセス：**
   ```
   http://[PCのIPアドレス]:8501
   例：http://192.168.1.100:8501
   ```
3. **ホーム画面に追加**で、アプリのように使用可能！

#### 🌐 リモートデスクトップ使用
- **TeamViewer**、**Chrome Remote Desktop**などを使用
- PC画面を直接操作可能
- 最も確実で機能制限がない方法

## 🔧 トラブルシューティング

### 音声機能について
- iPhoneでは音声機能は制限される場合があります
- チャット機能は完全に動作します

### 画像生成について
- Stable Diffusionサーバーがローカルの場合は動作しません
- キャラクター機能とチャットは正常動作します

### デプロイメントについて
- リポジトリがPublicになっているか確認
- 必要なファイルが全て含まれているか確認
- 環境変数が正しく設定されているか確認

## 🔧 トラブルシューティング - バッチファイル

### 文字化けエラー
```
'��環境の確認中...' is not recognized...
```
**解決方法：**
- 修正済みのバッチファイルを使用
- コマンドプロンプトの文字エンコーディング問題を回避

### requirements.txtエラー
```
ERROR: Could not open requirements file
```
**解決方法：**
- バッチファイルをプロジェクトフォルダ内で実行
- requirements.txtファイルが存在することを確認

### 仮想環境エラー
```
エラー: 仮想環境の作成に失敗しました
```
**解決方法：**
- Pythonが正しくインストールされているか確認
- 管理者権限でコマンドプロンプトを実行

### Stable Diffusion WebUIが見つからない
```
Error: Stable Diffusion WebUI not found
```
**解決方法：**
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)をインストール
- バッチファイルの`SD_DIR`を正しいパスに変更

### ポートエラー
```
Port 8501 is already in use
```
**解決方法：**
- 既存のStreamlitプロセスを終了
- タスクマネージャーでpythonプロセスを確認
- 別のポートを使用: `streamlit run app.py --server.port 8502`

### ネットワークアクセスエラー
**iPhoneからPCにアクセスできない場合：**
- PCとiPhoneが同じWi-Fiに接続されているか確認
- WindowsファイアウォールでStreamlitポート（8501）を許可
- ルーターの設定でデバイス間通信が許可されているか確認

## 📞 サポート

問題が発生した場合は、以下をチェック：
1. Gemini APIキーが正しく設定されているか
2. GitHub repository が Public になっているか
3. ブラウザのエラーコンソールを確認

## 🎉 完了！

これでiPhoneからいつでもAIキャラクターチャットボットを楽しめます！

## 🔄 ローカル変更をStreamlit Cloudに反映

### 📤 変更のアップロード手順

ローカルでファイルを修正した後、Streamlit Cloudに反映するには：

#### 方法1: コマンドライン（推奨）

```bash
# プロジェクトフォルダに移動
cd "c:\Users\kohar\Desktop\script\chat"

# 変更をステージング
git add .

# コミット（変更内容を記録）
git commit -m "バッチファイル修正とエラー修正"

# GitHubにアップロード
git push origin main
```

#### 方法2: GitHub Desktop（GUI）

1. **GitHub Desktop**を開く
2. **Changes**タブで変更されたファイルを確認
3. **Summary**に変更内容を入力（例：「バッチファイル修正」）
4. **Commit to main**をクリック
5. **Push origin**をクリック

#### 方法3: GitHub Web（ブラウザ）

1. **GitHub.com**でリポジトリを開く
2. 修正したいファイルを選択
3. **Edit this file**（鉛筆アイコン）をクリック
4. ファイルを編集
5. **Commit changes**をクリック

### 🚀 Streamlit Cloudでの自動デプロイ

GitHubにpushすると：

1. **自動的にStreamlit Cloudが検知**
2. **新しいバージョンを自動デプロイ**
3. **約1-3分で反映完了**

### 📊 デプロイ状況の確認

1. **https://share.streamlit.io** にアクセス
2. **Your apps**から該当アプリを選択
3. **Status**でデプロイ状況を確認：
   - 🟢 **Running**: 正常稼働中
   - 🟡 **Building**: デプロイ中
   - 🔴 **Error**: エラー発生

### 🔍 デプロイログの確認

エラーが発生した場合：

1. アプリページで**Manage app**をクリック
2. **Logs**タブでエラー内容を確認
3. 必要に応じてローカルで修正→再push

### ⚡ 即座に反映させたい場合

```bash
# すべての変更を一度にアップロード
git add . && git commit -m "修正完了" && git push origin main
```

### 🔄 変更反映のワークフロー

```
ローカル修正 → git add . → git commit → git push → Streamlit Cloud自動デプロイ
     ↓              ↓           ↓           ↓              ↓
   ファイル編集    変更記録    コメント追加  GitHub送信   本番環境更新
```

### 💡 よくある問題と解決策

#### 🚨 プッシュできない場合
```bash
# リモートの最新状態を取得
git pull origin main

# 競合がある場合は解決後
git add .
git commit -m "競合解決"
git push origin main
```

#### 🔄 強制アップデート（注意して使用）
```bash
# ローカルの変更で上書きしたい場合
git push origin main --force
```

### 📋 チェックリスト

デプロイ前に確認：
- [ ] ローカルでアプリが正常動作する
- [ ] APIキーなどの秘密情報がコードに含まれていない
- [ ] requirements.txtが最新の状態
- [ ] .gitignoreで不要ファイルを除外済み

## 🔧 Git関連のトラブルシューティング

### ブランチ分岐エラー
```
Your branch and 'origin/main' have diverged
```
**解決方法：**
```bash
# 安全な解決方法
git pull origin main --rebase
git push origin main

# または強制上書き（注意）
git push origin main --force
```

### 関係ないファイルが検出される
**症状：**
- `../` から始まるファイルパスが表示される
- 他のプロジェクトのファイルが含まれる

**解決方法：**
1. `.gitignore`ファイルを更新
2. 関係ないファイルを除外ルールに追加
3. 適切なディレクトリでgitコマンドを実行

### コミットできない場合
```bash
# 変更をリセット
git reset

# 特定のファイルのみ追加
git add app.py requirements.txt
git commit -m "必要なファイルのみ更新"
git push origin main
```

## 🌐 Streamlit Cloud画面の詳細説明

### 🔍 Streamlit Cloudにアクセス

1. **ブラウザで https://share.streamlit.io を開く**
2. **右上の「Sign in」または「Log in」をクリック**
3. **「Continue with GitHub」をクリック**してGitHubアカウントでログイン

### 📱 メイン画面の構成

ログイン後の画面：

```
┌─────────────────────────────────────┐
│ Streamlit Cloud          [プロフィール] │
├─────────────────────────────────────┤
│ 🏠 Your apps                        │
│ ➕ New app                          │
│ 📊 Analytics (有料プラン)             │
│ ⚙️  Settings                        │
└─────────────────────────────────────┘
```

### 🔧 Settingsメニューの場所

#### 方法1: 左側メニューから
- 左側のサイドバーで **「Settings」** をクリック

#### 方法2: プロフィールメニューから
- 右上の **プロフィール画像** または **ユーザー名** をクリック
- ドロップダウンメニューで **「Settings」** を選択

### ⚙️ Settings画面の内容

Settings画面には以下のタブがあります：
- **「Account」** ← ここをクリック
- **「Billing」** (有料プラン関連)
- **「Teams」** (チーム管理)

### 🔗 GitHub連携の管理

**Account**タブ内で：

```
Account Settings
├── Profile information
├── Connected accounts
│   └── 🔗 GitHub: [あなたのユーザー名]
│       └── [Disconnect] ボタン ← これをクリック
└── Danger zone
```

### 📱 具体的な手順

1. **https://share.streamlit.io** を開く
2. **右上の自分のアイコンをクリック** (丸いアイコンまたはイニシャル)
3. **「Settings」を選択**
4. **「Account」タブをクリック**
5. **「Connected accounts」セクションを見つける**
6. **GitHub の横にある「Disconnect」をクリック**
7. **確認ダイアログで「Yes, disconnect」をクリック**
8. **「Connect GitHub」ボタンが表示されるのでクリック**
9. **GitHubの認証画面で許可**

### 🚀 New appでリポジトリを追加

再連携後：
1. **左側メニューの「New app」をクリック**
2. **「From existing repo」を選択**
3. **Repository**欄で `koharyou1215/highligh` を入力または選択
4. **Branch**: `main`
5. **Main file path**: `app.py`
6. **「Deploy!」をクリック**

### 🔍 見つからない場合の代替方法

もしSettingsが見つからない場合：
1. **ブラウザのURL欄に直接入力**:
   ```
   https://share.streamlit.io/settings/account
   ```
2. **または、New appから直接リポジトリを指定**してデプロイを試す

現在の画面はどのような状況ですか？「Your apps」や「New app」のボタンは見えていますか？
