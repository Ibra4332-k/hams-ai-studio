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

# ---------------- CONFIG ----------------
st.set_page_config(page_title="HAMS Universal AI Studio", layout="wide")

genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))

DB_FILE = "hams_master_archive.json"

# ---------------- STYLES ----------------
st.markdown("""
<style>

.stApp{
background:#001f3f;
color:white;
}

.stSidebar{
background:#000b1a !important;
border-right:2px solid #87CEEB;
}

h1,h2,h3{
color:#87CEEB !important;
}

.stButton>button{
background:#87CEEB;
color:#001f3f;
font-weight:bold;
border-radius:12px;
height:3em;
width:100%;
}

.brand-header{
text-align:center;
padding:20px;
background:linear-gradient(135deg,#001f3f,#002b5c);
border-radius:15px;
border-bottom:4px solid #87CEEB;
margin-bottom:25px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- VOICE INPUT (CHATGPT STYLE) ----------------

def chatgpt_voice_input(key):

    html_code = f"""
    <div style="display:flex;align-items:center;gap:8px;">
    
    <input id="{key}" 
    style="flex:1;padding:10px;border-radius:10px;border:none;" 
    placeholder="Ask anything..." />

    <button onclick="startRec()" 
    style="background:#87CEEB;border:none;padding:8px;border-radius:10px;">
    🎤
    </button>

    </div>

    <div id="voicebox" style="display:none;margin-top:10px;
    background:#002b5c;padding:10px;border-radius:10px;color:white">

    🎙️ Listening...

    <br><br>

    <button onclick="sendRec()" style="margin-right:10px;">Send</button>

    <button onclick="cancelRec()">Cancel</button>

    </div>

<script>

let transcript = "";

function startRec(){{
document.getElementById("voicebox").style.display="block";

const recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();

recognition.lang="en-US";

recognition.onresult=function(e){{
transcript = e.results[0][0].transcript;
}}

recognition.start();

window.rec = recognition;
}}

function sendRec(){{
document.getElementById("{key}").value = transcript;

window.parent.postMessage({{
type:"streamlit:set_widget_value",
key:"{key}",
value:transcript
}}, "*");

document.getElementById("voicebox").style.display="none";
}}

function cancelRec(){{
if(window.rec) window.rec.stop();
document.getElementById("voicebox").style.display="none";
}}

</script>
"""

    components.html(html_code, height=120)

    return st.text_input("Search or Prompt", key=key)


# ---------------- DATABASE ----------------

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE,"w") as f:
            json.dump([],f)

    try:
        with open(DB_FILE,"r") as f:
            return json.load(f)
    except:
        return []

def save_to_db(cat,typ,title,cont,meta=None):

    db = load_db()

    db.append({
        "date":time.strftime("%Y-%m-%d %H:%M"),
        "cat":cat,
        "typ":typ,
        "title":title,
        "cont":cont,
        "meta":meta or {}
    })

    with open(DB_FILE,"w") as f:
        json.dump(db,f)

# ---------------- AI ENGINE ----------------

def ask_hams_ai(prompt):

    try:

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        st.error(f"AI Error: {e}")

        return None


# ---------------- AUTH ----------------

if "auth" not in st.session_state:
    st.session_state.auth=False

if not st.session_state.auth:

    st.markdown('<div class="brand-header"><h1>HAMS AI Portal</h1></div>', unsafe_allow_html=True)

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):

        if u=="admin" and p=="hams2026":

            st.session_state.auth=True

            st.rerun()

    st.stop()


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("### 💠 HAMS COMMAND")

    mode = st.radio("Menu",[

        "🚀 Dashboard",
        "📊 PPT Architect",
        "📄 PDF Gen",
        "📈 Excel Intelligence",
        "🎥 Media Lab",
        "📂 Archives"

    ])

    st.markdown("---")

    if st.button("Logout"):

        st.session_state.auth=False

        st.rerun()


# ---------------- MODULES ----------------


# -------- DASHBOARD --------

if mode=="🚀 Dashboard":

    st.markdown('<div class="brand-header"><h1>Global Search</h1></div>', unsafe_allow_html=True)

    q = chatgpt_voice_input("main_q")

    if st.button("Generate Insight"):

        ans = ask_hams_ai(q)

        if ans:

            st.info(ans)

            save_to_db("Doc","Search",q[:20],ans)



# -------- PPT CREATOR --------

elif mode=="📊 PPT Architect":

    st.header("PPT Creator")

    topic = chatgpt_voice_input("ppt_t")

    if st.button("Build PPT"):

        cont = ask_hams_ai(f"Create 5 slides for {topic}. Use SLIDE: for each title")

        if cont:

            prs = Presentation()

            for s in cont.split("SLIDE:")[1:]:

                slide = prs.slides.add_slide(prs.slide_layouts[1])

                lines = s.strip().split("\n")

                slide.shapes.title.text = lines[0]

                slide.placeholders[1].text = "\n".join(lines[1:])

            buf = BytesIO()

            prs.save(buf)

            save_to_db("Doc","PPT",topic,cont)

            st.download_button("Download PPT", buf.getvalue(), f"{topic}.pptx")



# -------- MEDIA LAB --------

elif mode=="🎥 Media Lab":

    st.header("Media Lab")

    prompt = chatgpt_voice_input("media_p")

    tab1,tab2,tab3 = st.tabs(["🖼 Image","🎬 Video","🎵 Music"])

    with tab1:

        if st.button("Gen Image"):

            save_to_db("Media","Image","Image",prompt)

            st.image("https://via.placeholder.com/400x200?text=HAMS+Image")

    with tab2:

        if st.button("Gen Video"):

            save_to_db("Media","Video","Video",prompt)

            st.info("Video prompt archived")

    with tab3:

        voice = st.radio("Voice Style",["Female","Male","Child"])

        if st.button("Gen Music"):

            save_to_db("Media","Music","Music",prompt,{"voice":voice})

            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")



# -------- ARCHIVES --------

elif mode=="📂 Archives":

    st.header("History")

    data = load_db()

    for x in reversed(data):

        with st.expander(f"{x['date']} | {x['typ']} : {x['title']}"):

            st.write(x["cont"])