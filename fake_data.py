import openai
import psycopg2
import json
from dotenv import load_dotenv
load_dotenv()
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

courses = [
    {
        "content": "Data Science Bootcamp: Learn Python, Pandas, and Machine Learning fundamentals.",
        "metadata": {
            "title": "Data Science Bootcamp",
            "domain": "Data Science",
            "level": "Beginner",
            "duration": "8 weeks",
            "source": "Coursera"
        }
    },
    # add more...
]

conn = psycopg2.connect("postgresql://postgres:Cabbage123!@db.dalwxdmhpaxngzjvkhfc.supabase.co:5432/postgres")
cur = conn.cursor()

for course in courses:
    response = openai.Embedding.create(
        input=course["content"],
        model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]
    cur.execute("""
        INSERT INTO documents (content, embedding, metadata)
        VALUES (%s, %s, %s)
    """, (course["content"], embedding, json.dumps(course["metadata"])))

conn.commit()
cur.close()
conn.close()
