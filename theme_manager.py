from typing import Dict
import streamlit as st

class ThemeManager:
    def __init__(self):
        """
        テーマ管理クラスの初期化
        """
        self.themes = {
            "default": {
                "name": "デフォルト",
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "background_color": "#ffffff",
                "text_color": "#000000",
                "accent_color": "#007bff",
                "card_background": "#f8f9fa",
                "border_color": "#dee2e6"
            },
            "cute": {
                "name": "キュート",
                "primary_color": "#FF69B4",
                "secondary_color": "#FFB6C1",
                "background_color": "#FFF0F5",
                "text_color": "#2F2F2F",
                "accent_color": "#FF1493",
                "card_background": "#FFEBEF",
                "border_color": "#FFB6C1"
            },
            "cool": {
                "name": "クール",
                "primary_color": "#4169E1",
                "secondary_color": "#6495ED",
                "background_color": "#F0F8FF",
                "text_color": "#2F2F2F",
                "accent_color": "#0000CD",
                "card_background": "#E6F3FF",
                "border_color": "#6495ED"
            },
            "elegant": {
                "name": "エレガント",
                "primary_color": "#9370DB",
                "secondary_color": "#DDA0DD",
                "background_color": "#F8F8FF",
                "text_color": "#2F2F2F",
                "accent_color": "#8A2BE2",
                "card_background": "#F5F0FF",
                "border_color": "#DDA0DD"
            },
            "warm": {
                "name": "ウォーム",
                "primary_color": "#FF6347",
                "secondary_color": "#FFA500",
                "background_color": "#FFF8DC",
                "text_color": "#2F2F2F",
                "accent_color": "#FF4500",
                "card_background": "#FFEFD5",
                "border_color": "#FFA500"
            },
            "dark": {
                "name": "ダーク",
                "primary_color": "#2F4F4F",
                "secondary_color": "#696969",
                "background_color": "#1E1E1E",
                "text_color": "#FFFFFF",
                "accent_color": "#4169E1",
                "card_background": "#2F2F2F",
                "border_color": "#696969"
            },
            "nature": {
                "name": "ナチュラル",
                "primary_color": "#228B22",
                "secondary_color": "#90EE90",
                "background_color": "#F0FFF0",
                "text_color": "#2F2F2F",
                "accent_color": "#32CD32",
                "card_background": "#F5FFFA",
                "border_color": "#90EE90"
            }
        }
    
    def get_theme_css(self, theme_name: str = "default") -> str:
        """
        テーマに応じたCSSを生成
        
        Args:
            theme_name (str): テーマ名
            
        Returns:
            str: CSS文字列
        """
        theme = self.themes.get(theme_name, self.themes["default"])
        
        css = f"""
        <style>
        .main-header {{
            background: linear-gradient(90deg, {theme['primary_color']} 0%, {theme['secondary_color']} 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }}

        .character-card {{
            background: {theme['card_background']};
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid {theme['border_color']};
            margin-bottom: 1rem;
            color: {theme['text_color']};
        }}

        .chat-container {{
            max-height: 500px;
            overflow-y: auto;
            padding: 1rem;
            border: 1px solid {theme['border_color']};
            border-radius: 10px;
            background: {theme['card_background']};
        }}

        .user-message {{
            background: {theme['accent_color']};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 15px 15px 5px 15px;
            margin: 0.5rem 0;
            margin-left: 20%;
            text-align: right;
        }}

        .ai-message {{
            background: {theme['primary_color']};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 15px 15px 15px 5px;
            margin: 0.5rem 0;
            margin-right: 20%;
        }}

        .emotion-indicator {{
            background: {theme['secondary_color']};
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin: 0.2rem;
        }}

        .stats-card {{
            background: {theme['card_background']};
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid {theme['border_color']};
            margin-bottom: 1rem;
            color: {theme['text_color']};
        }}

        .voice-controls {{
            background: {theme['card_background']};
            padding: 0.8rem;
            border-radius: 8px;
            border: 1px solid {theme['border_color']};
            margin: 0.5rem 0;
        }}

        /* サイドバーのスタイル調整 */
        .css-1d391kg {{
            background-color: {theme['card_background']};
        }}

        /* メトリクスのスタイル */
        [data-testid="metric-container"] {{
            background-color: {theme['card_background']};
            border: 1px solid {theme['border_color']};
            padding: 1rem;
            border-radius: 0.5rem;
            color: {theme['text_color']};
        }}

        /* エクスパンダーのスタイル */
        .streamlit-expanderHeader {{
            background-color: {theme['primary_color']};
            color: white;
        }}

        /* ボタンのスタイル */
        .stButton > button {{
            background-color: {theme['primary_color']};
            color: white;
            border: none;
            border-radius: 5px;
        }}

        .stButton > button:hover {{
            background-color: {theme['secondary_color']};
        }}
        </style>
        """
        
        return css
    
    def apply_character_theme(self, character_data: Dict) -> str:
        """
        キャラクターに応じたテーマを適用
        
        Args:
            character_data (Dict): キャラクターデータ
            
        Returns:
            str: 適用されたテーマ名
        """
        # キャラクターからテーマを推定
        character_name = character_data.get('name', '').lower()
        personality = character_data.get('personality', '').lower()
        
        # キャラクター設定で明示的にテーマが指定されている場合
        if 'theme' in character_data:
            theme_name = character_data['theme']
            if theme_name in self.themes:
                return theme_name
        
        # 性格からテーマを推定
        if any(keyword in personality for keyword in ['可愛い', 'かわいい', '少女', '萌え', 'ツンデレ']):
            return 'cute'
        elif any(keyword in personality for keyword in ['クール', '冷静', '知的', '大人']):
            return 'cool'
        elif any(keyword in personality for keyword in ['上品', 'エレガント', '高貴', '優雅']):
            return 'elegant'
        elif any(keyword in personality for keyword in ['温かい', 'あたたかい', '優しい', '穏やか']):
            return 'warm'
        elif any(keyword in personality for keyword in ['ダーク', '暗い', 'ゴシック', 'ミステリアス']):
            return 'dark'
        elif any(keyword in personality for keyword in ['自然', 'ナチュラル', '森', '癒し']):
            return 'nature'
        else:
            return 'default'
    
    def get_theme_selector_ui(self) -> str:
        """
        テーマ選択UIを表示
        
        Returns:
            str: 選択されたテーマ名
        """
        theme_options = {name: theme['name'] for name, theme in self.themes.items()}
        
        selected_theme = st.selectbox(
            "🎨 テーマ選択",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            key="theme_selector"
        )
        
        return selected_theme
    
    def get_theme_preview(self, theme_name: str) -> Dict:
        """
        テーマのプレビュー情報を取得
        
        Args:
            theme_name (str): テーマ名
            
        Returns:
            Dict: テーマ情報
        """
        return self.themes.get(theme_name, self.themes["default"])
    
    def create_custom_theme(self, theme_data: Dict) -> str:
        """
        カスタムテーマを作成
        
        Args:
            theme_data (Dict): テーマデータ
            
        Returns:
            str: 作成されたテーマ名
        """
        theme_name = f"custom_{len(self.themes)}"
        self.themes[theme_name] = theme_data
        return theme_name
    
    def get_emotion_theme(self, emotion_color_scheme: Dict) -> str:
        """
        感情に応じた一時的なテーマを作成
        
        Args:
            emotion_color_scheme (Dict): 感情カラースキーム
            
        Returns:
            str: 感情テーマCSS
        """
        css = f"""
        <style>
        .emotion-header {{
            background: linear-gradient(90deg, {emotion_color_scheme['primary']} 0%, {emotion_color_scheme['secondary']} 100%);
            padding: 0.5rem;
            border-radius: 8px;
            color: white;
            text-align: center;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }}

        .emotion-message {{
            background: {emotion_color_scheme['background']};
            border-left: 4px solid {emotion_color_scheme['primary']};
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 0 8px 8px 0;
        }}
        </style>
        """
        
        return css
