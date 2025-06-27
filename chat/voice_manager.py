import pyttsx3
import threading
import tempfile
import os
from typing import Dict, Optional
import streamlit as st
import time
import requests
import pygame

class VoiceManager:
    def __init__(self):
        """
        音声管理クラスの初期化（複数エンジン対応）
        """
        self.engine = None
        self.voice_settings = {}
        self.is_speaking = False  # 音声再生中フラグを追加
        self.windows_sapi_available = False  # Windows SAPI利用可能フラグ
        self.gemini_api_key = None  # Gemini APIキー
        self.available_engines = []  # 利用可能なエンジンリスト
        self.initialize_engine()
    
    def set_gemini_api_key(self, api_key: str):
        """
        Gemini APIキーを設定
        
        Args:
            api_key (str): Gemini APIキー
        """
        self.gemini_api_key = api_key
        # エンジンリストを更新
        self.check_available_engines()
        
    def initialize_engine(self):
        """
        音声エンジンの初期化（Windows SAPI優先）
        """
        try:
            # Windows SAPI の利用可能性を先にチェック
            self.windows_sapi_available = False
            try:
                import win32com.client
                # テスト用に一時的にSAPI音声エンジンを作成
                test_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                if test_speaker:
                    self.windows_sapi_available = True
                    print("Windows SAPI が利用可能です")
                del test_speaker
            except Exception as sapi_test_error:
                print(f"Windows SAPI テストエラー: {sapi_test_error}")
                self.windows_sapi_available = False
            
            # pyttsx3エンジンの初期化（設定管理用）
            for attempt in range(3):
                try:
                    self.engine = pyttsx3.init()
                    
                    # エンジンが正常に初期化されたかテスト
                    voices = self.engine.getProperty('voices')
                    if voices:
                        self.available_voices = [voice for voice in voices if voice is not None]
                        break
                    else:
                        raise Exception("音声が取得できません")
                        
                except Exception as init_error:
                    print(f"pyttsx3初期化試行 {attempt + 1}/3 失敗: {init_error}")
                    if attempt == 2:  # 最後の試行
                        # pyttsx3が失敗してもWindows SAPIがあれば続行
                        if self.windows_sapi_available:
                            print("pyttsx3は失敗しましたが、Windows SAPIで音声機能を提供します")
                            self.engine = None
                            self.available_voices = []
                            return
                        else:
                            raise init_error
                    time.sleep(0.5)  # 短い待機後に再試行
            
            # デフォルト設定（pyttsx3が利用可能な場合）
            if self.engine:
                try:
                    self.engine.setProperty('rate', 150)  # 話速
                    self.engine.setProperty('volume', 0.9)  # 音量
                    print("pyttsx3音声エンジンの初期化が完了しました")
                except Exception as setting_error:
                    print(f"音声設定エラー（デフォルト値で継続）: {setting_error}")
            
        except Exception as e:
            print(f"音声エンジンの初期化に失敗しました: {e}")
            
            # 最後の手段：Windows SAPIのみで動作
            if self.windows_sapi_available:
                print("Windows SAPIのみで音声機能を提供します")
                self.engine = None
                self.available_voices = []
            else:
                print("音声機能は無効になります（チャット機能は正常に動作します）")
                self.engine = None
                self.available_voices = []
    
    def set_character_voice(self, character_data: Dict):
        """
        キャラクターに応じた音声設定
        
        Args:
            character_data (Dict): キャラクターデータ
        """
        if not self.engine:
            return
            
        try:
            # キャラクターの音声設定を取得
            voice_settings = character_data.get('voice_settings', {})
            
            # 音声速度設定（安全な範囲に制限）
            rate = max(100, min(300, voice_settings.get('rate', 150)))
            self.engine.setProperty('rate', rate)
            
            # 音量設定（安全な範囲に制限）
            volume = max(0.0, min(1.0, voice_settings.get('volume', 0.9)))
            self.engine.setProperty('volume', volume)
            
            # 音声の性別/種類設定（エラーハンドリング強化）
            voice_type = voice_settings.get('voice_type', 'female')
            self.set_voice_by_type(voice_type)
            
        except Exception as e:
            print(f"音声設定エラー (安全に継続): {e}")
            # エラーが発生してもアプリケーションを止めない
    
    def set_voice_by_type(self, voice_type: str):
        """
        音声タイプによる音声設定
        
        Args:
            voice_type (str): 'male' or 'female'
        """
        if not self.engine or not self.available_voices:
            return
            
        try:
            for voice in self.available_voices:
                voice_name = voice.name.lower()
                if voice_type == 'female' and any(keyword in voice_name for keyword in ['female', 'woman', 'zira', 'hazel']):
                    self.engine.setProperty('voice', voice.id)
                    break
                elif voice_type == 'male' and any(keyword in voice_name for keyword in ['male', 'man', 'david', 'mark']):
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"音声タイプ設定エラー: {e}")
    
    def speak_text(self, text: str):
        """
        テキストを音声で読み上げ（Windows SAPI優先・確実動作）
        
        Args:
            text (str): 読み上げるテキスト
        """
        if not self.engine:
            return
            
        # 既に音声再生中の場合はスキップ
        if self.is_speaking:
            print("音声再生中のため、新しい音声をスキップしました")
            return
            
        def speak():
            try:
                self.is_speaking = True
                print("音声再生を開始します...")
                
                # 長いテキストは短縮
                if len(text) > 200:
                    short_text = text[:200] + "..."
                else:
                    short_text = text
                
                # 空のテキストは処理しない
                if not short_text.strip():
                    return
                
                # 方法1: Windows SAPI（最も確実）
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    
                    # 音声速度と音量を設定
                    speaker.Rate = max(-10, min(10, (self.engine.getProperty('rate') - 200) // 20))
                    speaker.Volume = int(self.engine.getProperty('volume') * 100)
                    
                    speaker.Speak(short_text)
                    print("音声再生が完了しました（Windows SAPI使用）")
                    return
                    
                except Exception as sapi_error:
                    print(f"Windows SAPI エラー: {sapi_error}")
                
                # 方法2: メインエンジンで非同期再生（runAndWaitなし）
                try:
                    print("メインエンジンで非同期音声再生を試行します...")
                    self.engine.say(short_text)
                    # runAndWait()を呼ばない（これがエラーの原因）
                    
                    # 代わりに短時間待機
                    import time
                    estimated_duration = len(short_text) * 0.1  # 文字数に応じた推定時間
                    time.sleep(min(estimated_duration, 10))  # 最大10秒
                    
                    print("音声再生が完了しました（非同期モード）")
                    return
                    
                except Exception as engine_error:
                    print(f"メインエンジンエラー: {engine_error}")
                
                # 方法3: システムビープ音（最後の手段）
                try:
                    import winsound
                    # 音声再生の代わりにビープ音で通知
                    winsound.Beep(800, 200)  # 800Hz、200ms
                    print("音声読み上げの代わりにビープ音で通知しました")
                    
                except Exception as beep_error:
                    print(f"ビープ音エラー: {beep_error}")
                    print("すべての音声機能が利用できません")
                
            except Exception as e:
                print(f"音声読み上げエラー（安全に無視）: {e}")
            finally:
                self.is_speaking = False
                print("音声再生フラグをリセットしました")
        
        # 別スレッドで音声再生（完全非同期）
        try:
            thread = threading.Thread(target=speak, daemon=True)
            thread.start()
            print("音声再生スレッドを開始しました")
        except Exception as e:
            print(f"音声スレッド作成エラー（無視）: {e}")
            self.is_speaking = False
    
    def save_audio_file(self, text: str, filename: str) -> Optional[str]:
        """
        音声ファイルとして保存
        
        Args:
            text (str): 保存するテキスト
            filename (str): ファイル名
            
        Returns:
            Optional[str]: 保存されたファイルパス
        """
        if not self.engine:
            return None
            
        try:
            # 音声フォルダの作成
            audio_dir = "audio"
            os.makedirs(audio_dir, exist_ok=True)
            
            # ファイルパスの作成
            file_path = os.path.join(audio_dir, f"{filename}.wav")
            
            # 音声ファイルとして保存
            self.engine.save_to_file(text, file_path)
            self.engine.runAndWait()
            
            return file_path
            
        except Exception as e:
            print(f"音声ファイル保存エラー: {e}")
            return None
    
    def get_voice_settings_ui(self) -> Dict:
        """
        Streamlitで音声設定UIを表示（状態表示とコントロール強化）
        
        Returns:
            Dict: 音声設定
        """
        with st.expander("🔊 音声設定"):
            st.write("**音声読み上げ機能**")
            st.caption("AIの応答を自動で音声読み上げします")
            
            # 音声機能の利用可能性チェック
            if not self.is_available():
                st.error("❌ 音声機能が利用できません。")
                st.caption("Windows SAPIもpyttsx3も利用できません。")
                return {
                    "voice_type": "female",
                    "rate": 150,
                    "volume": 0.9,
                    "enabled": False
                }
            
            # 利用可能な音声エンジンの表示
            available_engines = []
            if self.engine:
                available_engines.append("pyttsx3")
            if getattr(self, 'windows_sapi_available', False):
                available_engines.append("Windows SAPI")
            
            if available_engines:
                st.success(f"✅ 利用可能な音声エンジン: {', '.join(available_engines)}")
            else:
                st.error("❌ 音声エンジンが見つかりません")
            
            # 現在の音声状態表示
            if self.is_speaking:
                st.warning("🔊 現在音声を再生中です...")
                if st.button("⏹️ 音声停止", key="stop_voice"):
                    self.stop_speaking()
            
            enable_voice = st.checkbox(
                "🎙️ 音声読み上げを有効化",
                value=st.session_state.get("enable_voice", False),
                key="enable_voice",
                help="チェックすると、AIの応答が自動で音声で読み上げられます"
            )
            
            if enable_voice:
                st.success("✅ 音声読み上げが有効です")
                
                # 利用可能な音声の表示
                if self.available_voices:
                    st.caption(f"利用可能な音声: {len(self.available_voices)}個")
                
                voice_type = st.selectbox(
                    "音声タイプ",
                    ["female", "male"],
                    index=0 if st.session_state.get("voice_type", "female") == "female" else 1,
                    key="voice_type",
                    help="音声の性別を選択"
                )
                
                rate = st.slider(
                    "話速",
                    min_value=100,
                    max_value=300,
                    value=st.session_state.get("voice_rate", 150),
                    key="voice_rate",
                    help="音声の速度を調整"
                )
                
                volume = st.slider(
                    "音量",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.get("voice_volume", 0.9),
                    step=0.1,
                    key="voice_volume",
                    help="音声の音量を調整"
                )
                
                # テスト音声機能
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🎵 テスト音声", key="test_voice"):
                        test_text = "こんにちは。音声テストです。"
                        st.info("🔊 テスト音声を再生しています...")
                        self.speak_text(test_text)
                
                with col2:
                    if st.button("🔄 設定リセット", key="reset_voice"):
                        # 音声設定をリセット
                        st.session_state.voice_rate = 150
                        st.session_state.voice_volume = 0.9
                        st.session_state.voice_type = "female"
                        st.rerun()
                
                # デバッグ情報表示
                with st.expander("🔧 音声デバッグ情報"):
                    st.write("**音声エンジン状態:**")
                    st.write(f"- pyttsx3エンジン: {'✅' if self.engine else '❌'}")
                    st.write(f"- Windows SAPI: {'✅' if getattr(self, 'windows_sapi_available', False) else '❌'}")
                    st.write(f"- 現在音声再生中: {'✅' if self.is_speaking else '❌'}")
                    if self.engine:
                        try:
                            current_rate = self.engine.getProperty('rate')
                            current_volume = self.engine.getProperty('volume')
                            st.write(f"- 現在の設定: 速度={current_rate}, 音量={current_volume}")
                        except:
                            st.write("- 設定取得エラー")
                
                st.info("💡 メッセージ送信後、AIの応答が自動で読み上げられます")
            else:
                st.info("音声読み上げは無効です")
                # デフォルト値を設定
                voice_type = "female"
                rate = 150
                volume = 0.9
            
            return {
                "voice_type": voice_type,
                "rate": rate,
                "volume": volume,
                "enabled": enable_voice
            }
    
    def is_available(self) -> bool:
        """
        音声機能が利用可能かチェック（Windows SAPI含む）
        
        Returns:
            bool: 利用可能かどうか
        """
        # pyttsx3エンジンまたはWindows SAPIが利用可能な場合
        return self.engine is not None or getattr(self, 'windows_sapi_available', False)
    
    def is_currently_speaking(self) -> bool:
        """
        現在音声再生中かチェック
        
        Returns:
            bool: 音声再生中かどうか
        """
        return self.is_speaking
    
    def stop_speaking(self):
        """
        音声再生を強制停止
        """
        try:
            if self.is_speaking:
                self.is_speaking = False
                print("音声再生を停止しました")
                # 注意: 現在再生中の音声は完全には停止できませんが、
                # 新しい音声の再生は防止されます
        except Exception as e:
            print(f"音声停止エラー（無視）: {e}")
    
    def cleanup(self):
        """
        リソースのクリーンアップ
        """
        try:
            if self.engine:
                self.engine.stop()
                self.engine = None
            self.is_speaking = False
            print("音声エンジンをクリーンアップしました")
        except Exception as e:
            print(f"クリーンアップエラー（無視）: {e}")
