from turtle import color
from narwhals import col
import streamlit as st
import sys 
import time
from PIL import Image, ImageDraw, ImageFont
import base64
import json
from io import BytesIO
from pathlib import Path
from src.inference import YOLOv11Inference
from src.utils import save_metadata, load_metadata, get_unique_classes_counts

sys.path.append(str(Path(__file__).parent))

def img_to_base64(image: Image.Image) -> str:
    """Convert a PIL Image to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def init_session_state():
    session_defaults = {
        "metadata": None,
        "unique_classes": [],
        "count_options": {},
        "search_results": [],
        "search_params": {
            "search_mode": "Any of selected classes OR",
            "selected_classes": [],
            "thresholds": {}
        },
        "show_boxes": True,
        "grid_columns": 3,
        "highlight_matches": True
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


#st.write(f"st.session_state.unique_classes: {st.session_state.unique_options}")

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
            st.subheader("Set Minimum Confidence Thresholds")
            cols = st.columns(len(st.session_state.search_params["selected_classes"]))
            for i, cls in enumerate(st.session_state.search_params["selected_classes"]):
                with cols[i]:
                    st.session_state.search_params["thresholds"][cls] = st.selectbox(
                        f"Max count for class '{cls}':",
                        options= ["None"] + st.session_state.count_options.get(cls, [])
                )

        if st.button("Search Images", type="primary") and st.session_state.search_params["selected_classes"]:
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

        #st.write(st.session_state.search_results)

if st.session_state.search_results:
    results =  st.session_state.search_results
    search_params = st.session_state.search_params

    st.subheader(f"Search Results: Found {len(results)} images matching criteria ({search_params['search_mode']})")

    with st.expander("Display Options", expanded=True):
        cols = st.columns(3)
        with cols[0]:
            st.session_state.show_boxes = st.checkbox("Show bounding boxes on images", value=st.session_state.show_boxes)
        with cols[1]:
            st.session_state.grid_columns = st.slider("Grid columns", min_value=1, max_value=6, value=st.session_state.grid_columns)
        with cols[2]:
            st.session_state.highlight_matches = st.checkbox("Highlight matched classes", value=st.session_state.highlight_matches)


    #create grid using streamlit columns
    grid_cols = st.columns(st.session_state.grid_columns)
    col.index = 0

    for result in results:
        with grid_cols[col.index]:
            try:
                img = Image.open(result["image_path"])
                draw = ImageDraw.Draw(img)
            
                if st.session_state.show_boxes:
                    try:
                        font = ImageFont.truetype("arial.ttf", 15)
                    except:
                        font = ImageFont.load_default()

                    for det in result["detections"]:
                        cls = det['class']
                        #conf = det['confidence']
                        bbox = det['bbox']  # [x1, y1, x2, y2]

                        if cls in search_params["selected_classes"]:
                            box_color = "#23ff2e"
                            thickness = 3
                        elif not st.session_state.highlight_matches:
                            box_color = "#ff3838"
                            thickness = 1
                        else:
                            continue

                        draw.rectangle(bbox, outline=box_color, width=thickness)

                        if cls in search_params["selected_classes"] and not st.session_state.highlight_matches:
                            label = f"{cls} {det['confidence']:.2f}"
                            text_bbox = draw.textbbox((0,0), label, font=font)
                            text_width = text_bbox[2] - text_bbox[0] #x2 - x1
                            text_height = text_bbox[3] - text_bbox[1] #y2 - y1

                            draw.rectangle([bbox[0], bbox[1], bbox[0] + text_width + 8, bbox[1] + text_height + 4], 
                                            outline = box_color, fill=box_color)
                            
                            draw.text((bbox[0] + 4, bbox[1] + 2), label, fill="white", font=font)

                meta_items = [f"{k}: {v}" for k, v in result['class_counts'].items() if k in search_params["selected_classes"]]
                        
                # Display card with image and metadata overlay
                st.markdown(f"""
                <div class="image-card">
                    <div class="image-container">
                        <img src="data:image/png;base64,{img_to_base64(img)}">
                    </div>
                    <div class="meta-overlay">
                        <strong>{Path(result['image_path']).name}</strong><br>
                        {", ".join(meta_items) if meta_items else "No matches"}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error loading image {result['image_path']}: {str(e)}")

        col.index = (col.index + 1) % st.session_state.grid_columns

    with st.expander("Export Search Results Metadata"):
        st.download_button(
            label="Download Metadata as JSON",
            data=json.dumps(results, indent=4),
            file_name="search_results_metadata.json",
            mime="application/json"
        )