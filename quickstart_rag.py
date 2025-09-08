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

questions = client.collections.use("Question")

response = questions.generate.near_text(
    query="biology",
    limit=2,
    grouped_task="Write a tweet with emojis about these facts."
)

print(response.generative.text)  # Inspect the generated text

client.close()  # Free up resources