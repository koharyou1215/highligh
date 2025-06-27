import re
from typing import Dict, List, Optional
from enum import Enum

class Emotion(Enum):
    """感情の種類"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    WORRIED = "worried"
    SHY = "shy"

class EmotionAnalyzer:
    def __init__(self):
        """
        感情分析クラスの初期化
        """
        # 感情キーワード辞書
        self.emotion_keywords = {
            Emotion.HAPPY: [
                "嬉しい", "楽しい", "幸せ", "喜ぶ", "笑う", "笑顔", "ハッピー", "最高", "素晴らしい",
                "やったー", "わーい", "やった", "良かった", "ありがとう", "感謝", "ありがたい"
            ],
            Emotion.SAD: [
                "悲しい", "辛い", "寂しい", "泣く", "涙", "残念", "落ち込む", "憂鬱", "がっかり",
                "つらい", "悲しみ", "さみしい", "しょんぼり", "ため息"
            ],
            Emotion.ANGRY: [
                "怒る", "腹立つ", "イライラ", "むかつく", "怒り", "キレる", "頭にくる", "許せない",
                "ふざけるな", "バカ", "あほ", "うざい", "腹が立つ"
            ],
            Emotion.SURPRISED: [
                "驚く", "びっくり", "まさか", "え！", "えー", "うそ", "信じられない", "すごい",
                "わあ", "おお", "驚き", "びっくりした"
            ],
            Emotion.EXCITED: [
                "興奮", "ワクワク", "ドキドキ", "楽しみ", "期待", "待ちきれない", "テンション",
                "やる気", "元気", "活発", "エネルギッシュ"
            ],
            Emotion.WORRIED: [
                "心配", "不安", "気になる", "大丈夫", "どうしよう", "困る", "悩む", "迷う",
                "緊張", "ドキドキ", "ハラハラ", "気がかり"
            ],
            Emotion.SHY: [
                "恥ずかしい", "照れる", "はずかしい", "もじもじ", "赤面", "テレる", "恥",
                "内気", "シャイ", "遠慮", "控えめ"
            ]
        }
        
        # 感情に対応する画像プロンプト修飾子
        self.emotion_prompts = {
            Emotion.HAPPY: "smiling, happy expression, bright eyes, cheerful",
            Emotion.SAD: "sad expression, teary eyes, melancholic, downturned mouth",
            Emotion.ANGRY: "angry expression, furrowed brow, intense eyes, serious",
            Emotion.SURPRISED: "surprised expression, wide eyes, open mouth, amazed",
            Emotion.NEUTRAL: "calm expression, peaceful, serene",
            Emotion.EXCITED: "excited expression, bright eyes, energetic, animated",
            Emotion.WORRIED: "worried expression, concerned look, anxious, thoughtful",
            Emotion.SHY: "shy expression, blushing, bashful, timid, cute"
        }
    
    def analyze_emotion(self, text: str) -> Emotion:
        """
        テキストから感情を分析
        
        Args:
            text (str): 分析するテキスト
            
        Returns:
            Emotion: 検出された感情
        """
        emotion_scores = {emotion: 0 for emotion in Emotion}
        
        # 各感情のキーワードをチェック
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    emotion_scores[emotion] += 1
        
        # 最もスコアの高い感情を返す
        max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        if max_emotion[1] > 0:
            return max_emotion[0]
        else:
            return Emotion.NEUTRAL
    
    def get_emotion_prompt(self, emotion: Emotion, base_prompt: str) -> str:
        """
        感情に応じた画像生成プロンプトを作成
        
        Args:
            emotion (Emotion): 感情
            base_prompt (str): 基本プロンプト
            
        Returns:
            str: 感情を反映したプロンプト
        """
        emotion_modifier = self.emotion_prompts.get(emotion, "")
        
        if emotion_modifier:
            return f"{base_prompt}, {emotion_modifier}"
        else:
            return base_prompt
    
    def get_emotion_color_scheme(self, emotion: Emotion) -> Dict[str, str]:
        """
        感情に応じたカラースキームを取得
        
        Args:
            emotion (Emotion): 感情
            
        Returns:
            Dict[str, str]: カラースキーム
        """
        color_schemes = {
            Emotion.HAPPY: {
                "primary": "#FFD700",  # ゴールド
                "secondary": "#FFA500",  # オレンジ
                "background": "#FFFACD"  # レモンシフォン
            },
            Emotion.SAD: {
                "primary": "#4169E1",  # ロイヤルブルー
                "secondary": "#6495ED",  # コーンフラワーブルー
                "background": "#E6F3FF"  # ライトブルー
            },
            Emotion.ANGRY: {
                "primary": "#DC143C",  # クリムゾン
                "secondary": "#B22222",  # ファイアブリック
                "background": "#FFE4E1"  # ミスティローズ
            },
            Emotion.SURPRISED: {
                "primary": "#FF69B4",  # ホットピンク
                "secondary": "#FF1493",  # ディープピンク
                "background": "#FFF0F5"  # ラベンダーブラッシュ
            },
            Emotion.NEUTRAL: {
                "primary": "#708090",  # スレートグレー
                "secondary": "#778899",  # ライトスレートグレー
                "background": "#F5F5F5"  # ホワイトスモーク
            },
            Emotion.EXCITED: {
                "primary": "#FF4500",  # オレンジレッド
                "secondary": "#FF6347",  # トマト
                "background": "#FFEFD5"  # パパイヤホイップ
            },
            Emotion.WORRIED: {
                "primary": "#9370DB",  # ミディアムパープル
                "secondary": "#8A2BE2",  # ブルーバイオレット
                "background": "#F8F8FF"  # ゴーストホワイト
            },
            Emotion.SHY: {
                "primary": "#FF69B4",  # ホットピンク
                "secondary": "#FFB6C1",  # ライトピンク
                "background": "#FFF0F5"  # ラベンダーブラッシュ
            }
        }
        
        return color_schemes.get(emotion, color_schemes[Emotion.NEUTRAL])
    
    def get_emotion_description(self, emotion: Emotion) -> str:
        """
        感情の説明を取得
        
        Args:
            emotion (Emotion): 感情
            
        Returns:
            str: 感情の説明
        """
        descriptions = {
            Emotion.HAPPY: "😊 幸せ・喜び",
            Emotion.SAD: "😢 悲しみ",
            Emotion.ANGRY: "😠 怒り",
            Emotion.SURPRISED: "😲 驚き",
            Emotion.NEUTRAL: "😐 中立",
            Emotion.EXCITED: "🤩 興奮",
            Emotion.WORRIED: "😟 心配",
            Emotion.SHY: "😳 恥ずかしさ"
        }
        
        return descriptions.get(emotion, "😐 中立")

class EmotionalCharacterManager:
    def __init__(self):
        """
        感情表現キャラクター管理クラスの初期化
        """
        self.emotion_analyzer = EmotionAnalyzer()
        self.current_emotion = Emotion.NEUTRAL
        self.emotion_history = []
    
    def update_emotion(self, text: str) -> Emotion:
        """
        テキストから感情を更新
        
        Args:
            text (str): 分析するテキスト
            
        Returns:
            Emotion: 更新された感情
        """
        emotion = self.emotion_analyzer.analyze_emotion(text)
        self.current_emotion = emotion
        
        # 感情履歴に追加
        import datetime
        self.emotion_history.append({
            "emotion": emotion,
            "text": text[:100],  # 最初の100文字のみ保存
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # 履歴は最新10件まで保持
        if len(self.emotion_history) > 10:
            self.emotion_history = self.emotion_history[-10:]
        
        return emotion
    
    def get_emotional_image_prompt(self, base_prompt: str, emotion: Emotion = None) -> str:
        """
        感情に応じた画像プロンプトを生成
        
        Args:
            base_prompt (str): 基本プロンプト
            emotion (Emotion): 感情（指定されない場合は現在の感情）
            
        Returns:
            str: 感情を反映したプロンプト
        """
        if emotion is None:
            emotion = self.current_emotion
        
        return self.emotion_analyzer.get_emotion_prompt(emotion, base_prompt)
    
    def get_current_emotion_info(self) -> Dict:
        """
        現在の感情情報を取得
        
        Returns:
            Dict: 感情情報
        """
        return {
            "emotion": self.current_emotion,
            "description": self.emotion_analyzer.get_emotion_description(self.current_emotion),
            "color_scheme": self.emotion_analyzer.get_emotion_color_scheme(self.current_emotion)
        }
    
    def get_emotion_statistics(self) -> Dict:
        """
        感情統計を取得
        
        Returns:
            Dict: 感情統計
        """
        if not self.emotion_history:
            return {}
        
        emotion_counts = {}
        for entry in self.emotion_history:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total = len(self.emotion_history)
        emotion_percentages = {
            emotion: (count / total) * 100
            for emotion, count in emotion_counts.items()
        }
        
        return {
            "counts": emotion_counts,
            "percentages": emotion_percentages,
            "total_messages": total,
            "most_frequent": max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else Emotion.NEUTRAL
        }
