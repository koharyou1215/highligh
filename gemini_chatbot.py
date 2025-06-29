try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai not available. Please install it.")
    genai = None

from typing import List, Dict, Optional

class GeminiChatbot:
    def __init__(self, api_key: str):
        """
        ジェミニチャットボットクラスの初期化
        
        Args:
            api_key (str): Google Gemini API キー
        """
        if genai is None:
            raise ImportError("google-generativeai is not installed. Please install it using: pip install google-generativeai")
        
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        self.model_name = 'gemini-1.5-pro'
        self.model = genai.GenerativeModel(self.model_name)
        
        self.current_character: Optional[Dict] = None
        self.user_persona: str = ""
        self.chat_session: Optional[genai.ChatSession] = None
        # UIと同期するための会話履歴（テキストのみ）
        self.conversation_history: List[Dict] = []
        
    def set_character(self, character_data: Dict):
        """
        現在のキャラクターを設定し、チャットセッションをリセットする。
        
        Args:
            character_data (Dict): キャラクターデータ
        """
        self.current_character = character_data
        self.clear_conversation()

    def set_user_persona(self, persona: str):
        """
        ユーザーのペルソナを設定する。ペルソナが変更された場合、チャットはリセットされる。
        
        Args:
            persona (str): ユーザーペルソナのテキスト
        """
        if self.user_persona != persona:
            self.user_persona = persona
            self.clear_conversation()

    def _initialize_chat(self):
        """
        キャラクターとユーザーペルソナに基づいてチャットセッションを初期化する。
        """
        if not self.current_character:
            system_instruction = "あなたは親切なAIアシスタントです。"
        else:
            base_prompt = self.current_character.get('base_prompt', "あなたは親切なAIアシスタントです。")
            persona_prompt = f"補足：ユーザーは「{self.user_persona}」という人物として振る舞います。その点を考慮して応答してください。" if self.user_persona else ""
            system_instruction = f"{base_prompt}\n\n{persona_prompt}".strip()

        # 新しいシステム指示でモデルを再初期化
        self.model = genai.GenerativeModel(
            self.model_name,
            system_instruction=system_instruction
        )
        # 新しいチャットセッションを開始
        self.chat_session = self.model.start_chat(history=[])
        self.conversation_history = []
    
    def chat(self, user_message: str) -> str:
        """
        ユーザーメッセージに対する応答を生成
        
        Args:
            user_message (str): ユーザーメッセージ
            
        Returns:
            str: AIの応答
        """
        try:
            if self.chat_session is None:
                self._initialize_chat()
            
            self.conversation_history.append({"role": "user", "content": user_message})

            request_options = {"timeout": 30}
            response = self.chat_session.send_message(user_message, request_options=request_options) # type: ignore
            ai_response = response.text
            
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            error_message = f"エラーが発生しました: {str(e)}"
            # エラー時も履歴に追加してUIで確認できるようにする
            self.conversation_history.append({"role": "assistant", "content": error_message})
            return error_message
    
    def get_conversation_starter(self) -> str:
        """
        キャラクターの会話開始メッセージを取得
        
        Returns:
            str: 会話開始メッセージ
        """
        if not self.current_character:
            return "こんにちは！何かお話ししましょうか？"
        
        starters = self.current_character.get('conversation_starters', [])
        if starters:
            import random
            return random.choice(starters)
        
        return f"こんにちは！私は{self.current_character.get('name', 'AI')}です。何かお話ししましょうか？"
    
    def clear_conversation(self):
        """
        会話履歴とチャットセッションをクリア
        """
        self.chat_session = None
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """
        会話の要約を取得
        
        Returns:
            str: 会話の要約
        """
        if not self.conversation_history:
            return "まだ会話がありません。"
        
        user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
        ai_messages = [msg for msg in self.conversation_history if msg["role"] == "assistant"]
        
        return f"メッセージ数: ユーザー {len(user_messages)}件, AI {len(ai_messages)}件"

    def load_history(self, history: List[Dict]):
        """
        指定された履歴からチャットセッションを復元する。
        
        Args:
            history (List[Dict]): アプリケーション形式の会話履歴
        """
        # チャットが初期化されていなければ、まず初期化
        if self.chat_session is None:
            self._initialize_chat()
            
        # UIと同期するための内部履歴を更新
        self.conversation_history = history
        
        # APIが要求する形式に履歴を変換
        api_history = []
        for msg in history:
            # AIの役割名を 'assistant' から 'model' に変更
            role = 'model' if msg.get('role') == 'assistant' else 'user'
            # contentキーが存在するかチェック
            content = msg.get('content', '')
            api_history.append({'role': role, 'parts': [{'text': content}]})
        
        # チャットセッションの履歴を上書き
        if self.chat_session:
            self.chat_session.history = api_history

    def regenerate_response(self) -> Optional[str]:
        """
        最後のAI応答を再生成する。
        """
        if len(self.conversation_history) < 1 or self.chat_session is None:
            return None

        # 最後のメッセージがAI応答でない場合は不可
        if self.conversation_history[-1].get("role") != "assistant":
            return None

        try:
            # 履歴から最後の往復（AI応答と、その前のユーザー入力）を削除
            self.conversation_history.pop()  # AI response
            last_user_message_dict = self.conversation_history.pop()
            last_user_message = last_user_message_dict["content"]

            self.chat_session.history.pop() # AI
            self.chat_session.history.pop() # User

            # 最後のユーザーメッセージを再度送信して再生成
            return self.chat(last_user_message)

        except (IndexError, Exception) as e:
            print(f"Error during regeneration: {e}")
            return f"再生成中にエラーが発生しました: {str(e)}"

    def summarize_for_image(self, text: str) -> str:
        """与えられたテキストを画像生成用の短いプロンプトに要約する"""
        text_to_summarize = text[:200]
        
        prompt = f"""以下の文章を、情景を英語のキーワードで描写する画像生成プロンプトに要約してください。
人物の特徴（髪の色、服装など）、場所、雰囲気を重視してください。

文章:「{text_to_summarize}」

プロンプト(英語):
"""
        try:
            summarizer_model = genai.GenerativeModel('gemini-1.5-flash')
            request_options = {"timeout": 30}
            response = summarizer_model.generate_content(prompt, request_options=request_options) # type: ignore
            return response.text.strip()
        except Exception as e:
            print(f"Error during image summary: {e}")
            return " ".join(text.split()[:15])
