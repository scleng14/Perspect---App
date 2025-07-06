import streamlit as st
import random
import pandas as pd
from datetime import datetime
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------- Page Setup -----------------
st.set_page_config(page_title="LeadFocal", page_icon="👁‍🗨", layout="wide", initial_sidebar_state="expanded")

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
        "enter_username_history": "请输入用户名以查看历史记录。"
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
    },
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

# ----------------- Utilities -----------------
def analyze_emotion(image):
    emotions = ["Happy", "Sad", "Angry", "Neutral", "Surprised"]
    return random.choice(emotions)

def get_location(image):
    locations = ["Kuala Lumpur, Malaysia", "Tokyo, Japan", "Paris, France", "Unknown"]
    return random.choice(locations)

def save_history(username, emotion, location):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = pd.DataFrame([[username, emotion, location, now]], columns=["Username", "Emotion", "Location", "timestamp"])
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
            st.image(uploaded_file, caption="Image Preview", use_column_width=True)
            emotion = analyze_emotion(uploaded_file)
            location = get_location(uploaded_file)
            st.success(f"{T['detected_emotion']}: **{emotion}**")
            st.info(f"{T['estimated_location']}: **{location}**")
            save_history(username, emotion, location)
        else:
            st.warning(f"{T['upload_prompt']}")
    else:
        st.warning(T["start_prompt"])

# ----------------- Tab 2: Location Map -----------------
with tabs[1]:
    st.map(pd.DataFrame({
        'lat': [3.1390 + random.uniform(-0.01, 0.01)],
        'lon': [101.6869 + random.uniform(-0.01, 0.01)]
    }))

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

        st.markdown("**🎚️ Set confidence level:**")
        level = st.select_slider("Confidence", options=["Low", "Medium", "High"])

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
