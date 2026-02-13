import os
import PyPDF2
import json
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text

        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        raise Exception("unsupported file format, only pdf and txt file are supported")


def get_table_data(quiz_str):
    try:
        #covert the quiz from string to dict
        if isinstance(quiz_str, dict):
            quiz_dict = quiz_str
        else:
            # Clean up the string if it contains markdown
            if "```json" in quiz_str:
                quiz_str = quiz_str.split("```json")[1].split("```")[0]
            elif "```" in quiz_str:
                quiz_str = quiz_str.split("```")[1].split("```")[0]
            
            # Find start and end of json
            start = quiz_str.find('{')
            end = quiz_str.rfind('}') + 1
            if start != -1 and end != -1:
                quiz_str = quiz_str[start:end]
                
            import ast
            try:
                quiz_dict = json.loads(quiz_str)
            except Exception:
                 quiz_dict = ast.literal_eval(quiz_str)
            
        quiz_table_data=[]

        #iterate over the dict and extract info
        for key, value in quiz_dict.items():
            mcq=value["mcq"]
            options=" || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                ]
            )
            correct=value["correct"]
            quiz_table_data.append(
                {
                    "MCQ": mcq,
                    "Options": options,
                    "Correct Answer": correct
                }
            )
        return quiz_table_data
    except Exception as e:
        traceback.print_exc()
        print(f"Failed quiz_str: {quiz_str}")
        raise Exception("Error parsing quiz data")
