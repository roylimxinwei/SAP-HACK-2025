import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
from dotenv import load_dotenv
load_dotenv()
import os

# Best practice: store your credentials in environment variables
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)

print(client.is_ready())  # Should print: `True`

courses = client.collections.create(
    name="Course",
    vector_config=Configure.Vectors.text2vec_weaviate(), # Configure the Weaviate Embeddings integration
    generative_config=Configure.Generative.cohere()             # Configure the Cohere generative AI integration
)

print("Courses collection created successfully.")

client.close()  # Free up resources