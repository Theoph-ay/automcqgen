import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
import streamlit as st

# ---- YOUR INTERNAL MODULES ----
from src.mcqgenerator.mcqgen import generate_evaluate_chain
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logger


# ==============================
# LOAD ENV VARIABLES
# ==============================
load_dotenv()


# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="AI MCQ Generator",
    page_icon="🧠",
    layout="wide"
)


# ==============================
# LOAD RESPONSE JSON
# ==============================
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "response.json")

try:
    with open(json_path, 'r') as f:
        response_json = json.load(f)
except Exception as e:
    st.error("Could not load response.json")
    st.stop()


# ==============================
# CUSTOM CSS (PORTFOLIO UI)
# ==============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #141e30, #243b55);
    color: white;
}

.main-title {
    text-align: center;
    font-size: 55px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #d3d3d3;
    margin-bottom: 40px;
}

.glass-card {
    background: rgba(255, 255, 255, 0.07);
    padding: 25px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-bottom: 25px;
}

div.stButton > button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 12px;
    height: 3em;
    font-weight: bold;
    border: none;
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #7f00ff, #e100ff);
}
</style>
""", unsafe_allow_html=True)


# ==============================
# HEADER
# ==============================
st.markdown('<div class="main-title">🧠 AI MCQ Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate High-Quality MCQs using LangChain + Groq</div>', unsafe_allow_html=True)


# ==============================
# INPUT SECTION
# ==============================
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("📄 Upload PDF or TXT", type=["pdf", "txt"])
        subject = st.text_input("📘 Subject", placeholder="e.g. Physiology")

    with col2:
        mcq_count = st.slider("🧮 Number of MCQs", 3, 50, 5)
        tone = st.selectbox("🎯 Difficulty Level", ["Easy", "Medium", "Hard"])

    generate_btn = st.button("🚀 Generate MCQs")

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================
# GENERATION LOGIC
# ==============================
if generate_btn:

    if uploaded_file is None:
        st.warning("Please upload a file first.")
        st.stop()

    if not subject:
        st.warning("Please enter a subject.")
        st.stop()

    with st.spinner("Generating MCQs..."):

        try:
            # Read File
            text = read_file(uploaded_file)

            # Generate MCQs
            result = generate_evaluate_chain.invoke({
                "text": text,
                "number": mcq_count,
                "subject": subject,
                "tone": tone,
                "response_json": response_json
            })

        except Exception as e:
            logger.error(traceback.format_exc())
            st.error("Something went wrong while generating MCQs.")
            st.text(str(e))

        else:
            if isinstance(result, dict):

                quiz = result.get("quiz")
                review = result.get("review")

                if quiz:

                    table_data = get_table_data(quiz)

                    if table_data:

                        st.success("MCQs Generated Successfully!")

                        for i, row in enumerate(table_data, 1):

                            question = row.get("MCQ") or row.get("question") or row.get("Question")

                            # Try multiple possible formats safely
                            option_a = row.get("Option A") or row.get("A") or row.get("option_a")
                            option_b = row.get("Option B") or row.get("B") or row.get("option_b")
                            option_c = row.get("Option C") or row.get("C") or row.get("option_c")
                            option_d = row.get("Option D") or row.get("D") or row.get("option_d")

                            correct = row.get("Correct Answer") or row.get("correct") or row.get("answer")

                            st.markdown(f"""
                            <div class="glass-card">
                                <h3>Question {i}</h3>
                                <p><b>{question}</b></p>
                                <p>A. {option_a}</p>
                                <p>B. {option_b}</p>
                                <p>C. {option_c}</p>
                                <p>D. {option_d}</p>
                                <p style="color:#00ffcc;"><b>Correct Answer:</b> {correct}</p>
                            </div>
                            """, unsafe_allow_html=True)


                        # Review Section
                        if review:
                            st.markdown("## 📝 AI Review")
                            st.markdown(f'<div class="glass-card">{review}</div>', unsafe_allow_html=True)

                    else:
                        st.error("Error processing quiz data.")

                else:
                    st.write(result)

            else:
                st.write(result)


# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr style="border: 1px solid #444;">
<p style='text-align:center; color:gray;'>
Built with ❤️ using Streamlit, LangChain & Groq
</p>
""", unsafe_allow_html=True)