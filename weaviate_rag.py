import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv
load_dotenv()
import os

# Best practice: store your credentials in environment variables
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
cohere_api_key = os.getenv("COHERE_APIKEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,                                    # Replace with your Weaviate Cloud URL
    auth_credentials=Auth.api_key(weaviate_api_key),             # Replace with your Weaviate Cloud key
    headers={"X-Cohere-Api-Key": cohere_api_key},           # Replace with your Cohere API key
)

courses = client.collections.use("Course")

response = courses.generate.near_text(
    query="data science",
    limit=3,
    grouped_task="Provide the title and product name as well as the direct link to the product page for these facts."
)

print(response.generative.text)  # Inspect the generated text

client.close()  # Free up resources