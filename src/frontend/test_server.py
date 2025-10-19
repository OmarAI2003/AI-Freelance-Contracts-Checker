"""
Simple local test server for Action Agent frontend
Run this to test the Action Agent without AWS deployment
"""

import json
import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs
import sys
import os

# Add parent directory to path to import agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.action.agent import ActionAgent


class ActionAgentHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves frontend and processes Action Agent requests"""
    
    def do_GET(self):
        """Serve the HTML file"""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/action_agent_test.html'
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle Action Agent API requests"""
        if self.path == '/api/action-agent/analyze':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                # Extract parameters
                contract_text = data.get('contract_text', '')
                issue_description = data.get('issue_description', '')
                amount = data.get('amount_at_stake', 0)
                jurisdiction = data.get('jurisdiction', 'usa')
                freelancer_info = data.get('freelancer_info', {})
                
                print(f"\n🔍 Analyzing issue: {issue_description[:100]}...")
                print(f"💰 Amount: ${amount}")
                print(f"📍 Jurisdiction: {jurisdiction.upper()}")
                if contract_text:
                    print(f"📄 Contract provided: {len(contract_text)} characters")
                
                # Initialize agent
                agent = ActionAgent()
                
                # Run analysis (synchronous wrapper for async)
                result = asyncio.run(agent.analyze(
                    contract_text=contract_text,
                    issue_description=issue_description,
                    jurisdiction=jurisdiction,
                    freelancer_info=freelancer_info,
                    amount_at_stake=amount
                ))
                
                print("✅ Analysis complete!")
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Send error response
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    'error': str(e),
                    'message': 'Failed to analyze issue. Check server logs for details.'
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def main():
    """Start the test server"""
    # Change to frontend directory
    os.chdir(os.path.dirname(__file__))
    
    port = 8000
    server = HTTPServer(('localhost', port), ActionAgentHandler)
    
    print("\n" + "="*60)
    print("🚀 ContractGuard Action Agent Test Server")
    print("="*60)
    print(f"\n✅ Server running at: http://localhost:{port}")
    print(f"✅ Frontend available at: http://localhost:{port}/action_agent_test.html")
    print("\n📋 Make sure you have installed dependencies:")
    print("   pip install duckduckgo-search aiohttp boto3")
    print("\n🔑 Make sure AWS credentials are configured (already done)")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        server.shutdown()


if __name__ == '__main__':
    main()
