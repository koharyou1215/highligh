import streamlit as st
import datetime
import os
import html
import logging

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
st.set_page_config(
    page_title="AI Character Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（モバイル対応強化）
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
    try:
        character_manager = CharacterManager()
        chatbot = GeminiChatbot(GEMINI_API_KEY)
        sd_api = StableDiffusionAPI()
        voice_manager = VoiceManager()
        conversation_manager = ConversationManager()
        emotion_manager = EmotionalCharacterManager()
        theme_manager = ThemeManager()
        
        # Gemini API接続テスト
        test_response = chatbot.chat("テスト")
        if not test_response:
            st.warning("Gemini APIの接続に問題がある可能性があります。")
        
        return character_manager, chatbot, sd_api, voice_manager, conversation_manager, emotion_manager, theme_manager
    except Exception as e:
        st.error(f"コンポーネントの初期化に失敗しました: {e}")
        return None, None, None, None, None, None, None
        print(f"音声マネージャー初期化完了: {voice_manager.is_available()}")
        print(f"利用可能メソッド: {[method for method in dir(voice_manager) if not method.startswith('_')]}")
        
        return character_manager, chatbot, sd_api, voice_manager, conversation_manager, emotion_manager, theme_manager
    except Exception as e:
        print(f"コンポーネント初期化エラー: {e}")
        # エラー時は基本機能のみ
        character_manager = CharacterManager()
        chatbot = GeminiChatbot(GEMINI_API_KEY)
        sd_api = StableDiffusionAPI()
        voice_manager = None  # 音声機能を無効化
        conversation_manager = ConversationManager()
        emotion_manager = EmotionalCharacterManager()
        theme_manager = ThemeManager()
        return character_manager, chatbot, sd_api, voice_manager, conversation_manager, emotion_manager, theme_manager

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

def main():
    # コンポーネントの初期化
    components = initialize_components()
    if None in components:
        st.error("アプリケーションの初期化に失敗しました。")
        st.stop()
    
    character_manager, chatbot, sd_api, voice_manager, conversation_manager, emotion_manager, theme_manager = components
    initialize_session_state()
    
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
        
        # 会話履歴管理
        loaded_conversation = conversation_manager.get_conversation_ui()
        if loaded_conversation:
            # 会話を復元
            st.session_state.messages = loaded_conversation.get('messages', [])
            character_name = loaded_conversation.get('character_name', '')
            
            # キャラクターも復元
            character_data = character_manager.get_character_by_name(character_name)
            if character_data:
                st.session_state.current_character = character_data
                chatbot.set_character(character_data)
                
                # 音声設定（エラーハンドリング追加）
                try:
                    if voice_manager:
                        voice_manager.set_character_voice(character_data)
                except Exception as e:
                    st.warning(f"音声設定でエラーが発生しました: {e}")
            
            st.success(f"✅ 会話が復元されました: {character_name}")
            # リロードを削除（自動で反映される）
        
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
        sd_connected = sd_api.check_connection()
        
        if sd_connected:
            st.success("✅ Stable Diffusion接続OK")
            
            if st.session_state.current_character and st.button("キャラクター画像生成"):
                with st.spinner("画像生成中..."):
                    character = st.session_state.current_character
                    base_prompt = character.get('image_prompt', '')
                    negative_prompt = character.get('image_negative_prompt', '')
                    
                    # 感情に応じたプロンプト調整
                    if st.session_state.emotion_tracking and base_prompt:
                        emotional_prompt = emotion_manager.get_emotional_image_prompt(base_prompt)
                        image_prompt = emotional_prompt
                    else:
                        image_prompt = base_prompt
                    
                    if image_prompt:
                        image = sd_api.generate_character_image(
                            image_prompt, 
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
                                    'prompt': image_prompt
                                })
                                st.success("✅ 画像が生成されました！")
                                # 画像生成後のリロードを削除（不要）
                            else:
                                st.error("画像の保存に失敗しました。")
                        else:
                            st.error("画像生成に失敗しました。")
                    else:
                        st.warning("画像プロンプトが設定されていません。")
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
                        # 安全なHTMLエスケープ
                        escaped_content = html.escape(message["content"])
                        st.markdown(f"""
                        <div class="ai-message">
                            🤖 {escaped_content}
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
        
        # チャット入力
        if st.session_state.current_character:
            user_input = st.chat_input("メッセージを入力してください...")
            
            if user_input:
                # ユーザーメッセージを追加
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # 感情分析
                if st.session_state.emotion_tracking:
                    detected_emotion = emotion_manager.update_emotion(user_input)
                
                # AI応答を生成
                with st.spinner("応答生成中..."):
                    ai_response = chatbot.chat(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                    # 音声読み上げ（完全安全モード）
                    if st.session_state.voice_enabled and voice_manager:
                        try:
                            # 音声マネージャーが利用可能な場合のみ実行
                            if voice_manager.is_available():
                                st.info("🔊 音声読み上げを開始します...")
                                voice_manager.speak_text(ai_response)
                            else:
                                st.warning("❌ 音声機能が利用できません")
                        except Exception as voice_error:
                            # 音声エラーは完全に無視してチャットを継続
                            print(f"音声読み上げエラー（安全に無視）: {voice_error}")
                            st.caption("⚠️ 音声読み上げは利用できませんが、チャットは正常に動作しています")
                    elif st.session_state.voice_enabled and not voice_manager:
                        st.caption("❌ 音声機能が初期化されていません")
                    
                    # AI応答の感情分析
                    if st.session_state.emotion_tracking:
                        emotion_manager.update_emotion(ai_response)
                
                # チャット送信後にリロードして表示を更新
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
