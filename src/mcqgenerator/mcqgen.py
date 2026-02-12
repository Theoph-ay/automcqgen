import os
import json
import pandas as pd
import traceback
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import PyPDF2
import langchain
from langchain_core.globals import set_debug
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data

load_dotenv()
set_debug(True)

llm = ChatGroq(model="openai/gpt-oss-120b",
api_key=os.getenv("GROQ_API_KEY"),
temperature=0.5)

with open(r"C:\Users\Loba\automcqgen\response.json", "r") as f:
    response_json = json.dumps(f.read(), indent=2)

#PROMPT 1
quiz_generation_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """You are an expert MCQ maker. 
        It is your job to create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 
        
        Make sure the questions are not repeated and check all the questions to be conforming the text as well.
        Make sure to format your response like the RESPONSE_JSON below and use it as a guide. 
        Ensure to make {number} MCQs.
        
        ### RESPONSE_JSON
        {response_json}"""
    ),
    (
        "human", 
        "Text: {text}"
    )
])

quiz_chain = quiz_generation_prompt | llm | StrOutputParser()

# --- PROMPT 2: EVALUATION (Your new template) ---
review_prompt = ChatPromptTemplate.from_template(
    """You are an expert english grammarian and writer. 
    Given a Multiple Choice Quiz for {subject} students.
    You need to evaluate the complexity of the question and give a complete analysis of the quiz.
    
    Quiz_MCQs:
    {quiz}
    
    Check from an expert English Writer of the above quiz:"""
)

# Input: {subject, quiz} -> Output: String (The Review) 
review_chain = review_prompt | llm | StrOutputParser()

#Combine the two chains
generate_evaluate_chain = (
    # Step 1: Pass inputs through, but ALSO run quiz_chain and store result in 'quiz'
    RunnablePassthrough.assign(quiz=quiz_chain)
    
    # Step 2: Now that 'quiz' is in the state, run review_chain and store in 'review'
    | RunnablePassthrough.assign(review=review_chain)
)