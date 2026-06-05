import cv2
import numpy as np
import math
import os
from typing import List, Dict, Any

def extract_geometry_from_image(image_path: str, scale_px_per_m: float = 100.0) -> Dict[str, Any]:
    """
    Extracts wall geometry from an architectural plan image using OpenCV.
    Identifies walls as parallel line pairs and rooms as closed shapes.
    """
    if not image_path or not os.path.exists(image_path):
        return {
            "walls": [],
            "detected_rooms": 0,
            "scale_confidence": 0.0,
            "geometry_quality": "POOR",
            "error": "Image not found"
        }

    # 1. Load Image
    img = cv2.imread(image_path)
    if img is None:
        return {"walls": [], "detected_rooms": 0, "scale_confidence": 0.0, "geometry_quality": "POOR"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Edge Detection
    # Use Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # 3. Line Detection (Hough Transform)
    # Using HoughLinesP for segment detection
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    
    wall_candidates = []
    if lines is not None:
        # Group lines by orientation (Horizontal/Vertical)
        h_lines = []
        v_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            
            if dx > dy * 5: # Horizontal-ish
                h_lines.append(line[0])
            elif dy > dx * 5: # Vertical-ish
                v_lines.append(line[0])

        # 4. Pair Parallel Lines (Walls)
        # For simplicity, we look for pairs of horizontal/vertical lines with "small" gap
        # Distance threshold for thickness (e.g. 8px to 60px for various wall thicknesses)
        thickness_range = (8, 60)  # Expanded range to catch more walls 
        
        detected_walls = []
        
        # Helper to find pairs
        def find_pairs(segments, is_horizontal=True):
            pairs = []
            used = set()
            sorted_segs = sorted(segments, key=lambda x: x[1] if is_horizontal else x[0])
            
            for i in range(len(sorted_segs)):
                if i in used: continue
                for j in range(i + 1, len(sorted_segs)):
                    if j in used: continue
                    
                    s1 = sorted_segs[i]
                    s2 = sorted_segs[j]
                    
                    # Distance between lines
                    dist = abs(s1[1] - s2[1]) if is_horizontal else abs(s1[0] - s2[0])
                    
                    if thickness_range[0] <= dist <= thickness_range[1]:
                        # Check overlap (crudely)
                        overlap = False
                        if is_horizontal:
                            # x-ranges should overlap significantly
                            max_start = max(s1[0], s2[0])
                            min_end = min(s1[2], s2[2])
                            if min_end - max_start > 30: # at least 30px overlap
                                overlap = True
                        else:
                            # y-ranges should overlap
                            max_start = max(s1[1], s2[1])
                            min_end = min(s1[3], s2[3])
                            if min_end - max_start > 30:
                                overlap = True
                                
                        if overlap:
                            pairs.append((s1, s2, dist))
                            used.add(i)
                            used.add(j)
                            break
            return pairs

        h_pairs = find_pairs(h_lines, is_horizontal=True)
        v_pairs = find_pairs(v_lines, is_horizontal=False)
        
        # Construct Wall Objects
        for idx, (p1, p2, dist) in enumerate(h_pairs + v_pairs):
            wall_id = f"W{idx+1}"
            # Length is average of segments
            if dist in [p[2] for p in h_pairs]: # Horizontal
                length_px = (abs(p1[2] - p1[0]) + abs(p2[2] - p2[0])) / 2
            else: # Vertical
                length_px = (abs(p1[3] - p1[1]) + abs(p2[3] - p2[1])) / 2
                
            length_m = round(length_px / scale_px_per_m, 2)
            # Infer thickness category (e.g. 150mm, 200mm, 300mm)
            raw_thickness_mm = (dist / scale_px_per_m) * 1000
            
            # Snap to common sizes
            common_sizes = [100, 150, 200, 230, 300, 400]
            thickness_mm = min(common_sizes, key=lambda x: abs(x - raw_thickness_mm))
            
            detected_walls.append({
                "wall_id": wall_id,
                "length_m": length_m,
                "thickness_mm": thickness_mm,
                "confidence": 0.85 if dist < 30 else 0.7,
                "source": "geometry"
            })
            
        # 5. Room Detection (Contours)
        # Dilate edges to close small gaps
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)  # Increased iterations
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        rooms = 0
        min_room_area = 3000  # Reduced threshold to catch smaller rooms
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter by area and perimeter to avoid noise
            perimeter = cv2.arcLength(cnt, True)
            if area > min_room_area and perimeter > 100:  # Added perimeter filter
                rooms += 1

        quality = "GOOD" if len(detected_walls) > 5 else "FAIR" if len(detected_walls) > 0 else "POOR"
        
        return {
            "walls": detected_walls,
            "detected_rooms": rooms,
            "scale_confidence": 0.8 if scale_px_per_m == 100.0 else 0.5,
            "geometry_quality": quality
        }

    return {
        "walls": [],
        "detected_rooms": 0,
        "scale_confidence": 0.0,
        "geometry_quality": "POOR"
    }
