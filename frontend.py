import streamlit as st
from streamlit_option_menu import option_menu
import requests

# --- PAGE CONFIG ---
st.set_page_config(page_title="Meeting Summarizer", page_icon="🎥", layout="wide")

# --- INIT SESSION STATE ---
if "video_file" not in st.session_state:
    st.session_state.video_file = None
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None
if "summary" not in st.session_state:
    st.session_state.summary = None

# --- API CONFIG ---
API_URL = "http://127.0.0.1:5000/summarize"  # Flask backend

# --- NAVIGATION BAR ---
with st.sidebar:
    selected = option_menu(
        menu_title="📌 Navigation",
        options=["Upload Video", "Upload PDF", "Summarization Result"],
        icons=["camera-video", "file-earmark-pdf", "file-text"],
        menu_icon="list",
        default_index=0,
    )

# --- PAGES ---
if selected == "Upload Video":
    st.header("🎥 Upload Meeting Video")
    video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

    if video is not None and st.session_state.video_file is None:
        # Save video bytes into session state
        st.session_state.video_file = {"name": video.name, "data": video.getvalue()}

    if st.session_state.video_file:
        # Show video
        st.video(st.session_state.video_file["data"])

        if st.button("Summarize Video"):
            with st.spinner("⏳ Processing video, please wait..."):
                try:
                    files = {"file": (st.session_state.video_file["name"], st.session_state.video_file["data"])}
                    response = requests.post(API_URL, files=files)
                    data = response.json()

                    if "summary" in data:
                        st.session_state.summary = data["summary"]
                        st.success("✅ Summarization complete! Go to 'Summarization Result'.")
                    else:
                        st.error(f"Error: {data.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {e}")

    if st.button("Clear Video"):
         st.session_state.video_file = None
         st.session_state.summary = None
         st.rerun()

elif selected == "Upload PDF":
    st.header("📄 Upload PDF File")
    pdf = st.file_uploader("Upload a PDF file", type=["pdf"])

    if pdf is not None and st.session_state.pdf_file is None:
        # Save PDF bytes into session state
        st.session_state.pdf_file = {"name": pdf.name, "data": pdf.getvalue()}

    if st.session_state.pdf_file:
        st.success(f"Uploaded: {st.session_state.pdf_file['name']}")

        if st.button("Summarize PDF"):
            with st.spinner("⏳ Processing PDF, please wait..."):
                try:
                    files = {"file": (st.session_state.pdf_file["name"], st.session_state.pdf_file["data"])}
                    response = requests.post("http://127.0.0.1:5000/summarize_pdf", files=files)
                    data = response.json()

                    if "summary" in data:
                        st.session_state.summary = data["summary"]
                        st.success("✅ PDF summarization complete! Go to 'Summarization Result'.")
                    else:
                        st.error(f"Error: {data.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {e}")

    if st.button("Clear PDF"):
        st.session_state.pdf_file = None
        st.session_state.summary = None
        st.rerun()

elif selected == "Summarization Result":
    st.header("📝 Summarization Result")

    if st.session_state.summary:
        st.write(st.session_state.summary)
    else:
        st.info("No summarization yet. Upload a video or PDF and click Summarize.")

    if st.button("Clear Result"):
        st.session_state.summary = None
        st.session_state.video_file = None
        st.session_state.pdf_file = None
        st.rerun()