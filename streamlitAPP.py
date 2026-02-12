import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv

from src.mcqgenerator.mcqgen import generate_evaluate_chain
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from src.mcqgenerator.logger import logger