import os, streamlit as st
import sys, subprocess
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
import random
import os
import plotly.express as px
from emotion_utils.detector import EmotionDetector
import tempfile
from location_utils.extract_gps import extract_gps, convert_gps
from location_utils.geocoder import get_address_from_coords
from location_utils.landmark import load_models, detect_landmark, query_landmark_coords, LANDMARK_KEYWORDS


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

# Load CLIP models once
processor, clip_model = load_models()


def save_history(username, emotion, confidence, location):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[username, emotion, confidence, location, now]],
                      columns=["Username", "Emotion", "Confidence", "Location", "timestamp"])
    try:
        if os.path.exists("history.csv"):
            prev = pd.read_csv("history.csv")
            df = pd.concat([prev, df], ignore_index=True)
        df.to_csv("history.csv", index=False)
    except Exception as e:
        st.error(f"Failed to save history: {e}")


def show_detection_guide():
    with st.expander("ℹ️ How Emotion Detection Works", expanded=False):
        st.markdown("""
        *Detection Logic Explained:*
        - 😊 Happy: Smile present, cheeks raised
        - 😠 Angry: Eyebrows lowered, eyes wide open
        - 😐 Neutral: No strong facial movements
        - 😢 Sad: Eyebrows raised, lip corners down
        - 😲 Surprise: Eyebrows raised, mouth open
        - 😨 Fear: Eyes tense, lips stretched
        - 🤢 Disgust: Nose wrinkled, upper lip raised

        *Tips for Better Results:*
        - Use clear, front-facing images
        - Ensure good lighting
        - Avoid obstructed faces
        """)


def sidebar_design(username):
    if username:
        st.sidebar.success(f"👤 Logged in as: {username}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("## Quick Navigation")
    st.sidebar.markdown("- Upload and detect emotions")
    st.sidebar.markdown("- View and filter upload history")
    st.sidebar.markdown("- Visualize your emotion distribution")
    st.sidebar.divider()
    st.sidebar.info("Enhance your experience by ensuring clear, well-lit facial images.")


def main():
    st.title("👁‍🗨 AI Emotion & Location Detector")
    st.caption("Upload a photo to detect facial emotions and estimate location.")

    # Initialize variables for sharing across tabs
    coords_result = None
    method = ""

    tabs = st.tabs([
        "🏠 Home",
        "🗺️ Detected Map",
        "📜 Upload History",
        "📊 Emotion Analysis Chart"
    ])

    # Tab 0: Home / Detection
    with tabs[0]:
        username = st.text_input("👤 Enter your username")
        sidebar_design(username)
    
        if username:
            uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "png"])
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_path = tmp_file.name

                try:
                    image = Image.open(temp_path).convert("RGB")
                    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    detections = detector.detect_emotions(img)
                    detected_img = detector.draw_detections(img, detections)

                    location = "Unknown"
                    method = ""

                    # 1) Try EXIF GPS
                    gps_info = extract_gps(temp_path)
                    if gps_info:
                        coords = convert_gps(gps_info)
                        if coords:
                            coords_result = coords
                            location = get_address_from_coords(coords)
                            method = "GPS Metadata"

                    # 2) Fallback to CLIP landmark
                    if coords_result is None:
                        landmark = detect_landmark(temp_path, threshold=0.15, top_k=5)
                        if landmark:
                            st.write(f"🔍 CLIP predicted landmark: **{landmark}**")
                            coords_loc, source = query_landmark_coords(landmark)
                            if coords_loc:
                                coords_result = coords_loc
                                method = f"Landmark ({source})"
                                addr = get_address_from_coords(coords_loc)
                                if addr not in (
                                    "Unknown location",
                                    "Geocoding service unavailable"
                                ):  # Valid address
                                    location = addr
                                else:
                                    info = LANDMARK_KEYWORDS.get(landmark)
                                    if info:
                                        location = f"{info[0]}, {info[1]}"
                                    else:
                                        lat, lon = coords_loc
                                        location = f"{landmark.title()} ({lat:.4f}, {lon:.4f})"
                        else:
                            st.write("🔍 No landmark detected with sufficient confidence")

                except Exception as e:
                    st.error(f"❌ Something went wrong during processing: {e}")

                # Display detection results
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader("🔍 Detection Results")
                    if detections:
                        emotions = [d["emotion"] for d in detections]
                        confidences = [d["confidence"] for d in detections]
                        st.success(f"🎭 {len(detections)} face(s) detected")
                        for i, (emo, conf) in enumerate(zip(emotions, confidences)):
                            st.write(f"- Face {i+1}: {emo} ({conf}%)")
                        show_detection_guide()
                        st.write(
                            f"📍 Estimated Location: **{location}** ({method})"
                        )
                        save_history(
                            username,
                            emotions[0],
                            confidences[0],
                            location
                        )
                    else:
                        st.warning("No faces were detected in the uploaded image.")

                with col2:
                    tab_o, tab_p = st.tabs([
                        "Original Image",
                        "Processed Image"
                    ])
                    with tab_o:
                        st.image(image, use_container_width=True)
                    with tab_p:
                        st.image(
                            detected_img,
                            channels="BGR",
                            use_container_width=True,
                            caption=f"Detected {len(detections)} face(s)"
                        )

    # Tab 1: Detected Map
    with tabs[1]:
        st.subheader("🗺️ Detected Location Map")
        if coords_result:
            lat, lon = coords_result
            map_df = pd.DataFrame({"lat": [lat], "lon": [lon]})
            st.map(map_df)
            st.caption(f"Source: {method}")
        else:
            st.info("No detected location to display on map.")

    # Tab 2: Upload History
    with tabs[2]:
        st.subheader("📜 Upload History")
        if username:
            if os.path.exists("history.csv"):
                df = pd.read_csv("history.csv")
                df_filtered = df[
                    df["Username"].str.contains(username, case=False)
                ]
                if not df_filtered.empty:
                    df_filtered = (
                        df_filtered
                        .sort_values("timestamp", ascending=False)
                        .reset_index(drop=True)
                    )
                    df_filtered.index = range(1, len(df_filtered) + 1)
                    st.dataframe(df_filtered)
                    st.caption(
                        f"Total records found for {username}: {len(df_filtered)}"
                    )
                else:
                    st.info("No upload records found.")
            else:
                st.info("No history file found.")
        else:
            st.warning("Please enter your username to view your upload history.")

    # Tab 3: Emotion Analysis Chart
    with tabs[3]:
        st.subheader("📊 Emotion Analysis Chart")
        if username:
            if os.path.exists("history.csv"):
                df = pd.read_csv("history.csv")
                df_filtered = df[
                    df["Username"].str.contains(username, case=False)
                ]
                if not df_filtered.empty:
                    fig = px.pie(
                        df_filtered,
                        names="Emotion",
                        title=f"Emotion Distribution for {username}"
                    )
                    st.plotly_chart(fig)
                    st.caption(
                        "Chart is based on your personal upload history."
                    )
                else:
                    st.info("No emotion records found for this username.")
            else:
                st.info("History file not found.")
        else:
            st.warning(
                "Please enter your username to generate your emotion chart."
            )


if __name__ == "__main__":
    main()

