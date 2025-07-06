import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import plotly.express as px
import random
import os
from geopy.geocoders import Nominatim
from deepface import DeepFace

# ----------------- Page Setup -----------------
st.set_page_config(page_title="Emotion & Location Detection", page_icon="👁‍🗨", layout="wide", initial_sidebar_state="expanded")

# ----------------- Language Setup -----------------
lang = st.sidebar.selectbox("🌐 Select Language", ["English","中文", "Malay"])

translations = {
    "English": {
        "title": "Emotion & Location Recognition System",
        "subtitle": "Try uploading a local photo to analyze emotion and estimate location.",
        "username_prompt": "Enter your username:",
        "logged_in": "Logged in as:",
        "upload_prompt": "Upload an image",
        "detected_emotion": "Detected Emotion",
        "estimated_location": "Estimated Location",
        "start_prompt": "Please enter your username to begin.",
        "nav_home": "Home",
        "nav_location_map": "Location Map",
        "nav_history": "History",
        "nav_filter": "Search & Filter",
        "upload_history": "Upload History",
        "no_history": "No history available yet.",
        "filter_user": "Filter by username (optional):",
        "records_shown": "record(s) shown.",
        "no_record_found": "No record found yet.",
        "enter_username_history": "Please enter your username to view history.",
        "detection_guide": "How Emotion Detection Works",
        "detection_logic": "Detection Logic Explained:",
        "happy_logic": "😊 Happy: Detected when smile is present",
        "angry_logic": "😠 Angry: Detected when eyes are wide open and positioned in upper face",
        "neutral_logic": "😐 Neutral: Default state when no strong indicators found",
        "sad_logic": "😢 Sad: Detected when eyes are positioned higher than normal",
        "tips": "Tips for Better Results:",
        "tip1": "Use clear, front-facing images",
        "tip2": "Ensure good lighting",
        "tip3": "Avoid obstructed faces",
        "faces_detected": "face(s) detected",
        "original_image": "Original Image",
        "analysis_result": "Analysis Result",
        "no_faces": "No faces detected"
    },
    "中文": {
        "title": "情绪与位置识别系统",
        "subtitle": "尝试上传本地照片，体验情绪识别与位置推测功能。",
        "username_prompt": "请输入用户名：",
        "logged_in": "已登录用户：",
        "upload_prompt": "上传图片",
        "detected_emotion": "识别的情绪",
        "estimated_location": "推测的位置",
        "start_prompt": "请输入用户名以开始。",
        "nav_home": "主页",
        "nav_location_map": "位置地图",
        "nav_history": "历史记录",
        "nav_filter": "查找 & 筛选",
        "upload_history": "上传历史",
        "no_history": "暂无历史记录。",
        "filter_user": "按用户名筛选（可选）：",
        "records_shown": "条记录已显示。",
        "no_record_found": "尚未找到任何记录。",
        "enter_username_history": "请输入用户名以查看历史记录。",
        "detection_guide": "情绪检测工作原理",
        "detection_logic": "检测逻辑说明:",
        "happy_logic": "😊 开心: 检测到微笑时",
        "angry_logic": "😠 生气: 当眼睛睁大且位于面部上方时检测到",
        "neutral_logic": "😐 中性: 未发现明显特征时的默认状态",
        "sad_logic": "😢 悲伤: 当眼睛位置比正常高时检测到",
        "tips": "获取更好结果的提示:",
        "tip1": "使用清晰的正面图像",
        "tip2": "确保良好的照明",
        "tip3": "避免面部被遮挡",
        "faces_detected": "检测到人脸",
        "original_image": "原始图片",
        "analysis_result": "分析结果",
        "no_faces": "未检测到人脸"
    },
    "Malay": {
        "title": "Sistem Pengecaman Emosi dan Lokasi",
        "subtitle": "Cuba muat naik foto tempatan untuk menganalisis emosi dan menganggar lokasi.",
        "username_prompt": "Masukkan nama pengguna anda:",
        "logged_in": "Log masuk sebagai:",
        "upload_prompt": "Muat naik imej",
        "detected_emotion": "Emosi Dikesan",
        "estimated_location": "Lokasi Dianggar",
        "start_prompt": "Sila masukkan nama pengguna untuk bermula.",
        "nav_home": "Halaman Utama",
        "nav_location_map": "Peta Lokasi",
        "nav_history": "Sejarah",
        "nav_filter": "Cari & Tapis",
        "upload_history": "Sejarah Muat Naik",
        "no_history": "Tiada sejarah tersedia buat masa ini.",
        "filter_user": "Tapis mengikut nama pengguna (pilihan):",
        "records_shown": "rekod dipaparkan.",
        "no_record_found": "Tiada rekod dijumpai setakat ini.",
        "enter_username_history": "Sila masukkan nama pengguna untuk melihat sejarah.",
        "detection_guide": "Bagaimana Pengesanan Emosi Berfungsi",
        "detection_logic": "Logik Pengesanan Dijelaskan:",
        "happy_logic": "😊 Gembira: Dikesan apabila senyuman hadir",
        "angry_logic": "😠 Marah: Dikesan apabila mata terbuka lebar dan berada di bahagian atas muka",
        "neutral_logic": "😐 Neutral: Keadaan lalai apabila tiada penunjuk kuat ditemui",
        "sad_logic": "😢 Sedih: Dikesan apabila mata berada lebih tinggi daripada biasa",
        "tips": "Petua untuk Hasil yang Lebih Baik:",
        "tip1": "Gunakan imej yang jelas dan menghadap ke hadapan",
        "tip2": "Pastikan pencahayaan yang baik",
        "tip3": "Elakkan muka yang terhalang",
        "faces_detected": "muka dikesan",
        "original_image": "Imej Asal",
        "analysis_result": "Keputusan Analisis",
        "no_faces": "Tiada muka dikesan"
    }
}
T = translations[lang]

