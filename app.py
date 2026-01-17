import streamlit as st
import sys 
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def init_session_state():
    session_defaults = {
        "image_dir": "path",
    }

    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

st.set_page_config(
    page_title="Image Search App",
    page_icon="🔍",
    layout="wide"
)

st.title("Computer Vision powered Image Search Application")

# Radio button for user to choose between processing new images or loading existing metadata
option = st.radio("Choose an option", ("Process new images", "Load existing metadata"), horizontal=True)