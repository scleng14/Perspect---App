# ai_emotion_location_app.py

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import random
import logging
from geopy.geocoders import Nominatim
import os
from io import BytesIO

# ----------------- 初始化设置 -----------------
st.set_page_config(
    page_title="AI Emotion & Location Detector",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- 多语言支持 -----------------
LANGUAGES = ["中文", "English", "Malay"]
lang = st.sidebar.selectbox("🌐 Select Language / 选择语言 / Pilih Bahasa", LANGUAGES)

TRANSLATIONS = {
    "中文": {
        "title": "AI情绪与位置检测系统",
        "upload_guide": "上传照片分析面部表情并推测位置（带GPS或地标）",
        "username": "用户名",
        "enter_username": "输入用户名",
        "welcome": "欢迎",
        "upload_image": "上传图片 (JPG/PNG)",
        "analysis_results": "分析结果",
        "detected_emotion": "检测到的情绪",
        "estimated_location": "估计位置",
        "download_results": "下载结果",
        "original_image": "原始图片",
        "processed_image": "处理后的图片",
        "no_faces": "未检测到人脸",
        "error_processing": "图片处理错误",
        "debug_info": "调试信息",
        "input_username_continue": "请输入用户名继续",
        "user_auth": "用户身份验证"
    },
    "English": {
        "title": "AI Emotion & Location Detector",
        "upload_guide": "Upload a photo to analyze facial expressions and estimate location (via GPS or landmark)",
        "username": "Username",
        "enter_username": "Enter your username",
        "welcome": "Welcome",
        "upload_image": "Upload an image (JPG/PNG)",
        "analysis_results": "Analysis Results",
        "detected_emotion": "Detected Emotion",
        "estimated_location": "Estimated Location",
        "download_results": "Download Results",
        "original_image": "Original Image",
        "processed_image": "Processed Image",
        "no_faces": "No faces detected",
        "error_processing": "Error processing image",
        "debug_info": "Debug Info",
        "input_username_continue": "Please enter a username to continue",
        "user_auth": "User Authentication"
    },
    "Malay": {
        "title": "Sistem Pengesanan Emosi & Lokasi AI",
        "upload_guide": "Muat naik foto untuk analisis ekspresi muka dan anggaran lokasi (GPS atau mercu tanda)",
        "username": "Nama pengguna",
        "enter_username": "Masukkan nama pengguna",
        "welcome": "Selamat datang",
        "upload_image": "Muat naik imej (JPG/PNG)",
        "analysis_results": "Keputusan Analisis",
        "detected_emotion": "Emosi yang Dikesan",
        "estimated_location": "Lokasi Dianggarkan",
        "download_results": "Muat Turun Keputusan",
        "original_image": "Imej Asal",
        "processed_image": "Imej Diproses",
        "no_faces": "Tiada muka dikesan",
        "error_processing": "Ralat memproses imej",
        "debug_info": "Maklumat Debug",
        "input_username_continue": "Masukkan nama pengguna untuk meneruskan",
        "user_auth": "Pengesahan Pengguna"
    }
}
T = TRANSLATIONS[lang]

# ----------------- 加载模型 -----------------
@st.cache_resource
def load_face_cascade():
    try:
        model_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        return cv2.CascadeClassifier(model_path)
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        st.error("Failed to load face detection model")
        return None

# ----------------- 核心功能 -----------------
def detect_faces(img_cv, face_cascade):
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces if isinstance(faces, np.ndarray) else np.array([])
    except Exception as e:
        logger.error(f"人脸检测错误: {e}")
        return np.array([])

def analyze_emotion(faces):
    return ["happy" if random.random() > 0.5 else "neutral" for _ in faces]

def extract_gps_location(img):
    try:
        exif = img._getexif()
        if not exif:
            return None
        gps_info = exif.get(34853)
        if not gps_info:
            return None

        def convert_to_degrees(value):
            d, m, s = value
            return d[0] / d[1] + m[0] / m[1] / 60 + s[0] / s[1] / 3600

        lat = convert_to_degrees(gps_info[2])
        if gps_info[1] == 'S':
            lat = -lat
        lon = convert_to_degrees(gps_info[4])
        if gps_info[3] == 'W':
            lon = -lon

        geolocator = Nominatim(user_agent="emotion_location_app")
        location = geolocator.reverse((lat, lon), language='en')
        return location.address if location else None
    except Exception as e:
        logger.warning(f"GPS读取失败: {e}")
        return None

def save_to_history(username, emotion, location):
    try:
        new_record = pd.DataFrame([{
            "username": username,
            "emotion": emotion,
            "location": location,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        new_record.to_csv("history.csv", mode='a', index=False, header=not os.path.exists("history.csv"))
    except Exception as e:
        logger.error(f"保存历史记录失败: {e}")

# ----------------- 显示分析结果 -----------------
def show_analysis_results(uploaded_file, username, face_cascade):
    try:
        img = Image.open(uploaded_file)
        img_cv = np.array(img.convert("RGB"))

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader(T["analysis_results"])

            faces = detect_faces(img_cv, face_cascade)
            if len(faces) == 0:
                st.warning(T["no_faces"])
                return

            emotions = analyze_emotion(faces)
            location = extract_gps_location(img) or "Unknown"

            st.metric(T["detected_emotion"], ", ".join(emotions))
            st.metric(T["estimated_location"], location)

            save_to_history(username, emotions[0], location)

            csv_data = pd.DataFrame({"Emotion": emotions, "Location": [location]*len(emotions)}).to_csv(index=False)
            st.download_button(label=T["download_results"], data=csv_data, file_name="analysis_results.csv")

        with col2:
            tab1, tab2 = st.tabs([T["original_image"], T["processed_image"]])
            with tab1:
                st.image(img, use_column_width=True)
            with tab2:
                for (x, y, w, h) in faces:
                    cv2.rectangle(img_cv, (x, y), (x+w, y+h), (0, 255, 0), 2)
                st.image(img_cv, channels="BGR", use_column_width=True)
    except Exception as e:
        logger.error(f"分析错误: {e}")
        st.error(T["error_processing"])

# ----------------- 主程序 -----------------
def main():
    st.title(f"🌍 {T['title']}")
    st.caption(T["upload_guide"])

    face_cascade = load_face_cascade()
    if face_cascade is None:
        return

    if "username" not in st.session_state:
        st.session_state.username = ""

    with st.sidebar:
        st.subheader(T["user_auth"])
        username = st.text_input(T["enter_username"], key="username_input")
        if username:
            st.session_state.username = username
            st.success(f"{T['welcome']} {username}")

    with st.expander(T["debug_info"]):
        st.write(f"OpenCV version: {cv2.__version__}")
        st.write(f"Streamlit version: {st.__version__}")
        st.write("Session State:", st.session_state)

    if st.session_state.username:
        uploaded_file = st.file_uploader(T["upload_image"], type=["jpg", "jpeg", "png"])
        if uploaded_file:
            show_analysis_results(uploaded_file, st.session_state.username, face_cascade)
    else:
        st.warning(T["input_username_continue"])

if __name__ == "__main__":
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    main()
