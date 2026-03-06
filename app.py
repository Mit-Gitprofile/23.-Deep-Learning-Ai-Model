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
        "Theme",
        ["🌈 Colorful","🌙 Dark","🤍 White"]
    )

    nav = st.radio("Navigation",["Assistant","Analytics"])

    if st.button("🧹 Clear History"):
        st.session_state.history=[]

# ======================================================
# THEMES
# ======================================================

if "Colorful" in theme:
    background="linear-gradient(135deg,#ff9a9e,#fad0c4)"
    text_color="black"

elif "Dark" in theme:
    background="linear-gradient(135deg,#141E30,#243B55)"
    text_color="white"

else:
    background="white"
    text_color="black"

st.markdown(f"""
<style>

.stApp{{
background:{background};
color:{text_color};
}}

.chat-box{{
padding:15px;
border-radius:12px;
margin-bottom:10px;
}}

.user{{background:#d1e7ff;}}
.ai{{background:#c3f7d3;}}

</style>
""",unsafe_allow_html=True)

# ======================================================
# LOAD MODEL
# ======================================================

@st.cache_resource
def load_model():
    return tf.keras.applications.MobileNetV2(weights="imagenet")

model=load_model()

# ======================================================
# IMAGE CLASSIFICATION
# ======================================================

def classify_image(image):

    image=image.convert("RGB")

    img=image.resize((224,224))

    arr=tf.keras.preprocessing.image.img_to_array(img)

    arr=np.expand_dims(arr,axis=0)

    arr=tf.keras.applications.mobilenet_v2.preprocess_input(arr)

    preds=model.predict(arr)

    decoded=tf.keras.applications.mobilenet_v2.decode_predictions(preds,top=1)[0][0]

    return decoded[1],float(decoded[2])*100

# ======================================================
# AI ANSWER ENGINE
# ======================================================

def generate_answer(label,confidence,question):

    base=f"This appears to be a {label}."

    if confidence>80:
        certainty="Model is highly confident."
    elif confidence>50:
        certainty="Model is moderately confident."
    else:
        certainty="Model confidence is lower."

    q=question.lower()

    if "price" in q:
        return f"{base} Price depends on brand and quality. {certainty}"

    elif "use" in q:
        return f"{base} It is commonly used in daily life. {certainty}"

    elif "where" in q:
        return f"{base} It is usually found in relevant environments. {certainty}"

    else:
        return f"{base} {certainty}"

# ======================================================
# MAIN PAGE
# ======================================================

if nav=="Assistant":

    st.title("🧠 Advanced Multi-Modal AI Assistant")

    col1,col2=st.columns(2)

# ================= IMAGE INPUT =================

    with col1:

        uploaded_file=st.file_uploader("Upload Image",type=["jpg","png","jpeg"])

        if uploaded_file:

            image=Image.open(uploaded_file)

            st.image(image,width=350)

            label,confidence=classify_image(image)

            st.success(f"Detected: {label}")

            st.progress(int(confidence))

            st.session_state.detected_objects.append(label)

# ================= QUESTION INPUT =================

    with col2:

        st.subheader("💬 Ask Question")

        question=st.text_input("Type your question")

        st.markdown("### 🎤 Voice Question")

        html_code="""
        <button onclick="startDictation()" 
        style="background:#ff4b2b;color:white;padding:10px 20px;border:none;border-radius:8px;">
        🎤 Start Listening
        </button>

        <p id="status" style="color:red;"></p>

<script>

function startDictation(){

if(!('webkitSpeechRecognition' in window)){
alert("Speech recognition not supported");
return;
}

var recognition=new webkitSpeechRecognition();

recognition.lang="en-US";
recognition.continuous=false;

document.getElementById("status").innerHTML="🎧 Listening...";

recognition.start();

recognition.onresult=function(event){

var transcript=event.results[0][0].transcript;

var inputs=window.parent.document.querySelectorAll("input");

if(inputs.length>0){
inputs[inputs.length-1].value=transcript;
inputs[inputs.length-1].dispatchEvent(new Event("input",{bubbles:true}));
}

document.getElementById("status").innerHTML="✅ Voice captured";

};

recognition.onerror=function(){
document.getElementById("status").innerHTML="Error capturing voice";
};

}

</script>
"""

        html(html_code,height=130)

        if st.button("🚀 Ask AI"):

            if uploaded_file and question:

                answer=generate_answer(label,confidence,question)

                st.session_state.history.append({
                    "question":question,
                    "response":answer,
                    "confidence":confidence
                })

            else:

                st.warning("Upload image and ask question")

# ================= CHAT HISTORY =================

    st.markdown("---")

    st.subheader("Conversation")

    for chat in st.session_state.history:

        st.markdown(f"""
        <div class='chat-box user'>
        <b>You:</b><br>{chat['question']}
        </div>
        """,unsafe_allow_html=True)

        st.markdown(f"""
        <div class='chat-box ai'>
        <b>AI:</b><br>{chat['response']}
        </div>
        """,unsafe_allow_html=True)

# ======================================================
# ANALYTICS
# ======================================================

else:

    st.title("📊 Analytics")

    total=len(st.session_state.history)

    st.metric("Total Questions",total)

    if total>0:

        avg=np.mean([c["confidence"] for c in st.session_state.history])

        st.metric("Average Confidence",f"{avg:.2f}%")

        counts=Counter(st.session_state.detected_objects)

        st.bar_chart(counts)

    else:

        st.info("No data yet.")