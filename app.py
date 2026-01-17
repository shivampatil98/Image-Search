import streamlit as st
import sys 
import time
from pathlib import Path
from src.inference import YOLOv11inference
from src.utils import save_metadata, load_metadata, get_unique_classes_counts

sys.path.append(str(Path(__file__).parent))

def init_session_state():
    session_defaults = {
        "metadata": None,
        "unique_classes": [],
        "count_options": {}
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

if option == "Process new images":
    with st.expander("Instructions", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            image_dir = st.text_input("Enter the directory path containing images:", placeholder="path/")
        with col2:
            model_path = st.text_input("Model weights path:", "yolo11m.pt")

        if st.button("Start Inference"):
            if image_dir:
                try:
                    with st.spinner("Running object detection inference..."):
                        inferencer = YOLOv11inference(model_path)
                        metadata = inferencer.process_directory(image_dir)
                        metadata_path = save_metadata(metadata, image_dir)
                        st.success(f"Processed {len(metadata)} images: {metadata_path}")
                        st.code(str(metadata_path))
                        st.session_state.metadata = metadata
                        st.session_state.unique_classes, st.session_state.count_options = get_unique_classes_counts(metadata)

                        time.sleep(3)  # Simulate some processing time in secs
                        st.success("Search completed successfully!")
                except Exception as e:
                    st.error(f"An error occurred during inference: {str(e)}")
            else:
                st.warning(f"Please enter an image directory path")
else:
    with st.expander("Load Metadata", expanded=True):
        metadata_path = st.text_input("Enter the metadata file path:", placeholder="path/to/metadata.json")

        if st.button("Load Metadata"):
            if metadata_path:
                try:
                    with st.spinner("Loading metadata..."):
                            metadata = load_metadata(metadata_path)
                            st.session_state.metadata = metadata
                            st.session_state.unique_classes, st.session_state.count_options = get_unique_classes_counts(metadata)
                            time.sleep(3)  # Simulate some loading time in secs
                            st.success(f"Metadata loaded successfully for {len(metadata)} images!")
                except Exception as e:
                    st.error(f"An error occurred while loading metadata: {str(e)}")
            else:
                st.warning(f"Please enter a metadata file path")