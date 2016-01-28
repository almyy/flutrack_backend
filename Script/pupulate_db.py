from pymongo import MongoClient
import requests

client = MongoClient()
db = client.flutrack_db
collection = db.tweets