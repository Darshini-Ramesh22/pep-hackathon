"""
Configuration settings for Campaign Brain
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env (local development)
load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """
    Retrieve a secret from Streamlit secrets (Streamlit Cloud) or
    fall back to environment variables (local / other deployments).
    """
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


# Clear any system proxy variables that might interfere with the OpenAI client
# This is needed because the OpenAI SDK may try to use them incorrectly
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

class Config:
    """Configuration class for Campaign Brain agents"""
    
    # AI Gateway Configuration (using your company's gateway)
    API_KEY = _get_secret("AI_GATEWAY_API_KEY", "sk-samplekey123")
    BASE_URL = "https://api.ai-gateway.tigeranalytics.com"
    MODEL_NAME = "gemini-2.5-flash"
    
    # Agent Configuration
    MAX_ITERATIONS = 10
    TIMEOUT_SECONDS = 300
    
    # Database Configuration (if using SQL tools)
    DATABASE_URL = _get_secret("DATABASE_URL", "sqlite:///campaign_data.db")
    
    # Data Sources
    SOCIAL_MEDIA_APIS = {
        "twitter": _get_secret("TWITTER_API_KEY"),
        "instagram": _get_secret("INSTAGRAM_API_KEY"),
        "linkedin": _get_secret("LINKEDIN_API_KEY"),
    }
    
    # Campaign Settings
    DEFAULT_CAMPAIGN_DURATION_DAYS = 30
    MIN_BUDGET = 1000
    MAX_BUDGET = 1000000
    
    # Trend Analysis
    TREND_SOURCES = [
        "google_trends",
        "social_media",
        "news_sentiment",
        "market_research"
    ]
    
    @classmethod
    def get_openai_client(cls):
        """Get configured OpenAI client for your company's gateway"""
        import openai
        
        try:
            print(f"🔧 Initializing OpenAI client with base_url: {cls.BASE_URL}")
            print(f"🔧 Using model: {cls.MODEL_NAME}")
            
            # Create the OpenAI client with explicit parameters
            # Use httpx client to avoid proxy issues
            try:
                import httpx
                
                # Create a custom HTTP client that explicitly disables proxies
                http_client = httpx.Client(
                    #proxies=None,  # Explicitly disable proxies
                    verify=False   # For development/testing purposes
                )
                
                client = openai.OpenAI(
                    api_key=cls.API_KEY,
                    base_url=cls.BASE_URL,
                    http_client=http_client,
                    timeout=300.0
                )
                print("✅ OpenAI client initialized successfully (with custom HTTP client)")
                return client
                
            except ImportError:
                # If httpx is not available, try without custom client
                print("⚠️  httpx not available, using default client configuration")
                client = openai.OpenAI(
                    api_key=cls.API_KEY,
                    base_url=cls.BASE_URL,
                    timeout=300.0
                )
                print("✅ OpenAI client initialized successfully")
                return client
            
        except TypeError as e:
            print(f"❌ Error initializing OpenAI client: {str(e)}")
            print(f"   File: config.py")
            print(f"   Method: Config.get_openai_client()")
            print(f"   Error details: {str(e)}")
            raise