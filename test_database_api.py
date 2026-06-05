import requests
import json

BASE_URL = "http://127.0.0.1:8000/database"

def test_database():
    print("1. Creating a new project...")
    project_payload = {
        "filename": "test_blueprint.pdf",
        "scale": "1:100"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_payload)
    if response.status_code != 200:
        print(f"Failed to create project: {response.text}")
        return
    project = response.json()
    project_id = project["id"]
    print(f"Success! Project created with ID: {project_id}\n")

    print("2. Adding a wall to the project...")
    wall_payload = {
        "wall_id": "Wall_A",
        "length_m": 12.5,
        "height_m": 3.0,
        "thickness_mm": 200.0,
        "openings_area_m2": 2.5
    }
    response = requests.post(f"{BASE_URL}/projects/{project_id}/walls/", json=wall_payload)
    if response.status_code == 200:
        print(f"Success! Added wall to Project {project_id}\n")
    else:
        print(f"Failed to add wall: {response.text}\n")

    print("3. Fetching the project back to see the relations...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    if response.status_code == 200:
        fetched_project = response.json()
        print("Success! Fetched project data:")
        print(json.dumps(fetched_project, indent=2))
        
if __name__ == "__main__":
    test_database()
