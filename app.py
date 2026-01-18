import streamlit as st
import sys 
import time
from pathlib import Path
from src.inference import YOLOv11Inference
from src.utils import save_metadata, load_metadata, get_unique_classes_counts

sys.path.append(str(Path(__file__).parent))

def init_session_state():
    session_defaults = {
        "metadata": None,
        "unique_classes": [],
        "count_options": {},
        "search_results": [],
        "search params": {
            "search_mode": "Any of selected classes OR",
            "selected_classes": [],
            "thresholds": {}
        }
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
                        inferencer = YOLOv11Inference(model_path)
                        metadata = inferencer.process_directory(image_dir)
                        metadata_path = save_metadata(metadata, image_dir)
                        st.success(f"Processed {len(metadata)} images: {metadata_path}")
                        st.code(str(metadata_path))
                        st.session_state.metadata = metadata
                        st.session_state.unique_classes, st.session_state.count_options = get_unique_classes_counts(metadata)

                        #time.sleep(3)  # Simulate some processing time in secs
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
                            #time.sleep(3)  # Simulate some loading time in secs
                            st.success(f"Metadata loaded successfully for {len(metadata)} images!")
                except Exception as e:
                    st.error(f"An error occurred while loading metadata: {str(e)}")
            else:
                st.warning(f"Please enter a metadata file path")


#st.write(f"st.session_state.unique_classes: {st.session_state.unique_classes}")

if st.session_state.metadata:
    st.header("Search Images by Detected Objects")

    with st.container():
        st.session_state.search_params["search_mode"] = st.radio("Select search type:", 
                        ("Any of selected classes OR", "All selected Classes"), 
                        horizontal=True, key="search_type")

        st.session_state.search_params["selected_classes"] = st.multiselect(
            "Select object classes to search for:",
            options=st.session_state.unique_classes
        )   


        if st.session_state.search_params["selected_classes"]:
            st.subheader("Set Minimum Confidence Thresholds for Selected Classes")
            cols = st.columns(len(st.session_state.search_params["selected_classes"]))
            for i, cls in enumerate(st.session_state.search_params["selected_classes"]):
                with cols[i]:
                    st.sessiomn_state.search_params["thresholds"][cls] = st.selectbox(
                        f"Max count for class '{cls}':",
                        options= ["None"] + st.session_state.count_options.get(cls, [])
                )
                    
        if st.button("Search Images", type="primary") and st.session_state.select_params["selected_classes"]:
            results = []
            search_params = st.session_state.search_params

            for item in st.session_state.metadata:
                matches = False
                class_matches = {}


                for cls in search_params["selected_classes"]:
                    class_detections = [det for det in item["detections"] if det["class"] == cls]
                    class_count = len(class_detections)
                    class_matches[cls] = False

                    threshold = search_params["thresholds"].get(cls, "None")
                    if threshold == "None" or class_count <= int(threshold):
                        class_matches[cls] = (class_count >= 1) 
                    else:
                        class_matches[cls] = (class_count >= 1 and class_count <= int(threshold))


                if search_params["search_mode"] == "Any of selected classes OR":
                    matches = any(class_matches.values())

                else:
                    matches = all(class_matches.values())

                if matches:
                    results.append(item)

            st.session_state.search_results = results

        st.write(st.session_state.search_results)