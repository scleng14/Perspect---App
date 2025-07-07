import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import random
import os
import plotly.express as px
from emotion_utils.detector import EmotionDetector

# ----------------- App Configuration -----------------
st.set_page_config(
    page_title="AI Emotion & Location Detector",
    page_icon="👁‍🗨",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_detector():
    return EmotionDetector()

detector = get_detector()

def save_history(username, emotion, confidence, location="Unknown"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[username, emotion, confidence, location, now]], 
                     columns=["Username","Emotion","Confidence","Location","timestamp"])
    try:
        if os.path.exists("history.csv"):
            prev = pd.read_csv("history.csv")
            df = pd.concat([prev, df])
        df.to_csv("history.csv", index=False)
    except Exception as e:
        st.error(f"Failed to save history: {e}")

def show_detection_guide():
    with st.expander("ℹ️ How Emotion Detection Works", expanded=False):
        st.markdown("""
        **Detection Model Details:**
        - Uses DeepFace with a hybrid CNN architecture
        - Detects 7 primary emotions: Happy, Sad, Angry, Neutral, Surprise, Fear, Disgust
        - Displays confidence scores for each detected face

        **Tips for Best Accuracy:**
        - Upload clear, front-facing images
        - Use well-lit environments
        - Ensure the face is not obstructed
        """)

def sidebar_design():
    st.sidebar.markdown("## Quick Navigation")
    st.sidebar.markdown("- Upload and detect emotions")
    st.sidebar.markdown("- View and filter your history")
    st.sidebar.markdown("- Visualize your emotion distribution")
    st.sidebar.divider()
    st.sidebar.info("Tip: Upload clear, front-facing, well-lit images for best results.")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**App Version:** 1.0.0")
    st.sidebar.markdown("**Developer:** AI Labs Team")
    st.sidebar.markdown("[GitHub Repository](https://github.com/example/emotion-location-app)")

def main():
    st.title("👁‍🗨 AI Emotion & Location Detector")
    st.caption("Try face detection by uploading a photo. The system will identify facial emotions and log a sample location.")
    sidebar_design()
    tabs = st.tabs(["🏠 Home", "🗺️ Location Map", "📜 Upload History", "📊 Emotion Analysis Chart"])

    with tabs[0]:
        username = st.text_input("👤 Enter your username")
        if username:
            st.sidebar.success(f"👤 Logged in as: {username}")
            uploaded_file = st.file_uploader("Upload an image (JPG or PNG)", type=["jpg", "png"])
            if uploaded_file:
                try:
                    image = Image.open(uploaded_file)
                    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    detections = detector.detect_emotions(img)
                    detected_img = detector.draw_detections(img, detections)

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.subheader("🔍 Detection Results")
                        if detections:
                            emotions = [d["emotion"] for d in detections]
                            confidences = [d["confidence"] for d in detections]
                            st.success(f"🎭 {len(detections)} face(s) detected")
                            for i, (emo, conf) in enumerate(zip(emotions, confidences)):
                                st.write(f"- Face {i + 1}: {emo} ({conf}%)")
                            show_detection_guide()
                            save_history(username, emotions[0], confidences[0], "Unknown")
                        else:
                            st.warning("No faces were detected in the uploaded image.")
                    with col2:
                        t1, t2 = st.tabs(["Original Image", "Processed Image"])
                        with t1:
                            st.image(image, use_container_width=True)
                        with t2:
                            st.image(detected_img, channels="BGR", use_container_width=True,
                                     caption=f"Detected {len(detections)} face(s)")
                except Exception as e:
                    st.error(f"Error while processing the image: {e}")

    with tabs[1]:
        st.subheader("🗺️ Random Location Sample (Demo Only)")
        st.map(pd.DataFrame({
            'lat': [3.139 + random.uniform(-0.01, 0.01)],
            'lon': [101.6869 + random.uniform(-0.01, 0.01)]
        }))
        st.caption("Note: Real location detection will be available in future updates.")

    with tabs[2]:
        st.subheader("📜 Upload History Viewer")
        if username:
            try:
                if os.path.exists("history.csv"):
                    df = pd.read_csv("history.csv")
                    if df.empty:
                        st.info("No upload records found.")
                    else:
                        df_filtered = df[df["Username"].str.contains(username, case=False)]
                        df_filtered = df_filtered.sort_values("timestamp", ascending=False).reset_index(drop=True)
                        df_filtered.index = df_filtered.index + 1
                        st.dataframe(df_filtered)
                        st.caption(f"Total records for {username}: {len(df_filtered)}")
                else:
                    st.info("No history file found.")
            except:
                st.warning("Error loading history records.")
        else:
            st.warning("Please enter your username above to view your history.")

    with tabs[3]:
        st.subheader("📊 Emotion Distribution Chart")
        if username:
            try:
                if os.path.exists("history.csv"):
                    df = pd.read_csv("history.csv")
                    df_filtered = df[df["Username"].str.contains(username, case=False)]
                    if not df_filtered.empty:
                        fig = px.pie(df_filtered, names="Emotion", title=f"Emotion Distribution for {username}")
                        st.plotly_chart(fig)
                    else:
                        st.info("No emotion records found for this user.")
                else:
                    st.info("History file not found.")
            except Exception as e:
                st.error(f"Error generating chart: {e}")
        else:
            st.warning("Please enter your username to generate your personal emotion chart.")

if __name__ == "__main__":
    main()
