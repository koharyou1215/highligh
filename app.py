import streamlit as st
import datetime
import os
import html
import logging
import base64
from config_manager import ConfigManager
import traceback
from PIL import Image
import io
from memory_manager import MemoryManager

# ログレベルを設定してパフォーマンスを向上
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

try:
    from character_manager import CharacterManager
    from gemini_chatbot import GeminiChatbot
    from stable_diffusion_api import StableDiffusionAPI
    from voice_manager import VoiceManager
    from conversation_manager import ConversationManager
    from emotion_analyzer import EmotionalCharacterManager, Emotion
    from theme_manager import ThemeManager
except ImportError as e:
    st.error(f"モジュールの読み込みに失敗しました: {e}")
    st.error("必要なパッケージがインストールされていない可能性があります。")
    st.stop()

# ページ設定
config_manager = ConfigManager()
page_icon = config_manager.data.get("images", {}).get("icon", "🤖")
st.set_page_config(
    page_title="AI Character Chatbot",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# 背景画像を適用（存在する場合のみ）
bg_path = config_manager.data.get("images", {}).get("background")
if bg_path and os.path.exists(bg_path):
    with open(bg_path, "rb") as _bg_fp:
        encoded_bg = base64.b64encode(_bg_fp.read()).decode()
    bg_css = """
    <style>
    .stApp {
        background-image: url('data:image/png;base64,ENCODED_BG');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
    }
    </style>
    """.replace("ENCODED_BG", encoded_bg)
    st.markdown(bg_css, unsafe_allow_html=True)

# カスタムCSS（モバイル対応強化）
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, rgba(102,126,234,0.6) 0%, rgba(118,75,162,0.6) 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.character-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin-bottom: 1rem;
}

.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 1rem;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    background: #f8f9fa;
}

.user-message {
    background: #007bff;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 15px 15px 5px 15px;
    margin: 0.5rem 0;
    margin-left: 20%;
    text-align: right;
    word-wrap: break-word;
}

.ai-message {
    background: #28a745;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 15px 15px 15px 5px;
    margin: 0.5rem 0;
    margin-right: 20%;
    word-wrap: break-word;
}

/* モバイル対応 */
@media (max-width: 768px) {
    .main-header {
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
    }
    
    .user-message, .ai-message {
        margin-left: 10%;
        margin-right: 10%;
        padding: 0.7rem;
        font-size: 0.9rem;
    }
    
    .character-card {
        padding: 0.7rem;
        font-size: 0.85rem;
    }
    
    .stSelectbox > div > div {
        font-size: 0.9rem;
    }
    
    .stTextArea > div > div > textarea {
        font-size: 0.9rem;
    }
}

