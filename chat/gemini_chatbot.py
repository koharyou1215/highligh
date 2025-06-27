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
        
        # モデルの設定
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # 会話履歴
        self.conversation_history = []
        self.current_character = None
        
    def set_character(self, character_data: Dict):
        """
        現在のキャラクターを設定
        
        Args:
            character_data (Dict): キャラクターデータ
        """
        self.current_character = character_data
        self.conversation_history = []
        
        # システムプロンプトを設定
        system_prompt = character_data.get('base_prompt', '')
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })
    
    def chat(self, user_message: str) -> str:
        """
        ユーザーメッセージに対する応答を生成
        
        Args:
            user_message (str): ユーザーメッセージ
            
        Returns:
            str: AIの応答
        """
        try:
            # 会話履歴にユーザーメッセージを追加
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # プロンプトを構築
            prompt = self._build_prompt()
            
            # Gemini APIに送信
            response = self.model.generate_content(prompt)
            ai_response = response.text
            
            # 会話履歴にAI応答を追加
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"
    
    def _build_prompt(self) -> str:
        """
        会話履歴からプロンプトを構築
        
        Returns:
            str: 構築されたプロンプト
        """
        prompt_parts = []
        
        for message in self.conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"システム: {content}")
            elif role == "user":
                prompt_parts.append(f"ユーザー: {content}")
            elif role == "assistant":
                prompt_parts.append(f"アシスタント: {content}")
        
        return "\n\n".join(prompt_parts)
    
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
        会話履歴をクリア
        """
        self.conversation_history = []
        if self.current_character and self.current_character.get('base_prompt'):
            self.conversation_history.append({
                "role": "system",
                "content": self.current_character['base_prompt']
            })
    
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
