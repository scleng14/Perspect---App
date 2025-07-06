
import streamlit as st
import random
import pandas as pd
import plotly.express as px
from datetime import datetime

# App setup
st.set_page_config(page_title="LeadFocal", page_icon="😶‍🌫", layout="wide", initial_sidebar_state="expanded")

# Language Options
lang = st.sidebar.selectbox("Select Language", ["English", "中文", "Malay"])

# Translations
translations = {
    "English": {
        "title": "Emotion & Location Recognition System",
        "subtitle": "Try upload a local photo to analyze emotion and estimate location.",
        "username_prompt": "Enter your username:",
        "logged_in": " 👤 Logged in as:",
        "upload_prompt": "Upload an image",
        "detected_emotion": "Detected Emotion",
        "estimated_location": "Estimated Location",
        "start_prompt": "Please enter your username to begin.",
        "nav_home": "Home",
        "nav_history": "History",
        "upload_history": "Upload History",
        "no_history": "No history available yet.",
        "filter_user": "Filter by username (optional):",
        "records_shown": "record(s) shown.",
        "no_record_found": "No record found yet.",
        "enter_username_history": "Please enter your username to view history.",
    },
    "中文": {
        "title": "情绪与位置识别系统",
        "subtitle": "尝试上传本地照片，体验情绪识别与位置推测功能。",
        "username_prompt": "请输入用户名：",
        "logged_in": " 👤 已登录用户：",
        "upload_prompt": "上传图片",
        "detected_emotion": "识别的情绪",
        "estimated_location": "推测的位置",
        "start_prompt": "请输入用户名以开始。",
        "nav_home": "主页",
        "nav_history": "历史记录",
        "upload_history": "上传历史",
        "no_history": "暂无历史记录。",
        "filter_user": "按用户名筛选（可选）：",
        "records_shown": "条记录已显示。",
        "no_record_found": "尚未找到任何记录。",
        "enter_username_history": "请输入用户名以查看历史记录。",
    },
    "Malay": {
        "title": "Sistem Pengecaman Emosi dan Lokasi",
        "subtitle": "Cuba muat naik foto tempatan untuk menganalisis emosi dan menganggar lokasi.",
        "username_prompt": "Masukkan nama pengguna anda:",
        "logged_in": " 👤 Log masuk sebagai:",
        "upload_prompt": "Muat naik imej",
        "detected_emotion": "Emosi Dikesan",
        "estimated_location": "Lokasi Dianggar",
        "start_prompt": "Sila masukkan nama pengguna untuk bermula.",
        "nav_home": "Halaman Utama",
        "nav_history": "Sejarah",
        "upload_history": "Sejarah Muat Naik",
        "no_history": "Tiada sejarah tersedia buat masa ini.",
        "filter_user": "Tapis mengikut nama pengguna (pilihan):",
        "records_shown": "rekod dipaparkan.",
        "no_record_found": "Tiada rekod dijumpai setakat ini.",
        "enter_username_history": "Sila masukkan nama pengguna untuk melihat sejarah.",
    },
}
T = translations[lang]

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [T["nav_home"], T["nav_history"]])

# Processing Functions
def analyze_emotion(image):
    emotions = ["Happy", "Sad", "Angry", "Neutral", "Surprised"]
    return random.choice(emotions)

def get_location(image):
    locations = ["Kuala Lumpur, Malaysia", "Tokyo, Japan", "Paris, France", "Unknown"]
    return random.choice(locations)

def save_history(username, emotion, location):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame([[username, emotion, location, timestamp]], columns=["Username", "Emotion", "Location", "timestamp"])
    try:
        history_df = pd.read_csv("history.csv")
        history_df = pd.concat([history_df, new_record], ignore_index=True)
    except FileNotFoundError:
        history_df = new_record
    history_df.to_csv("history.csv", index=False)

# Main UI
st.title(T["title"])
st.caption(T["subtitle"])
username = st.text_input(T["username_prompt"])

if page == T["nav_home"]:
    if username:
        st.sidebar.success(f"{T['logged_in']} {username}")
        uploaded_file = st.file_uploader(T["upload_prompt"], type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, caption="Image Preview", use_container_width=True)
            emotion = analyze_emotion(uploaded_file)
            location = get_location(uploaded_file)
            st.success(f"{T['detected_emotion']}: **{emotion}**")
            st.info(f"{T['estimated_location']}: **{location}**")
            save_history(username, emotion, location)
        else:
            st.warning(T["upload_prompt"])
    else:
        st.warning(T["start_prompt"])

elif page == T["nav_history"]:
    st.header(T["upload_history"])
    if username:
        try:
            history_df = pd.read_csv("history.csv")
            if history_df.empty:
                st.info(T["no_history"])
            else:
                keyword = st.text_input(T["filter_user"]).strip()
                filtered_df = history_df[history_df["Username"].str.lower() == keyword.lower()] if keyword else history_df
                st.dataframe(filtered_df)
                st.caption(f"{len(filtered_df)} {T['records_shown']}")

                # Emotion Distribution Chart
                if not filtered_df.empty:
                    emotion_count = filtered_df["Emotion"].value_counts().reset_index()
                    emotion_count.columns = ["Emotion", "Count"]
                    fig = px.pie(emotion_count, names="Emotion", values="Count", title="Emotion Distribution")
                    st.plotly_chart(fig)

                    # Toast if available
                    st.toast("✅ History loaded successfully.")
        except FileNotFoundError:
            st.info(T["no_record_found"])
    else:
        st.warning(T["enter_username_history"])
