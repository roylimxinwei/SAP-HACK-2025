import weaviate
from weaviate.classes.init import Auth
import requests, json, os
from dotenv import load_dotenv
load_dotenv()
import os

# Best practice: store your credentials in environment variables
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,                                    # Replace with your Weaviate Cloud URL
    auth_credentials=Auth.api_key(weaviate_api_key),             # Replace with your Weaviate Cloud key
)

# Step 2: Load sample data
with open("sap_learning_catalog.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# If from a URL:
# resp = requests.get("https://yoururl.com/sample_data.json")
# data = json.loads(resp.text)

# Define helper function BEFORE using it
def to_list(val):
    if isinstance(val, str) and "," in val:
        return [item.strip() for item in val.split(",")]
    elif isinstance(val, str):
        return [val.strip()]
    return val  # return as-is (e.g. if already list or None)

# Step 3: Use the "Course" collection
courses = client.collections.use("Course")

# Step 4: Batch import data
with courses.batch.fixed_size(batch_size=200) as batch:
    for d in data:
        batch.add_object(
            properties={
                "LSC_product": d.get("LSC_product"),
                "LSC_product_category": d.get("LSC_product_category"),
                "LSC_product_subcategory": d.get("LSC_product_subcategory"),
                "Role": d.get("Role"),
                "Description": d.get("Description", ""),
                "Title": d.get("Title"),
                "Duration_in_hours": float(d.get("Duration_in_hours", 0)),
                "Level": d.get("Level"),
                "Learning_object_ID": d.get("Learning_object_ID"),
                "Learning_type": d.get("Learning_type"),
                "Learning_objectives": d.get("Learning_objectives", ""),
                "Direct_link": d.get("Direct_link", {}).get("hyperlink"),
                "Content_available_from": d.get("Content_available_from"),
            }
        )

        # Optional early stop if too many errors
        if batch.number_errors > 10:
            print("Batch import stopped due to excessive errors.")
            break

# Step 5: Check for any failed imports
failed_objects = courses.batch.failed_objects
if failed_objects:
    print(f"Number of failed imports: {len(failed_objects)}")
    print("First failed object:", failed_objects[0])

print("Data import completed.")

client.close()  # Free up resources