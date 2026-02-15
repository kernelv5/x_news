from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

XAccountType = Literal["Blogger", "Official", "Ancore", "WebSites", "Others"]

class XAccount(BaseModel):
    """X Account Model"""
    x_account: str = Field(..., description="Twitter username (case sensitive)")
    x_account_id: Optional[str] = Field(None, description="Twitter user ID from API")
    x_account_type: XAccountType = Field("Blogger", description="Account type")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(True, description="Whether account is active for crawling")

class XAccountCreate(BaseModel):
    """Create X Account Request"""
    x_account: str = Field(..., description="Twitter username (case sensitive)")
    x_account_type: XAccountType = Field("Blogger", description="Account type")

class XAccountUpdate(BaseModel):
    """Update X Account Request"""
    x_account_type: Optional[XAccountType] = None
    is_active: Optional[bool] = None

class XAccountResponse(BaseModel):
    """X Account Response"""
    id: str
    x_account: str
    x_account_id: Optional[str]
    x_account_type: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
