"""Dynamic pricing module for Spend Hawk SDK."""
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError


# Hardcoded fallback pricing (per 1K tokens)
FALLBACK_PRICING = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
    },
    "anthropic": {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
    },
    "google": {
        "gemini-pro": {"input": 0.0005, "output": 0.0015},
        "gemini-pro-vision": {"input": 0.0025, "output": 0.0075},
        "gemini-1.5-pro": {"input": 0.00075, "output": 0.003},
        "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    }
}

# Cache configuration
CACHE_DIR = Path.home() / ".spend_hawk"
CACHE_FILE = CACHE_DIR / "pricing.json"
CACHE_TTL_DAYS = 7
PRICING_API_URL = "https://spendhawk-backend.vercel.app/api/v1/pricing"

# Global pricing cache
_pricing_cache: Optional[Dict] = None
_cache_loaded_at: Optional[float] = None


def _ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _fetch_pricing_from_backend() -> Optional[Dict]:
    """
    Fetch pricing data from backend API.
    
    Returns:
        Dict of pricing data, or None if fetch fails
    """
    try:
        req = Request(PRICING_API_URL, headers={"User-Agent": "spend-hawk-sdk/0.1.2"})
        with urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data
    except (URLError, json.JSONDecodeError, Exception):
        pass
    
    return None


def _save_pricing_to_cache(pricing: Dict):
    """
    Save pricing data to local cache file.
    
    Args:
        pricing: Pricing data to cache
    """
    try:
        _ensure_cache_dir()
        cache_data = {
            "pricing": pricing,
            "cached_at": time.time()
        }
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        pass  # Fail silently if cache write fails


def _load_pricing_from_cache() -> Optional[Dict]:
    """
    Load pricing data from local cache if not expired.
    
    Returns:
        Dict of pricing data, or None if cache is invalid/expired
    """
    try:
        if not CACHE_FILE.exists():
            return None
        
        with open(CACHE_FILE, "r") as f:
            cache_data = json.load(f)
        
        cached_at = cache_data.get("cached_at", 0)
        age_seconds = time.time() - cached_at
        age_days = age_seconds / (24 * 3600)
        
        # Check if cache is still valid
        if age_days < CACHE_TTL_DAYS:
            return cache_data.get("pricing")
    except Exception:
        pass
    
    return None


def init_pricing():
    """
    Initialize pricing data on SDK startup.
    
    Tries in order:
    1. Fetch from backend API
    2. Load from local cache (if < 7 days old)
    3. Use hardcoded fallback
    
    This is called automatically on first use.
    """
    global _pricing_cache, _cache_loaded_at
    
    if _pricing_cache is not None:
        return  # Already initialized
    
    # Try to fetch from backend
    pricing = _fetch_pricing_from_backend()
    if pricing:
        _pricing_cache = pricing
        _cache_loaded_at = time.time()
        _save_pricing_to_cache(pricing)
        return
    
    # Try to load from cache
    pricing = _load_pricing_from_cache()
    if pricing:
        _pricing_cache = pricing
        _cache_loaded_at = time.time()
        return
    
    # Fall back to hardcoded pricing
    _pricing_cache = {}
    for provider, models in FALLBACK_PRICING.items():
        for model, prices in models.items():
            _pricing_cache[model] = prices
    _cache_loaded_at = time.time()


def get_pricing() -> Dict:
    """
    Get current pricing data.
    
    Returns:
        Dict mapping model name to {"input": float, "output": float}
    """
    if _pricing_cache is None:
        init_pricing()
    
    return _pricing_cache or {}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost for an API call.
    
    Args:
        model: Model name (e.g., "gpt-4", "claude-3-opus-20240229")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Cost in USD
    """
    pricing = get_pricing()
    model_pricing = pricing.get(model, {})
    
    if not model_pricing:
        return 0.0
    
    # Pricing is per 1K tokens
    input_cost = (input_tokens / 1000) * model_pricing.get("input", 0)
    output_cost = (output_tokens / 1000) * model_pricing.get("output", 0)
    
    return round(input_cost + output_cost, 6)


def refresh_pricing():
    """
    Force refresh pricing data from backend.
    
    This bypasses the cache and fetches fresh data from the API.
    """
    global _pricing_cache, _cache_loaded_at
    
    pricing = _fetch_pricing_from_backend()
    if pricing:
        _pricing_cache = pricing
        _cache_loaded_at = time.time()
        _save_pricing_to_cache(pricing)
        return True
    
    return False