# ----------------- Main Title -----------------
st.markdown(f"""
    <h1 style='text-align: center; color: #444444;'>👁‍🗨 {T['title']}</h1>
    <h4 style='text-align: center; color: #888888;'>{T['subtitle']}</h4>
""", unsafe_allow_html=True)

# ----------------- Tabs -----------------
tabs = st.tabs([
    f"🏠 {T['nav_home']}",
    f"📊 {T['nav_location_map']}",
    f"📂 {T['nav_history']}",
    f"📊 {T['nav_filter']}"
])

# ----------------- Load Models -----------------
@st.cache_resource
def load_models():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    return face_cascade, eye_cascade, smile_cascade

face_cascade, eye_cascade, smile_cascade = load_models()

# ----------------- Emotion Detection Functions -----------------
def detect_emotion(img):
    """Detect emotions using OpenCV (happy, neutral, sad, angry)"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    emotions = []
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        
        # Detect smiles
        smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
        # Detect eyes
        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        # Emotion detection logic
        emotion = "neutral"  # default
        
        # Anger detection
        if len(eyes) >= 2:
            eye_centers = [y + ey + eh/2 for (ex,ey,ew,eh) in eyes[:2]]
            avg_eye_height = np.mean(eye_centers)
            eye_sizes = [eh for (ex,ey,ew,eh) in eyes[:2]]
            avg_eye_size = np.mean(eye_sizes)
            
            if avg_eye_size > h/5 and avg_eye_height < h/2.5:
                emotion = "angry"
            elif avg_eye_height < h/3:
                emotion = "sad"
        
        # Happiness detection (priority)
        if len(smiles) > 0:
            emotion = "happy"
        
        emotions.append(emotion)
    
    return emotions, faces

def draw_detections(img, emotions, faces):
    """Draw detection boxes with labels"""
    output_img = img.copy()
    
    # Color mapping
    color_map = {
        "happy": (0, 255, 0),     # green
        "neutral": (255, 255, 0), # yellow
        "sad": (0, 0, 255),       # red
        "angry": (0, 165, 255)    # orange
    }
    
    for i, ((x,y,w,h), emotion) in enumerate(zip(faces, emotions)):
        color = color_map.get(emotion, (255, 255, 255))
        
        # Draw face rectangle
        cv2.rectangle(output_img, (x,y), (x+w,y+h), color, 3)
        
        # Add emotion label
        cv2.putText(output_img, 
                   emotion.upper(), 
                   (x+5, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.8, 
                   color, 
                   2)
    
    return output_img

def show_detection_guide():
    """Show detection guide in expandable section"""
    with st.expander(f"ℹ️ {T['detection_guide']}", expanded=False):
        st.markdown(f"""
        **{T['detection_logic']}**
        
        - {T['happy_logic']}
        - {T['angry_logic']}
        - {T['neutral_logic']}
        - {T['sad_logic']}
        
        **{T['tips']}**
        - {T['tip1']}
        - {T['tip2']}
        - {T['tip3']}
        """)

# ----------------- Location Estimation -----------------
def get_location(image):
    """Estimate location based on image metadata or random selection"""
    try:
        # Try to get location from image metadata
        img = Image.open(image)
        info = img._getexif()
        if info and 34853 in info:  # GPSInfo tag
            gps_info = info[34853]
            # Convert GPS coordinates to readable location
            geolocator = Nominatim(user_agent="geo_locator")
            location = geolocator.reverse(f"{gps_info[2][0]}, {gps_info[4][0]}")
            return location.address
    except:
        pass
    
    # Fallback to random location if no metadata
    locations = ["Kuala Lumpur, Malaysia", "Tokyo, Japan", "Paris, France", "New York, USA", "London, UK"]
    return random.choice(locations)

# ----------------- History Management -----------------
def save_history(username, emotion, location):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame([[username, emotion, location, now]], 
                            columns=["Username", "Emotion", "Location", "timestamp"])
    
    try:
        history_df = pd.read_csv("history.csv")
        history_df = pd.concat([history_df, new_record], ignore_index=True)
    except FileNotFoundError:
        history_df = new_record
    
    history_df.to_csv("history.csv", index=False)

# ----------------- Tab 1: Home -----------------
with tabs[0]:
    username = st.text_input(f"👤 {T['username_prompt']}")
    if username:
        st.sidebar.success(f"👤 {T['logged_in']} {username}")
        uploaded_file = st.file_uploader(f"📄 {T['upload_prompt']}", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            # Convert image format
            image = Image.open(uploaded_file)
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Two-column layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("🔍 Detection Results")
                # Detect emotions
                emotions, faces = detect_emotion(img)
                
                if emotions:
                    # Count each emotion type
                    emotion_count = {}
                    for emo in emotions:
                        emotion_count[emo] = emotion_count.get(emo, 0) + 1
                    
                    # Format the result string
                    result_parts = []
                    for emo, count in emotion_count.items():
                        result_parts.append(f"{count} {emo.capitalize()}")
                    
                    st.success(f"🎭 {T['detected_emotion']}: " + ", ".join(result_parts))
                    
                    # Estimate location
                    location = get_location(uploaded_file)
                    st.info(f"📍 {T['estimated_location']}: {location}")
                    
                    # Save to history
                    save_history(username, ", ".join(emotions), location)
                    
                    # Show detection guide
                    show_detection_guide()
                else:
                    st.warning(T["no_faces"])
            
            with col2:
                tab1, tab2 = st.tabs([T["original_image"], T["analysis_result"]])
                with tab1:
                    st.image(image, use_container_width=True)
                with tab2:
                    if faces:
                        detected_img = draw_detections(img.copy(), emotions, faces)
                        st.image(detected_img, channels="BGR", use_container_width=True,
                               caption=f"{len(faces)} {T['faces_detected']}")
    else:
        st.warning(T["start_prompt"])

# ----------------- Tab 2: Location Map -----------------
with tabs[1]:
    try:
        history_df = pd.read_csv("history.csv")
        if not history_df.empty:
            # Get unique locations
            unique_locations = history_df['Location'].value_counts().reset_index()
            unique_locations.columns = ['Location', 'Count']
            
            # Generate random coordinates for demo (in real app, use geocoding)
            unique_locations['lat'] = [3.1390 + random.uniform(-0.1, 0.1) for _ in range(len(unique_locations))]
            unique_locations['lon'] = [101.6869 + random.uniform(-0.1, 0.1) for _ in range(len(unique_locations))]
            
            st.map(unique_locations)
        else:
            st.info(T["no_history"])
    except FileNotFoundError:
        st.info(T["no_record_found"])

# ----------------- Tab 3: History -----------------
with tabs[2]:
    st.header(f"📜 {T['upload_history']}")
    if username:
        try:
            history_df = pd.read_csv("history.csv")
            if history_df.empty:
                st.info(T["no_history"])
            else:
                keyword = st.text_input(T["filter_user"]).strip()
                if keyword:
                    filtered_df = history_df[history_df["Username"].str.lower() == keyword.lower()]
                else:
                    filtered_df = history_df
                st.dataframe(filtered_df)
                st.caption(f"{len(filtered_df)} {T['records_shown']}")
        except FileNotFoundError:
            st.info(T["no_record_found"])
    else:
        st.warning(T["enter_username_history"])

# ----------------- Tab 4: Filter -----------------
with tabs[3]:
    st.subheader(f"🧪 {T['nav_filter']}")
    try:
        df = pd.read_csv("history.csv")
        chart = df["Emotion"].value_counts().reset_index()
        chart.columns = ["Emotion", "Count"]
        fig = px.pie(chart, names="Emotion", values="Count", title="Emotion Analysis")
        st.plotly_chart(fig)
    except:
        st.warning("📂 No data available to generate chart.")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**🔘 Choose emotion:**")
        emotion = st.radio("Emotion?", ["😊 Happy", "😢 Sad", "😡 Angry"], horizontal=True)

        st.markdown("**📅 Select date:**")
        date = st.date_input("Date of entry")

        st.markdown("**⌛ Progress bar example:**")
        progress = st.progress(0)
        for i in range(100):
            progress.progress(i + 1)

    with col2:
        st.success("✅ Everything looks good!")
        st.info("ℹ️ Use left controls to customize analysis")
        st.warning("⚠️ No image uploaded yet")

    st.toast("🔔 This is a toast message!", icon="✅")
    dummy_data = pd.DataFrame({"Emotion": ["Happy", "Sad"], "Count": [10, 8]})
    st.download_button("⬇️ Download Dummy CSV", data=dummy_data.to_csv(), file_name="dummy.csv")
