import json
import os
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "model": {
        "system_prompt": "",
        "temperature": 0.7,
        "top_p": 0.9,
    },
    "sd": {
        "positive_prompt": "",
        "negative_prompt": "",
        "steps": 30,
    },
    "voice": {
        "enabled": False,
        "speed": 1.0,
        "pitch": 1.0,
    },
    "theme": {
        "name": "default",
    },
    "images": {
        "background": "",
        "icon": "",
    },
    "user": {
        "name": "",
        "persona": "",
    },
}


class ConfigManager:
    """アプリ全体で共有する設定を JSON で永続化するユーティリティ。"""

    def __init__(self, path: str = "config.json") -> None:
        self.path = path
        self.data: Dict[str, Any] = {}
        self._ensure_file()
        self.data = self._load()
        self._apply_defaults()

    # ---------------------------------------------------------------------
    # public
    # ---------------------------------------------------------------------
    def save(self) -> None:
        """現在の設定内容をファイルへ保存する。"""
        with open(self.path, "w", encoding="utf-8") as fp:
            json.dump(self.data, fp, ensure_ascii=False, indent=2)

    def reset(self) -> None:
        """設定をデフォルトに戻し、ファイルへ即時保存する。"""
        self.data = DEFAULT_CONFIG.copy()
        self.save()

    def update(self, section: str, key: str, value: Any) -> None:
        """指定セクションのキーを更新して保存する。存在しない場合は無視。"""
        if section in self.data and isinstance(self.data[section], dict):
            self.data[section][key] = value
            self.save()

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------
    def _ensure_file(self) -> None:
        """設定ファイルが存在しなければデフォルトを生成する。"""
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as fp:
                json.dump(DEFAULT_CONFIG, fp, ensure_ascii=False, indent=2)

    def _load(self) -> Dict[str, Any]:
        """設定ファイルを読み込む。壊れていればデフォルトで上書きする。"""
        try:
            with open(self.path, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except Exception:
            # 破損時はデフォルトで上書き
            return DEFAULT_CONFIG.copy()

    # ------------------------------------------------------------------
    # defaults merge
    # ------------------------------------------------------------------
    def _apply_defaults(self) -> None:
        """self.data に DEFAULT_CONFIG の欠落キーを再帰的に補完する。"""
        def merge(d: Dict[str, Any], template: Dict[str, Any]):
            for k, v in template.items():
                if k not in d:
                    # shallow copy で OK
                    d[k] = v.copy() if isinstance(v, dict) else v
                elif isinstance(v, dict) and isinstance(d[k], dict):
                    merge(d[k], v)

        merge(self.data, DEFAULT_CONFIG)
        # もし補完が入ったら保存しておく
        self.save() 