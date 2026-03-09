"""
Analytics Tool for Campaign Brain - Data analysis and insights generation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .sql_tool import SQLTool
from .data_loader import DataLoader


class TrendAnalyzer:
    """
    Tool for analyzing trends and market data to provide insights
    for campaign planning and optimization.
    """
    
    def __init__(self):
        self.sql_tool = SQLTool()
        self.data_loader = DataLoader()
    
    def analyze_campaign_performance(
        self, 
        campaign_id: int
    ) -> Dict[str, Any]:
        """Analyze performance metrics for a specific campaign"""
        
        try:
            # Get campaign data
            campaign_data = self.sql_tool.get_campaign_summary(campaign_id)
            
            if not campaign_data:
                return {"error": "Campaign not found"}
            
            metrics = campaign_data.get("performance_metrics", [])
            
            analysis = {
                "campaign_overview": campaign_data["campaign"],
                "performance_summary": self._calculate_performance_summary(metrics),
                "channel_performance": self._analyze_channel_performance(metrics),
                "recommendations": self._generate_performance_recommendations(metrics),
                "benchmarks": self._compare_to_benchmarks(metrics)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def get_trending_topics(
        self, 
        keywords: List[str], 
        audience: str = ""
    ) -> Dict[str, Any]:
        """Analyze trending topics relevant to keywords and audience"""
        
        try:
            # Load trend data
            trends = self.data_loader.load_industry_trends()
            external_trends = self.data_loader.fetch_external_trends(keywords)
            
            # Analyze relevance to keywords
            relevant_trends = []
            for trend in trends:
                relevance_score = self._calculate_keyword_relevance(
                    trend, keywords
                )
                if relevance_score > 0.3:  # Threshold for relevance
                    trend["keyword_relevance"] = relevance_score
                    relevant_trends.append(trend)
            
            # Sort by combined relevance and impact
            relevant_trends.sort(
                key=lambda x: x.get("relevance_score", 0) * x.get("keyword_relevance", 0),
                reverse=True
            )
            
            return {
                "trends": relevant_trends[:10],
                "external_data": external_trends,
                "trend_analysis": self._analyze_trend_patterns(relevant_trends)
            }
            
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def analyze_audience_segments(
        self, 
        target_audience: str
    ) -> Dict[str, Any]:
        """Analyze audience segments and behavior patterns"""
        
        try:
            # Load audience data
            audience_data = self.data_loader.load_audience_insights(target_audience)
            
            # Analyze segments
            segments = self._identify_audience_segments(audience_data)
            personas = self._generate_persona_insights(audience_data, segments)
            
            return {
                "audience_overview": audience_data,
                "segments": segments,
                "persona_insights": personas,
                "engagement_predictions": self._predict_engagement(audience_data)
            }
            
        except Exception as e:
            return {"error": f"Audience analysis failed: {str(e)}"}
    
    def calculate_campaign_roi(
        self, 
        campaign_metrics: List[Dict[str, Any]],
        budget: float
    ) -> Dict[str, Any]:
        """Calculate ROI and performance metrics for campaign"""
        
        try:
            # Extract key metrics
            total_reach = sum(
                m.get("metric_value", 0) for m in campaign_metrics
                if m.get("metric_name") == "reach"
            )
            
            total_conversions = sum(
                m.get("metric_value", 0) for m in campaign_metrics
                if m.get("metric_name") == "conversions"
            )
            
            total_revenue = sum(
                m.get("metric_value", 0) for m in campaign_metrics
                if m.get("metric_name") == "revenue"
            )
            
            # Calculate derived metrics
            cpa = budget / total_conversions if total_conversions > 0 else 0
            roi = ((total_revenue - budget) / budget * 100) if budget > 0 else 0
            cpm = (budget / total_reach * 1000) if total_reach > 0 else 0
            
            return {
                "budget": budget,
                "total_reach": total_reach,
                "total_conversions": total_conversions,
                "total_revenue": total_revenue,
                "cost_per_acquisition": cpa,
                "return_on_investment": roi,
                "cost_per_thousand": cpm,
                "efficiency_score": self._calculate_efficiency_score(
                    roi, cpa, total_reach, budget
                )
            }
            
        except Exception as e:
            return {"error": f"ROI calculation failed: {str(e)}"}
    
    def compare_channel_performance(
        self, 
        channels: List[str],
        metric: str = "conversion_rate"
    ) -> Dict[str, Any]:
        """Compare performance across different marketing channels"""
        
        try:
            channel_data = []
            
            for channel in channels:
                # Get historical data for channel
                performance_data = self.sql_tool.get_historical_performance(
                    channel=channel,
                    metric_name=metric
                )
                
                if performance_data:
                    avg_performance = np.mean([
                        d["metric_value"] for d in performance_data
                    ])
                    
                    channel_data.append({
                        "channel": channel,
                        "average_performance": avg_performance,
                        "data_points": len(performance_data),
                        "performance_trend": self._calculate_trend(performance_data)
                    })
            
            # Sort by performance
            channel_data.sort(
                key=lambda x: x["average_performance"], 
                reverse=True
            )
            
            return {
                "metric": metric,
                "channel_rankings": channel_data,
                "best_performer": channel_data[0] if channel_data else None,
                "recommendations": self._generate_channel_recommendations(channel_data)
            }
            
        except Exception as e:
            return {"error": f"Channel comparison failed: {str(e)}"}
    
    def predict_campaign_performance(
        self, 
        campaign_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict campaign performance based on historical data and parameters"""
        
        try:
            # Find similar campaigns
            similar_campaigns = self.sql_tool.search_similar_campaigns(
                objective=campaign_params.get("objective", ""),
                budget_range=(
                    campaign_params.get("budget", 0) * 0.8,
                    campaign_params.get("budget", 0) * 1.2
                )
            )
            
            if not similar_campaigns:
                return self._generate_baseline_predictions(campaign_params)
            
            # Calculate predictions based on similar campaigns
            predictions = {}
            
            for campaign in similar_campaigns:
                budget = campaign.get("budget", 0)
                performance = campaign.get("avg_performance", 0)
                
                if budget > 0:
                    # Scale predictions based on budget ratio
                    budget_ratio = campaign_params.get("budget", 0) / budget
                    scaled_performance = performance * (budget_ratio ** 0.8)  # Diminishing returns
                    
                    predictions.setdefault("predicted_performance", []).append(scaled_performance)
            
            # Calculate final predictions
            if predictions.get("predicted_performance"):
                avg_prediction = np.mean(predictions["predicted_performance"])
                confidence = min(len(similar_campaigns) / 5.0, 1.0)  # Max confidence with 5+ campaigns
                
                return {
                    "predicted_metrics": {
                        "expected_performance": avg_prediction,
                        "confidence_level": confidence,
                        "performance_range": {
                            "low": avg_prediction * 0.8,
                            "high": avg_prediction * 1.2
                        }
                    },
                    "based_on_campaigns": len(similar_campaigns),
                    "recommendations": self._generate_prediction_recommendations(
                        avg_prediction, confidence
                    )
                }
            
            return self._generate_baseline_predictions(campaign_params)
            
        except Exception as e:
            return {"error": f"Performance prediction failed: {str(e)}"}
    
    def _calculate_performance_summary(
        self, 
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate summary statistics for campaign performance"""
        
        if not metrics:
            return {"status": "No metrics available"}
        
        # Group metrics by type
        metric_groups = {}
        for metric in metrics:
            metric_name = metric.get("metric_name", "unknown")
            metric_groups.setdefault(metric_name, []).append(
                metric.get("avg_value", metric.get("metric_value", 0))
            )
        
        summary = {}
        for metric_name, values in metric_groups.items():
            summary[metric_name] = {
                "average": np.mean(values),
                "max": np.max(values),
                "min": np.min(values),
                "data_points": len(values)
            }
        
        return summary
    
    def _analyze_channel_performance(
        self, 
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze performance by marketing channel"""
        
        channel_metrics = {}
        for metric in metrics:
            channel = metric.get("channel", "unknown")
            if channel not in channel_metrics:
                channel_metrics[channel] = []
            channel_metrics[channel].append(metric)
        
        channel_analysis = {}
        for channel, channel_data in channel_metrics.items():
            total_performance = sum(
                m.get("avg_value", m.get("metric_value", 0)) 
                for m in channel_data
            )
            
            channel_analysis[channel] = {
                "total_performance": total_performance,
                "metrics_count": len(channel_data),
                "avg_performance": total_performance / len(channel_data) if channel_data else 0
            }
        
        return channel_analysis
    
    def _calculate_keyword_relevance(
        self, 
        trend: Dict[str, Any], 
        keywords: List[str]
    ) -> float:
        """Calculate relevance score between trend and keywords"""
        
        trend_text = f"{trend.get('name', '')} {trend.get('description', '')}".lower()
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in trend_text:
                matches += 1
        
        return matches / len(keywords) if keywords else 0
    
    def _analyze_trend_patterns(
        self, 
        trends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze patterns in trend data"""
        
        if not trends:
            return {"status": "No trends to analyze"}
        
        # Category analysis
        categories = {}
        for trend in trends:
            category = trend.get("category", "other")
            categories[category] = categories.get(category, 0) + 1
        
        # Score analysis
        relevance_scores = [t.get("relevance_score", 0) for t in trends]
        impact_scores = [t.get("impact_score", 0) for t in trends]
        
        return {
            "category_distribution": categories,
            "score_analysis": {
                "avg_relevance": np.mean(relevance_scores),
                "avg_impact": np.mean(impact_scores),
                "high_impact_trends": len([s for s in impact_scores if s > 0.8])
            },
            "trend_velocity": self._calculate_trend_velocity(trends)
        }
    
    def _calculate_trend_velocity(self, trends: List[Dict[str, Any]]) -> str:
        """Calculate how fast trends are emerging"""
        
        # Simplified calculation based on recency
        recent_count = len([
            t for t in trends 
            if self._is_recent_trend(t.get("date_identified", ""))
        ])
        
        velocity_ratio = recent_count / len(trends) if trends else 0
        
        if velocity_ratio > 0.6:
            return "high"
        elif velocity_ratio > 0.3:
            return "medium"
        else:
            return "low"
    
    def _is_recent_trend(self, date_str: str) -> bool:
        """Check if trend is recent (within last 30 days)"""
        try:
            trend_date = datetime.strptime(date_str, "%Y-%m-%d")
            cutoff_date = datetime.now() - timedelta(days=30)
            return trend_date > cutoff_date
        except:
            return False
    
    def _identify_audience_segments(
        self, 
        audience_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify key audience segments"""
        
        demographics = audience_data.get("demographics", {})
        
        segments = []
        
        # Age-based segments
        age_dist = demographics.get("age_distribution", {})
        for age_group, percentage in age_dist.items():
            if percentage > 0.2:  # Significant segment (>20%)
                segments.append({
                    "name": f"Age {age_group}",
                    "size": percentage,
                    "characteristics": self._get_age_characteristics(age_group)
                })
        
        return segments
    
    def _get_age_characteristics(self, age_group: str) -> List[str]:
        """Get characteristics for age group"""
        
        characteristics_map = {
            "18-24": ["Tech-savvy", "Price-sensitive", "Social media heavy"],
            "25-34": ["Career-focused", "Quality-conscious", "Income growing"],
            "35-44": ["Family-oriented", "Value-driven", "Time-conscious"],
            "45+": ["Brand-loyal", "Quality-focused", "Traditional channels"]
        }
        
        return characteristics_map.get(age_group, ["General audience"])
    
    def _generate_persona_insights(
        self, 
        audience_data: Dict[str, Any], 
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights for persona development"""
        
        behaviors = audience_data.get("behaviors", [])
        preferences = audience_data.get("preferences", {})
        
        return {
            "key_behaviors": behaviors[:5],
            "content_preferences": preferences.get("content_types", []),
            "channel_preferences": preferences.get("channels", []),
            "decision_factors": preferences.get("purchase_factors", []),
            "segment_insights": [
                {
                    "segment": seg["name"],
                    "priority_score": seg["size"],
                    "targeting_approach": self._suggest_targeting_approach(seg)
                }
                for seg in segments
            ]
        }
    
    def _suggest_targeting_approach(self, segment: Dict[str, Any]) -> str:
        """Suggest targeting approach for segment"""
        
        size = segment.get("size", 0)
        characteristics = segment.get("characteristics", [])
        
        if size > 0.4:
            return "Primary target - broad reach strategy"
        elif size > 0.2:
            return "Secondary target - focused campaigns"
        else:
            return "Niche opportunity - specialized messaging"
    
    def _predict_engagement(
        self, 
        audience_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict engagement levels for different content types"""
        
        preferences = audience_data.get("preferences", {})
        content_types = preferences.get("content_types", [])
        
        # Simplified engagement prediction
        engagement_predictions = {}
        for content_type in content_types:
            # Mock prediction based on content type popularity
            base_engagement = {
                "Video": 0.08,
                "Images": 0.06,
                "Articles": 0.04,
                "Reviews": 0.07
            }.get(content_type, 0.05)
            
            engagement_predictions[content_type] = {
                "predicted_engagement": base_engagement,
                "confidence": 0.75,
                "recommendation": self._get_content_recommendation(content_type)
            }
        
        return engagement_predictions
    
    def _get_content_recommendation(self, content_type: str) -> str:
        """Get content recommendation for type"""
        
        recommendations = {
            "Video": "Focus on short-form, mobile-optimized videos",
            "Images": "Use high-quality, authentic imagery",
            "Articles": "Create in-depth, valuable content",
            "Reviews": "Encourage user-generated reviews"
        }
        
        return recommendations.get(content_type, "Create engaging content")
    
    def _generate_performance_recommendations(
        self, 
        metrics: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on performance data"""
        
        recommendations = []
        
        if not metrics:
            return ["Implement comprehensive tracking across all channels"]
        
        # Analyze metrics for recommendations
        channel_performance = self._analyze_channel_performance(metrics)
        
        if channel_performance:
            best_channel = max(
                channel_performance.items(),
                key=lambda x: x[1]["avg_performance"]
            )[0]
            
            recommendations.append(f"Increase investment in {best_channel} - best performing channel")
        
        recommendations.extend([
            "Implement A/B testing for creative variations",
            "Monitor performance daily for optimization opportunities",
            "Set up automated alerts for performance thresholds"
        ])
        
        return recommendations
    
    def _compare_to_benchmarks(
        self, 
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare campaign metrics to industry benchmarks"""
        
        benchmarks = self.data_loader.load_performance_benchmarks()
        
        comparison = {}
        for metric in metrics:
            metric_name = metric.get("metric_name", "")
            metric_value = metric.get("avg_value", metric.get("metric_value", 0))
            channel = metric.get("channel", "").lower().replace(" ", "_")
            
            if channel in benchmarks and metric_name in benchmarks[channel]:
                benchmark_data = benchmarks[channel][metric_name]
                
                if metric_value >= benchmark_data["excellent"]:
                    performance_level = "excellent"
                elif metric_value >= benchmark_data["good"]:
                    performance_level = "good"
                elif metric_value >= benchmark_data["average"]:
                    performance_level = "average"
                else:
                    performance_level = "below_average"
                
                comparison[f"{channel}_{metric_name}"] = {
                    "actual": metric_value,
                    "benchmark_average": benchmark_data["average"],
                    "performance_level": performance_level,
                    "improvement_opportunity": benchmark_data["excellent"] - metric_value
                }
        
        return comparison
    
    def _calculate_trend(self, data_points: List[Dict[str, Any]]) -> str:
        """Calculate trend direction from data points"""
        
        if len(data_points) < 2:
            return "insufficient_data"
        
        # Sort by date and calculate trend
        values = [d.get("metric_value", 0) for d in data_points[-5:]]  # Last 5 points
        
        if len(values) < 2:
            return "stable"
        
        trend_slope = (values[-1] - values[0]) / len(values)
        
        if trend_slope > 0.1:
            return "increasing"
        elif trend_slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_channel_recommendations(
        self, 
        channel_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on channel performance"""
        
        if not channel_data:
            return ["Establish baseline performance tracking"]
        
        recommendations = []
        
        best_performer = channel_data[0]
        worst_performer = channel_data[-1] if len(channel_data) > 1 else None
        
        recommendations.append(
            f"Scale up {best_performer['channel']} - showing best performance"
        )
        
        if worst_performer and worst_performer['average_performance'] < best_performer['average_performance'] * 0.5:
            recommendations.append(
                f"Optimize or reduce {worst_performer['channel']} budget"
            )
        
        recommendations.extend([
            "Test new creative formats on top-performing channels",
            "Implement cross-channel attribution tracking",
            "Monitor performance weekly for trend identification"
        ])
        
        return recommendations
    
    def _calculate_efficiency_score(
        self, 
        roi: float, 
        cpa: float, 
        reach: int, 
        budget: float
    ) -> float:
        """Calculate overall campaign efficiency score"""
        
        # Normalize and combine different efficiency metrics
        roi_score = min(roi / 100, 2.0)  # Cap at 200% ROI
        reach_efficiency = (reach / budget) if budget > 0 else 0
        
        # Weight different components
        efficiency_score = (
            roi_score * 0.4 +  # ROI is most important
            (1 / (cpa + 1)) * 0.3 +  # Lower CPA is better
            min(reach_efficiency / 100, 1.0) * 0.3  # Reach efficiency
        )
        
        return min(efficiency_score, 1.0)  # Cap at 1.0
    
    def _generate_baseline_predictions(
        self, 
        campaign_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate baseline predictions when no historical data available"""
        
        budget = campaign_params.get("budget", 0)
        
        # Industry average estimates
        baseline_metrics = {
            "expected_reach": budget * 50,  # $1 = 50 impressions
            "expected_engagement_rate": 0.035,  # 3.5% industry average
            "expected_conversion_rate": 0.02,  # 2% industry average
            "expected_cpa": budget * 0.15,  # 15% of budget for acquisition costs
            "expected_roi": 150  # 150% ROI target
        }
        
        return {
            "predicted_metrics": baseline_metrics,
            "confidence_level": 0.3,  # Low confidence without historical data
            "note": "Predictions based on industry averages - low confidence without historical data",
            "recommendations": [
                "Start with small budget to gather performance data",
                "Implement comprehensive tracking from day one",
                "Plan for 2-4 weeks of optimization period"
            ]
        }
    
    def _generate_prediction_recommendations(
        self, 
        predicted_performance: float, 
        confidence: float
    ) -> List[str]:
        """Generate recommendations based on predictions"""
        
        recommendations = []
        
        if confidence > 0.7:
            recommendations.append("High confidence prediction - proceed with full budget")
        elif confidence > 0.4:
            recommendations.append("Moderate confidence - consider phased rollout")
        else:
            recommendations.append("Low confidence - start with test budget")
        
        if predicted_performance > 0.8:
            recommendations.append("Strong predicted performance - consider scaling up")
        elif predicted_performance < 0.3:
            recommendations.append("Below-average predictions - review strategy")
        
        recommendations.extend([
            "Monitor actual vs predicted performance closely",
            "Prepare contingency plans for underperformance",
            "Set up automated optimization rules"
        ])
        
        return recommendations