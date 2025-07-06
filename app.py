# design_demo.py
import streamlit as st
import random
import pandas as pd
from datetime import datetime
import plotly.express as px

# ----------------- Page Setup -----------------
st.set_page_config(page_title="LeadFocal Demo", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# ----------------- Demo Title -----------------
st.markdown("""
    <h1 style='text-align: center; color: #444444;'>🎨 Advanced Streamlit Design Demo</h1>
    <h4 style='text-align: center; color: #888888;'>Try out interactive elements, layout tricks, and visual designs</h4>
""", unsafe_allow_html=True)

# ----------------- Tabs -----------------
tabs = st.tabs(["📤 Upload & Image Viewer", "📈 Charts", "🧪 Widgets & Layout", "🌍 Location Map", "📦 Other Tricks"])

# ----------------- Tab 1: Upload & Preview -----------------
with tabs[0]:
    st.subheader("📤 Upload Image(s)")
    files = st.file_uploader("Upload images (you can select multiple)", type=["jpg", "png"], accept_multiple_files=True)
    if files:
        for file in files:
            st.image(file, caption=file.name, use_column_width=True)

# ----------------- Tab 2: Charts -----------------
with tabs[1]:
    st.subheader("📊 Emotion Distribution Example")
    dummy_data = pd.DataFrame({
        "Emotion": ["Happy", "Sad", "Neutral", "Angry"],
        "Count": [random.randint(5, 15) for _ in range(4)]
    })
    fig = px.pie(dummy_data, names="Emotion", values="Count", title="Emotion Analysis")
    st.plotly_chart(fig)

# ----------------- Tab 3: Widgets & Layout -----------------
with tabs[2]:
    st.subheader("🧪 Try Widgets")

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

# ----------------- Tab 4: Map -----------------
with tabs[3]:
    st.subheader("📍 Random Location Viewer")
    map_data = pd.DataFrame({
        'lat': [3.1390 + random.uniform(-0.01, 0.01)],
        'lon': [101.6869 + random.uniform(-0.01, 0.01)]
    })
    st.map(map_data)

# ----------------- Tab 5: Miscellaneous -----------------
with tabs[4]:
    st.subheader("📦 Extra Design Examples")
    with st.expander("📘 Click to see instructions"):
        st.markdown("""
        **This page demonstrates:**
        - Tabs and layout
        - Charts using Plotly
        - File uploader and image viewer
        - Toggle, radio, slider, date input
        - Map with coordinates
        - Message styles: success/info/warning
        """)

    st.toast("🔔 This is a toast message!", icon="✅")
    st.download_button("⬇️ Download Dummy CSV", data=dummy_data.to_csv(), file_name="dummy.csv")
