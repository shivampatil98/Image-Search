from pathlib import Path
import json

# Utility functions for handling file paths and saving metadata
def ensure_processed_dir(raw_path):
    raw_path = Path(raw_path) # Convert to Path object if not already
    processed_path = raw_path.parent.parent/"processed"/raw_path.name # Define processed directory path
    processed_path.mkdir(parent=True, exist_ok=True) # Create directory if it doesn't exist
    return processed_path

# Function to save metadata as a JSON file
def save_metadata(metadata, raw_path):
    
    processed_path = ensure_processed_dir(raw_path) # Ensure processed directory exists

    output_path = processed_path/"metadata.json" # Define output metadata file path
    
    with open(output_path, 'w') as f: # Open file for writing
        json.dump(metadata, f)
        
    return output_path

def load_metadata(metadata_path):
    metadata_path = Path(metadata_path) 
    if not metadata_path.exists():
        processed_path = metadata_path.parent.parent / "processed" / metadata_path.name / "metadata.json"
        if processed_path.exists():
            metadata_path = processed_path
        else:
            raise FileNotFoundError(f"Metadata file not found at {metadata_path} or {processed_path}")
        
    with open(metadata_path, 'r') as f: # Open file for reading        
        metadata = json.load(f) # Load JSON data

def get_unique_classes_counts(metadata):
    unique_classes = set()
    count_options = {}

    for item in metadata:
        for cls in item['detection']:
            unique_classes.add(cls['class_id'])
            if cls['class_id'] not in count_options:
                count_options[cls['class_id']] = set()
            count_options[cls['class_id']].add(cls['count'])    

    sorted_unique_classes = sorted(unique_classes)
    for cls_id in count_options:
        count_options[cls_id] = sorted(count_options[cls_id])

    return unique_classes, count_options