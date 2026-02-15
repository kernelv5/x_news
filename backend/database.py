import os
from pymongo import MongoClient
from typing import Optional

class Database:
    client: Optional[MongoClient] = None
    
    @classmethod
    def connect_db(cls):
        """Connect to MongoDB"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        cls.client = MongoClient(mongodb_url)
        return cls.client
    
    @classmethod
    def get_database(cls):
        """Get eNews database"""
        if cls.client is None:
            cls.connect_db()
        db_name = os.getenv("MONGODB_DB", "eNews")
        return cls.client[db_name]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get specific collection"""
        db = cls.get_database()
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
        return db[collection_name]
    
    @classmethod
    def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()

def get_x_account_collection():
    """Get x_account collection"""
    return Database.get_collection("x_account")

def get_source_twitter_collection():
    """Get source-twitter collection for storing tweets"""
    return Database.get_collection("source-twitter")
