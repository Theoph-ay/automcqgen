import os
import json
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
# INIT SESSION STATE
# ==============================
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "review_text" not in st.session_state:
    st.session_state.review_text = None
if "answers" not in st.session_state:
    st.session_state.answers = {}  # {question_index: selected_option_letter}


# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
    font-family: 'Inter', sans-serif;
}

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(90deg, #00c6ff, #0072ff, #7f00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #a0a0c0;
    margin-bottom: 40px;
}

.glass-card {
    background: rgba(255, 255, 255, 0.06);
    padding: 28px;
    border-radius: 18px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 25px;
}

.question-header {
    font-size: 14px;
    font-weight: 700;
    color: #7f8cff;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.question-text {
    font-size: 18px;
    font-weight: 600;
    color: #eee;
    margin-bottom: 18px;
    line-height: 1.5;
}

/* Option button styling */
div.stButton > button {
    background: rgba(255, 255, 255, 0.07);
    color: #d0d0e8;
    border-radius: 12px;
    height: auto;
    min-height: 3em;
    padding: 12px 18px;
    font-weight: 500;
    font-size: 15px;
    border: 1px solid rgba(255,255,255,0.1);
    transition: all 0.25s ease;
    width: 100%;
    text-align: left;
    white-space: normal;
    word-wrap: break-word;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    background: rgba(127, 140, 255, 0.2);
    border-color: rgba(127, 140, 255, 0.4);
    box-shadow: 0 4px 20px rgba(127, 140, 255, 0.15);
    color: white;
}

/* Generate button special styling */
div[data-testid="stHorizontalBlock"] > div:first-child div.stButton > button,
.generate-btn button {
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    color: white;
    font-weight: 700;
    border: none;
}

.generate-btn button:hover {
    background: linear-gradient(135deg, #7f00ff, #e100ff);
    transform: scale(1.03);
}

/* Success/Error styling */
.correct-msg {
    background: rgba(0, 255, 150, 0.12);
    border: 1px solid rgba(0, 255, 150, 0.3);
    border-radius: 12px;
    padding: 14px 18px;
    color: #00ff96;
    font-weight: 600;
    margin-top: 12px;
}

.wrong-msg {
    background: rgba(255, 70, 70, 0.12);
    border: 1px solid rgba(255, 70, 70, 0.3);
    border-radius: 12px;
    padding: 14px 18px;
    color: #ff6b6b;
    font-weight: 600;
    margin-top: 12px;
}

.explanation-box {
    background: rgba(255, 255, 255, 0.04);
    border-left: 3px solid #7f8cff;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    color: #c0c0d8;
    margin-top: 10px;
    font-size: 14px;
    line-height: 1.6;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 10px 24px;
    color: #a0a0c0;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.08);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,198,255,0.2), rgba(0,114,255,0.2));
    color: white;
    border-color: rgba(0,198,255,0.4);
}

/* Expander (hint) styling */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    color: #a0a0c0;
    font-weight: 600;
}

/* Score card */
.score-card {
    background: linear-gradient(135deg, rgba(0,198,255,0.15), rgba(127,0,255,0.15));
    border: 1px solid rgba(127,140,255,0.3);
    border-radius: 18px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
}

