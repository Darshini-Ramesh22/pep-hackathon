"""
Data Loader for Campaign Brain - Load data from various sources
"""
import pandas as pd
import requests
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class DataLoader:
    """
    Tool for loading data from various sources including
    social media APIs, CSV files, and external data sources.
    """
    
    def __init__(self):
        self.api_keys = Config.SOCIAL_MEDIA_APIS
    
    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            print(f"✅ Loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            print(f"❌ Error loading CSV: {str(e)}")
            return pd.DataFrame()
    
    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Loaded JSON data from {file_path}")
            return data
        except Exception as e:
            print(f"❌ Error loading JSON: {str(e)}")
            return {}
    
    def load_sample_campaign_data(self) -> List[Dict[str, Any]]:
        """Load sample campaign data for testing"""
        sample_campaigns = [
            {
                "name": "Summer Product Launch",
                "objective": "Increase brand awareness and drive product sales",
                "target_audience": "Young professionals aged 25-35",
                "budget": 50000,
                "duration_days": 30,
                "channels": ["Social Media", "Google Ads", "Email"],
                "performance_metrics": [
                    {"channel": "Social Media", "metric": "engagement_rate", "value": 0.045},
                    {"channel": "Social Media", "metric": "reach", "value": 125000},
                    {"channel": "Google Ads", "metric": "ctr", "value": 0.032},
                    {"channel": "Email", "metric": "open_rate", "value": 0.28}
                ]
            },
            {
                "name": "Holiday Sales Campaign",
                "objective": "Drive seasonal sales and customer acquisition",
                "target_audience": "Families with children, aged 30-50",
                "budget": 75000,
                "duration_days": 45,
                "channels": ["TV", "Social Media", "Influencer Marketing"],
                "performance_metrics": [
                    {"channel": "TV", "metric": "brand_lift", "value": 0.18},
                    {"channel": "Social Media", "metric": "conversion_rate", "value": 0.024},
                    {"channel": "Influencer", "metric": "engagement_rate", "value": 0.067}
                ]
            },
            {
                "name": "B2B Lead Generation",
                "objective": "Generate qualified leads for enterprise software",
                "target_audience": "IT managers and CTOs",
                "budget": 30000,
                "duration_days": 60,
                "channels": ["LinkedIn", "Content Marketing", "Webinars"],
                "performance_metrics": [
                    {"channel": "LinkedIn", "metric": "lead_quality_score", "value": 8.2},
                    {"channel": "Content Marketing", "metric": "content_views", "value": 45000},
                    {"channel": "Webinars", "metric": "attendance_rate", "value": 0.35}
                ]
            }
        ]
        
        print(f"✅ Loaded {len(sample_campaigns)} sample campaigns")
        return sample_campaigns
    
    def load_industry_trends(self, industry: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load sample industry trend data"""
        trends = [
            {
                "name": "AI-Powered Personalization",
                "category": "Technology",
                "relevance_score": 0.9,
                "impact_score": 0.85,
                "description": "Increasing use of AI for personalized customer experiences",
                "source": "Industry Reports",
                "date_identified": "2024-03-01"
            },
            {
                "name": "Sustainable Marketing",
                "category": "Sustainability", 
                "relevance_score": 0.8,
                "impact_score": 0.75,
                "description": "Growing consumer preference for environmentally conscious brands",
                "source": "Consumer Research",
                "date_identified": "2024-02-15"
            },
            {
                "name": "Short-Form Video Content", 
                "category": "Content",
                "relevance_score": 0.95,
                "impact_score": 0.9,
                "description": "Continued dominance of short-form video across platforms",
                "source": "Social Media Analytics",
                "date_identified": "2024-03-10"
            },
            {
                "name": "Voice Commerce Growth",
                "category": "E-commerce",
                "relevance_score": 0.7,
                "impact_score": 0.8,
                "description": "Increasing adoption of voice-activated shopping",
                "source": "Market Research",
                "date_identified": "2024-02-28"
            },
            {
                "name": "Privacy-First Marketing",
                "category": "Privacy",
                "relevance_score": 0.85,
                "impact_score": 0.8,
                "description": "Adapting marketing strategies to privacy regulations and consumer preferences",
                "source": "Legal & Tech Reports",
                "date_identified": "2024-01-20"
            }
        ]
        
        if industry:
            # Filter trends by industry (simplified matching)
            filtered_trends = [
                trend for trend in trends 
                if industry.lower() in trend["category"].lower() or 
                industry.lower() in trend["description"].lower()
            ]
            trends = filtered_trends if filtered_trends else trends
        
        print(f"✅ Loaded {len(trends)} industry trends")
        return trends
    
    def load_competitor_data(self, industry: Optional[str] = None) -> Dict[str, Any]:
        """Load sample competitor analysis data"""
        competitor_data = {
            "competitors": [
                {
                    "name": "Market Leader A",
                    "market_share": 0.32,
                    "strengths": ["Strong brand recognition", "Extensive distribution", "Premium positioning"],
                    "weaknesses": ["High pricing", "Limited digital presence"],
                    "recent_campaigns": ["Premium product launch", "Celebrity endorsement"],
                    "budget_estimate": 1000000
                },
                {
                    "name": "Challenger B",
                    "market_share": 0.18,
                    "strengths": ["Innovative products", "Strong social media", "Young audience appeal"],
                    "weaknesses": ["Limited market reach", "Brand awareness gaps"],
                    "recent_campaigns": ["Influencer partnerships", "TikTok viral campaign"],
                    "budget_estimate": 500000
                },
                {
                    "name": "Disruptor C",
                    "market_share": 0.08,
                    "strengths": ["Low pricing", "Direct-to-consumer model", "Digital-first approach"],
                    "weaknesses": ["Limited product range", "Quality concerns"],
                    "recent_campaigns": ["Price comparison ads", "User-generated content"],
                    "budget_estimate": 250000
                }
            ],
            "market_insights": [
                "Digital advertising spend increased by 15% industry-wide",
                "Influencer marketing showing highest ROI growth",
                "Video content driving 3x higher engagement rates",
                "Mobile-first strategies becoming standard"
            ],
            "opportunities": [
                "Underserved niche segments",
                "Emerging platform adoption",
                "Real-time customer service gaps",
                "Sustainability messaging opportunities"
            ]
        }
        
        print("✅ Loaded competitor analysis data")
        return competitor_data
    
    def load_audience_insights(self, target_audience: str) -> Dict[str, Any]:
        """Load audience research data based on target description"""
        # Simplified audience insights based on common segments
        audience_data = {
            "demographics": {
                "age_distribution": {"18-24": 0.15, "25-34": 0.35, "35-44": 0.30, "45+": 0.20},
                "gender_distribution": {"female": 0.52, "male": 0.45, "other": 0.03},
                "income_levels": {"low": 0.25, "middle": 0.50, "high": 0.25},
                "education": {"high_school": 0.30, "college": 0.45, "graduate": 0.25}
            },
            "behaviors": [
                "Active on social media platforms",
                "Researches products online before purchasing",
                "Values peer reviews and recommendations",
                "Prefers mobile-friendly content",
                "Responds to personalized messaging"
            ],
            "preferences": {
                "content_types": ["Video", "Images", "Articles", "Reviews"],
                "channels": ["Instagram", "Facebook", "Google", "Email"],
                "purchase_factors": ["Price", "Quality", "Brand reputation", "Reviews"],
                "communication_style": ["Authentic", "Informative", "Visual"]
            },
            "pain_points": [
                "Information overload when researching products",
                "Difficulty comparing options",
                "Concerns about online privacy",
                "Time constraints for decision making"
            ]
        }
        
        print(f"✅ Loaded audience insights for: {target_audience}")
        return audience_data
    
    def fetch_external_trends(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch trend data from external sources
        Note: This is a placeholder for actual API integration
        """
        # In a real implementation, this would call Google Trends API, 
        # social media APIs, etc.
        
        mock_trends = []
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            mock_trends.append({
                "keyword": keyword,
                "trend_score": 0.7 + (hash(keyword) % 30) / 100,  # Mock score
                "search_volume": 10000 + (hash(keyword) % 50000),
                "competition": "medium",
                "related_topics": [f"{keyword} tips", f"best {keyword}", f"{keyword} guide"],
                "geographic_interest": ["United States", "United Kingdom", "Canada"]
            })
        
        print(f"✅ Fetched trends for {len(keywords)} keywords")
        return mock_trends
    
    def load_performance_benchmarks(
        self, 
        industry: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load industry performance benchmarks"""
        benchmarks = {
            "social_media": {
                "engagement_rate": {"average": 0.035, "good": 0.055, "excellent": 0.08},
                "reach_rate": {"average": 0.15, "good": 0.25, "excellent": 0.40},
                "click_through_rate": {"average": 0.012, "good": 0.018, "excellent": 0.025}
            },
            "email_marketing": {
                "open_rate": {"average": 0.22, "good": 0.28, "excellent": 0.35},
                "click_rate": {"average": 0.025, "good": 0.035, "excellent": 0.05},
                "conversion_rate": {"average": 0.015, "good": 0.025, "excellent": 0.04}
            },
            "paid_search": {
                "click_through_rate": {"average": 0.02, "good": 0.03, "excellent": 0.045},
                "conversion_rate": {"average": 0.025, "good": 0.04, "excellent": 0.06},
                "cost_per_click": {"average": 2.5, "good": 1.8, "excellent": 1.2}
            },
            "display_advertising": {
                "click_through_rate": {"average": 0.005, "good": 0.008, "excellent": 0.012},
                "viewability_rate": {"average": 0.65, "good": 0.75, "excellent": 0.85},
                "conversion_rate": {"average": 0.008, "good": 0.015, "excellent": 0.025}
            }
        }
        
        if channel and channel.lower().replace(" ", "_") in benchmarks:
            result = {channel: benchmarks[channel.lower().replace(" ", "_")]}
        else:
            result = benchmarks
        
        print(f"✅ Loaded performance benchmarks")
        return result
    
    def export_data(self, data: Any, file_path: str, format: str = "json") -> bool:
        """Export data to file"""
        try:
            if format.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            elif format.lower() == "csv" and isinstance(data, (list, pd.DataFrame)):
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = data
                df.to_csv(file_path, index=False)
            else:
                print(f"❌ Unsupported format: {format}")
                return False
            
            print(f"✅ Data exported to {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting data: {str(e)}")
            return False