import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv

from src.mcqgenerator.mcqgen import generate_evaluate_chain
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from src.mcqgenerator.logger import logger

#loading json file
# Get directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Join with filename
json_path = os.path.join(script_dir, "response.json")
with open(json_path, 'r') as f:
    response_json = json.load(f)

#Create Title
st.title('MCQ Generator With Langchain and Groq')

#Create Subtitle
st.subheader('Generate MCQs for your students')

#Create a form usinf st.form
with st.form("user_inputs"):
    #File upload
    text = st.file_uploader("Upload a PDF or text file", type=["pdf", "txt"])

    #Input Fields
    mcq_count=st.number_input("Number of MCQs", min_value=3, max_value=50)

    #Subject
    subject=st.text_input("Insert Subject", max_chars=20)

    #Quiz tone
    tone=st.text_input("Complexity Level of Questions", max_chars=20, placeholder="Simple")

    #Generate Button
    button = st.form_submit_button("Generate MCQs")

    #Check if the button is clicked and text is uploaded
    if button and text is not None and mcq_count and subject and tone:
        with st.spinner("Generating MCQs..."):
            try:
                #Read the file
                text = read_file(text)
                #Generate MCQs
                result = generate_evaluate_chain.invoke({
                "text": text,
                "number": mcq_count,
                "subject": subject,
                "tone": tone,
                "response_json": response_json
            })
            except Exception as e:
                logger.error(f"Error: {e}")
                st.error(f"Error: {e}")

            else:
                if isinstance(result, dict):

                    quiz=result.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index=df.index+1
                            st.dataframe(df)
                            # Display review
                            st.text_area(label="REview", value=result["review"])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(result)