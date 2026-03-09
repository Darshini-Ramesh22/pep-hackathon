"""
SQL Tool for Campaign Brain - Database interactions for campaign data
"""
import sqlite3
import sys
import os
import pandas as pd
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class SQLTool:
    """
    Tool for database interactions, storing campaign data,
    and retrieving historical performance metrics.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_URL.replace("sqlite:///", "")
        self.init_database()
    
    def init_database(self):
        """Initialize database tables for campaign data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Campaigns table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        objective TEXT,
                        target_audience TEXT,
                        budget REAL,
                        duration_days INTEGER,
                        start_date TEXT,
                        end_date TEXT,
                        status TEXT DEFAULT 'planned',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Performance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS campaign_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_id INTEGER,
                        channel TEXT,
                        metric_name TEXT,
                        metric_value REAL,
                        date_recorded TEXT,
                        FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
                    )
                """)
                
                # Trends table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trend_name TEXT,
                        category TEXT,
                        relevance_score REAL,
                        impact_score REAL,
                        source TEXT,
                        date_identified TEXT,
                        description TEXT
                    )
                """)
                
                # Personas table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS personas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_id INTEGER,
                        persona_name TEXT,
                        demographics TEXT,
                        goals TEXT,
                        pain_points TEXT,
                        behaviors TEXT,
                        FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
                    )
                """)
                
                conn.commit()
                print("✅ Database initialized successfully")
                
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
    
    def save_campaign(self, campaign_data: Dict[str, Any]) -> int:
        """Save campaign data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO campaigns (
                        name, objective, target_audience, budget, 
                        duration_days, start_date, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    campaign_data.get("name", "Campaign"),
                    campaign_data.get("objective", ""),
                    campaign_data.get("target_audience", ""),
                    campaign_data.get("budget", 0.0),
                    campaign_data.get("duration_days", 30),
                    campaign_data.get("start_date", ""),
                    campaign_data.get("status", "planned")
                ))
                
                campaign_id = cursor.lastrowid
                conn.commit()
                
                print(f"✅ Campaign saved with ID: {campaign_id}")
                return campaign_id
                
        except Exception as e:
            print(f"❌ Error saving campaign: {str(e)}")
            return -1
    
    def save_performance_metrics(
        self, 
        campaign_id: int, 
        metrics: List[Dict[str, Any]]
    ):
        """Save performance metrics to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for metric in metrics:
                    cursor.execute("""
                        INSERT INTO campaign_performance (
                            campaign_id, channel, metric_name, 
                            metric_value, date_recorded
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        campaign_id,
                        metric.get("channel", ""),
                        metric.get("metric_name", ""),
                        metric.get("metric_value", 0.0),
                        metric.get("date_recorded", "")
                    ))
                
                conn.commit()
                print(f"✅ Saved {len(metrics)} performance metrics")
                
        except Exception as e:
            print(f"❌ Error saving performance metrics: {str(e)}")
    
    def get_historical_performance(
        self, 
        channel: Optional[str] = None,
        metric_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve historical performance data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT cp.*, c.name as campaign_name 
                    FROM campaign_performance cp
                    JOIN campaigns c ON cp.campaign_id = c.id
                    WHERE 1=1
                """
                params = []
                
                if channel:
                    query += " AND cp.channel = ?"
                    params.append(channel)
                
                if metric_name:
                    query += " AND cp.metric_name = ?"
                    params.append(metric_name)
                
                query += " ORDER BY cp.date_recorded DESC LIMIT ?"
                params.append(limit)
                
                df = pd.read_sql_query(query, conn, params=params)
                return df.to_dict('records')
                
        except Exception as e:
            print(f"❌ Error retrieving performance data: {str(e)}")
            return []
    
    def get_campaign_summary(self, campaign_id: int) -> Dict[str, Any]:
        """Get comprehensive campaign summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get campaign details
                campaign_query = "SELECT * FROM campaigns WHERE id = ?"
                campaign_df = pd.read_sql_query(campaign_query, conn, params=[campaign_id])
                
                if campaign_df.empty:
                    return {}
                
                campaign = campaign_df.iloc[0].to_dict()
                
                # Get performance metrics
                metrics_query = """
                    SELECT channel, metric_name, AVG(metric_value) as avg_value,
                           MAX(metric_value) as max_value, COUNT(*) as data_points
                    FROM campaign_performance 
                    WHERE campaign_id = ?
                    GROUP BY channel, metric_name
                """
                metrics_df = pd.read_sql_query(metrics_query, conn, params=[campaign_id])
                metrics = metrics_df.to_dict('records')
                
                # Get personas
                personas_query = "SELECT * FROM personas WHERE campaign_id = ?"
                personas_df = pd.read_sql_query(personas_query, conn, params=[campaign_id])
                personas = personas_df.to_dict('records')
                
                return {
                    "campaign": campaign,
                    "performance_metrics": metrics,
                    "personas": personas
                }
                
        except Exception as e:
            print(f"❌ Error getting campaign summary: {str(e)}")
            return {}
    
    def search_similar_campaigns(
        self, 
        objective: str, 
        budget_range: tuple = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar campaigns for benchmarking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT c.*, 
                           AVG(cp.metric_value) as avg_performance
                    FROM campaigns c
                    LEFT JOIN campaign_performance cp ON c.id = cp.campaign_id
                    WHERE c.objective LIKE ?
                """
                params = [f"%{objective}%"]
                
                if budget_range:
                    query += " AND c.budget BETWEEN ? AND ?"
                    params.extend(budget_range)
                
                query += """
                    GROUP BY c.id
                    ORDER BY avg_performance DESC
                    LIMIT ?
                """
                params.append(limit)
                
                df = pd.read_sql_query(query, conn, params=params)
                return df.to_dict('records')
                
        except Exception as e:
            print(f"❌ Error searching similar campaigns: {str(e)}")
            return []
    
    def execute_custom_query(self, query: str, params: List = None) -> List[Dict[str, Any]]:
        """Execute custom SQL query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params or [])
                return df.to_dict('records')
                
        except Exception as e:
            print(f"❌ Error executing query: {str(e)}")
            return []
    
    def get_top_performing_channels(
        self, 
        metric_name: str = "conversion_rate",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing channels by metric"""
        query = """
            SELECT 
                channel,
                AVG(metric_value) as avg_performance,
                COUNT(*) as campaign_count
            FROM campaign_performance 
            WHERE metric_name = ?
            GROUP BY channel
            ORDER BY avg_performance DESC
            LIMIT ?
        """
        
        return self.execute_custom_query(query, [metric_name, limit])
    
    def get_trend_insights(
        self, 
        category: Optional[str] = None,
        min_relevance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get trending insights from trends table"""
        query = """
            SELECT * FROM trends 
            WHERE relevance_score >= ?
        """
        params = [min_relevance]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY relevance_score DESC, impact_score DESC"
        
        return self.execute_custom_query(query, params)