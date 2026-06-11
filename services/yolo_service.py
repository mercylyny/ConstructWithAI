import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger("yolo_service")

# Try importing ultralytics, handle if not installed yet
try:
    # On Render Free/Starter (512MB RAM), YOLO causes OOM crashes.
    # On Render Standard+ (2GB+ RAM), you CAN enable it.
    # Set YOLO_ENABLED=true in your Render environment variables to activate.
    _yolo_enabled_env = os.environ.get("YOLO_ENABLED", "false").lower()
    
    if _yolo_enabled_env == "true":
        from ultralytics import YOLO
        ULTRALYTICS_AVAILABLE = True
        logger.info("YOLO detection ENABLED (YOLO_ENABLED=true).")
    else:
        ULTRALYTICS_AVAILABLE = False
        logger.info("YOLO detection DISABLED. Set YOLO_ENABLED=true in env vars to activate on Standard+ plan.")
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    logger.warning("ultralytics package not found. YOLO object detection will be disabled.")

class YoloArchitecturalDetector:
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize the YOLO detector. 
        In production, model_path should point to a custom trained architectural model (e.g., yolov8-architectural.pt).
        We use yolov8n.pt as a fallback for structural readiness, though its default COCO classes lack specific architectural elements.
        """
        self.model_path = model_path
        self.model = None
        self.is_custom = "architectural" in model_path.lower()
        
        if ULTRALYTICS_AVAILABLE:
            try:
                # If custom model doesn't exist yet, fallback to yolov8n to prevent crashes
                if not os.path.exists(model_path) and self.is_custom:
                    logger.warning(f"Custom model {model_path} not found. Falling back to yolov8n.pt")
                    self.model = YOLO("yolov8n.pt")
                else:
                    self.model = YOLO(self.model_path)
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")

    def detect_components(self, image_paths: List[str]) -> Dict[str, int]:
        """
        Run YOLO detection on a list of images and aggregate counts for architectural components.
        Expected classes from a custom model: 'door', 'window', 'stairs', 'column'.
        """
        counts = {
            "doors": 0,
            "windows": 0,
            "stairs": 0,
            "columns": 0
        }
        
        if not self.model or not image_paths:
            return counts

        # Map assumed class indices/names for a custom architectural model
        # Adjust these based on the actual trained weights.
        target_classes = {
            "door": "doors",
            "doors": "doors",
            "window": "windows",
            "windows": "windows",
            "stair": "stairs",
            "stairs": "stairs",
            "column": "columns",
            "columns": "columns"
        }

        try:
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    continue
                    
                results = self.model.predict(source=img_path, conf=0.25, save=False, verbose=False)
                
                for r in results:
                    boxes = r.boxes
                    if boxes is None:
                        continue
                        
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        cls_name = self.model.names[cls_id].lower()
                        
                        # Increment matching target classes
                        for key, target in target_classes.items():
                            if key in cls_name:
                                counts[target] += 1
                                break
        except Exception as e:
            logger.error(f"Error during YOLO detection: {e}")

        return counts

# Singleton instance for the service
detector = None

def detect_architectural_components(image_paths: List[str]) -> Dict[str, int]:
    """
    Service wrapper for YOLO architectural detection.
    """
    global detector
    if detector is None:
        detector = YoloArchitecturalDetector(model_path="yolov8-architectural.pt")
    
    return detector.detect_components(image_paths)
