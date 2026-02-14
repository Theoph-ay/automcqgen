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
            if start != -1 and end != 0:
                quiz_str = quiz_str[start:end]
                
            import ast
            try:
                quiz_dict = json.loads(quiz_str)
            except Exception:
                 quiz_dict = ast.literal_eval(quiz_str)
            
        quiz_table_data=[]

        # Helper to do case-insensitive key lookup
        def get_flex(d, *keys):
            """Try multiple key names (case-insensitive) and return the first match."""
            lower_map = {k.lower(): v for k, v in d.items()}
            for key in keys:
                val = lower_map.get(key.lower())
                if val is not None:
                    return val
            return ""

        #iterate over the dict and extract info
        for key, value in quiz_dict.items():
            if not isinstance(value, dict):
                continue
            
            mcq = get_flex(value, "mcq", "question", "MCQ", "Question")
            options = get_flex(value, "options", "Options", "choices", "Choices")
            correct = get_flex(value, "correct", "correct_answer", "Correct Answer", "answer", "Answer")
            hint = get_flex(value, "hint", "Hint", "clue", "Clue")
            explanation = get_flex(value, "explanation", "Explanation", "reason", "Reason")
            
            # Parse options flexibly
            if isinstance(options, dict):
                opt_a = options.get("a") or options.get("A") or ""
                opt_b = options.get("b") or options.get("B") or ""
                opt_c = options.get("c") or options.get("C") or ""
                opt_d = options.get("d") or options.get("D") or ""
            else:
                opt_a = opt_b = opt_c = opt_d = ""
            
            quiz_table_data.append(
                {
                    "MCQ": mcq,
                    "Option A": opt_a,
                    "Option B": opt_b,
                    "Option C": opt_c,
                    "Option D": opt_d,
                    "Correct Answer": correct,
                    "Hint": hint,
                    "Explanation": explanation
                }
            )
        
        if not quiz_table_data:
            raise ValueError(f"No valid questions found in quiz data. Keys found: {list(quiz_dict.keys())}")
        
        return quiz_table_data
    except Exception as e:
        traceback.print_exc()
        # Include a snippet of the raw data for debugging
        raw_preview = str(quiz_str)[:500] if quiz_str else "None"
        raise Exception(f"Error parsing quiz data: {e}\n\nRaw data preview:\n{raw_preview}")

