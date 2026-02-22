"""Configuration module for Spend Hawk SDK."""
import os
from typing import Optional


class Config:
    """Configuration manager for Spend Hawk SDK."""
    
    def __init__(self):
        self.api_key: Optional[str] = os.getenv("SPEND_HAWK_API_KEY")
        self.api_endpoint: str = os.getenv(
            "SPEND_HAWK_API_ENDPOINT", 
            "https://api.spendhawk.com"
        )
        self.project_id: Optional[str] = os.getenv("SPEND_HAWK_PROJECT_ID")
        self.agent: Optional[str] = os.getenv("SPEND_HAWK_AGENT")
        self.enabled: bool = os.getenv("SPEND_HAWK_ENABLED", "true").lower() != "false"
        
    def is_configured(self) -> bool:
        """Check if SDK is properly configured."""
        return self.api_key is not None and self.enabled


# Global config instance
config = Config()
