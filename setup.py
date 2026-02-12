from setuptools import find_packages, setup

setup(
    name="automcqgen",
    version="0.0.1",
    author="Olayiwola Theophilus",
    author_email="olayiwolatheophilusayomide@gmail.com",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-groq",
        "streamlit",
        "python-dotenv",
        "PyPDF2",
    ],
)
