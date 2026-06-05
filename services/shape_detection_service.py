import cv2
import numpy as np
from typing import Dict, List
import os

def detect_architectural_shapes(image_path: str, debug: bool = False) -> Dict[str, int]:
    """
    Scans a floor plan image using OpenCV to visually count architectural symbols.
    Currently detects:
      - Columns: Small, solid, dense squares/rectangles.
      - Doors: Arcs/curves that have low solidity but square bounding boxes.
    """
    if not os.path.exists(image_path):
        return {"columns": 0, "doors": 0}
        
    try:
        # 1. Load image and convert to grayscale
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Thresholding to isolate black lines/symbols from white background
        # Since architectural plans usually have dark lines on light background
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        
        # 3. Detect Columns (Solid Squares)
        # We apply morphological closing to fill in any tiny gaps in columns
        kernel_col = np.ones((5, 5), np.uint8)
        closed_for_cols = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_col)
        
        col_contours, _ = cv2.findContours(closed_for_cols, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        column_count = 0
        door_count = 0
        
        # Determine image scale to define realistic areas
        h, w = gray.shape
        total_area = h * w
        
        # Expected column size on a high-res plan is usually tiny but visible
        # E.g., area between 0.0001% and 0.01% of total image
        min_col_area = total_area * 0.00005
        max_col_area = total_area * 0.005
        
        for cnt in col_contours:
            area = cv2.contourArea(cnt)
            if min_col_area < area < max_col_area:
                x, y, w_box, h_box = cv2.boundingRect(cnt)
                aspect_ratio = float(w_box) / h_box
                
                # Columns are usually square or slightly rectangular (0.5 to 2.0)
                if 0.5 <= aspect_ratio <= 2.0:
                    hull = cv2.convexHull(cnt)
                    hull_area = cv2.contourArea(hull)
                    
                    if hull_area > 0:
                        solidity = float(area) / hull_area
                        # Columns are solid filled blocks, so solidity should be high (> 0.8)
                        if solidity > 0.8:
                            column_count += 1
                            
        # 4. Detect Doors (Arcs)
        # Doors are usually drawn as quarter-circle arcs with lines
        # They have larger bounding boxes than columns, but are mostly empty space (low solidity)
        kernel_door = np.ones((2, 2), np.uint8)
        dilated_for_doors = cv2.dilate(thresh, kernel_door, iterations=1)
        door_contours, _ = cv2.findContours(dilated_for_doors, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        min_door_area = total_area * 0.0005
        max_door_area = total_area * 0.02
        
        for cnt in door_contours:
            area = cv2.contourArea(cnt)
            if min_door_area < area < max_door_area:
                x, y, w_box, h_box = cv2.boundingRect(cnt)
                aspect_ratio = float(w_box) / h_box
                
                # Door swings typically bound a square-ish area (the quarter circle)
                if 0.7 <= aspect_ratio <= 1.3:
                    hull = cv2.convexHull(cnt)
                    hull_area = cv2.contourArea(hull)
                    
                    if hull_area > 0:
                        solidity = float(area) / hull_area
                        # Doors are thin lines bounding a square area, so solidity is VERY low (< 0.3)
                        # but they take up a noticeable footprint.
                        if solidity < 0.35:
                            door_count += 1

        # Because these are heuristics, we apply a realistic upper bound 
        # based on standard building physics to avoid runaway false positives.
        if column_count > 40: 
            column_count = int(column_count * 0.3) # Heavy suppression if it misread a grid
        if door_count > 30:
            door_count = int(door_count * 0.3)

        return {
            "columns": column_count,
            "doors": door_count
        }
        
    except Exception as e:
        print(f"Shape detection failed for {image_path}: {e}")
        return {"columns": 0, "doors": 0}
