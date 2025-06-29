from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class MemoryManager:
    """チャットで抽出・保存された重要メモを管理するシンプルなクラス。\n\n    各キャラクターごとにメモを分離して JSON で永続化する。\n    ディレクトリ構造::\n
        memories/キャラクター名/yyyymmdd_HHMMSS.json\n    """

    def __init__(self, base_dir: str = "memories") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    # ------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------
    def add_memory(self, character_name: str, content: str, extra: Optional[Dict] = None) -> str:
        """メモを追加し、ファイルへ保存する。\n\n        Args:\n            character_name: メモ対象キャラクター\n            content: メモ本文\n            extra: 追加メタデータ\n\n        Returns:\n            保存したファイルパス\n        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        char_dir = os.path.join(self.base_dir, character_name)
        os.makedirs(char_dir, exist_ok=True)

        filename = f"{timestamp}.json"
        filepath = os.path.join(char_dir, filename)

        data = {
            "character_name": character_name,
            "content": content,
            "timestamp": timestamp,
            "extra": extra or {},
        }
        with open(filepath, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        return filepath

    def get_memories(self, character_name: str) -> List[Dict]:
        """指定キャラクターのメモ一覧を新しい順で取得。"""
        char_dir = os.path.join(self.base_dir, character_name)
        if not os.path.exists(char_dir):
            return []
        memories = []
        for filename in os.listdir(char_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(char_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    memories.append({
                        "filepath": filepath,
                        "timestamp": data.get("timestamp", ""),
                        "content": data.get("content", ""),
                    })
            except Exception:
                # 壊れたファイルは無視
                continue
        memories.sort(key=lambda x: x["timestamp"], reverse=True)
        return memories

    def delete_memory(self, filepath: str) -> bool:
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False 