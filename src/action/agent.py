"""
Action Agent - AWS Bedrock Agent
Helps freelancers take legal action on signed problematic contracts
"""
import json
import boto3
from typing import Dict
from .tools import ActionAgentTools


class ActionAgent:
    """Action Agent for post-signing contract disputes"""
    
    def __init__(self, config_path='src/infrastructure/config.json'):
        """Initialize Action Agent"""
        # Load config
        try:
            with open(config_path) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Config not found: {config_path}")
            self.config = {
                'region': 'us-east-1',
                'model_id': 'us.anthropic.claude-3-7-sonnet-20250219-v1:0'
            }
        
        self.tools = ActionAgentTools()
        self.bedrock = boto3.client('bedrock-runtime', region_name=self.config['region'])
    
    async def analyze(
        self,
        contract_text: str,
        issue_description: str,
        jurisdiction: str,
        freelancer_info: Dict,
        amount_at_stake: float = 0
    ) -> Dict:
        """
        Main analysis method - coordinates all tools
        
        Args:
            contract_text: The signed contract
            issue_description: What problem they're facing
            jurisdiction: 'usa', 'uk', 'eu'
            freelancer_info: User details
            amount_at_stake: Money involved
        
        Returns:
            Complete analysis with action plan, cases, evidence, resources
        """
        print(f"\n🚀 Action Agent: Analyzing dispute...")
        print(f"   Jurisdiction: {jurisdiction.upper()}")
        print(f"   Amount: ${amount_at_stake}")
        
        # Determine issue type from description
        issue_type = self._classify_issue(issue_description)
        print(f"   Issue type: {issue_type}")
        
        # Calculate days since issue
        days_since_issue = 30  # Default, could parse from user input
        
        results = {}
        
        # Step 1: Search for similar cases
        print("\n📚 Step 1: Searching for similar cases...")
        results['similar_cases'] = await self.tools.search_similar_cases(
            issue_type=issue_type,
            jurisdiction=jurisdiction,
            contract_text=contract_text,  # Pass contract to improve search
            keywords=f"{freelancer_info.get('role', 'freelancer')} contract"
        )
        
        # Step 2: Generate action plan
        print("\n📋 Step 2: Generating action plan...")
        results['action_plan'] = await self.tools.generate_action_plan(
            issue_description=issue_description,
            jurisdiction=jurisdiction,
            amount_at_stake=amount_at_stake,
            days_since_issue=days_since_issue
        )
        
        # Step 3: Get evidence checklist
        print("\n📝 Step 3: Creating evidence checklist...")
        results['evidence_checklist'] = self.tools.get_evidence_checklist(issue_type)
        
        # Step 4: Get legal resources
        print("\n⚖️ Step 4: Finding legal resources...")
        results['legal_resources'] = self.tools.get_legal_resources(
            jurisdiction=jurisdiction,
            issue_type=issue_type,
            amount_at_stake=amount_at_stake
        )
        
        # Step 5: Generate overall assessment
        print("\n🎯 Step 5: Creating overall assessment...")
        results['overall_assessment'] = await self._generate_assessment(
            issue_description,
            results,
            jurisdiction,
            amount_at_stake
        )
        
        # Add metadata
        results['metadata'] = {
            'issue_type': issue_type,
            'jurisdiction': jurisdiction,
            'amount_at_stake': amount_at_stake,
            'freelancer_role': freelancer_info.get('role', 'Unknown')
        }
        
        print("\n✅ Action Agent: Analysis complete!")
        
        return results
    
    def _classify_issue(self, description: str) -> str:
        """Classify the issue type from description"""
        description_lower = description.lower()
        
        # Priority order matters - check most specific first
        # Check for payment issues (most common for freelancers)
        payment_keywords = ['not paid', 'no payment', 'won\'t pay', 'non-payment', 'unpaid', 
                           'haven\'t received payment', 'refuses to pay', 'payment overdue',
                           'invoice', 'billing', 'money owed', 'hasn\'t paid', 'didn\'t pay']
        if any(word in description_lower for word in payment_keywords):
            return 'non_payment'
        
        # Check for scope creep
        scope_keywords = ['scope creep', 'extra work', 'more work', 'additional work', 
                         'beyond scope', 'additional features', 'more hours', 'unpaid work']
        if any(word in description_lower for word in scope_keywords):
            return 'scope_creep'
        
        # Check for IP theft (only if explicit IP/copyright terms)
        ip_keywords = ['copyright infringement', 'stole my work', 'using my code without permission',
                      'unauthorized use', 'intellectual property theft', 'my intellectual property']
        if any(word in description_lower for word in ip_keywords):
            return 'ip_theft'
        
        # Default to breach of contract
        return 'breach_of_contract'
    
    async def _generate_assessment(
        self,
        issue_description: str,
        analysis_results: Dict,
        jurisdiction: str,
        amount: float
    ) -> Dict:
        """Generate overall assessment using Claude"""
        
        # Extract key info
        similar_cases_count = len(analysis_results.get('similar_cases', {}).get('similar_cases', []))
        success_prob = analysis_results.get('action_plan', {}).get('success_probability', 'Unknown')
        recommended_path = analysis_results.get('legal_resources', {}).get('recommended_path', 'unknown')
        
        prompt = f"""Based on this freelancer contract dispute analysis, provide a clear overall assessment.

Issue: {issue_description}
Jurisdiction: {jurisdiction.upper()}
Amount at stake: ${amount}

Analysis findings:
- Found {similar_cases_count} similar cases
- Success probability: {success_prob}
- Recommended path: {recommended_path}

Provide a 2-3 sentence overall assessment and recommendation. Be realistic but supportive.
Format as JSON: {{"assessment": "...", "recommendation": "...", "next_immediate_step": "..."}}"""

        try:
            response = self.bedrock.invoke_model(
                modelId=self.config['model_id'],
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 500,
                    'temperature': 0.7
                })
            )
            
            result = json.loads(response['body'].read())
            content = result['content'][0]['text']
            
            # Try to parse JSON
            try:
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                return json.loads(content)
            except:
                return {
                    'assessment': content,
                    'recommendation': 'Follow the action plan provided',
                    'next_immediate_step': 'Review evidence checklist'
                }
                
        except Exception as e:
            print(f"⚠️ Assessment generation failed: {e}")
            return {
                'assessment': f'Contract dispute involving ${amount}. {similar_cases_count} similar cases found.',
                'recommendation': f'Recommended path: {recommended_path}',
                'next_immediate_step': 'Collect evidence from checklist'
            }


# Test the agent
async def test_agent():
    """Test the Action Agent"""
    print("\n🧪 Testing Action Agent\n")
    print("=" * 60)
    
    agent = ActionAgent()
    
    # Test scenario: Non-payment issue
    result = await agent.analyze(
        contract_text="[Contract text here]",
        issue_description="I delivered a $5,000 website 2 months ago but the client won't pay. The contract says Net 30 payment terms. I've sent 3 payment reminders but they keep making excuses.",
        jurisdiction='usa',
        freelancer_info={
            'role': 'Web Developer',
            'experience_years': 5,
            'location': 'California'
        },
        amount_at_stake=5000
    )
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    print(f"\nIssue Type: {result['metadata']['issue_type']}")
    print(f"Similar Cases Found: {result['similar_cases']['total_found']}")
    print(f"Success Probability: {result['action_plan'].get('success_probability', 'N/A')}")
    print(f"Recommended Path: {result['legal_resources']['recommended_path']}")
    print(f"\nOverall Assessment: {result['overall_assessment'].get('assessment', 'N/A')}")
    print(f"Next Step: {result['overall_assessment'].get('next_immediate_step', 'N/A')}")
    
    print("\n✅ Agent test complete!")
    
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())
