import requests
import json

BASE_URL = "http://127.0.0.1:8000"
# We assume 'test_pipeline_wall.pdf' was processed in the previous step and images exist.
# If not, this test might need to rely on the user running verify_pdf_pipeline.py first.
# To be safe, we'll try to use a filename we know likely has images or fail gracefully.
FILENAME = "test_pipeline_wall.pdf" 

def test_batch_ocr():
    url = f"{BASE_URL}/analyze/plan/ocr/images"
    payload = {"filename": FILENAME}
    
    print(f"Testing Batch OCR Endpoint: {url}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("\nSUCCESS! Batch OCR Response:")
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Verify text content
            text = data.get("extracted_text", "")
            if "Wall" in text or "Page" in text:
                print("\nTEST PASS: Extracted text contains expected keywords.")
            else:
                 print("\nTEST WARN: Extracted text might be empty or missing keywords.")
        elif response.status_code == 404:
             print(f"\nTEST NOTE: 404 Not Found. This is expected if '{FILENAME}' images haven't been generated yet.")
             print("Please run verify_pdf_pipeline.py first to generate images.")
        else:
            print(f"\nFAILED with {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    test_batch_ocr()
