import streamlit as st
import docx
import edge_tts
import asyncio
import base64
import re

st.set_page_config(
    page_title="LLB Mobile Audio Studio",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Responsive Dark Theme CSS
st.markdown("""
<style>
    .stApp { background-color: #090D16; color: #F1F5F9; }
    .reading-box {
        background-color: #131C2E;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #1E293B;
        max-height: 400px;
        overflow-y: auto;
        font-size: 1rem;
        line-height: 1.7;
        color: #CBD5E1;
    }
    .highlighted-sentence {
        background-color: #2563EB;
        color: #FFFFFF;
        padding: 3px 6px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def extract_text_from_docx(file):
    doc = docx.Document(file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

# Fast async TTS generation function
async def generate_speech_fast(text, voice, rate_str, output_filename="output.mp3"):
    # Limit maximum text chunk size per request to keep speed under 5 seconds
    tts = edge_tts.Communicate(text, voice, rate=rate_str)
    await tts.save(output_filename)

st.title("⚖️ LLB Mobile Audio Studio")
st.caption("⚡ Fast Indian AI Voice Reader for Commuting")

# Sidebar Voice Selection
st.sidebar.header("⚙️ Settings")
voices = {
    "🇮🇳 Prabhat (Male - Fast Podcast Voice)": "en-IN-PrabhatNeural",
    "🇮🇳 Neerja (Female - Clear Accent)": "en-IN-NeerjaNeural",
}
selected_voice_label = st.sidebar.selectbox("Voice", list(voices.keys()))
selected_voice = voices[selected_voice_label]

speed = st.sidebar.slider("Speed", min_value=0.75, max_value=2.0, value=1.0, step=0.1)
rate_percentage = f"{int((speed - 1.0) * 100):+d}%"

uploaded_file = st.file_uploader("Upload LLB .docx Document", type=["docx"])

if uploaded_file is not None:
    doc_text = extract_text_from_docx(uploaded_file)
    sentences = split_into_sentences(doc_text)
    
    st.info(f"📄 Loaded Document • {len(sentences)} Sentences")
    
    # Recommendation note for user
    st.markdown("💡 *Tip: Select **Range/Paragraph** mode for lightning fast (<3 second) generation.*")
    
    mode = st.radio("Playback Scope:", ["Select Range/Paragraph (Fast ⚡)", "Read Full File (Slower 🐢)"], horizontal=True)
    
    if mode == "Select Range/Paragraph (Fast ⚡)":
        start_idx, end_idx = st.select_slider(
            "Select sentence range:",
            options=range(1, len(sentences) + 1),
            value=(1, min(15, len(sentences)))
        )
        active_sentences = sentences[start_idx-1:end_idx]
        target_text = " ".join(active_sentences)
    else:
        active_sentences = sentences
        target_text = doc_text

    if st.button("▶️ Generate & Play Audio", type="primary", use_container_width=True):
        with st.spinner("Synthesizing fast audio..."):
            asyncio.run(generate_speech_fast(target_text, selected_voice, rate_percentage, "output.mp3"))
            
            with open("output.mp3", "rb") as f:
                audio_bytes = f.read()
            
            st.success("Audio Ready!")
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            
            b64 = base64.b64encode(audio_bytes).decode()
            href = f'<a href="data:file/mp3;base64,{b64}" download="LLB_Audio.mp3" style="display:block;text-align:center;background-color:#10B981;color:white;padding:12px;border-radius:8px;text-decoration:none;font-weight:bold;margin-top:10px;">📥 Save Audio MP3 to Phone</a>'
            st.markdown(href, unsafe_allow_html=True)

    st.subheader("📖 Text Reader")
    formatted_html = "<div class='reading-box'>"
    for sentence in sentences:
        if sentence in active_sentences:
            formatted_html += f"<span class='highlighted-sentence'>{sentence}</span> "
        else:
            formatted_html += f"<span>{sentence}</span> "
    formatted_html += "</div>"
    
    st.markdown(formatted_html, unsafe_allow_html=True)
