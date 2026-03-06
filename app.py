import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import json
import time
from collections import Counter
from streamlit.components.v1 import html

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Advanced Multi-Modal AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# SESSION STATE
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

    theme = st.radio(
        "🎨 Select Theme",
        ["🌈 Colorful", "🌙 Dark", "🤍 White"]
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
background:{background};
color:{text_color};
}}

.stButton>button {{
background:linear-gradient(45deg,#ff416c,#ff4b2b);
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
# IMAGE CLASSIFICATION
# ======================================================

def classify_image(image):

    image = image.convert("RGB")

    img = image.resize((224,224))

    arr = tf.keras.preprocessing.image.img_to_array(img)

    arr = np.expand_dims(arr, axis=0)

    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)

    preds = model.predict(arr)

    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0][0]

    return decoded[1], float(decoded[2])*100

# ======================================================
# AI ANSWER ENGINE
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
# MAIN PAGE
# ======================================================

if nav == "Assistant":

    st.title("🧠 Advanced Multi-Modal AI Assistant")

    col1, col2 = st.columns(2)

    label = None
    confidence = 0

    # ================= IMAGE INPUT =================

    with col1:

        st.subheader("🖼 Upload Image")

        uploaded_file = st.file_uploader("Choose Image", type=["jpg","jpeg","png"])

        if uploaded_file:

            image = Image.open(uploaded_file)

            st.image(image, width=350)

            label, confidence = classify_image(image)

            st.success(f"🔍 Detected: {label}")

            st.progress(int(confidence))

            st.session_state.detected_objects.append(label)

    # ================= QUESTION INPUT =================

    with col2:

        st.subheader("💬 Ask Question")

        question = st.text_input(
            "✍ Type your question:",
            value=st.session_state.question_text
        )

        st.markdown("### 🎤 Or Ask Using Voice")

        voice_html = """
        <button onclick="startDictation()" 
        style="background:#ff4b2b;color:white;padding:10px 20px;border:none;border-radius:10px;font-weight:bold;">
        🎤 Start Listening
        </button>

        <p id="status" style="color:red;font-weight:bold;"></p>

<script>

function startDictation(){

if(!('webkitSpeechRecognition' in window)){
alert("Speech Recognition not supported");
return;
}

var recognition = new webkitSpeechRecognition();

recognition.lang = "en-US";
recognition.continuous = false;
recognition.interimResults = false;

document.getElementById("status").innerHTML="🎧 Listening...";

recognition.start();

recognition.onresult=function(event){

var transcript = event.results[0][0].transcript;

var inputs = window.parent.document.querySelectorAll('input');

for (var i = 0; i < inputs.length; i++) {
    if(inputs[i].type === "text"){
        inputs[i].value = transcript;
        inputs[i].dispatchEvent(new Event('input',{bubbles:true}));
        break;
    }
}

document.getElementById("status").innerHTML="✅ Voice captured: " + transcript;

};

recognition.onerror=function(){
document.getElementById("status").innerHTML="❌ Voice error";
};

}

</script>
"""

        html(voice_html, height=150)

        # ================= ASK AI =================

        if st.button("🚀 Ask AI"):

            if question:

                if uploaded_file:
                    answer = generate_answer(label, confidence, question)
                    detected = label
                    conf = confidence

                else:
                    answer = f"You asked: {question}. Upload an image for object analysis."
                    detected = "No image"
                    conf = 0

                st.session_state.history.append({
                    "image": detected,
                    "question": question,
                    "response": answer,
                    "confidence": conf
                })

            else:
                st.warning("Please type or speak a question")

    # ================= CHAT HISTORY =================

    st.markdown("---")

    st.subheader("💬 Conversation")

    for chat in st.session_state.history:

        st.markdown(f"""
        <div class='chat-box user'>
        <b>🧑 You:</b><br>{chat['question']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='chat-box ai'>
        <b>🤖 AI:</b><br>{chat['response']}
        </div>
        """, unsafe_allow_html=True)

# ======================================================
# ANALYTICS PAGE
# ======================================================

else:

    st.title("📊 AI Analytics Dashboard")

    total_questions=len(st.session_state.history)

    st.metric("Total Questions", total_questions)

    if total_questions>0:

        avg_conf=np.mean([c["confidence"] for c in st.session_state.history])

        st.metric("Average Confidence", f"{avg_conf:.2f}%")

        obj_counts=Counter(st.session_state.detected_objects)

        most_common=obj_counts.most_common(1)[0][0]

        st.metric("Most Detected Object", most_common)

        st.subheader("📈 Object Frequency")

        st.bar_chart(obj_counts)

        st.subheader("📊 Confidence Trend")

        conf_list=[c["confidence"] for c in st.session_state.history]

        st.line_chart(conf_list)

    else:

        st.info("No analytics data yet.")