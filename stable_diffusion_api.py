import requests
import base64
import io
from PIL import Image
import os

class StableDiffusionAPI:
    def __init__(self, api_url="http://127.0.0.1:7860"):
        """
        Stable Diffusion WebUI APIの初期化
        
        Args:
            api_url (str): Stable Diffusion WebUIのAPI URL
        """
        self.api_url = api_url
        self.txt2img_url = f"{api_url}/sdapi/v1/txt2img"
        
    def check_connection(self):
        """
        Stable Diffusion WebUIとの接続をチェック
        
        Returns:
            bool: 接続成功ならTrue
        """
        try:
            response = requests.get(f"{self.api_url}/sdapi/v1/options", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_character_image(self, prompt, negative_prompt="", width=512, height=512):
        """
        キャラクター画像を生成
        
        Args:
            prompt (str): 画像生成プロンプト
            negative_prompt (str): ネガティブプロンプト
            width (int): 画像幅
            height (int): 画像高さ
            
        Returns:
            PIL.Image or None: 生成された画像またはNone
        """
        if not self.check_connection():
            return None
            
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": 20,
            "cfg_scale": 7,
            "sampler_name": "DPM++ 2M Karras",
            "seed": -1,
            "batch_size": 1,
            "n_iter": 1
        }
        
        try:
            response = requests.post(self.txt2img_url, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get('images'):
                    # Base64デコードして画像に変換
                    image_data = base64.b64decode(result['images'][0])
                    image = Image.open(io.BytesIO(image_data))
                    return image
        except Exception as e:
            print(f"画像生成エラー: {e}")
            
        return None
    
    def save_character_image(self, image, character_name, timestamp):
        """
        キャラクター画像を保存
        
        Args:
            image (PIL.Image): 保存する画像
            character_name (str): キャラクター名
            timestamp (str): タイムスタンプ
            
        Returns:
            str: 保存されたファイルパス
        """
        if image is None:
            return None
            
        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)
        
        filename = f"{character_name}_{timestamp}.png"
        filepath = os.path.join(images_dir, filename)
        
        image.save(filepath)
        return filepath
