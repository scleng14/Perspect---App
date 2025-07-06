import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
from utils.emotion import analyze_emotion
from utils.gps_utils import extract_gps_location
from utils.landmark import recognize_landmark

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="Emotion & Location Analyzer",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Session State ----------------
if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------------- Language Strings ----------------
LANGUAGES = {
    "English": {
        "upload_title": "Upload Image",
        "upload_caption": "Upload a photo to detect faces, emotions, and location",
        "face_detected": "Face Detected",
        "emotion_result": "Emotion: {} (Confidence: {:.2f}%)",
        "location_found": "📍 Location: {}",
        "no_gps": "No GPS info found. Trying landmark recognition...",
        "landmark_result": "🗼 Landmark: {}",
        "history": "View History",
        "timestamp": "Timestamp",
        "save_success": "✅ Record saved to history.csv",
        "download": "Download CSV History"
    },
    "中文": {
        "upload_title": "上传图片",
        "upload_caption": "上传照片以检测人脸、情绪和位置",
        "face_detected": "检测到人脸",
        "emotion_result": "情绪：{}（置信度：{:.2f}%）",
        "location_found": "📍 位置：{}",
        "no_gps": "未发现 GPS 信息，尝试识别地标...",
        "landmark_result": "🗼 地标：{}",
        "history": "查看记录",
        "timestamp": "时间戳",
        "save_success": "✅ 已保存至 history.csv",
        "download": "下载 CSV 记录"
    },
    "Malay": {
        "upload_title": "Muat Naik Imej",
        "upload_caption": "Muat naik gambar untuk kesan wajah, emosi dan lokasi",
        "face_detected": "Wajah Dikesan",
        "emotion_result": "Emosi: {} (Keyakinan: {:.2f}%)",
        "location_found": "📍 Lokasi: {}",
        "no_gps": "Tiada GPS. Mencuba pengecaman mercu tanda...",
        "landmark_result": "🗼 Mercu tanda: {}",
        "history": "Lihat Sejarah",
        "timestamp": "Cap Masa",
        "save_success": "✅ Rekod disimpan ke history.csv",
        "download": "Muat turun Sejarah CSV"
    }
}

# ---------------- Language Switcher ----------------
with st.container():
    cols = st.columns(3)
    for i, lang in enumerate(LANGUAGES):
        if cols[i].button(lang):
            st.session_state.language = lang
current_lang = LANGUAGES[st.session_state.language]

st.title(current_lang["upload_title"])
st.caption(current_lang["upload_caption"])

# ---------------- Upload Image ----------------
uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, use_column_width=True)

    # ----- Emotion -----
    result = analyze_emotion(image)
    if result:
        st.success(current_lang["face_detected"])
        st.write(current_lang["emotion_result"].format(result["emotion"], result["confidence"] * 100))
    else:
        st.warning("No face detected.")

    # ----- Location -----
    location = extract_gps_location(image)
    if location:
        st.info(current_lang["location_found"].format(location))
    else:
        st.warning(current_lang["no_gps"])
        landmark = recognize_landmark(image)
        if landmark:
            st.info(current_lang["landmark_result"].format(landmark))
            location = landmark
        else:
            location = "Unknown"

    # ----- Save History -----
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emotion = result["emotion"] if result else "None"
    record = pd.DataFrame([[timestamp, emotion, location]], columns=["timestamp", "emotion", "location"])

    if os.path.exists("history.csv"):
        old = pd.read_csv("history.csv")
        record = pd.concat([old, record], ignore_index=True)
    record.to_csv("history.csv", index=False)
    st.success(current_lang["save_success"])

# ---------------- History Page ----------------
st.subheader(current_lang["history"])
if os.path.exists("history.csv"):
    df = pd.read_csv("history.csv")
    st.dataframe(df)
    st.download_button(current_lang["download"], df.to_csv(index=False), file_name="history.csv")
else:
    st.info("No history found yet.")
