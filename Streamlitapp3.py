import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.mcqgen import generate_evaluate_chain
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from src.mcqgenerator.logger import logger

# Page configuration
st.set_page_config(
    page_title="AI MCQ Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, dynamic styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Container styling */
    .main .block-container {
        padding: 2rem 3rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        margin-top: 2rem;
    }
    
    /* Title styling with gradient */
    h1 {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
    }
    
    /* Subtitle styling */
    h3 {
        color: #6c757d;
        text-align: center;
        font-weight: 400;
        font-size: 1.3rem !important;
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Form container */
    .stForm {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(102, 126, 234, 0.2);
        animation: slideIn 0.6s ease-out;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* File uploader */
    .stFileUploader {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        border: 2px dashed #667eea;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        background: #f8f9fa;
    }
    
    /* Submit button */
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
        margin-top: 1rem;
    }
    
    .stFormSubmitButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Text areas */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 15px;
        font-size: 1rem;
        background: #f8f9fa;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
        animation: slideIn 0.5s ease-out;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Labels */
    label {
        font-weight: 600 !important;
        color: #495057 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        margin: 1rem 0;
        animation: fadeIn 1s ease-out;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Loading json file
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "response.json")
with open(json_path, 'r') as f:
    response_json = json.load(f)

# Header Section
st.markdown('<h1>🎓 AI-Powered MCQ Generator</h1>', unsafe_allow_html=True)
st.markdown('<h3>Harness the power of AI to create engaging multiple-choice questions instantly</h3>', unsafe_allow_html=True)

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# Create columns for stats
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">⚡</div>
        <div class="stat-label">Fast Generation</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">🤖</div>
        <div class="stat-label">AI-Powered</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">📚</div>
        <div class="stat-label">Smart Learning</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create a form
with st.form("user_inputs"):
    st.markdown("### 📝 Configure Your Quiz")
    
    # File upload with icon
    st.markdown("#### 📄 Upload Your Content")
    text = st.file_uploader(
        "Choose a PDF or text file",
        type=["pdf", "txt"],
        help="Upload the source material for generating MCQs"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create two columns for inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔢 Quiz Settings")
        mcq_count = st.number_input(
            "Number of MCQs",
            min_value=3,
            max_value=50,
            value=5,
            help="Choose how many questions to generate"
        )
        
        subject = st.text_input(
            "Subject",
            max_chars=20,
            placeholder="e.g., Biology, History, Math",
            help="Enter the subject area"
        )
    
    with col2:
        st.markdown("#### ⚙️ Difficulty Level")
        tone = st.text_input(
            "Complexity Level",
            max_chars=20,
            placeholder="Simple, Medium, or Complex",
            value="Simple",
            help="Set the difficulty of questions"
        )
        
        # Add a selectbox as alternative
        st.markdown("<br><br>", unsafe_allow_html=True)
        difficulty_preset = st.selectbox(
            "Or choose a preset",
            ["Custom", "Beginner", "Intermediate", "Advanced", "Expert"],
            help="Quick difficulty presets"
        )
        if difficulty_preset != "Custom":
            tone = difficulty_preset
    
    # Generate Button
    button = st.form_submit_button("🚀 Generate MCQs")

# Process form submission
if button and text is not None and mcq_count and subject and tone:
    with st.spinner("🔄 Generating your MCQs... Please wait..."):
        try:
            # Read the file
            text_content = read_file(text)
            
            # Generate MCQs
            result = generate_evaluate_chain.invoke({
                "text": text_content,
                "number": mcq_count,
                "subject": subject,
                "tone": tone,
                "response_json": response_json
            })
            
        except Exception as e:
            logger.error(f"Error: {e}")
            st.error(f"❌ Error: {e}")
            st.error(traceback.format_exc())
        else:
            if isinstance(result, dict):
                quiz = result.get("quiz", None)
                if quiz is not None:
                    # Success message
                    st.success("✅ MCQs generated successfully!")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 📊 Generated Questions")
                    
                    table_data = get_table_data(quiz)
                    if table_data is not None:
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        
                        # Display dataframe with custom styling
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Download button
                        csv = df.to_csv(index=True).encode('utf-8')
                        st.download_button(
                            label="📥 Download MCQs as CSV",
                            data=csv,
                            file_name=f"{subject}_mcqs.csv",
                            mime="text/csv",
                        )
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Display review
                        st.markdown("### 📝 AI Review & Feedback")
                        review_text = result.get("review", "No review available")
                        st.text_area(
                            label="Review",
                            value=review_text,
                            height=150,
                            disabled=True
                        )
                    else:
                        st.error("❌ Error in the table data")
                else:
                    st.warning("⚠️ No quiz data found in the result")
            else:
                st.write(result)

elif button:
    st.warning("⚠️ Please fill in all fields and upload a file to generate MCQs")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6c757d;'>Built with ❤️ using Streamlit, LangChain & Groq</p>",
    unsafe_allow_html=True
)