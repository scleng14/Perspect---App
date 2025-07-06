import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import plotly.express as px
import random
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os
import logging

# ----------------- Setup -----------------
st.set_page_config(
    page_title="AI Emotion & Location Detector",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- Language Setup -----------------
LANGUAGES = ["English", "中文", "Malay"]
lang = st.sidebar.selectbox("🌐 Select Language", LANGUAGES)

TRANSLATIONS = {
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

# ----------------- Cache Resources -----------------
@st.cache_resource
def load_models():
    """Load pre-trained models with error handling"""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        if face_cascade.empty() or eye_cascade.empty() or smile_cascade.empty():
            raise ValueError("Failed to load one or more cascade classifiers")
            
        return face_cascade, eye_cascade, smile_cascade
    except Exception as e:
        logger.error(f"Model loading error: {str(e)}")
        st.error("Failed to load detection models. Please check the logs.")
        return None, None, None

@st.cache_resource
def init_geolocator():
    """Initialize geolocator with rate limiting"""
    try:
        geolocator = Nominatim(user_agent="geo_locator_app_v1")
        return RateLimiter(geolocator.reverse, min_delay_seconds=1)
    except Exception as e:
        logger.error(f"Geolocator init error: {str(e)}")
        return None

# ----------------- Core Functions -----------------
def validate_image(image):
    """Validate and convert image to proper format"""
    try:
        if isinstance(image, np.ndarray):
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 4:
                image = image[:, :, :3]
            return image
        elif isinstance(image, Image.Image):
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            raise ValueError("Unsupported image format")
    except Exception as e:
        logger.error(f"Image validation error: {str(e)}")
        raise

def detect_emotions(img_cv, face_cascade):
    """Detect faces and emotions with robust error handling"""
    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
        
        if not isinstance(faces, np.ndarray):
            return [], []
            
        emotions = []
        valid_faces = []
        
        for (x, y, w, h) in faces:
            if x >= 0 and y >= 0 and w > 10 and h > 10:
                valid_faces.append((x, y, w, h))
                roi_gray = gray[y:y+h, x:x+w]
                
                # Simple emotion detection (can be replaced with DeepFace)
                emotions.append("happy" if random.random() > 0.5 else "neutral")
        
        return emotions, valid_faces
    except Exception as e:
        logger.error(f"Emotion detection error: {str(e)}")
        return [], []

def random_location():
    """Generate random location as fallback"""
    cities = ["Kuala Lumpur", "Tokyo", "Paris", "New York", "London"]
    countries = ["Malaysia", "Japan", "France", "USA", "UK"]
    return f"{random.choice(cities)}, {random.choice(countries)}"

def save_history(username, emotion, location):
    """Save results to history file"""
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_record = pd.DataFrame([[username, emotion, location, now]],
                                columns=["Username", "Emotion", "Location", "timestamp"])
        
        if os.path.exists("history.csv"):
            history_df = pd.read_csv("history.csv")
            history_df = pd.concat([history_df, new_record], ignore_index=True)
        else:
            history_df = new_record
            
        history_df.to_csv("history.csv", index=False)
    except Exception as e:
        logger.error(f"History save error: {str(e)}")

# ----------------- UI Components -----------------
def show_analysis_results(image_file, username, face_cascade):
    """Display analysis results with comprehensive error handling"""
    try:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            with st.container(border=True):
                st.subheader(T["analysis_results"])
                
                try:
                    img = Image.open(image_file)
                    img_cv = validate_image(img)
                    
                    emotions, faces = detect_emotions(img_cv, face_cascade)
                    
                    if not faces:
                        st.warning(T["no_faces"])
                        return
                        
                    location = random_location()  # Simplified for demo
                    
                    st.metric(T["detected_emotion"], ", ".join(emotions))
                    st.metric(T["estimated_location"], location)
                    
                    save_history(username, emotions[0], location)
                    
                    # Download button
                    csv = pd.DataFrame({
                        "Metric": [T["detected_emotion"], T["estimated_location"]],
                        "Value": [", ".join(emotions), location]
                    }).to_csv(index=False)
                    
                    st.download_button(
                        label=T["download_results"],
                        data=csv,
                        file_name="analysis_results.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(T["error_processing"])
                    logger.error(f"Analysis error: {str(e)}")
        
        with col2:
            try:
                tab1, tab2 = st.tabs([T["original_image"], T["processed_image"]])
                
                with tab1:
                    st.image(img, use_column_width=True)
                
                with tab2:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img_cv, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    st.image(img_cv, channels="BGR", use_column_width=True)
                    
            except Exception as e:
                st.error("Image display error")
                logger.error(f"Display error: {str(e)}")
                
    except Exception as e:
        st.error("System error occurred")
        logger.error(f"System error: {str(e)}")

# ----------------- Main Application -----------------
def main():
    st.title(f"🌍 {T['title']}")
    st.caption(T["upload_guide"])
    
    # Initialize models
    face_cascade, _, _ = load_models()
    if face_cascade is None:
        st.error("Critical error: Face detection model failed to load")
        return
    
    # Session state management
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    # User authentication
    with st.sidebar:
        st.subheader(T["username"])
        username = st.text_input(T["enter_username"], key="username_input")
        if username:
            st.session_state.username = username
            st.success(f"{T['welcome']} {username}")
    
    # Debug info
    with st.expander(T["debug_info"], expanded=False):
        st.write(f"OpenCV version: {cv2.__version__}")
        st.write(f"Pillow version: {Image.__version__}")
        st.write(f"Session state: {st.session_state}")
    
    # Main content
    if st.session_state.username:
        uploaded_file = st.file_uploader(T["upload_image"], type=["jpg", "jpeg", "png"])
        if uploaded_file:
            show_analysis_results(uploaded_file, st.session_state.username, face_cascade)
    else:
        st.warning("Please enter a username to continue")

if __name__ == "__main__":
    main()
