import requests
import json
import os

url = "http://127.0.0.1:8000/upload/plan"

# Create a dummy file to upload
dummy_filename = "test_plan.txt"
with open(dummy_filename, "w") as f:
    f.write("This is a dummy construction plan content.")

files = {
    'file': (dummy_filename, open(dummy_filename, 'rb'), 'text/plain')
}
data = {
    'scale': '1:100'
}

print(f"Testing POST {url} with file '{dummy_filename}' and scale '1:100'...")

try:
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("\nSUCCESS! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nFAILED with {response.status_code}:")
        print(response.text)
except Exception as e:
    print(f"\nERROR: {e}")
finally:
    # Cleanup dummy file
    if os.path.exists(dummy_filename):
        os.remove(dummy_filename)
