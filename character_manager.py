import json
import os
from typing import Dict, List, Optional

class CharacterManager:
    def __init__(self, characters_dir="characters"):
        """
        キャラクター管理クラスの初期化
        
        Args:
            characters_dir (str): キャラクターファイルディレクトリ
        """
        self.characters_dir = characters_dir
        self.characters = {}
        self.load_all_characters()
    
    def load_all_characters(self):
        """
        全てのキャラクターファイルを読み込み
        """
        if not os.path.exists(self.characters_dir):
            os.makedirs(self.characters_dir)
            return
            
        for filename in os.listdir(self.characters_dir):
            if filename.endswith('.json'):
                character_id = filename[:-5]  # .jsonを除去
                character_data = self.load_character(character_id)
                if character_data:
                    self.characters[character_id] = character_data
    
    def load_character(self, character_id: str) -> Optional[Dict]:
        """
        指定されたキャラクターを読み込み
        
        Args:
            character_id (str): キャラクターID
            
        Returns:
            Dict or None: キャラクターデータまたはNone
        """
        filepath = os.path.join(self.characters_dir, f"{character_id}.json")
        
        if not os.path.exists(filepath):
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            return self._normalize(raw)
        except Exception as e:
            print(f"キャラクター読み込みエラー ({character_id}): {e}")
            return None
    
    def save_character(self, character_id: str, character_data: Dict) -> bool:
        """
        キャラクターデータを保存
        
        Args:
            character_id (str): キャラクターID
            character_data (Dict): キャラクターデータ
            
        Returns:
            bool: 保存成功ならTrue
        """
        filepath = os.path.join(self.characters_dir, f"{character_id}.json")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=4)
            
            # メモリ上のデータも更新
            self.characters[character_id] = character_data
            return True
        except Exception as e:
            print(f"キャラクター保存エラー ({character_id}): {e}")
            return False
    
    def get_character_list(self) -> List[str]:
        """
        利用可能なキャラクターリストを取得
        
        Returns:
            List[str]: キャラクター名のリスト
        """
        return [data.get('name', char_id) for char_id, data in self.characters.items()]
    
    def get_character_by_name(self, name: str) -> Optional[Dict]:
        """
        名前でキャラクターを検索
        
        Args:
            name (str): キャラクター名
            
        Returns:
            Dict or None: キャラクターデータまたはNone
        """
        for char_id, data in self.characters.items():
            if data.get('name') == name:
                return data
        return None
    
    def get_character_id_by_name(self, name: str) -> Optional[str]:
        """
        名前でキャラクターIDを検索
        
        Args:
            name (str): キャラクター名
            
        Returns:
            str or None: キャラクターIDまたはNone
        """
        for char_id, data in self.characters.items():
            if data.get('name') == name:
                return char_id
        return None
    
    def create_new_character(self, character_data: Dict) -> str:
        """
        新しいキャラクターを作成
        
        Args:
            character_data (Dict): キャラクターデータ
            
        Returns:
            str: 作成されたキャラクターID
        """
        # キャラクター名からIDを生成
        name = character_data.get('name', 'unnamed')
        base_id = name.lower().replace(' ', '_').replace('　', '_')
        
        # 重複を避けるためにIDを調整
        character_id = base_id
        counter = 1
        while character_id in self.characters:
            character_id = f"{base_id}_{counter}"
            counter += 1
        
        self.save_character(character_id, character_data)
        return character_id
    
    def delete_character(self, character_id: str) -> bool:
        """
        キャラクターを削除
        
        Args:
            character_id (str): キャラクターID
            
        Returns:
            bool: 削除成功ならTrue
        """
        filepath = os.path.join(self.characters_dir, f"{character_id}.json")
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if character_id in self.characters:
                del self.characters[character_id]
            
            return True
        except Exception as e:
            print(f"キャラクター削除エラー ({character_id}): {e}")
            return False

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _normalize(self, data: Dict) -> Dict:
        """新スキーマ / 旧スキーマを吸収し、アプリで既存利用しているキーを保証する。"""
        # 旧スキーマのままなら何もしない
        if "base_prompt" in data:
            return data

        # 新スキーマを簡易マッピング
        intro = data.get("introduction", "")
        personality = data.get("character_definition", {}).get("personality", {})
        summary = personality.get("summary", "")

        # base_prompt を生成
        base_prompt_parts = [intro]
        if summary and summary not in intro:
            base_prompt_parts.append(summary)
        data["base_prompt"] = " ".join(base_prompt_parts).strip()

        # conversation_starters
        first_msgs = data.get("first_message", [])
        if first_msgs and isinstance(first_msgs, list):
            data["conversation_starters"] = first_msgs

        # image prompts
        img_gen = data.get("image_generation", {})
        data["image_prompt"] = img_gen.get("positive_prompt", "")
        data["image_negative_prompt"] = img_gen.get("negative_prompt", "")

        # simple card fields for UI
        data["personality"] = summary
        data["background"] = data.get("character_definition", {}).get("background", "")
        data["speaking_style"] = data.get("character_definition", {}).get("speaking_style", {}).get("base", "")

        return data
