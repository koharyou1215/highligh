<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI Character Chatbot Project Instructions

このプロジェクトは、ジェミニAPIとStable Diffusionを使用したキャラクター設定可能なチャットボットアプリケーションです。

## プロジェクト構成

- **app.py**: Streamlitメインアプリケーション
- **character_manager.py**: キャラクター設定の管理
- **gemini_chatbot.py**: ジェミニAPIとの連携
- **stable_diffusion_api.py**: Stable Diffusion画像生成API
- **characters/**: キャラクター設定JSONファイル
- **images/**: 生成画像保存フォルダ

## 開発時の注意点

1. **文字エンコーディング**: 全てのファイルはUTF-8で保存
2. **APIキー管理**: ジェミニAPIキーはコード内で直接設定済み
3. **エラーハンドリング**: API呼び出しには適切な例外処理を実装
4. **ファイルパス**: Windowsパスに対応した処理を実装

## コーディング規約

- 日本語コメントを使用
- クラス名はPascalCase
- 関数名はsnake_case
- 定数は大文字のSNAKE_CASE
