#!/usr/bin/env python
"""
Quick test to verify JSON structure is correct
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.trend_scout import TrendScout

# Test the trend scout
print("🧪 Testing TrendScout JSON structure...")
print("=" * 60)

try:
    trend_scout = TrendScout()
    
    # Get fallback trends (guaranteed structure)
    trends = trend_scout._get_fallback_trends()
    
    # Validate structure
    print("\n✅ Fallback trends structure:")
    print(f"   - Type: {type(trends)}")
    print(f"   - Is dict: {isinstance(trends, dict)}")
    
    print(f"\n   Keys in response:")
    for key in trends.keys():
        print(f"      - {key}: {type(trends[key])}")
    
    print(f"\n   Trends count: {len(trends['trends'])}")
    print(f"   First trend: {trends['trends'][0]['name'] if trends['trends'] else 'None'}")
    
    print(f"\n   Competitor Analysis keys: {list(trends['competitor_analysis'].keys())}")
    print(f"   Market Insights count: {len(trends['market_insights'])}")
    
    # Validate structure
    assert isinstance(trends, dict), "❌ Result must be dict"
    assert "trends" in trends, "❌ Missing 'trends' key"
    assert "competitor_analysis" in trends, "❌ Missing 'competitor_analysis' key"
    assert "market_insights" in trends, "❌ Missing 'market_insights' key"
    assert isinstance(trends["trends"], list), "❌ 'trends' must be list"
    assert isinstance(trends["competitor_analysis"], dict), "❌ 'competitor_analysis' must be dict"
    assert isinstance(trends["market_insights"], list), "❌ 'market_insights' must be list"
    assert len(trends["trends"]) > 0, "❌ Must have at least one trend"
    
    print("\n" + "=" * 60)
    print("✅ JSON structure validation PASSED!")
    print("   - All required keys present")
    print("   - All types correct")
    print("   - Contains valid data")

except Exception as e:
    print(f"\n❌ Validation FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
