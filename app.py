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
from io import BytesIO

# ----------------- Environment Setup -----------------
st.set_page_config(
    page_title="AI Emotion & Location Detector",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Language Setup -----------------
LANGUAGES = ["English", "中文", "Malay"]
lang = st.sidebar.selectbox("🌐 Select Language", LANGUAGES)

TRANSLATIONS = {
    "English": {
        "title": "AI Emotion & Location Detector",
        "upload_guide": "Upload a photo to analyze facial expressions and estimate location",
        # ... (保持之前的翻译内容不变)
    },
    "中文": {
        "title": "AI情绪与位置检测系统",
        "upload_guide": "上传照片分析面部表情并推测位置",
        # ... (保持之前的翻译内容不变)
    },
    "Malay": {
        "title": "Sistem Pengesanan Emosi & Lokasi AI",
        "upload_guide": "Muat naik foto untuk analisis ekspresi muka dan anggaran lokasi",
        # ... (保持之前的翻译内容不变)
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
        return face_cascade, eye_cascade, smile_cascade
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None, None, None

@st.cache_resource
def init_geolocator():
    """Initialize geolocator with rate limiting"""
    geolocator = Nominatim(user_agent="geo_locator_app")
    return RateLimiter(geolocator.reverse, min_delay_seconds=1)

# ----------------- Core Functions -----------------
def detect_emotion_deepface(img):
    """Advanced emotion detection using DeepFace"""
    try:
        results = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        return [result['dominant_emotion'] for result in results]
    except:
        return []

def get_location_metadata(image_file):
    """Get location from image metadata with fallback"""
    try:
        with Image.open(image_file) as img:
            exif = img._getexif()
            if exif and 34853 in exif:  # GPSInfo tag
                gps_info = exif[34853]
                lat = gps_info[2][0] + gps_info[2][1]/60 + gps_info[2][2]/3600
                lon = gps_info[4][0] + gps_info[4][1]/60 + gps_info[4][2]/3600
                return f"GPS: {lat:.4f}, {lon:.4f}"
    except:
        pass
    return None

# ----------------- UI Components -----------------
def show_analysis_results(image_file, username):
    """Display analysis results in a structured layout"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.container(border=True):
            st.subheader(T["analysis_results"])
            
            # Convert and analyze image
            img = Image.open(image_file)
            img_arr = np.array(img)
            img_cv = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
            
            # Emotion detection
            emotions = detect_emotion_deepface(img_cv)
            if not emotions:
                emotions = ["neutral"]  # Fallback
            
            st.metric(T["detected_emotion"], ", ".join(emotions))
            
            # Location estimation
            location = get_location_metadata(image_file) or random_location()
            st.metric(T["estimated_location"], location)
            
            # Save to history
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

    with col2:
        tab1, tab2 = st.tabs([T["original_image"], T["processed_image"]])
        
        with tab1:
            st.image(img, use_column_width=True)
        
        with tab2:
            # Process image with face detection
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                cv2.rectangle(img_cv, (x, y), (x+w, y+h), (0, 255, 0), 2)
            st.image(img_cv, channels="BGR", use_column_width=True)

# ----------------- Main Application -----------------
def main():
    st.title(f"🌍 {T['title']}")
    st.caption(T["upload_guide"])
    
    # Initialize session state
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    # User authentication
    with st.sidebar:
        st.subheader(T["user_auth"])
        username = st.text_input(T["enter_username"], key="username_input")
        if username:
            st.session_state.username = username
            st.success(f"{T['welcome']} {username}")
    
    # Main content
    if st.session_state.username:
        uploaded_file = st.file_uploader(T["upload_image"], type=["jpg", "jpeg", "png"])
        if uploaded_file:
            show_analysis_results(uploaded_file, st.session_state.username)
    else:
        st.warning(T["auth_warning"])

if __name__ == "__main__":
    face_cascade, eye_cascade, smile_cascade = load_models()
    if None not in (face_cascade, eye_cascade, smile_cascade):
        main()
