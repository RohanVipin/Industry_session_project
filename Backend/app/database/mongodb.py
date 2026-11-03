from pymongo import MongoClient

MONGO_URL = "mongodb://127.0.0.1:27017"

client = MongoClient(MONGO_URL)

database = client["Customer_churn_db"]

users_collection = database["users"]
predictions_collection = database["predictions"]
customers_collection = database["customers"]