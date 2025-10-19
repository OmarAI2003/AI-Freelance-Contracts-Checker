"""
Quick Start - Test the Frontend with Dummy Agents
Run this to test the UI and orchestration logic before teammates deploy their agents
"""

import subprocess
import sys
import os
import webbrowser
import time

def check_dependencies():
    """Check if required packages are installed."""
    print("🔍 Checking dependencies...")
    try:
        import flask
        import flask_cors
        import boto3
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("\n🔐 Checking AWS credentials...")
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        account = identity['Account']
        user = identity['Arn'].split('/')[-1]
        print(f"✅ AWS configured - Account: {account}, User: {user}")
        return True
    except Exception as e:
        print(f"⚠️  AWS credentials not configured or invalid")
        print(f"   Error: {e}")
        print("\n   Run: aws configure")
        print("   Account: 897722703585")
        print("   Region: us-east-1")
        return False

def create_uploads_dir():
    """Create uploads directory if it doesn't exist."""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Created uploads/ directory")

def print_welcome():
    """Print welcome message with instructions."""
    print("\n" + "="*60)
    print("🚀 Freelancer Legal Assistant - Frontend Test")
    print("="*60)
    print("\n📋 What's Working:")
    print("   ✅ Beautiful landing page with file upload")
    print("   ✅ Modern chat interface")
    print("   ✅ Intent classification")
    print("   ✅ Agent routing logic")
    print("   ✅ Action Agent (REAL - deployed to AWS)")
    print("   ⏳ Analysis Agent (Dummy - awaiting Dev 1)")
    print("   ⏳ Explanation Agent (Dummy - awaiting Dev 2)")
    print("   ⏳ Negotiation Agent (Dummy - awaiting Dev 3)")
    
    print("\n🧪 Test Scenarios:")
    print("   1. Type: 'My client won't pay me' → Routes to Action Agent ✅")
    print("   2. Type: 'Can you analyze this contract?' → Shows dummy Analysis")
    print("   3. Type: 'What does indemnification mean?' → Shows dummy Explanation")
    print("   4. Type: 'I want to negotiate terms' → Shows dummy Negotiation")
    
    print("\n💡 Debug Commands (in browser console):")
    print("   - debugState() - View application state")
    print("   - testAllAgents() - Test all agent UI components")
    
    print("\n" + "="*60)
    print("🌐 Server starting on: http://localhost:5000")
    print("="*60 + "\n")

def main():
    """Run the quick start test."""
    print("🎬 Freelancer Legal Assistant - Quick Start\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Failed to install dependencies")
        return
    
    # Check AWS
    aws_ok = check_aws_credentials()
    if not aws_ok:
        print("\n⚠️  Continuing without AWS (dummy responses only)")
    
    # Create directories
    create_uploads_dir()
    
    # Print welcome
    print_welcome()
    
    # Open browser after short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Flask app
    print("⏳ Starting Flask server...\n")
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thanks for testing!")
        print("💡 Next steps:")
        print("   1. Get agent ARNs from teammates when ready")
        print("   2. Update AGENT_ARNS in app.py")
        print("   3. Test A2A communication with real agents")

if __name__ == "__main__":
    main()
