import httpx
from typing import Optional, Dict
from urllib.parse import unquote

class TwitterAPI:
    """Twitter API Integration - Official Twitter API v2"""
    
    def __init__(self, bearer_token: str):
        # Use the token as-is (do not decode)
        self.bearer_token = bearer_token
        self.base_url = "https://api.x.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "eNewPaper/1.0"
        }
        print(f"[DEBUG] Twitter API initialized")
        print(f"[DEBUG] Token length: {len(self.bearer_token)}")
        print(f"[DEBUG] Token starts with: {self.bearer_token[:20]}...")
    
    async def get_user_id_by_username(self, username: str) -> Optional[Dict]:
        """
        Fetch Twitter user ID by username
        Official API: GET https://api.x.com/2/users/by/username/:username
        Documentation: https://docs.x.com/x-api/users/lookup/introduction
        """
        url = f"{self.base_url}/users/by/username/{username}"
        
        print(f"[DEBUG] Requesting URL: {url}")
        print(f"[DEBUG] Headers: Authorization: Bearer {self.bearer_token[:20]}...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                print(f"[DEBUG] Response status: {response.status_code}")
                print(f"[DEBUG] Response body: {response.text[:500]}")
                response.raise_for_status()
                data = response.json()
                
                if "data" in data:
                    return {
                        "id": data["data"]["id"],
                        "username": data["data"]["username"],
                        "name": data["data"].get("name")
                    }
                return None
        except httpx.HTTPError as e:
            print(f"[ERROR] HTTP Error: {e}")
            print(f"[ERROR] Response: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
            return None
    
    async def get_user_tweets(self, user_id: str, max_results: int = 10) -> Optional[Dict]:
        """
        Fetch user's recent tweets
        Official API: GET https://api.x.com/2/users/:id/tweets
        Documentation: https://docs.x.com/x-api/posts/lookup/introduction
        """
        url = f"{self.base_url}/users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,text"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching tweets: {e}")
            return None