/* iPhone対応 */
@media (max-width: 480px) {
    .main-header h1 {
        font-size: 1.3rem;
    }
    
    .main-header p {
        font-size: 0.8rem;
    }
    
    .user-message, .ai-message {
        margin-left: 5%;
        margin-right: 5%;
        padding: 0.6rem;
        font-size: 0.85rem;
    }
}
</style>
""", unsafe_allow_html=True)

# APIキーの設定（環境変数対応）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB6swTTIlDM3pgyALHjZDFTUIQf2fhzLAE")

# 初期化（キャッシュリセット機能付き）
@st.cache_resource
def initialize_components():
    """
    アプリケーションの全コンポーネントを初期化します。
    失敗した場合は、Noneのタプルを返します。
    """
    try:
        # 必須コンポーネントの初期化
        character_manager = CharacterManager()
        chatbot = GeminiChatbot(GEMINI_API_KEY)
        sd_api = StableDiffusionAPI()
        conversation_manager = ConversationManager()
        emotion_manager = EmotionalCharacterManager()
        theme_manager = ThemeManager()
        memory_manager = MemoryManager()

        # 音声マネージャーは失敗しても良いオプションコンポーネント
        voice_manager = None
        try:
            voice_manager = VoiceManager()
            if not voice_manager.is_available():
                st.toast("🔊 音声エンジンは利用可能ですが、正常に動作していません。", icon="⚠️")
        except Exception as e:
            print(f"VoiceManagerの初期化に失敗: {e}")
            st.toast("🔊 音声機能の初期化に失敗したため、無効化されました。", icon="⚠️")
            voice_manager = None

        # Gemini APIへの接続をテスト
        try:
            # chatbotがNoneでないことを確認してからテストを実行
            if chatbot:
                test_response = chatbot.chat("テスト")
                if not test_response:
                    st.warning("Gemini APIの接続に問題がある可能性があります。")
        except Exception as e:
            st.error(f"Gemini APIへの接続テストに失敗しました: {e}")
            st.info("APIキーが正しいか、ネットワーク接続が有効か確認してください。")
            return (None,) * 8 # Return a tuple of Nones matching the number of managers

        return character_manager, chatbot, sd_api, voice_manager, conversation_manager, emotion_manager, theme_manager, memory_manager

    except Exception as e:
        st.error("アプリケーションの初期化中に致命的なエラーが発生しました。")
        st.error(f"エラー詳細: {e}")
        st.code(traceback.format_exc())
        st.info("必要なパッケージがすべてインストールされているか、`requirements.txt`を確認してください。")
        return (None,) * 8 # Return a tuple of Nones matching the number of managers

# セッション状態の初期化
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_character' not in st.session_state:
        st.session_state.current_character = None
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'current_theme' not in st.session_state:
        st.session_state.current_theme = 'default'
    if 'voice_enabled' not in st.session_state:
        st.session_state.voice_enabled = False
    if 'emotion_tracking' not in st.session_state:
        st.session_state.emotion_tracking = True
    if 'conversation_starter' not in st.session_state:
        st.session_state.conversation_starter = None
    if 'lora_weights' not in st.session_state:
        st.session_state.lora_weights = {}
    if 'needs_ai_response' not in st.session_state:
        st.session_state.needs_ai_response = False
    if 'needs_image_generation' not in st.session_state:
        st.session_state.needs_image_generation = False

def main():
    # コンポーネントの初期化
    components = initialize_components()
    character_manager, chatbot, sd_api, voice_manager, conversation_manager, emotion_manager, theme_manager, memory_manager = components

    # 必須コンポーネントが初期化されたかチェック
    # voice_managerはオプションなのでNoneでも許容
    required_components_map = {
        "CharacterManager": character_manager,
        "GeminiChatbot": chatbot,
        "StableDiffusionAPI": sd_api,
        "ConversationManager": conversation_manager,
        "EmotionalCharacterManager": emotion_manager,
        "ThemeManager": theme_manager,
        "MemoryManager": memory_manager
    }
    
    failed_components = [name for name, comp in required_components_map.items() if comp is None]

    if failed_components:
        st.error(f"アプリケーションの必須コンポーネントの初期化に失敗しました: {', '.join(failed_components)}")
        st.info("コンソールに表示されているエラーメッセージや、APIキーなどの設定を確認してください。")
        return  # ここで処理を終了
    
    # リンターにNoneでないことを伝える
    assert character_manager is not None
    assert chatbot is not None
    assert sd_api is not None
    assert conversation_manager is not None
    assert emotion_manager is not None
    assert theme_manager is not None
    assert memory_manager is not None

    initialize_session_state()
    
    # ユーザーペルソナをチャットボットへ適用
    user_persona = config_manager.data.get("user", {}).get("persona", "")
    if user_persona:
        chatbot.set_user_persona(user_persona)
    
    # テーマ適用
    current_theme = st.session_state.current_theme
    if st.session_state.current_character:
        auto_theme = theme_manager.apply_character_theme(st.session_state.current_character)
        if auto_theme != current_theme:
            current_theme = auto_theme
            st.session_state.current_theme = current_theme
    
    # テーマCSSを適用
    theme_css = theme_manager.get_theme_css(current_theme)
    st.markdown(theme_css, unsafe_allow_html=True)
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Character Chatbot</h1>
        <p>キャラクター設定可能なAIチャットボット with Stable Diffusion & 感情表現</p>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # テーマ設定
        st.subheader("🎨 テーマ設定")
        selected_theme = theme_manager.get_theme_selector_ui()
        if selected_theme != st.session_state.current_theme:
            st.session_state.current_theme = selected_theme
            # テーマ変更は即座に反映（リロード不要）
        
        st.divider()
        
        # 音声設定
        st.subheader("🔊 音声設定")
        try:
            if voice_manager and voice_manager.is_available():
                voice_settings = voice_manager.get_voice_settings_ui()
                st.session_state.voice_enabled = voice_settings.get('enabled', False)
            else:
                st.warning("音声機能が利用できません")
                st.caption("音声エンジンの初期化に失敗しました")
                st.session_state.voice_enabled = False
        except Exception as e:
            st.error(f"音声設定エラー: {e}")
            st.session_state.voice_enabled = False
        
        st.divider()
        
        # 感情トラッキング設定
        st.subheader("😊 感情設定")
        st.session_state.emotion_tracking = st.checkbox(
            "感情トラッキングを有効化",
            value=st.session_state.emotion_tracking,
            key="emotion_tracking_toggle"
        )
        
        if st.session_state.emotion_tracking:
            emotion_info = emotion_manager.get_current_emotion_info()
            st.markdown(f"""
            <div class="emotion-indicator">
                現在の感情: {emotion_info['description']}
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # 📝 メモ管理
        st.subheader("📝 メモ")
        if st.session_state.current_character:
            char_name = st.session_state.current_character.get("name", "unknown")
            # 既存メモ一覧
            memories = memory_manager.get_memories(char_name)
            if memories:
                for mem in memories:
                    with st.expander(f"{mem['timestamp']}"):
                        st.write(mem["content"])
                        if st.button("削除", key=f"delmem_{mem['timestamp']}"):
                            if memory_manager.delete_memory(mem["filepath"]):
                                st.success("削除しました")
                                st.rerun()
            else:
                st.caption("メモはまだありません")

            # 新規メモ追加
            new_mem = st.text_area("新しいメモ", key="new_memory")
            if st.button("保存", key="save_memory") and new_mem.strip():
                memory_manager.add_memory(char_name, new_mem.strip())
                st.success("メモを保存しました")
                st.rerun()
        else:
            st.caption("キャラクターを選択するとメモ機能が有効になります")

        st.divider()
        
        # 会話履歴管理
        loaded_conversation = conversation_manager.get_conversation_ui()
        if loaded_conversation:
            # 会話を復元
            loaded_messages = loaded_conversation.get('messages', [])
            character_name = loaded_conversation.get('character_name', '')
            
            # キャラクターも復元
            character_data = character_manager.get_character_by_name(character_name)
            if character_data:
                st.session_state.current_character = character_data
                # 【重要】UIとAIの履歴を同期させるための修正
                # 1. キャラクターを設定 (AI内部の履歴がクリアされる)
                chatbot.set_character(character_data)
                # 2. 保存された履歴をAIに読み込ませる
                chatbot.load_history(loaded_messages)
                # 3. UIの履歴をAIの履歴に完全に一致させる
                st.session_state.messages = chatbot.conversation_history

                # 音声設定（エラーハンドリング追加）
                try:
                    if voice_manager:
                        voice_manager.set_character_voice(character_data)
                except Exception as e:
                    st.warning(f"音声設定でエラーが発生しました: {e}")
            
            st.success(f"✅ 会話が復元されました: {character_name}")
            # 状態を完全に更新して不整合を防ぐために再実行が必須
            st.rerun()
        
        st.divider()
        
        # キャラクター選択
        st.subheader("📖 キャラクター選択")
        character_names = character_manager.get_character_list()
        
        if character_names:
            selected_character_name = st.selectbox(
                "キャラクターを選択:",
                character_names,
                key="character_select"
            )
            
            if st.button("キャラクターを設定", type="primary"):
                character_data = character_manager.get_character_by_name(selected_character_name)
                if character_data:
                    # 全ての設定をまとめて実行
                    st.session_state.current_character = character_data
                    chatbot.set_character(character_data)
                    
                    # 音声設定（エラーハンドリング追加）
                    try:
                        if voice_manager:
                            voice_manager.set_character_voice(character_data)
                    except Exception as e:
                        st.warning(f"音声設定でエラーが発生しました: {e}")
                    
                    # 感情とメッセージをリセット
                    emotion_manager.current_emotion = Emotion.NEUTRAL
                    emotion_manager.emotion_history = []
                    st.session_state.messages = []
                    st.session_state.conversation_starter = None  # スターターもリセット
                    
                    # キャラクターに応じたテーマを自動適用
                    auto_theme = theme_manager.apply_character_theme(character_data)
                    st.session_state.current_theme = auto_theme
                    
                    st.success(f"✅ {selected_character_name}が設定されました！")
                    # リロードを削除（状態が更新されれば自動で反映される）
        else:
            st.warning("キャラクターファイルが見つかりません。")
        
        st.divider()
        
        # キャラクター作成
        st.subheader("✨ 新しいキャラクター作成")
        with st.expander("キャラクター作成フォーム"):
            new_char_name = st.text_input("名前")
            new_char_personality = st.text_area("性格")
            new_char_background = st.text_area("背景設定")
            new_char_speaking_style = st.text_area("話し方")
            new_char_base_prompt = st.text_area("基本プロンプト")
            new_char_image_prompt = st.text_area("画像生成プロンプト")
            new_char_image_negative = st.text_area("ネガティブプロンプト")
            
            if st.button("キャラクター作成"):
                if new_char_name and new_char_personality:
                    new_character = {
                        "name": new_char_name,
                        "personality": new_char_personality,
                        "background": new_char_background,
                        "speaking_style": new_char_speaking_style,
                        "base_prompt": new_char_base_prompt,
                        "image_prompt": new_char_image_prompt,
                        "image_negative_prompt": new_char_image_negative,
                        "conversation_starters": [
                            f"こんにちは！私は{new_char_name}です。",
                            "何かお話ししましょうか？",
                            "今日はどんな日でしたか？"
                        ]
                    }
                    
                    char_id = character_manager.create_new_character(new_character)
                    st.success(f"✅ キャラクター '{new_char_name}' が作成されました！")
                    # 作成後は手動で選択してもらう（自動リロードしない）
                else:
                    st.error("名前と性格は必須です。")
        
        st.divider()
        
        # Stable Diffusion設定
        st.subheader("🎨 画像生成")
        # 直近の会話を画像プロンプトに使うか選択
        use_chat_prompt = st.checkbox("直近の会話を画像プロンプトに使用", value=True, help="オンの場合、直近のユーザーメッセージを画像プロンプトに含めます")

        # LoRA設定
        available_loras = sd_api.get_loras()
        if available_loras:
            st.subheader("🎛️ LoRA設定")
            selected_loras = st.multiselect(
                "適用するLoRAを選択",
                options=available_loras,
                default=[name for name in st.session_state.lora_weights.keys() if name in available_loras],
                help="複数のLoRAを組み合わせることができます。"
            )

            # 選択されなかったLoRAをリセット
            for lora_name in list(st.session_state.lora_weights.keys()):
                if lora_name not in selected_loras:
                    del st.session_state.lora_weights[lora_name]

            # 選択されたLoRAの強度スライダーを生成
            for lora_name in selected_loras:
                st.session_state.lora_weights[lora_name] = st.slider(
                    f"強度: {lora_name}",
                    min_value=0.0,
                    max_value=1.5,
                    value=st.session_state.lora_weights.get(lora_name, 0.7),
                    step=0.05,
                    key=f"lora_weight_{lora_name}"
                )
        else:
            st.caption("利用可能なLoRAが見つかりません。")

        sd_connected = sd_api.check_connection()
        
        if sd_connected:
            st.success("✅ Stable Diffusion接続OK")
            
            if st.session_state.current_character and st.button("キャラクター画像生成"):
                with st.spinner("画像生成中..."):
                    character = st.session_state.current_character
                    base_prompt = character.get('image_prompt', '')
                    negative_prompt = character.get('image_negative_prompt', '')
                    
                    # プロンプト決定ロジック
                    image_prompt = base_prompt or ""
                    if use_chat_prompt and st.session_state.messages:
                        # 直近のユーザー発言を取得
                        last_user_msg = None
                        for msg in reversed(st.session_state.messages):
                            if msg["role"] == "user":
                                last_user_msg = msg["content"]
                                break
                        if last_user_msg:
                            image_prompt = f"{image_prompt} {last_user_msg}".strip()
                    if not image_prompt:
                        st.warning("画像プロンプトが生成できませんでした。会話を入力するか、キャラクターの image_prompt を設定してください。")
                    else:
                        # LoRAプロンプトを追加
                        lora_prompts = []
                        if 'lora_weights' in st.session_state:
                            for lora_name, weight in st.session_state.lora_weights.items():
                                if weight > 0:
                                    lora_prompts.append(f"<lora:{lora_name}:{weight}>")
                        
                        final_prompt = f"{image_prompt} {' '.join(lora_prompts)}".strip()

                        image = sd_api.generate_character_image(
                            final_prompt, 
                            negative_prompt
                        )
                        
                        if image:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            emotion_info = emotion_manager.get_current_emotion_info()
                            
                            saved_path = sd_api.save_character_image(
                                image, 
                                character.get('name', 'character'), 
                                timestamp
                            )
                            
                            if saved_path:
                                st.session_state.generated_images.append({
                                    'image': image,
                                    'path': saved_path,
                                    'character': character.get('name', ''),
                                    'timestamp': timestamp,
                                    'emotion': emotion_info['description'],
                                    'prompt': final_prompt
                                })
                                st.success("✅ 画像が生成されました！")
                                # 画像生成後のリロードを削除（不要）
                            else:
                                st.error("画像の保存に失敗しました。")
                        else:
                            st.error("画像生成に失敗しました。")
        else:
            st.error("❌ Stable Diffusion未接続")
            st.caption("Stable Diffusion WebUIが起動していることを確認してください。")
        
        # 会話保存・リセット
        st.divider()
        col_save, col_reset = st.columns(2)
        
        with col_save:
            if st.button("💾 会話保存") and st.session_state.current_character and st.session_state.messages:
                character_name = st.session_state.current_character.get('name', 'Unknown')
                metadata = {
                    "theme": st.session_state.current_theme,
                    "voice_enabled": st.session_state.voice_enabled,
                    "emotion_tracking": st.session_state.emotion_tracking
                }
                
                saved_path = conversation_manager.save_conversation(
                    character_name, 
                    st.session_state.messages,
                    metadata
                )
                
                if saved_path:
                    st.success("✅ 会話が保存されました！")
                else:
                    st.error("❌ 保存に失敗しました")
        
        with col_reset:
            if st.button("🔄 会話リセット", key="reset_conversation"):
                st.session_state.messages = []
                st.session_state.conversation_starter = None  # スターターもリセット
                if st.session_state.current_character:
                    chatbot.clear_conversation()
                    emotion_manager.current_emotion = Emotion.NEUTRAL
                    emotion_manager.emotion_history = []
                st.success("✅ 会話がリセットされました！")
        
        # 開発者向けツール
        st.divider()
        st.caption("🔧 開発者ツール")
        col_debug1, col_debug2 = st.columns(2)
        
        with col_debug1:
            if st.button("🔄 キャッシュクリア", help="コンポーネントキャッシュをクリアします"):
                st.cache_resource.clear()
                st.success("✅ キャッシュをクリアしました")
                st.info("ページを再読み込みしてください")
        
        with col_debug2:
            if st.button("🐛 デバッグ情報", help="システム状態を表示"):
                st.write("**システム状態:**")
                st.write(f"- 音声マネージャー: {'✅' if voice_manager else '❌'}")
                if voice_manager:
                    st.write(f"- 音声利用可能: {'✅' if voice_manager.is_available() else '❌'}")
                st.write(f"- 現在のキャラクター: {st.session_state.current_character.get('name', 'None') if st.session_state.current_character else 'None'}")
                st.write(f"- メッセージ数: {len(st.session_state.messages)}")
                st.write(f"- 音声有効: {'✅' if st.session_state.voice_enabled else '❌'}")
    
    # メインエリア
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 チャット")
        
        # デバッグ情報を追加
        if st.session_state.messages:
            st.caption(f"💬 メッセージ数: {len(st.session_state.messages)}件")
        
        # 現在のキャラクター表示
        if st.session_state.current_character:
            character = st.session_state.current_character
            st.markdown(f"""
            <div class="character-card">
                <h4>🎭 現在のキャラクター: {character.get('name', 'Unknown')}</h4>
                <p><strong>性格:</strong> {character.get('personality', 'N/A')}</p>
                <p><strong>背景:</strong> {character.get('background', 'N/A')}</p>
                <p><strong>話し方:</strong> {character.get('speaking_style', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ キャラクターが選択されていません。サイドバーからキャラクターを選択してください。")
        
        # チャット履歴表示
        chat_container = st.container()
        with chat_container:
            if st.session_state.messages:
                for i, message in enumerate(st.session_state.messages):
                    if message["role"] == "user":
                        # 安全なHTMLエスケープ
                        escaped_content = html.escape(message["content"])
                        st.markdown(f"""
                        <div class="user-message">
                            👤 {escaped_content}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # AIメッセージ（画像付き）
                        escaped_content = html.escape(message["content"])
                        image_html = ""
                        # "image"キーが存在し、中身がNoneでないことを確認
                        if message.get("image"):
                            try:
                                # PIL ImageをBase64に変換
                                buffered = io.BytesIO()
                                message["image"].save(buffered, format="PNG")
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                image_html = f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; border-radius: 10px; margin-top: 10px;">'
                            except Exception as e:
                                print(f"画像のHTML変換でエラー: {e}")

                        st.markdown(f"""
                        <div class="ai-message">
                            🤖 {escaped_content}
                            {image_html}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                if st.session_state.current_character:
                    # 一度だけ会話スターターを生成
                    if st.session_state.conversation_starter is None:
                        st.session_state.conversation_starter = chatbot.get_conversation_starter()
                    
                    # 安全なHTMLエスケープ
                    escaped_starter = html.escape(st.session_state.conversation_starter)
                    st.markdown(f"""
                    <div class="ai-message">
                        🤖 {escaped_starter}
                    </div>
                    """, unsafe_allow_html=True)
        
        # チャット入力ロジックを修正
        if st.session_state.current_character:
            # --- Stage 1: ユーザー入力受付 ---
            user_input = st.chat_input("メッセージを入力してください...")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input, "image": None})
                st.session_state.needs_ai_response = True
                st.rerun()

            # --- Stage 2: AIテキスト応答生成 ---
            if st.session_state.get('needs_ai_response', False):
                st.session_state.needs_ai_response = False  # フラグ消費
                
                last_user_message = ""
                # 履歴から最後のユーザーメッセージを探す
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "user":
                        last_user_message = msg["content"]
                        break
                
                if last_user_message:
                    with st.spinner("応答生成中..."):
                        # 感情分析 (ユーザー入力に対して)
                        if st.session_state.emotion_tracking:
                            emotion_manager.update_emotion(last_user_message)
                        
                        # AI応答生成
                        ai_response = chatbot.chat(last_user_message)
                        st.session_state.messages = chatbot.conversation_history

                        # 感情分析 (AI応答に対して)
                        if st.session_state.emotion_tracking:
                            emotion_manager.update_emotion(ai_response)
                        
                        # 音声読み上げ
                        if st.session_state.voice_enabled and voice_manager and voice_manager.is_available():
                            try:
                                voice_manager.speak_text(ai_response)
                            except Exception as e:
                                print(f"音声読み上げエラー: {e}")
                    
                    # 画像生成フラグを立てて、再描画（ここでテキストが表示される）
                    if sd_api.check_connection():
                        st.session_state.needs_image_generation = True
                    st.rerun()

            # --- Stage 3: 画像生成 ---
            if st.session_state.get('needs_image_generation', False):
                st.session_state.needs_image_generation = False # フラグ消費

                last_ai_message_content = ""
                # 履歴から最後のAIメッセージを探す
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "assistant":
                        last_ai_message_content = msg["content"]
                        break

                if last_ai_message_content and "エラーが発生しました" not in last_ai_message_content:
                    with st.spinner("画像生成中..."):
                        image_summary = chatbot.summarize_for_image(last_ai_message_content)
                        character = st.session_state.current_character
                        assert character is not None
                        character_base_prompt = character.get("image_prompt", "")
                        negative_prompt = character.get("image_negative_prompt", "")
                        final_image_prompt = f"{character_base_prompt}, {image_summary}".strip(", ")
                        
                        lora_prompts = []
                        if 'lora_weights' in st.session_state:
                            for lora_name, weight in st.session_state.lora_weights.items():
                                if weight > 0:
                                    lora_prompts.append(f"<lora:{lora_name}:{weight}>")
                        final_image_prompt_with_lora = f"{final_image_prompt} {' '.join(lora_prompts)}".strip()

                        generated_image = sd_api.generate_character_image(final_image_prompt_with_lora, negative_prompt)

                        # 最後のメッセージに画像を追加
                        if st.session_state.messages:
                            st.session_state.messages[-1]["image"] = generated_image
                    
                    # 再描画して画像を表示
                    st.rerun()

            # 操作ボタン
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                # 【修正】再生成ボタンのロジックを簡素化
                if st.button("🔄", key="btn_regen") and st.session_state.messages:
                    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
                        with st.spinner("応答と画像を再生成中..."):
                            # 1. テキストを再生成
                            new_resp = chatbot.regenerate_response()
                            
                            # 2. 応答があれば画像も生成
                            if new_resp and "エラー" not in new_resp:
                                st.session_state.messages = chatbot.conversation_history
                                generated_image = None
                                if sd_api.check_connection():
                                    image_summary = chatbot.summarize_for_image(new_resp)
                                    character = st.session_state.current_character
                                    assert character is not None
                                    character_base_prompt = character.get("image_prompt", "")
                                    negative_prompt = character.get("image_negative_prompt", "")
                                    final_image_prompt = f"{character_base_prompt}, {image_summary}".strip(", ")
                                    
                                    lora_prompts = []
                                    if 'lora_weights' in st.session_state:
                                        for lora_name, weight in st.session_state.lora_weights.items():
                                            if weight > 0:
                                                lora_prompts.append(f"<lora:{lora_name}:{weight}>")
                                    final_image_prompt_with_lora = f"{final_image_prompt} {' '.join(lora_prompts)}".strip()

                                    generated_image = sd_api.generate_character_image(final_image_prompt_with_lora, negative_prompt)
                                
                                if st.session_state.messages:
                                    st.session_state.messages[-1]["image"] = generated_image
                        
                        # 3. 最後に一度だけ再描画
                        st.rerun()

            with col_btn2:
                if st.button("⏪ 巻き戻し (最後の往復を削除)", key="btn_rollback") and len(st.session_state.messages) >= 2:
                    chatbot.conversation_history.pop()
                    chatbot.conversation_history.pop()
                    if chatbot.chat_session:
                        chatbot.chat_session.history.pop()
                        chatbot.chat_session.history.pop()
                    
                    st.session_state.messages = chatbot.conversation_history
                    st.rerun()

        else:
            st.chat_input("キャラクターを選択してください...", disabled=True)
    
    with col2:
        st.header("🖼️ 生成画像")
        
        if st.session_state.generated_images:
            for i, img_data in enumerate(reversed(st.session_state.generated_images)):
                with st.expander(f"{img_data['character']} - {img_data['timestamp']}"):
                    st.image(img_data['image'], caption=f"生成日時: {img_data['timestamp']}")
                    st.caption(f"感情: {img_data.get('emotion', 'N/A')}")
                    st.caption(f"プロンプト: {img_data.get('prompt', 'N/A')[:100]}...")
                    st.caption(f"保存先: {img_data['path']}")
        else:
            st.info("まだ画像が生成されていません。\nサイドバーから画像生成を試してください。")
        
        # 統計情報
        st.header("📊 統計")
        if st.session_state.current_character:
            summary = chatbot.get_conversation_summary()
            st.info(summary)
            
            # 感情統計
            if st.session_state.emotion_tracking:
                emotion_stats = emotion_manager.get_emotion_statistics()
                if emotion_stats:
                    st.subheader("😊 感情統計")
                    
                    # 最も多い感情
                    most_frequent = emotion_stats.get('most_frequent')
                    if most_frequent:
                        emotion_analyzer = emotion_manager.emotion_analyzer
                        most_frequent_desc = emotion_analyzer.get_emotion_description(most_frequent)
                        st.metric("最も多い感情", most_frequent_desc)
                    
                    # 感情の分布
                    st.write("**感情の分布:**")
                    for emotion, percentage in emotion_stats.get('percentages', {}).items():
                        emotion_desc = emotion_analyzer.get_emotion_description(emotion)
                        st.write(f"- {emotion_desc}: {percentage:.1f}%")
        
        total_characters = len(character_manager.get_character_list())
        total_images = len(st.session_state.generated_images)
        total_conversations = len(conversation_manager.get_conversation_list())
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("キャラクター数", total_characters)
            st.metric("生成画像数", total_images)
        with col_stat2:
            st.metric("保存会話数", total_conversations)
            if st.session_state.current_character:
                st.metric("現在のテーマ", theme_manager.themes[st.session_state.current_theme]['name'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+Cでアプリが終了された場合のクリーンアップ
        print("\nアプリケーションを終了します...")
        try:
            # 音声エンジンのクリーンアップ（セッション状態から取得）
            import streamlit as st
            if hasattr(st, 'session_state') and hasattr(st.session_state, '_voice_manager'):
                st.session_state._voice_manager.cleanup()
        except:
            pass
    except Exception as e:
        print(f"アプリケーションエラー: {e}")
        # エラーが発生してもアプリケーションを正常終了
