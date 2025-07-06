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
    page_title="AI Emotion Detector",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- 多语言支持 -----------------
LANGUAGES = ["English", "中文", "Malay"]
lang = st.sidebar.selectbox("🌐 Select Language", LANGUAGES)

TRANSLATIONS = {
    "English": {
        "title": "AI Emotion Detection",
        "upload_guide": "Upload a photo to analyze facial expressions",
        "upload_prompt": "Upload an image (JPG/PNG)",
        "detected_emotion": "Detected Emotion",
        "analysis_results": "Analysis Results",
        "original_image": "Original Image",
        "processed_image": "Processed Image",
        "no_faces": "No faces detected",
        "error_processing": "Error processing image",
        "detection_guide": "How Emotion Detection Works",
        "detection_logic": "Detection Logic:",
        "happy_logic": "😊 Happy: Detected when smile is present",
        "angry_logic": "😠 Angry: Wide open eyes in upper face",
        "neutral_logic": "😐 Neutral: Default state",
        "sad_logic": "😢 Sad: Eyes positioned higher than normal",
        "tips_title": "Tips for Better Results:",
        "tip1": "Use clear, front-facing images",
        "tip2": "Ensure good lighting",
        "tip3": "Avoid obstructed faces"
    },
    "中文": {
        "title": "AI情绪检测系统",
        "upload_guide": "上传照片分析面部表情",
        "upload_prompt": "上传图片 (JPG/PNG)",
        "detected_emotion": "检测到的情绪",
        "analysis_results": "分析结果",
        "original_image": "原始图片",
        "processed_image": "处理后的图片",
        "no_faces": "未检测到人脸",
        "error_processing": "图片处理错误",
        "detection_guide": "情绪检测原理",
        "detection_logic": "检测逻辑:",
        "happy_logic": "😊 开心: 检测到微笑时",
        "angry_logic": "😠 生气: 眼睛睁大且位于面部上方",
        "neutral_logic": "😐 中性: 默认状态",
        "sad_logic": "😢 悲伤: 眼睛位置较高",
        "tips_title": "优化建议:",
        "tip1": "使用清晰的正面图像",
        "tip2": "确保良好光线",
        "tip3": "避免面部被遮挡"
    },
    "Malay": {
        "title": "Sistem Pengesanan Emosi AI",
        "upload_guide": "Muat naik foto untuk analisis ekspresi muka",
        "upload_prompt": "Muat naik imej (JPG/PNG)",
        "detected_emotion": "Emosi yang Dikesan",
        "analysis_results": "Keputusan Analisis",
        "original_image": "Imej Asal",
        "processed_image": "Imej Diproses",
        "no_faces": "Tiada muka dikesan",
        "error_processing": "Ralat memproses imej",
        "detection_guide": "Cara Pengesanan Emosi Berfungsi",
        "detection_logic": "Logik Pengesanan:",
        "happy_logic": "😊 Gembira: Dikesan apabila senyuman hadir",
        "angry_logic": "😠 Marah: Mata terbuka lebar di bahagian atas muka",
        "neutral_logic": "😐 Neutral: Keadaan lalai",
        "sad_logic": "😢 Sedih: Mata berada lebih tinggi daripada biasa",
        "tips_title": "Petua untuk Hasil Lebih Baik:",
        "tip1": "Gunakan imej jelas menghadap depan",
        "tip2": "Pastikan pencahayaan baik",
        "tip3": "Elakkan muka terhalang"
    }
}
T = TRANSLATIONS[lang]

# ----------------- 加载模型 -----------------
@st.cache_resource
def load_models():
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        return face_cascade, eye_cascade, smile_cascade
    except Exception as e:
        logger.error(f"Model loading failed: {str(e)}")
        st.error("Failed to load detection models")
        return None, None, None

face_cascade, eye_cascade, smile_cascade = load_models()

# ----------------- 核心功能 -----------------
def detect_emotion(img):
    """Detect emotions using OpenCV"""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        emotions = []
        valid_faces = []
        
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            
            # Detect facial features
            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
            eyes = eye_cascade.detectMultiScale(roi_gray)
            
            # Emotion detection logic
            emotion = "neutral"
            
            if len(eyes) >= 2:
                eye_centers = [y + ey + eh/2 for (ex,ey,ew,eh) in eyes[:2]]
                avg_eye_height = np.mean(eye_centers)
                eye_sizes = [eh for (ex,ey,ew,eh) in eyes[:2]]
                avg_eye_size = np.mean(eye_sizes)
                
                if avg_eye_size > h/5 and avg_eye_height < h/2.5:
                    emotion = "angry"
                elif avg_eye_height < h/3:
                    emotion = "sad"
            
            if len(smiles) > 0:
                emotion = "happy"
            
            emotions.append(emotion)
            valid_faces.append((x,y,w,h))
        
        return emotions, np.array(valid_faces)
    except Exception as e:
        logger.error(f"Emotion detection error: {str(e)}")
        return [], np.array([])

def draw_detections(img, emotions, faces):
    """Draw detection boxes with labels"""
    output_img = img.copy()
    color_map = {
        "happy": (0, 255, 0),     # green
        "neutral": (255, 255, 0),  # yellow
        "sad": (0, 0, 255),        # red
        "angry": (0, 165, 255)     # orange
    }
    
    for (x,y,w,h), emotion in zip(faces, emotions):
        color = color_map.get(emotion, (255, 255, 255))
        cv2.rectangle(output_img, (x,y), (x+w,y+h), color, 2)
        cv2.putText(output_img, emotion.upper(), (x+5, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return output_img

def show_detection_guide(show_full=True):
    """Show detection guide"""
    with st.expander(f"ℹ️ {T['detection_guide']}", expanded=False):
        if show_full:
            st.markdown(f"**{T['detection_logic']}**")
            st.markdown(f"- {T['happy_logic']}")
            st.markdown(f"- {T['angry_logic']}")
            st.markdown(f"- {T['neutral_logic']}")
            st.markdown(f"- {T['sad_logic']}")
        
        st.markdown(f"**{T['tips_title']}**")
        st.markdown(f"- {T['tip1']}")
        st.markdown(f"- {T['tip2']}")
        st.markdown(f"- {T['tip3']}")

# ----------------- 主程序 -----------------
def main():
    st.title(f"🎭 {T['title']}")
    st.caption(T["upload_guide"])
    
    uploaded_file = st.file_uploader(T["upload_prompt"], type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        try:
            # 转换图像格式
            image = Image.open(uploaded_file)
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 检测情绪
            emotions, faces = detect_emotion(img)
            
            # 两栏布局
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader(T["analysis_results"])
                if len(faces) > 0:
                    # 统计情绪类型
                    emotion_counts = {e: emotions.count(e) for e in set(emotions)}
                    result = ", ".join([f"{count} {emo}" for emo, count in emotion_counts.items()])
                    
                    st.success(f"🎭 Detected {len(faces)} face(s): {result}")
                    show_detection_guide(show_full=True)
                else:
                    st.warning(T["no_faces"])
                    show_detection_guide(show_full=False)
            
            with col2:
                tab1, tab2 = st.tabs([T["original_image"], T["processed_image"]])
                with tab1:
                    st.image(image, use_column_width=True)
                with tab2:
                    if len(faces) > 0:
                        detected_img = draw_detections(img, emotions, faces)
                        st.image(detected_img, channels="BGR", use_column_width=True,
                               caption=f"Detected {len(faces)} faces")
                    else:
                        st.image(img, channels="BGR", use_column_width=True)
                        
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            st.error(T["error_processing"])

if __name__ == "__main__":
    main()
