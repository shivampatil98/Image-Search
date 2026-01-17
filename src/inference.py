from ultralytics import YOLO
from pathlib import Path
from src.config import load_config

class YOLOv11inference:
    def __init__(self, model_name, device='cuda'):
        self.model = YOLO(model_name)
        self.device = device
        self.model.to(self.device) 

        # loading config from default.yaml
        config = load_config()
        self.conf_threshold = config['model']['conf_threshold']
        self.image_extensions = config['data']['image extensions']


    def process_image(self, image_path):
      
      # Run inference
        results = self.model.predict(
            source=image_path,
            conf=self.conf_threshold,
            device=self.device
      )

    # process results
        detection = []
        class_counts = {}

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].tolist()
            detection.append({
                'class_id': cls_id,
                'confidence': conf,
                'bbox': bbox,
                #"bbox": box.xyxy[0].tolist()
                'count': 1
            })
            class_counts[cls_id] = class_counts.get(cls_id, 0) + 1

            for det in detection:
                det['count'] = class_counts[det['class_id']]

            return {
            'image_path': str(image_path),
            'detection': detection,
            'total_objects': len(detection),
            'unique_class': list(class_counts.keys()),
            'class_counts': class_counts
            }
    
    def process_directory(self, directory):
        
        metadata = []

        patterns = [f"*{ext}" for ext in self.extensions]

        image_paths = []

        for pattern in patterns:
            image_paths.extend(Path(directory).glob(pattern))

        for image_path in image_paths:
            try:
                metadata.append(self.process_image(image_path))
            except Exception as e:  
                print(f"Error processing {image_path}: {e}")
                continue    
        
        print(metadata)
        return metadata