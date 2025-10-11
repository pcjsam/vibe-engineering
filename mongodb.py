import os

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient


def fetch_team_members():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")

    if not uri:
        raise ValueError("MONGODB_URI environment variable is not set")

    client = MongoClient(uri, tlsCAFile=certifi.where())

    try:
        database = client.get_database("master")
        collection = database.get_collection("team")

        query = {}
        documents = collection.find(query)

        team_members = []
        for document in documents:
            team_members.append(document["name"])

        return team_members
    except Exception as e:
        raise Exception(f"Error fetching team members: {e}")
    finally:
        client.close()
