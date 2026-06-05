import requests, os

url = "http://127.0.0.1:8000/upload/plan"
print("Testing URL:", url)

# Create a small dummy file to upload
with open("test_dummy_plan.pdf", "wb") as f:
    f.write(b"Dummy PDF Content")

with open("test_dummy_plan.pdf", "rb") as f:
    files = {"file": ("test_dummy_plan.pdf", f, "application/pdf")}
    data = {"scale": "1:100"}
    
    try:
        response = requests.post(url, files=files, data=data)
        print("Status code:", response.status_code)
        
        try:
            print("Response JSON:", response.json())
        except Exception:
            print("Response Text:", response.text)
            
    except Exception as e:
        print("Request failed:", e)

# Clean up
try:
    os.remove("test_dummy_plan.pdf")
except:
    pass
