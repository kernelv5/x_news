import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId
from datetime import datetime

from database import Database, get_x_account_collection, get_source_twitter_collection
from models import XAccount, XAccountCreate, XAccountUpdate, XAccountResponse
from twitter_api import TwitterAPI

# Twitter Bearer Token from environment (required)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not TWITTER_BEARER_TOKEN:
    raise ValueError("TWITTER_BEARER_TOKEN environment variable is required")

app = FastAPI(title="eNewPaper Twitter Crawler API")

# CORS middleware - allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Twitter API
twitter_api = TwitterAPI(TWITTER_BEARER_TOKEN)

@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup"""
    Database.connect_db()
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    Database.close_db()
    print("Disconnected from MongoDB")

@app.get("/")
async def root():
    return {"message": "eNewPaper Twitter Crawler API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    try:
        # Check MongoDB connection
        db = Database.get_database()
        db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

@app.post("/api/accounts", response_model=XAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account: XAccountCreate):
    """
    Create a new X account and fetch its ID from Twitter API
    """
    collection = get_x_account_collection()
    
    # Check if account already exists
    existing = collection.find_one({"x_account": account.x_account})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account @{account.x_account} already exists"
        )
    
    # Fetch Twitter user ID from API
    user_data = await twitter_api.get_user_id_by_username(account.x_account)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Twitter account @{account.x_account} not found"
        )
    
    # Create account document
    account_doc = {
        "x_account": account.x_account,
        "x_account_id": user_data["id"],
        "x_account_type": account.x_account_type,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    }
    
    result = collection.insert_one(account_doc)
    account_doc["_id"] = result.inserted_id
    
    return XAccountResponse(
        id=str(account_doc["_id"]),
        x_account=account_doc["x_account"],
        x_account_id=account_doc["x_account_id"],
        x_account_type=account_doc["x_account_type"],
        created_at=account_doc["created_at"],
        updated_at=account_doc["updated_at"],
        is_active=account_doc["is_active"]
    )

@app.get("/api/accounts", response_model=List[XAccountResponse])
async def list_accounts():
    """
    List all X accounts
    """
    collection = get_x_account_collection()
    accounts = list(collection.find())
    
    return [
        XAccountResponse(
            id=str(acc["_id"]),
            x_account=acc["x_account"],
            x_account_id=acc.get("x_account_id"),
            x_account_type=acc.get("x_account_type", "Manual Entry"),
            created_at=acc["created_at"],
            updated_at=acc["updated_at"],
            is_active=acc.get("is_active", True)
        )
        for acc in accounts
    ]

@app.get("/api/accounts/{account_id}", response_model=XAccountResponse)
async def get_account(account_id: str):
    """
    Get specific X account by ID
    """
    collection = get_x_account_collection()
    
    try:
        account = collection.find_one({"_id": ObjectId(account_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return XAccountResponse(
        id=str(account["_id"]),
        x_account=account["x_account"],
        x_account_id=account.get("x_account_id"),
        x_account_type=account.get("x_account_type", "Manual Entry"),
        created_at=account["created_at"],
        updated_at=account["updated_at"],
        is_active=account.get("is_active", True)
    )

@app.put("/api/accounts/{account_id}", response_model=XAccountResponse)
async def update_account(account_id: str, update: XAccountUpdate):
    """
    Update X account type or active status
    """
    collection = get_x_account_collection()

    try:
        obj_id = ObjectId(account_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )

    fields = {k: v for k, v in update.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    fields["updated_at"] = datetime.utcnow()
    result = collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": fields},
        return_document=True
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    return XAccountResponse(
        id=str(result["_id"]),
        x_account=result["x_account"],
        x_account_id=result.get("x_account_id"),
        x_account_type=result.get("x_account_type", "Blogger"),
        created_at=result["created_at"],
        updated_at=result["updated_at"],
        is_active=result.get("is_active", True)
    )


@app.delete("/api/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str):
    """
    Delete X account
    """
    collection = get_x_account_collection()
    
    try:
        result = collection.delete_one({"_id": ObjectId(account_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return None

@app.get("/api/accounts/{account_id}/tweets")
async def get_account_tweets(account_id: str, max_results: int = 10):
    """
    Fetch tweets from a specific account and store in source-twitter collection
    """
    accounts_collection = get_x_account_collection()
    tweets_collection = get_source_twitter_collection()
    
    try:
        account = accounts_collection.find_one({"_id": ObjectId(account_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if not account.get("x_account_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account does not have Twitter ID"
        )
    
    tweets_data = await twitter_api.get_user_tweets(account["x_account_id"], max_results)
    
    if not tweets_data or "data" not in tweets_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not fetch tweets"
        )
    
    # Store tweets in source-twitter collection
    stored_count = 0
    for tweet in tweets_data.get("data", []):
        tweet_doc = {
            "tweet_id": tweet["id"],
            "text": tweet["text"],
            "created_at": tweet.get("created_at"),
            "x_account": account["x_account"],
            "x_account_id": account["x_account_id"],
            "public_metrics": tweet.get("public_metrics", {}),
            "fetched_at": datetime.utcnow()
        }
        
        # Upsert to avoid duplicates
        tweets_collection.update_one(
            {"tweet_id": tweet["id"]},
            {"$set": tweet_doc},
            upsert=True
        )
        stored_count += 1
    
    return {
        "message": f"Fetched and stored {stored_count} tweets",
        "account": account["x_account"],
        "tweets": tweets_data
    }

@app.post("/api/crawl/all")
async def crawl_all_active_accounts():
    """
    Crawl tweets from all active accounts
    """
    accounts_collection = get_x_account_collection()
    active_accounts = list(accounts_collection.find({"is_active": True}))
    
    results = []
    for account in active_accounts:
        try:
            tweets_data = await twitter_api.get_user_tweets(account["x_account_id"], 10)
            if tweets_data and "data" in tweets_data:
                tweet_count = len(tweets_data["data"])
                results.append({
                    "account": account["x_account"],
                    "status": "success",
                    "tweets_fetched": tweet_count
                })
            else:
                results.append({
                    "account": account["x_account"],
                    "status": "no_tweets",
                    "tweets_fetched": 0
                })
        except Exception as e:
            results.append({
                "account": account["x_account"],
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_accounts": len(active_accounts),
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
