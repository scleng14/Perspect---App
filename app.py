import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import random
import logging
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
        "upload_guide": "上传照片分析面部表情并推测位置",
        "username": "用户名",
        "user_auth": "用户认证",  # 新增
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
        "input_username_continue": "请输入用户名继续"
    },
    "English": {
        "title": "AI Emotion & Location Detector",
        "upload_guide": "Upload a photo to analyze facial expressions and estimate location",
        "username": "Username",
        "user_auth": "User Authentication",  # 新增
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
        "input_username_continue": "Please enter a username to continue"
    },
    "Malay": {
        "title": "Sistem Pengesanan Emosi & Lokasi AI",
        "upload_guide": "Muat naik foto untuk analisis ekspresi muka dan anggaran lokasi",
        "username": "Nama pengguna",
        "user_auth": "Pengesahan Pengguna",  # 新增
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
        "input_username_continue": "Masukkan nama pengguna untuk meneruskan"
    }
}
T = TRANSLATIONS[lang]

# ----------------- 加载模型 -----------------
@st.cache_resource
def load_face_cascade():
    try:
        # 使用OpenCV自带的模型路径
        model_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        cascade = cv2.CascadeClassifier(model_path)
        if cascade.empty():
            raise ValueError("Failed to load cascade classifier")
        
        return cascade
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        st.error("Failed to load face detection model")
        return None

# ----------------- 核心功能 -----------------
def detect_faces(img_cv, face_cascade):
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces if faces is not None else np.array([])
    except Exception as e:
        logger.error(f"人脸检测错误: {e}")
        return np.array([])

def analyze_emotion(faces):
    return ["happy" if random.random() > 0.5 else "neutral" for _ in faces]

def draw_detections(img, faces, emotions):
    """绘制检测框和情绪标签"""
    img_copy = img.copy()
    color_map = {
        "happy": (0, 255, 0),    # 绿色
        "neutral": (255, 255, 0), # 黄色
        "sad": (0, 0, 255),       # 红色
        "angry": (0, 165, 255)    # 橙色
    }
    
    for i, ((x, y, w, h), emotion) in enumerate(zip(faces, emotions)):
        color = color_map.get(emotion, (255, 255, 255))
        cv2.rectangle(img_copy, (x, y), (x+w, y+h), color, 2)
        cv2.putText(img_copy, emotion, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    return img_copy

def save_to_history(username, emotion, location):
    try:
        new_record = pd.DataFrame([{
            "username": username,
            "emotion": emotion,
            "location": location,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        if os.path.exists("history.csv"):
            history = pd.read_csv("history.csv")
            history = pd.concat([history, new_record])
        else:
            history = new_record
            
        history.to_csv("history.csv", index=False)
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
            location = "Unknown"  # 简化版，不使用geopy

            st.metric(T["detected_emotion"], ", ".join(emotions))
            st.metric(T["estimated_location"], location)

            save_to_history(username, emotions[0], location)

            csv_data = pd.DataFrame({
                "Emotion": emotions,
                "Location": [location]*len(emotions)
            }).to_csv(index=False)
            
            st.download_button(
                label=T["download_results"],
                data=csv_data,
                file_name="analysis_results.csv"
            )

        with col2:
            tab1, tab2 = st.tabs([T["original_image"], T["processed_image"]])
            with tab1:
                st.image(img, use_column_width=True)
            with tab2:
                detected_img = draw_detections(img_cv, faces, emotions)
                st.image(detected_img, channels="BGR", use_column_width=True,
                        caption=f"{len(faces)} {T['faces_detected']}")
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
