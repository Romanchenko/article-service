import os

import pymongo

mongo_user = os.getenv('MONGO_USER')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_address = os.getenv('MONGO_ADDRESS')
# Replace the uri string with your MongoDB deployment's connection string.
conn_str = f"mongodb://{mongo_user}:{mongo_password}@{mongo_address}"
# set a 5-second connection timeout
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000, uuidRepresentation='standard')
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to the server.")