.score-number {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #00c6ff, #7f00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
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

    with st.spinner("✨ Generating your interactive quiz..."):

        try:
            text = read_file(uploaded_file)

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
                    try:
                        table_data = get_table_data(quiz)
                    except Exception as parse_err:
                        st.error(f"Error processing quiz data:")
                        st.code(str(parse_err), language="text")
                        table_data = None

                    if table_data:
                        st.session_state.quiz_data = table_data
                        st.session_state.review_text = review
                        st.session_state.answers = {}
                        st.rerun()
                    else:
                        st.error("Error processing quiz data.")
                else:
                    st.write(result)
            else:
                st.write(result)


# ==============================
# QUIZ DISPLAY (TABBED LAYOUT)
# ==============================
if st.session_state.quiz_data:

    quiz_data = st.session_state.quiz_data
    review_text = st.session_state.review_text

    tab_quiz, tab_review = st.tabs(["📝 Quiz", "📊 Review"])

    # ---------------------------
    # TAB 1: Interactive Quiz
    # ---------------------------
    with tab_quiz:

        # Score tracker at top
        total = len(quiz_data)
        answered = len(st.session_state.answers)
        correct_count = sum(
            1 for idx, ans in st.session_state.answers.items()
            if ans.lower() == quiz_data[idx].get("Correct Answer", "").lower()
        )

        if answered > 0:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{correct_count} / {answered}</div>
                <div style="color:#a0a0c0; margin-top:8px; font-size:16px;">
                    correct so far · {total - answered} remaining
                </div>
            </div>
            """, unsafe_allow_html=True)

        for i, row in enumerate(quiz_data):

            question = row.get("MCQ") or row.get("question") or row.get("Question")
            option_a = row.get("Option A") or ""
            option_b = row.get("Option B") or ""
            option_c = row.get("Option C") or ""
            option_d = row.get("Option D") or ""
            correct = row.get("Correct Answer", "")
            hint = row.get("Hint", "")
            explanation = row.get("Explanation", "")

            st.markdown(f"""
            <div class="glass-card">
                <div class="question-header">Question {i + 1} of {total}</div>
                <div class="question-text">{question}</div>
            </div>
            """, unsafe_allow_html=True)

            already_answered = i in st.session_state.answers
            options = {
                "a": option_a,
                "b": option_b,
                "c": option_c,
                "d": option_d
            }

            # Option buttons in 2x2 grid
            col1, col2 = st.columns(2)

            for j, (letter, text) in enumerate(options.items()):
                col = col1 if j % 2 == 0 else col2
                with col:
                    label = f"{letter.upper()}. {text}"
                    btn = st.button(
                        label,
                        key=f"q{i}_opt_{letter}",
                        disabled=already_answered,
                        use_container_width=True
                    )

                    if btn and not already_answered:
                        st.session_state.answers[i] = letter
                        st.rerun()

            # Show result after answering
            if already_answered:
                selected = st.session_state.answers[i]
                is_correct = selected.lower() == correct.lower()

                if is_correct:
                    st.markdown(f"""
                    <div class="correct-msg">
                        ✅ <strong>Correct!</strong> You selected <strong>{selected.upper()}</strong> — well done!
                    </div>
                    """, unsafe_allow_html=True)
                    # Show balloons only on first correct answer render
                    if f"celebrated_{i}" not in st.session_state:
                        st.session_state[f"celebrated_{i}"] = True
                        st.balloons()
                else:
                    st.markdown(f"""
                    <div class="wrong-msg">
                        ❌ <strong>Incorrect.</strong> You selected <strong>{selected.upper()}</strong>, 
                        but the correct answer is <strong>{correct.upper()}</strong>.
                    </div>
                    """, unsafe_allow_html=True)

                    if explanation:
                        st.markdown(f"""
                        <div class="explanation-box">
                            💡 <strong>Explanation:</strong> {explanation}
                        </div>
                        """, unsafe_allow_html=True)

            # Hint expander (always available)
            if hint:
                with st.expander("💡 Need a hint?"):
                    st.info(hint)

            st.markdown("---")

        # Final score when all questions answered
        if answered == total and total > 0:
            pct = int((correct_count / total) * 100)
            if pct >= 80:
                emoji = "🏆"
                msg = "Outstanding!"
            elif pct >= 60:
                emoji = "👏"
                msg = "Good job!"
            elif pct >= 40:
                emoji = "💪"
                msg = "Keep practicing!"
            else:
                emoji = "📚"
                msg = "Time to review!"

            st.markdown(f"""
            <div class="score-card">
                <div style="font-size: 60px; margin-bottom: 10px;">{emoji}</div>
                <div class="score-number">{correct_count} / {total} ({pct}%)</div>
                <div style="color:#d0d0e8; margin-top:12px; font-size:20px; font-weight:600;">
                    {msg}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------------------
    # TAB 2: AI Review
    # ---------------------------
    with tab_review:
        if review_text:
            st.markdown("### 📊 AI Review & Analysis")
            st.markdown(f"""
            <div class="glass-card">
                {review_text}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No review available for this quiz.")


# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr style="border: 1px solid rgba(255,255,255,0.08); margin-top: 50px;">
<p style='text-align:center; color:#555; font-size:13px;'>
Built with ❤️ using Streamlit, LangChain & Groq
</p>
""", unsafe_allow_html=True)