# 🤖 AI Character Chatbot

キャラクター設定可能なAIチャットボットアプリケーション（iPhone/Android対応）

## ✨ 機能

- 🎭 **カスタムキャラクター**: JSON設定で独自キャラクター作成
- 💬 **Gemini AI**: Google Gemini 1.5 Flash使用
- 🎨 **画像生成**: Stable Diffusion連携
- � **音声読み上げ**: Windows SAPI + pyttsx3
- 😊 **感情分析**: リアルタイム感情トラッキング
- 🎨 **テーマ機能**: カスタマイズ可能なUI
- 💾 **会話保存**: 会話履歴の保存・復元

## 🚀 デプロイ済みアプリ

**📱 iPhone・Androidから直接アクセス可能！**

[こちらからアクセス](https://your-app-url.streamlit.app)

## 📱 モバイル対応

- ✅ iPhone Safari対応
- ✅ Android Chrome対応
- ✅ レスポンシブデザイン
- ✅ タッチ操作最適化
- ✨ 新しいキャラクター作成機能

## セットアップ

### 1. 必要な環境

- Python 3.10+
- Stable Diffusion WebUI (画像生成機能を使用する場合)

### 2. 依存関係のインストール

```bash
pip install streamlit google-generativeai pillow requests json5
```

### 3. Stable Diffusion WebUIの設定 (オプション)

画像生成機能を使用する場合は、Stable Diffusion WebUIを起動し、API機能を有効にしてください。

```bash
# WebUIを起動時に --api フラグを追加
python launch.py --api
```

## 使用方法

### 1. アプリケーションの起動

```bash
streamlit run app.py
```

### 2. キャラクターの設定

- サイドバーからキャラクターを選択
- 新しいキャラクターを作成することも可能

### 3. チャット

- 選択したキャラクターとリアルタイムでチャット
- キャラクターごとに異なる性格と話し方

### 4. 画像生成

- Stable Diffusion WebUIが起動している場合
- サイドバーから「キャラクター画像生成」ボタンをクリック

## ファイル構成

```
chat/
├── app.py                      # メインアプリケーション
├── character_manager.py        # キャラクター管理
├── gemini_chatbot.py          # ジェミニAPIチャットボット
├── stable_diffusion_api.py    # Stable Diffusion API連携
├── characters/                # キャラクター設定ファイル
│   ├── sample_character.json
│   └── cool_character.json
├── images/                    # 生成画像保存フォルダ
└── README.md
```

## キャラクター設定ファイル形式

```json
{
    "name": "キャラクター名",
    "personality": "性格の説明",
    "background": "背景設定",
    "speaking_style": "話し方の特徴",
    "base_prompt": "AIへの基本プロンプト",
    "image_prompt": "画像生成プロンプト",
    "image_negative_prompt": "ネガティブプロンプト",
    "conversation_starters": [
        "会話開始メッセージ1",
        "会話開始メッセージ2"
    ]
}
```

## 注意事項

- ジェミニAPIキーが正しく設定されていることを確認してください
- Stable Diffusion WebUIの画像生成は時間がかかる場合があります
- 生成された画像は `images/` フォルダに保存されます

## トラブルシューティング

### よくある問題

1. **ジェミニAPIエラー**
   - APIキーが正しく設定されているか確認
   - インターネット接続を確認

2. **Stable Diffusion接続エラー**
   - WebUIが起動していることを確認
   - `--api` フラグが設定されていることを確認
   - ポート7860でアクセスできることを確認

3. **キャラクターファイルエラー**
   - JSONファイルの形式が正しいか確認
   - 文字エンコーディングがUTF-8であることを確認

## ライセンス

MIT License
