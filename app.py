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
        "user_auth": "用户认证",
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
        "nav_home": "主页",
        "nav_location_map": "位置地图",
        "nav_history": "历史记录",
        "nav_filter": "查找 & 筛选",
        "nav_emotion_chart": "情绪分析图表",  # 新增
        "upload_history": "上传历史",
        "no_history": "暂无历史记录",
        "filter_user": "按用户名筛选",
        "records_shown": "条记录已显示",
        "no_record_found": "未找到记录",
        "enter_username_history": "请输入用户名查看历史"
    },
    "English": {
        "title": "AI Emotion & Location Detector",
        "upload_guide": "Upload a photo to analyze facial expressions and estimate location",
        "username": "Username",
        "user_auth": "User Authentication",
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
        "nav_home": "Home",
        "nav_location_map": "Location Map",
        "nav_history": "History",
        "nav_filter": "Search & Filter",
        "nav_emotion_chart": "Emotion Chart",  # 新增
        "upload_history": "Upload History",
        "no_history": "No history available",
        "filter_user": "Filter by username",
        "records_shown": "records shown",
        "no_record_found": "No records found",
        "enter_username_history": "Please enter username to view history"
    },
    "Malay": {
        "title": "Sistem Pengesanan Emosi & Lokasi AI",
        "upload_guide": "Muat naik foto untuk analisis ekspresi muka dan anggaran lokasi",
        "username": "Nama pengguna",
        "user_auth": "Pengesahan Pengguna",
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
        "nav_home": "Halaman Utama",
        "nav_location_map": "Peta Lokasi",
        "nav_history": "Sejarah",
        "nav_filter": "Cari & Tapis",
        "nav_emotion_chart": "Carta Emosi",  # 新增
        "upload_history": "Sejarah Muat Naik",
        "no_history": "Tiada sejarah tersedia",
        "filter_user": "Tapis mengikut nama pengguna",
        "records_shown": "rekod dipaparkan",
        "no_record_found": "Tiada rekod dijumpai",
        "enter_username_history": "Sila masukkan nama pengguna untuk melihat sejarah"
    }
}
T = TRANSLATIONS[lang]

# ----------------- 加载模型 -----------------
@st.cache_resource
def load_face_cascade():
    try:
        model_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
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
        return faces if faces is not None else np.array([])
    except Exception as e:
        logger.error(f"人脸检测错误: {e}")
        return np.array([])

def analyze_emotion(image):
    emotions = ["Happy", "Sad", "Angry", "Neutral", "Surprised"]
    return random.choice(emotions)

def save_history(username, emotion, location):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame([[username, emotion, location, now]], 
                            columns=["Username", "Emotion", "Location", "timestamp"])
    
    try:
        if os.path.exists("history.csv"):
            history_df = pd.read_csv("history.csv")
            history_df = pd.concat([history_df, new_record])
        else:
            history_df = new_record
        history_df.to_csv("history.csv", index=False)
    except Exception as e:
        logger.error(f"保存历史失败: {e}")

# ----------------- 主程序 -----------------
def main():
    st.title(f"🌍 {T['title']}")
    st.caption(T["upload_guide"])

    face_cascade = load_face_cascade()
    if face_cascade is None:
        return

    # 初始化标签页
    tabs = st.tabs([
        f"🏠 {T['nav_home']}",
        f"🗺️ {T['nav_location_map']}",
        f"📜 {T['nav_history']}",
        f"📊 {T['nav_filter']}"
    ])

    # 主页标签
    with tabs[0]:
        username = st.text_input(f"👤 {T['enter_username']}")
        if username:
            st.sidebar.success(f"👤 {T['welcome']} {username}")
            uploaded_file = st.file_uploader(f"📄 {T['upload_image']}", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader(T["analysis_results"])
                    emotion = analyze_emotion(img_cv)
                    location = "Unknown"  # 简化位置功能
                    
                    st.metric(T["detected_emotion"], emotion)
                    st.metric(T["estimated_location"], location)
                    save_history(username, emotion, location)
                
                with col2:
                    tab1, tab2 = st.tabs([T["original_image"], T["processed_image"]])
                    with tab1:
                        st.image(img, use_column_width=True)
                    with tab2:
                        faces = detect_faces(img_cv, face_cascade)
                        if len(faces) > 0:
                            for (x, y, w, h) in faces:
                                cv2.rectangle(img_cv, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        st.image(img_cv, channels="BGR", use_column_width=True)

    # 位置地图标签
    with tabs[1]:
        st.map(pd.DataFrame({
            'lat': [3.1390 + random.uniform(-0.01, 0.01)],
            'lon': [101.6869 + random.uniform(-0.01, 0.01)]
        }))

    # 历史记录标签
    with tabs[2]:
        st.header(f"📜 {T['upload_history']}")
        if 'username' in st.session_state and st.session_state.username:
            try:
                history_df = pd.read_csv("history.csv") if os.path.exists("history.csv") else pd.DataFrame()
                if not history_df.empty:
                    st.dataframe(history_df)
                else:
                    st.info(T["no_history"])
            except Exception as e:
                st.error(f"读取历史记录错误: {e}")
        else:
            st.warning(T["enter_username_history"])

    # 筛选标签
    with tabs[3]:
        st.subheader(f"🧪 {T['nav_filter']}")
        st.subheader(f"📊 {T['nav_emotion_chart']}")
        
        try:
            if os.path.exists("history.csv"):
                df = pd.read_csv("history.csv")
                if not df.empty:
                    fig = px.pie(df, names="Emotion", title=T["nav_emotion_chart"])
                    st.plotly_chart(fig)
                else:
                    st.warning(T["no_history"])
            else:
                st.warning(T["no_record_found"])
        except Exception as e:
            st.error(f"生成图表错误: {e}")

if __name__ == "__main__":
    if not os.path.exists(".streamlit"):
        os.makedirs(".streamlit")
    main()
