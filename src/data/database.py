import os

from pymongo import AsyncMongoClient
from dotenv import load_dotenv

load_dotenv()
client=None
db=None

async def connect_to_mongo():
    global client,db

    db_name=os.getenv("MONGO_DB_NAME")
    uri=os.getenv("MONGO_URI")

    if not uri or not db_name:
        raise Exception ( "mongo uri not set")

    client=AsyncMongoClient(
        uri
    )

    await client.admin.command({"ping":1})

    db=client[db_name]

async def close_mongo():
    if client:
        client.close()