import os
import streamlit as st
from config_manager import ConfigManager

st.set_page_config(page_title="🛠️ 設定", page_icon="⚙️", layout="centered")

cfg = ConfigManager()

st.title("⚙️ アプリ設定")

# -------------------------------------------
# モデル設定
# -------------------------------------------
with st.expander("🧠 モデル設定", expanded=True):
    system_prompt = st.text_area("システムプロンプト", value=cfg.data["model"].get("system_prompt", ""))
    col_temp, col_top_p = st.columns(2)
    with col_temp:
        temperature = st.slider("Temperature", 0.0, 1.0, value=float(cfg.data["model"].get("temperature", 0.7)), step=0.05)
    with col_top_p:
        top_p = st.slider("Top-p", 0.0, 1.0, value=float(cfg.data["model"].get("top_p", 0.9)), step=0.05)
    if st.button("💾 モデル設定を保存"):
        cfg.data["model"].update({
            "system_prompt": system_prompt,
            "temperature": temperature,
            "top_p": top_p,
        })
        cfg.save()
        st.success("モデル設定を保存しました")

# -------------------------------------------
# 画像生成設定
# -------------------------------------------
with st.expander("🎨 Stable Diffusion 設定", expanded=False):
    positive_prompt = st.text_area("ポジティブプロンプト", value=cfg.data["sd"].get("positive_prompt", ""))
    negative_prompt = st.text_area("ネガティブプロンプト", value=cfg.data["sd"].get("negative_prompt", ""))
    steps = st.number_input("ステップ数", min_value=5, max_value=150, value=int(cfg.data["sd"].get("steps", 30)))
    if st.button("💾 SD 設定を保存"):
        cfg.data["sd"].update({
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
        })
        cfg.save()
        st.success("Stable Diffusion 設定を保存しました")

# -------------------------------------------
# 画像アップロード
# -------------------------------------------
with st.expander("🖼️ 背景／アイコン画像", expanded=False):
    bg_file = st.file_uploader("背景画像をアップロード", type=["png", "jpg", "jpeg"], key="bg_uploader")
    icon_file = st.file_uploader("アイコン画像をアップロード", type=["png", "jpg", "jpeg"], key="icon_uploader")
    if st.button("💾 画像を保存"):
        assets_dir = "assets"
        os.makedirs(assets_dir, exist_ok=True)
        if bg_file is not None:
            bg_path = os.path.join(assets_dir, "background.png")
            with open(bg_path, "wb") as f:
                f.write(bg_file.getbuffer())
            cfg.data["images"]["background"] = bg_path
        if icon_file is not None:
            icon_path = os.path.join(assets_dir, "icon.png")
            with open(icon_path, "wb") as f:
                f.write(icon_file.getbuffer())
            cfg.data["images"]["icon"] = icon_path
        cfg.save()
        st.success("画像を保存しました。トップページをリロードすると反映されます。")
    if cfg.data["images"].get("background"):
        st.image(cfg.data["images"]["background"], caption="現在の背景画像", use_column_width=True)
    if cfg.data["images"].get("icon"):
        st.image(cfg.data["images"]["icon"], caption="現在のアイコン画像", width=100)

# -------------------------------------------
# その他
# -------------------------------------------
with st.expander("🔄 設定の再生成／リセット", expanded=False):
    col_reset, col_show = st.columns(2)
    with col_reset:
        if st.button("🗑️ 設定をリセット", type="primary"):
            cfg.reset()
            st.success("設定をデフォルトに戻しました。ページを再読み込みしてください。")
    with col_show:
        st.json(cfg.data)

# -------------------------------------------
# ユーザーペルソナ
# -------------------------------------------
with st.expander("👤 ユーザーペルソナ", expanded=False):
    user_section = cfg.data.get("user", {})
    user_name = st.text_input("あなたの名前", value=user_section.get("name", ""))
    persona_desc = st.text_area("あなたのペルソナ (AI に共有したい自己紹介や性格)", value=user_section.get("persona", ""))
    if st.button("💾 ペルソナを保存"):
        cfg.data.setdefault("user", {})
        cfg.data["user"].update({
            "name": user_name,
            "persona": persona_desc,
        })
        cfg.save()
        st.success("ペルソナを保存しました。チャット画面で再実行すると反映されます。") 