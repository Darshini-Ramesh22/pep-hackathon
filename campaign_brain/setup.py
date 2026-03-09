#!/usr/bin/env python
"""
Campaign Brain Setup Script
Quick setup for the hackathon project
"""

import os
import sys
import subprocess
import shutil

def print_header():
    print("🧠" + "="*50 + "🧠")
    print("    Campaign Brain - Quick Setup Script")
    print("    AI-Powered Campaign Planning System")
    print("🧠" + "="*50 + "🧠")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_environment():
    """Set up environment file"""
    print("\n🔧 Setting up environment...")
    
    if not os.path.exists(".env"):
        if os.path.exists(".env.template"):
            shutil.copy(".env.template", ".env")
            print("✅ Created .env file from template")
            print("💡 Please edit .env file with your API keys")
        else:
            # Create basic .env file
            with open(".env", "w") as f:
                f.write("# Campaign Brain Environment Variables\n")
                f.write("AI_GATEWAY_API_KEY=sk-samplekey123\n")
                f.write("DATABASE_URL=sqlite:///campaign_data.db\n")
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")
    
    return True

def test_installation():
    """Test if everything is working"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        sys.path.append(os.getcwd())
        from config import Config
        from tools.sql_tool import SQLTool
        from graph.builder import create_campaign_brain_graph
        
        print("✅ All imports successful")
        
        # Test database
        sql_tool = SQLTool()
        print("✅ Database initialization successful")
        
        # Test graph creation
        graph = create_campaign_brain_graph()
        print("✅ LangGraph workflow creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def show_usage_examples():
    """Show how to use the system"""
    print("\n🚀 Campaign Brain is ready! Here's how to use it:")
    print("\n" + "="*60)
    
    print("\n1️⃣  Interactive Mode (Recommended for first time):")
    print("   python app.py --mode interactive")
    
    print("\n2️⃣  Web Dashboard (Best for presentations):")
    print("   python app.py --mode ui")
    print("   Then open http://localhost:8501")
    
    print("\n3️⃣  Demo Mode (Great for showcasing):")
    print("   python app.py --mode demo")
    
    print("\n4️⃣  Command Line:")
    print('   python app.py --mode interactive \\')
    print('     --objective "Launch new product" \\')
    print('     --audience "Young professionals" \\')
    print('     --budget 50000')
    
    print("\n5️⃣  Test System:")
    print("   python app.py --mode test")
    
    print("\n" + "="*60)
    print("💡 For hackathon demo, we recommend starting with:")
    print("   python app.py --mode demo")
    print("💡 Then show the dashboard with:")
    print("   python app.py --mode ui")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n⚠️  Some tests failed, but you can still try running the application")
    
    # Show usage
    show_usage_examples()
    
    print("\n🎉 Setup completed successfully!")
    print("🏆 Campaign Brain is ready for the hackathon!")

if __name__ == "__main__":
    main()