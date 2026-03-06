import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import speech_recognition as sr
import json
import time
from collections import Counter

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Advanced Multi-Modal AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# SESSION STATE INIT
# ======================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "question_text" not in st.session_state:
    st.session_state.question_text = ""

if "detected_objects" not in st.session_state:
    st.session_state.detected_objects = []

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("⚙ Control Panel")

    st.markdown("### 🎨 Select Theme")
    theme = st.radio(
        "",
        ["🌈 Colorful", "🌙 Dark", "🤍 White"],
        horizontal=True
    )

    nav = st.radio("📌 Navigation", ["Assistant", "Analytics"])

    if st.button("🆕 New Chat"):
        st.session_state.history = []
        st.session_state.question_text = ""
        st.session_state.detected_objects = []

    if st.button("🧹 Clear History"):
        st.session_state.history = []

    st.markdown("---")
    session_time = int(time.time() - st.session_state.start_time)
    st.write(f"⏱ Session Duration: {session_time} sec")

# ======================================================
# THEMES
# ======================================================
if "Colorful" in theme:
    background = "linear-gradient(135deg,#ff9a9e,#fad0c4)"
    text_color = "black"
elif "Dark" in theme:
    background = "linear-gradient(135deg,#141E30,#243B55)"
    text_color = "white"
else:
    background = "white"
    text_color = "black"

st.markdown(f"""
<style>
.stApp {{
    background: {background};
    color: {text_color};
}}

.stButton>button {{
    background: linear-gradient(45deg,#ff416c,#ff4b2b);
    color:white;
    border-radius:12px;
    font-weight:bold;
}}

.chat-box {{
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    box-shadow:0px 2px 6px rgba(0,0,0,0.2);
}}

.user {{
    background:#d1e7ff;
}}

.ai {{
    background:#c3f7d3;
}}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD MODEL
# ======================================================
@st.cache_resource
def load_model():
    return tf.keras.applications.MobileNetV2(weights="imagenet")

model = load_model()

# ======================================================
# IMAGE CLASSIFICATION (RGB FIX INCLUDED)
# ======================================================
def classify_image(image):
    image = image.convert("RGB")  # 🔥 Prevent grayscale crash

    img = image.resize((224, 224))
    arr = tf.keras.preprocessing.image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)

    preds = model.predict(arr)
    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0][0]
    return decoded[1], float(decoded[2]) * 100

# ======================================================
# SMART ANSWER ENGINE
# ======================================================
def generate_answer(label, confidence, question):

    base = f"This appears to be a {label}."

    if confidence > 80:
        certainty = "The model is highly confident."
    elif confidence > 50:
        certainty = "The model is moderately confident."
    else:
        certainty = "The model confidence is lower."

    q = question.lower()

    if "price" in q or "cost" in q:
        return f"{base} Price depends on brand and quality. {certainty}"
    elif "healthy" in q:
        return f"{base} Health impact depends on ingredients or usage. {certainty}"
    elif "use" in q or "purpose" in q:
        return f"{base} It is commonly used in daily life. {certainty}"
    elif "where" in q:
        return f"{base} It is typically found in relevant environments. {certainty}"
    elif "why" in q:
        return f"{base} It serves a functional purpose. {certainty}"
    else:
        return f"{base} Your question relates to this object. {certainty}"

# ======================================================
# VOICE INPUT
# ======================================================
import tempfile
import speech_recognition as sr
import streamlit as st

def voice_input():

    uploaded_file = st.file_uploader(
        "Upload voice file",
        type=["wav"]
    )

    if uploaded_file is not None:

        recognizer = sr.Recognizer()

        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_audio_path = temp_audio.name

        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio)
            return text
        except:
            return "Speech not recognized"

    return None

# ======================================================
# MAIN NAVIGATION
# ======================================================
if nav == "Assistant":

    st.title("🧠 Advanced Multi-Modal AI Assistant")

    col1, col2 = st.columns(2)

    # IMAGE SECTION
    with col1:
        st.subheader("🖼 Upload Image")
        uploaded_file = st.file_uploader("Choose Image", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, width=350)

            label, confidence = classify_image(image)
            st.success(f"🔍 Detected: {label}")
            st.progress(int(confidence))

            st.session_state.detected_objects.append(label)

    # QUESTION SECTION
    with col2:
        st.subheader("💬 Ask Question")

        if st.button("🎤 Voice Input"):
            text = voice_input()
            if text:
                st.session_state.question_text = text

        question = st.text_input(
            "Type your question:",
            value=st.session_state.question_text
        )

        if st.button("🚀 Ask AI"):
            if uploaded_file and question:
                answer = generate_answer(label, confidence, question)

                st.session_state.history.append({
                    "image": label,
                    "question": question,
                    "response": answer,
                    "confidence": confidence
                })

                st.session_state.question_text = ""
            else:
                st.warning("Upload image and enter question.")

    # CONVERSATION SECTION
    st.markdown("---")
    st.subheader("💬 Conversation")

    for chat in st.session_state.history:

        st.markdown(
            f"""
            <div class='chat-box user'>
                <b>🧑 You:</b><br>{chat['question']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class='chat-box ai'>
                <b>🤖 AI:</b><br>{chat['response']}
            </div>
            """,
            unsafe_allow_html=True
        )

    # DOWNLOAD OPTIONS
    if st.session_state.history:
        st.download_button(
            "📥 Download JSON",
            json.dumps(st.session_state.history, indent=2),
            "chat_history.json"
        )

        txt_data = "\n\n".join([f"Q: {c['question']}\nA: {c['response']}" for c in st.session_state.history])
        st.download_button(
            "📄 Download TXT",
            txt_data,
            "chat_history.txt"
        )

# ======================================================
# ANALYTICS PAGE
# ======================================================
else:

    st.title("📊 AI Analytics Dashboard")

    total_questions = len(st.session_state.history)
    st.metric("Total Questions", total_questions)

    if total_questions > 0:
        avg_conf = np.mean([c["confidence"] for c in st.session_state.history])
        st.metric("Average Confidence", f"{avg_conf:.2f}%")

        obj_counts = Counter(st.session_state.detected_objects)
        most_common = obj_counts.most_common(1)[0][0]
        st.metric("Most Detected Object", most_common)

        st.subheader("📈 Object Frequency")
        st.bar_chart(obj_counts)

        st.subheader("📊 Confidence Trend")
        conf_list = [c["confidence"] for c in st.session_state.history]
        st.line_chart(conf_list)
    else:
        st.info("No analytics data yet.")