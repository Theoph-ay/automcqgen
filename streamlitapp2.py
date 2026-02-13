import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

# --- Import your custom modules ---
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.mcqgen import generate_evaluate_chain
from src.mcqgenerator.logger import logger

# --- 1. Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="MCQ Generator Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Load JSON Template ---
# Get directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "response.json")

try:
    with open(json_path, 'r') as f:
        response_json = json.load(f)
except Exception as e:
    st.error(f"Error loading response.json: {e}")
    response_json = {} 

# --- 3. Custom CSS for Styling ---
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f9f9f9;
    }
    /* Title styling */
    h1 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Button styling */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #45a049;
        color: white;
    }
    /* Success message */
    .stSuccess {
        background-color: #dff0d8;
        border-color: #d6e9c6;
        color: #3c763d;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. Sidebar Configuration ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=50) # Optional Logo
    st.title("⚙️ Configuration")
    st.markdown("Adjust your quiz settings below.")
    
    # Input Fields in Sidebar
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50, value=5)
    tone = st.selectbox("Complexity Level", ["Simple", "Intermediate", "Advanced", "Professional"], index=0)
    
    st.markdown("---")
    st.write("Powered by LangChain & Groq")

# --- 5. Main App Layout ---
st.title("🎓 Smart MCQ Generator")
st.markdown("### Transform your notes into quizzes instantly.")

# Create a clean container for the main inputs
with st.container():
    with st.form("user_inputs"):
        
        # Use columns for a better layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**1. Upload Content**")
            uploaded_file = st.file_uploader("Upload a PDF or Text file", type=["pdf", "txt"])
        
        with col2:
            st.markdown("**2. Subject Details**")
            subject = st.text_input("Subject / Topic", max_chars=50, placeholder="e.g. Biology, Python Programming")

        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        
        # Submit Button
        submitted = st.form_submit_button("🚀 Generate Quiz")

# --- 6. Processing Logic ---
if submitted:
    if uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("🧠 Analyzing document & generating questions..."):
            try:
                # 1. Read the file
                text = read_file(uploaded_file)
                
                # 2. Invoke the Chain
                # Note: We dump response_json to string to ensure safe passing
                result = generate_evaluate_chain.invoke({
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(response_json)
                })
                
                # 3. Handle the Response
                if isinstance(result, dict):
                    # Extract quiz data
                    quiz_str = result.get("quiz", None)
                    
                    if quiz_str is not None:
                        table_data = get_table_data(quiz_str)
                        
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            
                            # --- Display Results ---
                            st.success("✅ Quiz Generated Successfully!")
                            
                            # Tabbed View for better organization
                            tab1, tab2 = st.tabs(["📋 Generated MCQs", "📝 Expert Review"])
                            
                            with tab1:
                                st.dataframe(df, use_container_width=True)
                                
                                # CSV Download Button
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download Quiz as CSV",
                                    data=csv,
                                    file_name='generated_quiz.csv',
                                    mime='text/csv',
                                )
                                
                            with tab2:
                                st.markdown("### Complexity Analysis")
                                st.info(result.get("review", "No review generated."))
                                
                        else:
                            st.error("Error: Could not parse table data.")
                    else:
                        st.error("Error: Quiz data not found in response.")
                else:
                    st.write(result)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error(f"An error occurred: {e}")
                logger.error(f"Error: {e}")
    else:
        st.warning("⚠️ Please fill in all fields and upload a file.")