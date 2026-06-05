import requests
import os
from reportlab.pdfgen import canvas

# Configuration
BASE_URL = "http://127.0.0.1:8000"
PDF_FILENAME = "test_pipeline_wall.pdf"

def generate_test_pdf():
    """Generates a simple PDF with wall text."""
    c = canvas.Canvas(PDF_FILENAME)
    c.drawString(100, 750, "Construction Plan Level 1")
    c.drawString(100, 700, "Wall A length 5.0m")
    c.drawString(100, 650, "Wall B length 3.5m")
    c.drawString(100, 600, "Height 3.0m")
    c.save()
    print(f"Generated {PDF_FILENAME}")

def test_pipeline():
    # 1. Generate PDF
    generate_test_pdf()

    # 2. Upload PDF
    print("\n--- Step 1: Upload PDF ---")
    with open(PDF_FILENAME, "rb") as f:
        files = {"file": (PDF_FILENAME, f, "application/pdf")}
        data = {"scale": "1:100"}
        res = requests.post(f"{BASE_URL}/upload/plan", files=files, data=data)
        if res.status_code == 200:
            print("Upload Success:", res.json())
        else:
            print("Upload Failed:", res.text)
            return

    # 3. Convert PDF to Image
    print("\n--- Step 2: PDF to Image ---")
    res = requests.post(f"{BASE_URL}/analyze/plan/pdf-to-image", json={"filename": PDF_FILENAME})
    if res.status_code == 200:
        data = res.json()
        print("Conversion Success:", data)
        images = data.get("image_paths", [])
        if not images:
            print("No images returned.")
            return
        # Get relative filename of first image
        # The API returns relative paths like "outputs\\pdf_images\\...png"
        # We need just the filename for the OCR endpoint if we are relying on it finding it in outputs.
        # But wait, OCR endpoint takes "filename". It looks in UPLOADS first, then OUTPUTS/PDF_IMAGES.
        # So we can pass the basename.
        full_path = images[0] # e.g. outputs/pdf_images/test_pipeline_wall_page_1.png
        image_filename = os.path.basename(full_path) 
        print(f"Selected Image for OCR: {image_filename}")
    else:
        print("Conversion Failed:", res.text)
        return

    # 4. Perform OCR on the Image
    print(f"\n--- Step 3: OCR on {image_filename} ---")
    res = requests.post(f"{BASE_URL}/analyze/plan/ocr", json={"filename": image_filename})
    if res.status_code == 200:
        data = res.json()
        text = data.get("extracted_text", "")
        print("OCR Success. Extracted Text Snippet:", text[:50] + "...")
    else:
        print("OCR Failed:", res.text)
        return

    # 5. AI Interpret (using the OCR'd text)
    print(f"\n--- Step 4: AI Interpretation on {image_filename} ---")
    res = requests.post(f"{BASE_URL}/ai/interpret/ocr", json={"filename": image_filename})
    if res.status_code == 200:
        data = res.json()
        print("AI Interpretation Success:", data)
        walls = data.get("interpreted_data", {}).get("walls", [])
        if len(walls) >= 2:
            print("PASS: Detected expected walls.")
        else:
            print(f"WARN: Detected {len(walls)} walls, expected 2.")
    else:
        print("AI Interpretation Failed:", res.text)

if __name__ == "__main__":
    try:
        test_pipeline()
    finally:
        # Cleanup
        if os.path.exists(PDF_FILENAME):
            os.remove(PDF_FILENAME)
