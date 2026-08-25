import streamlit as st
import docx
import edge_tts
import asyncio
import base64
import re

# Page config configured for mobile viewports
st.set_page_config(
    page_title="LLB Mobile Audio Reader",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Responsive Dark-Mode Mobile CSS Injection
st.markdown("""
<style>
    .stApp {
        background-color: #090D16;
        color: #F1F5F9;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        .reading-box {
            max-height: 350px !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
            padding: 16px !important;
        }
    }
    .reading-box {
        background-color: #131C2E;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1E293B;
        max-height: 480px;
        overflow-y: auto;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #CBD5E1;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);
    }
    .highlighted-sentence {
        background-color: #2563EB;
        color: #FFFFFF;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        display: inline;
    }
    .stButton > button {
        border-radius: 10px !important;
        height: 3rem !important;
        font-weight: 700 !important;
        background-color: #2563EB !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:active {
        background-color: #1D4ED8 !important;
    }
    .mobile-download-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #10B981;
        color: white;
        padding: 14px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.05rem;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

async def generate_speech(text, voice, rate_str, output_filename="audio.mp3"):
    tts = edge_tts.Communicate(text, voice, rate=rate_str)
    await tts.save(output_filename)

st.title("⚖️ LLB Mobile Audio Studio")
st.caption("📱 Dark-mode optimized audio player for study commutes.")

st.sidebar.header("⚙️ Audio Customization")

voices = {
    "🇮🇳 Prabhat (Indian Male - Clear/Podcast)": "en-IN-PrabhatNeural",
    "🇮🇳 Neerja (Indian Female - Clear/Natural)": "en-IN-NeerjaNeural",
    "🇬🇧 Ryan (UK Male)": "en-GB-RyanNeural",
    "🇺🇸 Sonia (US Female)": "en-US-SoniaNeural"
}

selected_voice_label = st.sidebar.selectbox("Voice Accent", list(voices.keys()))
selected_voice = voices[selected_voice_label]

speed = st.sidebar.slider("Speed", min_value=0.75, max_value=2.0, value=1.0, step=0.05)
rate_percentage = f"{int((speed - 1.0) * 100):+d}%"

uploaded_file = st.file_uploader("Upload LLB .docx File", type=["docx"])

if uploaded_file is not None:
    doc_text = extract_text_from_docx(uploaded_file)
    sentences = split_into_sentences(doc_text)
    
    st.info(f"📄 Loaded Document • Total Sentences: {len(sentences)}")
    
    mode = st.radio("Playback Scope:", ["Read Full File", "Select Range/Paragraph"], horizontal=True)
    
    if mode == "Select Range/Paragraph":
        start_idx, end_idx = st.select_slider(
            "Select sentence range:",
            options=range(1, len(sentences) + 1),
            value=(1, min(10, len(sentences)))
        )
        active_sentences = sentences[start_idx-1:end_idx]
        target_text = " ".join(active_sentences)
    else:
        active_sentences = sentences
        target_text = doc_text

    if st.button("▶️ Generate & Play Audio", type="primary", use_container_width=True):
        with st.spinner("Synthesizing Indian AI Voice..."):
            asyncio.run(generate_speech(target_text, selected_voice, rate_percentage, "output.mp3"))
            
            with open("output.mp3", "rb") as f:
                audio_bytes = f.read()
            
            st.success("Ready for travel listening!")
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            
            b64 = base64.b64encode(audio_bytes).decode()
            href = f'<a href="data:file/mp3;base64,{b64}" download="LLB_Study_Audio.mp3" class="mobile-download-btn">📥 Download MP3 to Phone</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📖 Text Viewer")
    formatted_html = "<div class='reading-box'>"
    for sentence in sentences:
        if sentence in active_sentences:
            formatted_html += f"<span class='highlighted-sentence'>{sentence}</span> "
        else:
            formatted_html += f"<span>{sentence}</span> "
    formatted_html += "</div>"
    
    st.markdown(formatted_html, unsafe_allow_html=True)
else:
    st.info("Tap above to upload your Word document (.docx).")
