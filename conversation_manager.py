import json
import os
import datetime
from typing import List, Dict, Optional
import streamlit as st

class ConversationManager:
    def __init__(self):
        """
        会話履歴管理クラスの初期化
        """
        self.conversations_dir = "conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
    
    def save_conversation(self, character_name: str, messages: List[Dict], metadata: Dict = None) -> str:
        """
        会話履歴を保存
        
        Args:
            character_name (str): キャラクター名
            messages (List[Dict]): メッセージ履歴
            metadata (Dict): メタデータ
            
        Returns:
            str: 保存されたファイルパス
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{character_name}_{timestamp}.json"
            filepath = os.path.join(self.conversations_dir, filename)
            
            conversation_data = {
                "character_name": character_name,
                "timestamp": timestamp,
                "messages": messages,
                "metadata": metadata or {},
                "message_count": len(messages),
                "created_at": datetime.datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            print(f"会話保存エラー: {e}")
            return None
    
    def load_conversation(self, filepath: str) -> Optional[Dict]:
        """
        会話履歴を読み込み
        
        Args:
            filepath (str): ファイルパス
            
        Returns:
            Optional[Dict]: 会話データ
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"会話読み込みエラー: {e}")
            return None
    
    def get_conversation_list(self) -> List[Dict]:
        """
        保存された会話履歴リストを取得
        
        Returns:
            List[Dict]: 会話履歴リスト
        """
        conversations = []
        
        try:
            for filename in os.listdir(self.conversations_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.conversations_dir, filename)
                    conversation = self.load_conversation(filepath)
                    
                    if conversation:
                        conversations.append({
                            "filename": filename,
                            "filepath": filepath,
                            "character_name": conversation.get("character_name", "Unknown"),
                            "timestamp": conversation.get("timestamp", ""),
                            "message_count": conversation.get("message_count", 0),
                            "created_at": conversation.get("created_at", "")
                        })
            
            # 作成日時でソート（新しい順）
            conversations.sort(key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"会話リスト取得エラー: {e}")
        
        return conversations
    
    def delete_conversation(self, filepath: str) -> bool:
        """
        会話履歴を削除
        
        Args:
            filepath (str): ファイルパス
            
        Returns:
            bool: 削除成功かどうか
        """
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"会話削除エラー: {e}")
            return False
    
    def export_conversation_text(self, conversation_data: Dict) -> str:
        """
        会話をテキスト形式でエクスポート
        
        Args:
            conversation_data (Dict): 会話データ
            
        Returns:
            str: テキスト形式の会話
        """
        try:
            lines = []
            lines.append(f"=== {conversation_data['character_name']} との会話 ===")
            lines.append(f"作成日時: {conversation_data['created_at']}")
            lines.append(f"メッセージ数: {conversation_data['message_count']}")
            lines.append("")
            
            for message in conversation_data['messages']:
                role = "あなた" if message['role'] == 'user' else conversation_data['character_name']
                lines.append(f"[{role}]: {message['content']}")
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            print(f"テキストエクスポートエラー: {e}")
            return ""
    
    def get_conversation_ui(self) -> Dict:
        """
        Streamlitで会話履歴管理UIを表示
        
        Returns:
            Dict: 選択された会話データ
        """
        with st.expander("💾 会話履歴管理"):
            conversations = self.get_conversation_list()
            
            if conversations:
                st.subheader("保存された会話")
                
                for conv in conversations:
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{conv['character_name']}**")
                        st.caption(f"メッセージ数: {conv['message_count']}")
                    
                    with col2:
                        st.write(conv['timestamp'])
                    
                    with col3:
                        if st.button("読込", key=f"load_{conv['filename']}"):
                            conversation_data = self.load_conversation(conv['filepath'])
                            if conversation_data:
                                return conversation_data
                    
                    with col4:
                        if st.button("削除", key=f"delete_{conv['filename']}"):
                            if self.delete_conversation(conv['filepath']):
                                st.success("削除しました")
                                st.rerun()
                            else:
                                st.error("削除に失敗しました")
                
                st.divider()
                
                # 一括エクスポート
                if st.button("全会話をテキストファイルにエクスポート"):
                    export_text = ""
                    for conv in conversations:
                        conversation_data = self.load_conversation(conv['filepath'])
                        if conversation_data:
                            export_text += self.export_conversation_text(conversation_data)
                            export_text += "\n" + "="*50 + "\n\n"
                    
                    if export_text:
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        export_filename = f"all_conversations_{timestamp}.txt"
                        
                        with open(export_filename, 'w', encoding='utf-8') as f:
                            f.write(export_text)
                        
                        st.success(f"エクスポートしました: {export_filename}")
            else:
                st.info("保存された会話はありません")
        
        return None
