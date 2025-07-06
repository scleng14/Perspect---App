
import streamlit as st
from utils.emotion import analyze_emotion
from utils.gps_utils import get_gps_location
from utils.landmark import detect_landmark
from PIL import Image
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Emotion & Landmark Detector", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("<h1 style='text-align: center;'>🌍 Emotion & Location Recognition App</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload an image with or without GPS data", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    image = Image.open(uploaded_file)

    with st.spinner("Analyzing image..."):
        gps_location = get_gps_location(image)
        if not gps_location:
            gps_location = detect_landmark(image)

        emotion_result = analyze_emotion(image)
        st.success(f"Detected Emotion: {emotion_result['dominant_emotion']} ({emotion_result['emotion'][emotion_result['dominant_emotion']]:.2f}%)")
        st.info(f"Detected Location: {gps_location}")

        record = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Emotion": emotion_result['dominant_emotion'],
            "Location": gps_location
        }
        df = pd.DataFrame([record])
        if os.path.exists("history.csv"):
            df.to_csv("history.csv", mode='a', header=False, index=False)
        else:
            df.to_csv("history.csv", index=False)

st.sidebar.header("📜 History")
if os.path.exists("history.csv"):
    history_df = pd.read_csv("history.csv")
    st.sidebar.dataframe(history_df[::-1])
    st.sidebar.download_button("Download History", data=history_df.to_csv(index=False), file_name="history.csv")
