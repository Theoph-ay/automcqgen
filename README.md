# AI MCQ Generator & Reviewer 📝

An end-to-end LLM-powered application that transforms static PDF or TXT documents into interactive, high-quality multiple-choice quizzes. This tool leverages a **dual-LLM chain architecture**: one to generate the questions and another to provide a rigorous pedagogical and technical review.



## Features

* **Customizable Generation:** Specify the number of questions, subject matter, and difficulty level (Easy, Medium, Hard).
* **Intelligent Parsing:** Handles PDF and TXT files using LangChain’s document loaders.
* **Interactive Quiz UI:** A sleek Streamlit interface where users can take the quiz with real-time feedback, hints, and celebratory UI effects for correct answers.
* **Automated Quality Review:** A dedicated "Reviewer" agent generates a comprehensive **Review & Analysis** table evaluating:
    * **Vocabulary & Grammar:** Ensuring professional academic standards.
    * **Cognitive Complexity:** Alignment with Bloom’s Taxonomy (from Recall to Application).
    * **"Fix-it" Checklist:** Actionable feedback to improve question stems and distractors.
* **High-Speed Inference:** Powered by **GroQ** for near-instant response times, ensuring a seamless user experience.

## Tech Stack

* **Framework:** [LangChain](https://www.langchain.com/) (Agent orchestration and Prompt Chaining)
* **LLM Provider:** [GroQ](https://groq.com/) (GPT OSS 120B)
* **Frontend:** [Streamlit](https://streamlit.io/) with a little html
* **Language:** Python 3.10+

## Getting Started

### Prerequisites
* A GroQ API Key.
* Python 3.10 or higher.

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Theoph-ay/automcqgen.git
   cd automcqgen
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up your environment variables:**
Create a .env file in the root directory and add your key:

```bash
GROQ_API_KEY=your_api_key_here
```
4. **Run the application:**

```bash
streamlit run Srreamlitapp4.py
```
**Demo:**

(Check out the MCQGENERATOR.mp4 on my socials for a full walkthrough of the generation and review process.)

**Acknowledgments**
Special thanks to Halleluyah Oludele for the valuable tip on implementing the extra interactive quiz feature.

Inspired by the need for advanced active recall tools in medical education.

Developed by Theophilus Olayiwola, Medical Student & AI/ML Enthusiast [LinkedIn](https://www.linkedin.com/in/theophilus-olayiwola-ab914a231/) | [Twitter/X](https://x.com/Dr_Layi)
