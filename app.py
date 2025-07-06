import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import random
import logging
from geopy.geocoders import Nominatim

# ----------------- 初始化设置 -----------------
st.set_page_config(
    page_title="AI情绪与位置检测系统",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- 多语言支持 -----------------
LANGUAGES = ["中文", "English", "Malay"]
lang = st.sidebar.selectbox("🌐 选择语言", LANGUAGES)

TRANSLATIONS = {
    "中文": {
        "title": "AI情绪与位置检测系统",
        "upload_guide": "上传照片分析面部表情并推测位置",
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
        "debug_info": "调试信息"
    },
    "English": {
        "title": "AI Emotion & Location Detector",
        "upload_guide": "Upload a photo to analyze facial expressions and estimate location",
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
        "debug_info": "Debug Info"
    },
    "Malay": {
        "title": "Sistem Pengesanan Emosi & Lokasi AI",
        "upload_guide": "Muat naik foto untuk analisis ekspresi muka dan anggaran lokasi",
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
        "debug_info": "Maklumat Debug"
    }
}
T = TRANSLATIONS[lang]

# ----------------- 加载模型 -----------------
@st.cache_resource
def load_face_cascade():
    try:
        return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        st.error("无法加载人脸检测模型")
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
    """简化版情绪分析（实际项目建议用DeepFace）"""
    return ["happy" if random.random() > 0.5 else "neutral" for _ in faces]

def estimate_location():
    """随机位置生成（实际项目可用GPS元数据）"""
    cities = ["北京", "上海", "广州", "深圳", "成都"]
    return f"{random.choice(cities)}, 中国"

# ----------------- 界面组件 -----------------
def show_analysis_results(uploaded_file, username, face_cascade):
    try:
        img = Image.open(uploaded_file)
        img_cv = np.array(img)
        
        # 确保图像为3通道
        if len(img_cv.shape) == 2:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2BGR)
        elif img_cv.shape[2] == 4:
            img_cv = img_cv[:, :, :3]

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader(T["analysis_results"])
            
            faces = detect_faces(img_cv, face_cascade)
            if len(faces) == 0:
                st.warning(T["no_faces"])
                return

            emotions = analyze_emotion(faces)
            location = estimate_location()
            
            st.metric(T["detected_emotion"], ", ".join(emotions))
            st.metric(T["estimated_location"], location)

            # 保存结果
            save_to_history(username, emotions[0], location)
            
            # 下载按钮
            st.download_button(
                label=T["download_results"],
                data=pd.DataFrame({
                    "情绪": emotions,
                    "位置": [location]*len(emotions)
                }).to_csv(index=False),
                file_name="analysis_results.csv"
            )

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

# ----------------- 主程序 -----------------
def main():
    st.title(f"🌍 {T['title']}")
    st.caption(T["upload_guide"])
    
    face_cascade = load_face_cascade()
    if face_cascade is None:
        return
    
    # 用户登录
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    with st.sidebar:
        username = st.text_input(T["enter_username"], key="username_input")
        if username:
            st.session_state.username = username
            st.success(f"{T['welcome']} {username}")
    
    # 调试信息
    with st.expander(T["debug_info"]):
        st.write(f"OpenCV版本: {cv2.__version__}")
        st.write(f"Streamlit版本: {st.__version__}")
        st.write("会话状态:", st.session_state)
    
    # 主界面
    if st.session_state.username:
        uploaded_file = st.file_uploader(T["upload_image"], type=["jpg", "jpeg", "png"])
        if uploaded_file:
            show_analysis_results(uploaded_file, st.session_state.username, face_cascade)
    else:
        st.warning("请输入用户名继续")

if __name__ == "__main__":
    import os
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    main()
