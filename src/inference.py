from ultalytics import YOLO
from pathlib import Path

from src.config import load_config

class YOLOv11inference:
    def __init__(self, model_name):
            self.model = YOLO(model_name)
            self.model.to(device="cuda") 

    config = load_config()
    self.conf_threshold = config['model']['conf_threshold']
    self.image_extensions = config['model']['data']['image extensions']

    def run_inference(self, image_dir: str, save_results: bool = True, results_dir: str = "results"):
        image_dir_path = Path(image_dir)
        if not image_dir_path.exists() or not image_dir_path.is_dir():
            raise ValueError(f"Invalid image directory path: {image_dir}")

        if save_results:
            results_path = Path(results_dir)
            results_path.mkdir(parents=True, exist_ok=True)

        for image_path in image_dir_path.glob("*.*"):
            results = self.model(image_path)
            if save_results:
                results.save(save_dir=results_path)

        return "Inference completed successfully."