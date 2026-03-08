import streamlit as st
import pandas as pd
from pptx import Presentation
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openai import OpenAI
import time
import json
import os

# --- 1. SETTINGS & PWA ---
st.set_page_config(page_title="HAMS Universal AI Studio", layout="wide")

# Your OpenAI Key
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

DB_FILE = "hams_master_archive.json"

# PWA Header for Android/Windows Install
st.markdown("""
    <head><link rel="manifest" href="/manifest.json"><meta name="apple-mobile-web-app-capable" content="yes"></head>
    <style>
    .stApp { background-color: #001f3f; color: #f0f2f6; }
    .stSidebar { background-color: #000b1a !important; border-right: 2px solid #87CEEB; }
    h1, h2, h3 { color: #87CEEB !important; }
    .stButton>button { background-color: #87CEEB; color: #001f3f; font-weight: bold; border-radius: 12px; height: 3em; width: 100%; }
    .brand-header { text-align: center; padding: 20px; background: linear-gradient(135deg, #001f3f, #002b5c); border-radius: 15px; border-bottom: 4px solid #87CEEB; margin-bottom: 25px; }
    .mic-sidebar { text-align: center; padding: 10px; border: 1px solid #87CEEB; border-radius: 10px; margin-bottom: 20px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump([], f)
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return []

def save_to_db(cat, typ, title, cont, meta=None):
    db = load_db()
    db.append({"date": time.strftime("%Y-%m-%d %H:%M"), "cat": cat, "typ": typ, "title": title, "cont": cont, "meta": meta or {}})
    with open(DB_FILE, "w") as f: json.dump(db, f)

# --- 3. AI ENGINE ---
def ask_ai(prompt):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "Head Architect for Hajiya Amina Model School."}, {"role": "user", "content": prompt}])
        return response.choices[0].message.content
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

# --- 5. SIDEBAR WITH MIC ---
with st.sidebar:
    st.markdown('<div class="mic-sidebar">🎙️ Voice Active</div>', unsafe_allow_html=True)
    if st.button("Listen for Command"): st.toast("Listening...")
    st.markdown("---")
    mode = st.radio("Menu", ["🚀 Dashboard", "📊 PPT", "📄 PDF", "📈 Excel", "🎥 Media", "📂 Archives"])
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- 6. MODULES ---
if mode == "🚀 Dashboard":
    st.markdown('<div class="brand-header"><h1>Global Search</h1></div>', unsafe_allow_html=True)
    q = st.text_input("Generate prompts, questions, or guidelines...")
    if st.button("AI Search"):
        ans = ask_ai(q)
        if ans: st.info(ans); save_to_db("Doc", "Search", q[:20], ans)

elif mode == "📊 PPT":
    st.header("PPT Architect")
    t = st.text_input("Topic")
    if st.button("Build PPT"):
        cont = ask_ai(f"Outline 5 slides for {t}. Use 'SLIDE:' for titles.")
        if cont:
            prs = Presentation()
            for s in cont.split("SLIDE:")[1:]:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                lines = s.strip().split('\n')
                slide.shapes.title.text = lines[0]
                slide.placeholders[1].text = "\n".join(lines[1:])
            buf = BytesIO(); prs.save(buf)
            save_to_db("Doc", "PPT", t, cont)
            st.download_button("Download", buf.getvalue(), f"{t}.pptx")

elif mode == "📄 PDF":
    st.header("PDF Creator")
    t, p = st.text_input("Title"), st.text_area("Prompt")
    if st.button("Build PDF"):
        cont = ask_ai(p)
        if cont:
            buf = BytesIO(); c = canvas.Canvas(buf, pagesize=letter)
            c.drawString(100, 750, f"HAMS - {t}"); c.line(50, 730, 550, 730)
            text = c.beginText(50, 700)
            for l in cont.split('\n'): text.textLine(l)
            c.drawText(text); c.save()
            save_to_db("Doc", "PDF", t, cont)
            st.download_button("Download", buf.getvalue(), f"{t}.pdf")

elif mode == "📈 Excel":
    st.header("Excel Intelligence")
    d = st.text_input("Table Description")
    if st.button("Build Excel"):
        df = pd.DataFrame({"Name": ["Student A", "Student B"], "Score": [90, 85]})
        st.table(df)
        buf = BytesIO()
        with pd.ExcelWriter(buf) as w: df.to_excel(w, index=False)
        save_to_db("Doc", "Excel", d, "Table Gen")
        st.download_button("Download", buf.getvalue(), "HAMS.xlsx")

elif mode == "🎥 Media":
    st.header("Media Lab")
    i, v, m = st.tabs(["🖼️ Image", "🎬 Video", "🎵 Music"])
    with i:
        p = st.text_input("Image Prompt")
        if st.button("Gen Image"): 
            save_to_db("Media", "Image", "Image", p)
            st.image("https://via.placeholder.com/400x200?text=HAMS+Image")
    with v:
        p = st.text_input("Video Prompt")
        if st.button("Gen Video"): 
            save_to_db("Media", "Video", "Video", p)
            st.info("Video processing...")
    with m:
        p = st.text_input("Music Prompt")
        vc = st.radio("Voice", ["Female", "Male", "Child"])
        if st.button("Gen Music"): 
            save_to_db("Media", "Music", "Music", p, {"voice": vc})
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

elif mode == "📂 Archives":
    st.header("History")
    data = load_db()
    d_tab, m_tab = st.tabs(["Docs", "Media"])
    with d_tab:
        for x in reversed(data):
            if x['cat'] == "Doc":
                with st.expander(f"{x['date']} | {x['typ']}: {x['title']}"): st.write(x['cont'])
    with m_tab:
        for x in reversed(data):
            if x['cat'] == "Media":
                st.write(f"**{x['date']} - {x['typ']}**")
                st.write(f"Prompt: {x['cont']}")
                if 'voice' in x['meta']: st.write(f"Voice: {x['meta']['voice']}")
                st.markdown("---")