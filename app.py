import streamlit as st
import pandas as pd
from pptx import Presentation
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import google.generativeai as genai
import time
import json
import os
import streamlit.components.v1 as components

# --- 1. SETTINGS & PWA ---
st.set_page_config(page_title="HAMS Universal AI Studio", layout="wide")

# Using the GEMINI_API_KEY from your Streamlit Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Missing GEMINI_API_KEY in Secrets!")

DB_FILE = "hams_master_archive.json"

st.markdown("""
    <style>
    .stApp { background-color: #001f3f; color: #f0f2f6; }
    .stSidebar { background-color: #000b1a !important; border-right: 2px solid #87CEEB; }
    h1, h2, h3 { color: #87CEEB !important; }
    .stButton>button { background-color: #87CEEB; color: #001f3f; font-weight: bold; border-radius: 12px; height: 3em; }
    .brand-header { text-align: center; padding: 20px; background: linear-gradient(135deg, #001f3f, #002b5c); border-radius: 15px; border-bottom: 4px solid #87CEEB; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VOICE RECOGNITION (JavaScript) ---
def st_speech_button(label, key):
    script = f"""
    <script>
    function startRecognition() {{
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            window.parent.postMessage({{type: 'streamlit:set_widget_value', key: '{key}', value: transcript}}, '*');
        }};
        recognition.start();
    }}
    </script>
    <button onclick="startRecognition()" style="background-color: #87CEEB; border: none; border-radius: 10px; padding: 10px; cursor: pointer; font-weight: bold; width: 100%;">
        🎙️ {label}
    </button>
    """
    components.html(script, height=50)

# --- 3. FREE AI LOGIC ---
def ask_hams_ai(prompt):
    try:
        # Changed to 'gemini-pro' for maximum compatibility
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"HAMS School System: {prompt}")
        return response.text
    except Exception as e:
        st.error(f"AI Error: {e}"); return None

# --- 4. AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown('<div class="brand-header"><h1>HAMS AI Portal</h1></div>', unsafe_allow_html=True)
    u, p = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Login"):
        if u == "admin" and p == "hams2026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 💠 HAMS COMMAND")
    mode = st.radio("Menu", ["🚀 Dashboard", "📊 PPT", "📄 PDF", "📈 Excel", "🎥 Media Lab", "📂 Archives"])
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- 6. MODULES ---
if mode == "🚀 Dashboard":
    st.markdown('<div class="brand-header"><h1>Global Search</h1></div>', unsafe_allow_html=True)
    st_speech_button("Speak your question", "main_q")
    q = st.text_input("Search or Prompt", key="main_q")
    if st.button("Generate Insight"):
        ans = ask_hams_ai(q)
        if ans: st.info(ans)

elif mode == "📊 PPT":
    st.header("PPT Architect")
    st_speech_button("Speak Topic", "ppt_t")
    t = st.text_input("Topic", key="ppt_t")
    if st.button("Build PPT"):
        cont = ask_hams_ai(f"Outline 5 slides for {t}. Mark titles with 'SLIDE:'.")
        if cont:
            prs = Presentation()
            for s in cont.split("SLIDE:")[1:]:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                lines = s.strip().split('\n')
                slide.shapes.title.text = lines[0]
                slide.placeholders[1].text = "\n".join(lines[1:])
            buf = BytesIO(); prs.save(buf); st.download_button("Download PPT", buf.getvalue(), f"{t}.pptx")

elif mode == "🎥 Media Lab":
    st.header("Media Lab")
    st_speech_button("Speak Media Prompt", "media_p")
    p = st.text_input("Prompt", key="media_p")
    i, v, m = st.tabs(["🖼️ Image", "🎬 Video", "🎵 Music"])
    with i:
        if st.button("Gen Image"): st.image("https://via.placeholder.com/400x200?text=HAMS+Image+Request+Sent")
    with v:
        if st.button("Gen Video"): st.info("Video processing request sent to HAMS server...")
    with m:
        vc = st.radio("Voice Style", ["Female", "Male", "Child"])
        if st.button("Gen Music"): st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

elif mode == "📂 Archives":
    st.header("History")
    st.write("Session archives are being prepared...")
