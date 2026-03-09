"""
Campaign Brain - Main Application Entry Point

A multi-agent AI system for comprehensive campaign planning using LangGraph.
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Optional

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.builder import run_campaign_brain, create_campaign_brain_graph
from config import Config
from tools.sql_tool import SQLTool
from tools.data_loader import DataLoader
from tools.analytics import TrendAnalyzer


def main():
    """Main application entry point"""
    print("🧠 Welcome to Campaign Brain")
    print("=" * 50)
    print("AI-Powered Multi-Agent Campaign Planning System")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(description="Campaign Brain - AI Campaign Planner")
    parser.add_argument("--mode", 
                       choices=["interactive", "demo", "ui", "test"], 
                       default="interactive",
                       help="Run mode: interactive, demo, ui, or test")
    parser.add_argument("--objective", 
                       type=str,
                       help="Campaign objective (for non-interactive mode)")
    parser.add_argument("--audience", 
                       type=str,
                       help="Target audience description")
    parser.add_argument("--budget", 
                       type=float,
                       help="Campaign budget")
    parser.add_argument("--duration", 
                       type=int,
                       default=30,
                       help="Campaign duration in days")
    parser.add_argument("--output", 
                       type=str,
                       help="Output file path for results")
    
    args = parser.parse_args()
    
    if args.mode == "ui":
        launch_ui()
    elif args.mode == "demo":
        run_demo()
    elif args.mode == "test":
        run_tests()
    elif args.mode == "interactive":
        if args.objective and args.audience and args.budget:
            run_direct_campaign(args)
        else:
            run_interactive_mode()
    else:
        print("❌ Invalid mode selected")
        sys.exit(1)


def run_interactive_mode():
    """Run interactive campaign planning mode"""
    print("\n🚀 Interactive Campaign Planning Mode")
    print("Let's create your campaign plan step by step...\n")
    
    try:
        # Gather campaign requirements
        campaign_name = input("📝 Campaign Name: ").strip()
        if not campaign_name:
            campaign_name = f"Campaign_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        print("\n📋 Campaign Details:")
        objective = input("🎯 Campaign Objective: ").strip()
        if not objective:
            print("❌ Campaign objective is required!")
            return
        
        target_audience = input("👥 Target Audience: ").strip()
        if not target_audience:
            print("❌ Target audience description is required!")
            return
        
        try:
            budget = float(input("💰 Budget ($): ").strip())
            if budget <= 0:
                print("❌ Budget must be positive!")
                return
        except ValueError:
            print("❌ Invalid budget amount!")
            return
        
        try:
            duration = int(input("📅 Duration (days) [30]: ").strip() or "30")
            if duration <= 0:
                print("❌ Duration must be positive!")
                return
        except ValueError:
            print("❌ Invalid duration!")
            return
        
        brand_guidelines = input("🎨 Brand Guidelines (optional): ").strip()
        
        # Run campaign planning
        run_campaign_with_params(
            campaign_name=campaign_name,
            objective=objective,
            target_audience=target_audience,
            budget=budget,
            duration=duration,
            brand_guidelines=brand_guidelines
        )
        
    except KeyboardInterrupt:
        print("\n\n❌ Campaign planning cancelled by user")
    except Exception as e:
        print(f"\n❌ Error in interactive mode: {str(e)}")


def run_direct_campaign(args):
    """Run campaign planning with provided arguments"""
    print(f"\n🚀 Running campaign planning...")
    print(f"Objective: {args.objective}")
    print(f"Audience: {args.audience}")
    print(f"Budget: ${args.budget:,.2f}")
    print(f"Duration: {args.duration} days")
    
    run_campaign_with_params(
        campaign_name=f"Campaign_{datetime.now().strftime('%Y%m%d_%H%M')}",
        objective=args.objective,
        target_audience=args.audience,
        budget=args.budget,
        duration=args.duration,
        brand_guidelines="",
        output_file=args.output
    )


def run_campaign_with_params(
    campaign_name: str,
    objective: str,
    target_audience: str,
    budget: float,
    duration: int,
    brand_guidelines: str = "",
    output_file: Optional[str] = None
):
    """Run campaign planning with specified parameters"""
    
    print(f"\n🧠 Starting Campaign Brain workflow for '{campaign_name}'...")
    print("-" * 60)
    
    try:
        # Initialize database
        sql_tool = SQLTool()
        
        # Save campaign to database
        campaign_data = {
            "name": campaign_name,
            "objective": objective,
            "target_audience": target_audience,
            "budget": budget,
            "duration_days": duration,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "running"
        }
        
        campaign_id = sql_tool.save_campaign(campaign_data)
        print(f"💾 Campaign saved to database (ID: {campaign_id})")
        
        # Run the multi-agent workflow
        results = run_campaign_brain(
            campaign_objective=objective,
            target_audience=target_audience,
            budget=budget,
            duration_days=duration,
            brand_guidelines=brand_guidelines
        )
        
        # Display results summary
        display_results_summary(results)
        
        # Save results if output file specified
        if output_file:
            save_results_to_file(results, output_file)
        
        print("\n🎉 Campaign planning completed successfully!")
        print("💡 Run with --mode ui to view results in the web dashboard")
        
    except Exception as e:
        print(f"\n❌ Error during campaign planning: {str(e)}")
        print("💡 Please check your configuration and try again")


def display_results_summary(results):
    """Display a summary of campaign planning results"""
    print("\n" + "=" * 60)
    print("📋 CAMPAIGN PLAN SUMMARY")
    print("=" * 60)
    
    # Campaign overview
    print(f"🎯 Objective: {results.get('campaign_objective', 'N/A')}")
    print(f"💰 Budget: ${results.get('budget', 0):,.2f}")
    print(f"📅 Duration: {results.get('duration_days', 0)} days")
    print(f"👥 Target: {results.get('target_audience', 'N/A')[:100]}{'...' if len(results.get('target_audience', '')) > 100 else ''}")
    
    # Agent completion status
    print(f"\n🤖 Agents Completed: {len(results.get('completed_agents', []))}")
    for agent in results.get('completed_agents', []):
        print(f"   ✅ {agent.replace('_', ' ').title()}")
    
    # Key insights
    trends = results.get('current_trends', [])
    # Filter out trends with empty names
    valid_trends = [t for t in trends if t.get('name', '').strip()]
    print(f"\n🔍 Trends Identified: {len(valid_trends)}")
    for i, trend in enumerate(valid_trends[:5], 1):
        trend_name = trend.get('name', 'Unknown Trend').strip()
        trend_info = f"{i}. {trend_name}"
        if trend.get('impact'):
            trend_info += f" (Impact: {trend.get('impact')})"
        print(f"   {trend_info}")
    
    personas = results.get('persona_profiles', [])
    # Filter out personas with empty names
    valid_personas = [p for p in personas if p.get('name', '').strip()]
    print(f"\n👥 Personas Created: {len(valid_personas)}")
    for i, persona in enumerate(valid_personas[:5], 1):
        persona_name = persona.get('name', f'Persona {i}').strip()
        persona_info = f"{i}. {persona_name}"
        if persona.get('age_range'):
            persona_info += f" ({persona.get('age_range')})"
        print(f"   {persona_info}")
    
    channels = results.get('channel_recommendations', [])
    print(f"\n📱 Recommended Channels: {len(channels)}")
    for i, channel in enumerate(channels[:5], 1):
        print(f"   {i}. {channel.get('name', 'Unknown Channel')} - ${channel.get('budget_allocation', 0):,.0f}")
    
    # Implementation readiness
    if results.get('presentation_ready'):
        print(f"\n✅ Campaign plan is ready for implementation!")
    else:
        print(f"\n⏳ Campaign plan is still in progress...")
    
    print("=" * 60)


def save_results_to_file(results, output_file: str):
    """Save campaign results to file"""
    import json
    
    try:
        # Prepare results for JSON serialization
        json_results = {
            "campaign_plan": results.get('final_campaign_plan', {}),
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "objective": results.get('campaign_objective'),
                "budget": results.get('budget'),
                "duration": results.get('duration_days'),
                "trends_count": len(results.get('current_trends', [])),
                "personas_count": len(results.get('persona_profiles', [])),
                "channels_count": len(results.get('channel_recommendations', [])),
                "ready": results.get('presentation_ready', False)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")


def run_demo():
    """Run a demonstration with sample data"""
    print("\n🎬 Running Campaign Brain Demo")
    print("=" * 40)
    
    # Demo campaign parameters
    demo_campaigns = [
        {
            "name": "Tech Product Launch Demo",
            "objective": "Launch a new AI-powered productivity app targeting remote workers and increase brand awareness while driving app downloads",
            "target_audience": "Remote workers, freelancers, and small business owners aged 25-45 who use multiple productivity tools",
            "budget": 75000,
            "duration": 30,
            "brand_guidelines": "Professional yet approachable, focus on productivity and efficiency"
        },
        {
            "name": "E-commerce Holiday Campaign",
            "objective": "Drive holiday sales for our online fashion store and increase customer acquisition",
            "target_audience": "Fashion-conscious millennials and Gen Z, aged 18-35, who shop online frequently",
            "budget": 50000,
            "duration": 45,
            "brand_guidelines": "Trendy, vibrant, youthful energy with focus on style and affordability"
        }
    ]
    
    print("Available demo campaigns:")
    for i, campaign in enumerate(demo_campaigns, 1):
        print(f"{i}. {campaign['name']}")
    
    try:
        choice = input(f"\nSelect demo campaign (1-{len(demo_campaigns)}) [1]: ").strip()
        choice = int(choice) if choice else 1
        
        if choice < 1 or choice > len(demo_campaigns):
            print("❌ Invalid choice, using first demo campaign")
            choice = 1
        
        demo_campaign = demo_campaigns[choice - 1]
        
        print(f"\n🚀 Running demo: {demo_campaign['name']}")
        
        run_campaign_with_params(**demo_campaign)
        
    except KeyboardInterrupt:
        print("\n❌ Demo cancelled by user")
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")


def launch_ui():
    """Launch the Streamlit UI dashboard"""
    print("\n🌐 Launching Campaign Brain Dashboard...")
    
    try:
        import streamlit
        import subprocess
        
        dashboard_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
        
        print("🚀 Starting Streamlit server...")
        print("📱 Dashboard will open in your web browser")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.port=8501",
            "--server.headless=false"
        ])
        
    except ImportError:
        print("❌ Streamlit not installed. Install with: pip install streamlit")
    except Exception as e:
        print(f"❌ Error launching UI: {str(e)}")


def run_tests():
    """Run basic system tests"""
    print("\n🧪 Running Campaign Brain Tests")
    print("=" * 40)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Configuration
    tests_total += 1
    try:
        config_client = Config.get_openai_client()
        if config_client:
            print("✅ Configuration test passed")
            tests_passed += 1
        else:
            print("❌ Configuration test failed")
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
    
    # Test 2: Database initialization
    tests_total += 1
    try:
        sql_tool = SQLTool()
        print("✅ Database initialization test passed")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
    
    # Test 3: Graph creation
    tests_total += 1
    try:
        graph = create_campaign_brain_graph()
        if graph:
            print("✅ Graph creation test passed")
            tests_passed += 1
        else:
            print("❌ Graph creation test failed")
    except Exception as e:
        print(f"❌ Graph creation test failed: {str(e)}")
    
    # Test 4: Data loader
    tests_total += 1
    try:
        data_loader = DataLoader()
        sample_data = data_loader.load_sample_campaign_data()
        if sample_data:
            print("✅ Data loader test passed")
            tests_passed += 1
        else:
            print("❌ Data loader test failed")
    except Exception as e:
        print(f"❌ Data loader test failed: {str(e)}")
    
    # Test summary
    print(f"\n📊 Test Results: {tests_passed}/{tests_total} passed")
    if tests_passed == tests_total:
        print("🎉 All tests passed! Campaign Brain is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)


def create_main_package_init():
    """Create the main package __init__.py file"""
    init_content = '''"""
Campaign Brain - AI-Powered Multi-Agent Campaign Planning System

A sophisticated system that uses multiple AI agents working together
to create comprehensive marketing campaign plans.

Components:
- Trend Scout: Market trend analysis
- Strategist: Campaign strategy development
- Persona Simulator: Audience insight generation
- Designer: Creative concept creation
- Executor: Implementation planning

Usage:
    from campaign_brain import run_campaign_brain
    
    results = run_campaign_brain(
        campaign_objective="Your campaign goal",
        target_audience="Your target audience",
        budget=50000,
        duration_days=30
    )
"""

from .graph.builder import run_campaign_brain, create_campaign_brain_graph
from .config import Config

__version__ = "1.0.0"
__author__ = "Campaign Brain Team"

__all__ = [
    "run_campaign_brain",
    "create_campaign_brain_graph", 
    "Config"
]'''
    
    try:
        init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
        with open(init_path, 'w') as f:
            f.write(init_content)
        print("✅ Created main package __init__.py")
    except Exception as e:
        print(f"❌ Error creating __init__.py: {str(e)}")


if __name__ == "__main__":
    # Ensure package is properly initialized
    create_main_package_init()
    
    # Run main application
    main()