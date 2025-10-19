"""
Tools for Action Agent
"""
import os
import json
import asyncio
from typing import Dict, List
import boto3


class ActionAgentTools:
    """Tools for helping freelancers take legal action"""
    
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    async def search_similar_cases(
        self,
        issue_type: str,
        jurisdiction: str,
        contract_text: str = "",
        keywords: str = ""
    ) -> Dict:
        """
        Search for similar legal cases using DuckDuckGo + Case.law
        
        Args:
            issue_type: 'non_payment', 'breach_of_contract', 'ip_theft', 'scope_creep'
            jurisdiction: 'usa', 'uk', 'eu'
            contract_text: Full contract text to extract key terms
            keywords: Additional search terms
        
        Returns:
            Dict with similar_cases list
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return {
                'error': 'duckduckgo-search not installed. Run: pip install duckduckgo-search',
                'similar_cases': [],
                'total_found': 0
            }
        
        # Extract key terms from contract if provided
        contract_keywords = ""
        if contract_text:
            # Simple keyword extraction - look for payment terms, deliverables, etc.
            important_terms = ['payment', 'net 30', 'deliverable', 'milestone', 'invoice', 
                             'breach', 'termination', 'intellectual property', 'copyright',
                             'scope', 'change request', 'additional work']
            contract_lower = contract_text.lower()
            found_terms = [term for term in important_terms if term in contract_lower]
            if found_terms:
                contract_keywords = ' '.join(found_terms[:3])  # Use top 3 terms
        
        # Construct search query with more specific legal terms
        issue_map = {
            'non_payment': 'freelancer payment dispute contract breach',
            'breach_of_contract': 'contract breach lawsuit freelancer',
            'ip_theft': 'intellectual property theft freelancer copyright',
            'scope_creep': 'scope creep additional work compensation freelancer'
        }
        
        base_query = issue_map.get(issue_type, issue_type)
        query = f"{base_query} {jurisdiction} case law legal precedent"
        
        if contract_keywords:
            query += f" {contract_keywords}"
        if keywords:
            query += f" {keywords}"
        
        print(f"🔍 Searching for: {query}")
        
        try:
            # Search DuckDuckGo (synchronous version is more stable)
            ddgs = DDGS()
            web_results = list(ddgs.text(
                query,
                max_results=15,  # Get more to filter out non-English
                region='us-en',  # Force English results
                safesearch='off'
            ))
            
            # Parse and filter results
            cases = []
            for result in web_results:
                title = result.get('title', 'Untitled')
                body = result.get('body', 'No summary available')
                url = result.get('href', '')
                
                # Filter out non-English results (basic check for Chinese/other characters)
                if self._is_english_text(title) and self._is_english_text(body):
                    # Filter for legal content
                    is_legal = any(term in title.lower() or term in body.lower() 
                                  for term in ['case', 'court', 'lawsuit', 'legal', 'law', 
                                              'contract', 'dispute', 'attorney', 'claim'])
                    
                    if is_legal or len(cases) < 3:  # Keep at least 3 results
                        cases.append({
                            'title': title,
                            'summary': body[:300] + '...' if len(body) > 300 else body,
                            'source_url': url,
                            'source_type': 'web_search',
                            'relevance_score': 0.9 if is_legal else 0.6
                        })
            
            print(f"✅ Found {len(cases)} cases from web search")
            
            # If no cases found, provide fallback resources
            if not cases:
                print("⚠️ No web results, providing fallback legal resources")
                cases = self._get_fallback_cases(issue_type, jurisdiction)
            
            return {
                'similar_cases': cases,
                'total_found': len(cases),
                'search_query': query
            }
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            # Provide fallback cases instead of empty result
            fallback_cases = self._get_fallback_cases(issue_type, jurisdiction)
            return {
                'error': f'Search failed: {str(e)}',
                'similar_cases': fallback_cases,
                'total_found': len(fallback_cases),
                'note': 'Showing curated legal resources due to search limitations'
            }
    
    def _is_english_text(self, text: str) -> bool:
        """Check if text is primarily English (filter out Chinese, etc.)"""
        if not text:
            return False
        
        # Count ASCII printable characters (English uses these)
        ascii_count = sum(1 for c in text if ord(c) < 128)
        total_chars = len(text)
        
        # If >70% ASCII, consider it English
        return (ascii_count / total_chars) > 0.7 if total_chars > 0 else False
    
    def _get_fallback_cases(self, issue_type: str, jurisdiction: str) -> List[Dict]:
        """Provide curated legal case references when web search fails"""
        fallback_resources = {
            'non_payment': [
                {
                    'title': 'Freelancer Payment Disputes - Small Claims Court Guide',
                    'summary': 'Most freelancer payment disputes under $10,000 are resolved in small claims court. Courts typically rule in favor of freelancers who can prove: 1) Valid contract, 2) Work completed as agreed, 3) Invoice sent, 4) No payment received. Success rate: 70-85%.',
                    'source_url': 'https://www.nolo.com/legal-encyclopedia/small-claims-suits-freelancers.html',
                    'source_type': 'legal_guide',
                    'relevance_score': 0.9
                },
                {
                    'title': 'Independent Contractor Payment Rights',
                    'summary': 'Under contract law, when services are delivered as specified, payment is legally obligated within the agreed timeframe. Freelancers have the right to pursue legal action for breach of contract, including claiming interest and legal fees in many jurisdictions.',
                    'source_url': 'https://www.freelancersunion.org/resources/legal/',
                    'source_type': 'legal_reference',
                    'relevance_score': 0.85
                },
                {
                    'title': 'Contract Breach - Failure to Pay for Services',
                    'summary': 'Legal precedent strongly supports service providers when: contract terms are clear, deliverables were accepted, and payment terms were violated. Most courts award full payment plus interest (typically 6-10% annually) and may include attorney fees if contract specifies.',
                    'source_url': 'https://www.avvo.com/legal-guides/contract-disputes',
                    'source_type': 'case_law_summary',
                    'relevance_score': 0.8
                }
            ],
            'breach_of_contract': [
                {
                    'title': 'Material Breach of Contract - Freelancer Cases',
                    'summary': 'When one party fails to fulfill contractual obligations, the non-breaching party may seek remedies including: specific performance, monetary damages, or contract termination with compensation. Courts examine whether breach was material (significant) or minor.',
                    'source_url': 'https://www.nolo.com/legal-encyclopedia/material-breach-contract.html',
                    'source_type': 'legal_guide',
                    'relevance_score': 0.9
                },
                {
                    'title': 'Early Termination Without Cause - Contractor Rights',
                    'summary': 'If contract is terminated without just cause, freelancers typically entitled to: payment for completed work, compensation for work in progress, and potentially damages for lost future earnings specified in contract term.',
                    'source_url': 'https://www.freelegaladvice.org/contract-termination',
                    'source_type': 'legal_reference',
                    'relevance_score': 0.85
                }
            ],
            'ip_theft': [
                {
                    'title': 'Copyright Infringement - Freelance Work',
                    'summary': 'Unless contract explicitly states "work for hire," freelancer retains copyright to created work. Unauthorized use constitutes copyright infringement. Remedies include: cease and desist, damages ($750-$30,000 per work), and injunctive relief.',
                    'source_url': 'https://www.copyright.gov/help/faq/faq-fairuse.html',
                    'source_type': 'legal_guide',
                    'relevance_score': 0.9
                },
                {
                    'title': 'Work-for-Hire vs. Retained Rights',
                    'summary': 'Critical distinction: work-for-hire transfers all rights to client, while retained rights (default for freelancers) means creator keeps copyright. Review contract carefully. If no work-for-hire clause exists, you likely own the IP.',
                    'source_url': 'https://www.legalzoom.com/articles/work-for-hire-agreement',
                    'source_type': 'legal_reference',
                    'relevance_score': 0.85
                }
            ],
            'scope_creep': [
                {
                    'title': 'Scope Creep and Additional Compensation',
                    'summary': 'When client requests work beyond original scope, freelancer is entitled to additional compensation. Courts recognize: 1) Original scope is the contract, 2) Additional work = new agreement needed, 3) Work performed creates implied contract for reasonable payment.',
                    'source_url': 'https://www.nolo.com/legal-encyclopedia/contract-modifications.html',
                    'source_type': 'legal_guide',
                    'relevance_score': 0.9
                },
                {
                    'title': 'Quantum Meruit - Payment for Extra Work',
                    'summary': 'Legal principle "quantum meruit" (as much as deserved) allows freelancers to recover fair market value for work performed beyond contract scope, even without explicit agreement. Courts calculate based on: hours worked, market rates, and value delivered.',
                    'source_url': 'https://www.law.cornell.edu/wex/quantum_meruit',
                    'source_type': 'case_law_summary',
                    'relevance_score': 0.85
                }
            ]
        }
        
        return fallback_resources.get(issue_type, fallback_resources['breach_of_contract'])
    
    async def generate_action_plan(
        self,
        issue_description: str,
        jurisdiction: str,
        amount_at_stake: float,
        days_since_issue: int
    ) -> Dict:
        """
        Generate personalized step-by-step action plan using Claude
        
        Returns:
            Dict with immediate_actions, short_term, long_term, etc.
        """
        print(f"📋 Generating action plan for {jurisdiction}, ${amount_at_stake}")
        
        prompt = f"""You are a legal advisor helping a freelancer resolve a contract dispute.

Issue: {issue_description}
Jurisdiction: {jurisdiction.upper()}
Amount at stake: ${amount_at_stake}
Days since issue started: {days_since_issue}

Generate a detailed, actionable plan with:

1. IMMEDIATE ACTIONS (next 24 hours):
   - Urgent steps they should take right now
   - Clear, specific actions

2. SHORT-TERM ACTIONS (next 7 days):
   - Evidence collection
   - Formal notices to send
   - Documentation to gather

3. LONG-TERM ACTIONS (next 30 days):
   - Legal action steps if needed
   - Court filing procedures
   - Enforcement options

4. ESTIMATED TIMELINE: How long to resolution

5. ESTIMATED COST: Cost range for each path

6. SUCCESS PROBABILITY: Based on similar cases, estimate chances (e.g., "75% - strong precedent")

Format your response as valid JSON with these exact keys:
{{
  "immediate_actions": ["action 1", "action 2", ...],
  "short_term_actions": ["action 1", "action 2", ...],
  "long_term_actions": ["action 1", "action 2", ...],
  "estimated_duration": "X weeks/months",
  "estimated_cost": "$X-Y",
  "success_probability": "XX% - reason"
}}"""

        try:
            # Try Claude 3.5 Sonnet (more widely available) or fall back to Haiku
            model_ids = [
                'us.anthropic.claude-3-5-sonnet-20241022-v2:0',  # Claude 3.5 Sonnet v2
                'anthropic.claude-3-5-sonnet-20240620-v1:0',      # Claude 3.5 Sonnet v1
                'anthropic.claude-3-haiku-20240307-v1:0'          # Claude 3 Haiku (cheaper fallback)
            ]
            
            response = None
            last_error = None
            
            for model_id in model_ids:
                try:
                    response = self.bedrock_runtime.invoke_model(
                        modelId=model_id,
                        body=json.dumps({
                            'anthropic_version': 'bedrock-2023-05-31',
                            'messages': [{'role': 'user', 'content': prompt}],
                            'max_tokens': 2000,
                            'temperature': 0.7
                        })
                    )
                    print(f"✅ Using model: {model_id}")
                    break
                except Exception as e:
                    last_error = e
                    print(f"⚠️ Model {model_id} failed: {str(e)[:100]}")
                    continue
            
            if not response:
                raise last_error or Exception("All Bedrock models failed")
            
            result = json.loads(response['body'].read())
            content = result['content'][0]['text']
            
            # Try to parse as JSON
            try:
                # Extract JSON from markdown code blocks if present
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                action_plan = json.loads(content)
                print(f"✅ Action plan generated")
                return action_plan
                
            except json.JSONDecodeError:
                # Fallback: return as structured text
                print(f"⚠️ Could not parse JSON, returning text")
                return {
                    'immediate_actions': [content],
                    'short_term_actions': [],
                    'long_term_actions': [],
                    'estimated_duration': 'Unknown',
                    'estimated_cost': 'Unknown',
                    'success_probability': 'Unknown'
                }
                
        except Exception as e:
            print(f"❌ Action plan error: {str(e)}")
            return {
                'error': f'Failed to generate plan: {str(e)}',
                'immediate_actions': [],
                'short_term_actions': [],
                'long_term_actions': []
            }
    
    def get_evidence_checklist(self, issue_type: str) -> Dict:
        """
        Get evidence collection checklist for specific issue type
        
        Returns:
            Dict with critical_evidence, supporting_evidence, tips
        """
        print(f"📝 Getting evidence checklist for: {issue_type}")
        
        checklists = {
            'non_payment': {
                'critical_evidence': [
                    '✓ Original signed contract with payment terms',
                    '✓ All invoices sent to client',
                    '✓ Proof of work delivered (files, screenshots, commits)',
                    '✓ Email trail showing work was approved',
                    '✓ Payment reminders you sent'
                ],
                'supporting_evidence': [
                    '✓ Time tracking logs',
                    '✓ Communication showing scope was met',
                    '✓ Bank statements (no payment received)',
                    '✓ Client testimonials about your work'
                ],
                'optional_evidence': [
                    '✓ Similar projects you completed',
                    '✓ Industry standard payment terms',
                    '✓ Witness statements from other freelancers'
                ],
                'deadline': '7 days (before filing claim)',
                'tips': [
                    'Screenshot all emails before client deletes them',
                    'Download all project files you delivered',
                    'Get written statements from anyone who saw the work',
                    'Calculate exact amount owed including late fees'
                ]
            },
            'breach_of_contract': {
                'critical_evidence': [
                    '✓ Original contract with all amendments',
                    '✓ Proof of breach (emails, screenshots)',
                    '✓ Evidence you upheld your end',
                    '✓ Attempts to resolve amicably',
                    '✓ Documentation of damages'
                ],
                'supporting_evidence': [
                    '✓ Timeline of events',
                    '✓ Third-party communications',
                    '✓ Financial impact calculations',
                    '✓ Expert opinions if needed'
                ],
                'optional_evidence': [
                    '✓ Similar cases in your jurisdiction',
                    '✓ Industry standards violated',
                    '✓ Character references'
                ],
                'deadline': '7-14 days',
                'tips': [
                    'Document everything in chronological order',
                    'Keep original files (not copies)',
                    'Get lawyer to review before filing',
                    'Calculate all damages including opportunity cost'
                ]
            },
            'ip_theft': {
                'critical_evidence': [
                    '✓ Original contract specifying IP ownership',
                    '✓ Proof you created the work (timestamps, git commits)',
                    '✓ Evidence of unauthorized use',
                    '✓ Attempts to request takedown',
                    '✓ Financial harm calculations'
                ],
                'supporting_evidence': [
                    '✓ Copyright registration (if any)',
                    '✓ Industry expert opinion on originality',
                    '✓ Market value of stolen IP',
                    "✓ Client's revenue from stolen work"
                ],
                'optional_evidence': [
                    '✓ Similar IP theft cases',
                    '✓ Trademark registrations',
                    "✓ Client's past behavior"
                ],
                'deadline': '3-7 days (IP theft is time-sensitive)',
                'tips': [
                    'File copyright/trademark if you haven\'t',
                    'Send cease and desist immediately',
                    'Document every use of your work',
                    'Consult IP lawyer (this is complex)'
                ]
            },
            'scope_creep': {
                'critical_evidence': [
                    '✓ Original contract with defined scope',
                    '✓ All change requests from client',
                    '✓ Your responses about additional costs',
                    '✓ Work done beyond original scope',
                    '✓ Time/cost of extra work'
                ],
                'supporting_evidence': [
                    '✓ Industry standards for similar projects',
                    '✓ Quotes for additional work',
                    '✓ Communication about scope boundaries',
                    '✓ Time tracking for extra work'
                ],
                'optional_evidence': [
                    '✓ Similar projects scope definitions',
                    '✓ Expert opinion on reasonable scope',
                    '✓ Other freelancers\' experiences'
                ],
                'deadline': '7 days',
                'tips': [
                    'Calculate hours spent beyond original scope',
                    'Document every "one more thing" request',
                    'Show you communicated boundaries',
                    'Prove extra work has value'
                ]
            }
        }
        
        return checklists.get(issue_type, checklists['breach_of_contract'])
    
    def get_legal_resources(
        self,
        jurisdiction: str,
        issue_type: str,
        amount_at_stake: float
    ) -> Dict:
        """
        Get legal resources specific to jurisdiction
        
        Returns:
            Dict with small_claims_info, free_legal_aid, lawyer_referral, costs
        """
        print(f"⚖️ Getting legal resources for {jurisdiction}")
        
        resources = {
            'usa': {
                'small_claims_limit': 10000,
                'small_claims_info': {
                    'court_website': 'https://www.nolo.com/legal-encyclopedia/small-claims-court',
                    'filing_fee': '$30-100 (varies by state)',
                    'process_time': '1-3 months',
                    'lawyer_needed': False,
                    'description': 'Small claims court is designed for self-representation. You can file online in most states.'
                },
                'free_legal_aid': [
                    {
                        'name': 'Legal Services Corporation',
                        'url': 'https://www.lsc.gov/what-legal-aid/find-legal-aid',
                        'phone': 'Call 211 for local resources',
                        'eligibility': 'Low income (below 125% poverty line)'
                    },
                    {
                        'name': 'American Bar Association Free Legal Answers',
                        'url': 'https://abafreelegalanswers.org/',
                        'eligibility': 'Low/moderate income - get free legal advice online'
                    }
                ],
                'lawyer_referral': [
                    {
                        'name': 'American Bar Association Lawyer Referral',
                        'url': 'https://www.americanbar.org/groups/legal_services/flh-home/',
                        'cost': '$25-50 consultation fee'
                    },
                    {
                        'name': 'Rocket Lawyer',
                        'url': 'https://www.rocketlawyer.com/',
                        'cost': '$40/month membership + discounted lawyer fees'
                    }
                ],
                'estimated_costs': {
                    'small_claims': '$30-200 total (filing + service fees)',
                    'mediation': '$500-1500 (split with other party)',
                    'lawyer_hourly': '$200-400/hour',
                    'lawyer_flat_fee': '$2000-5000 for simple case',
                    'contingency_fee': '30-40% of recovery if you win'
                }
            },
            'uk': {
                'small_claims_limit': 10000,  # £10,000
                'small_claims_info': {
                    'court_website': 'https://www.gov.uk/make-court-claim-for-money',
                    'filing_fee': '£25-455 (based on claim amount)',
                    'process_time': '3-6 months',
                    'lawyer_needed': False,
                    'description': 'Money Claim Online (MCOL) service makes it easy to file claims up to £100,000.'
                },
                'free_legal_aid': [
                    {
                        'name': 'Civil Legal Advice',
                        'url': 'https://www.gov.uk/civil-legal-advice',
                        'phone': '0345 345 4 345',
                        'eligibility': 'Means-tested - check if you qualify'
                    },
                    {
                        'name': 'Citizens Advice',
                        'url': 'https://www.citizensadvice.org.uk/',
                        'phone': '0800 144 8848',
                        'eligibility': 'Free for everyone - expert advice on legal rights'
                    }
                ],
                'lawyer_referral': [
                    {
                        'name': 'Law Society Find a Solicitor',
                        'url': 'https://solicitors.lawsociety.org.uk/',
                        'cost': '£200-400/hour typical'
                    }
                ],
                'estimated_costs': {
                    'small_claims': '£25-455 court fees',
                    'mediation': '£300-1000',
                    'solicitor_hourly': '£200-400/hour',
                    'solicitor_flat_fee': '£1500-4000'
                }
            },
            'eu': {
                'small_claims_limit': 5000,  # €5,000
                'small_claims_info': {
                    'court_website': 'https://e-justice.europa.eu/489/EN/small_claims',
                    'filing_fee': 'Varies by country (€50-200 typical)',
                    'process_time': '3-9 months',
                    'lawyer_needed': False,
                    'description': 'EU Small Claims Procedure available for cross-border disputes under €5,000.'
                },
                'free_legal_aid': [
                    {
                        'name': 'EU Legal Aid Directory',
                        'url': 'https://e-justice.europa.eu/325/EN/legal_aid',
                        'eligibility': 'Varies by country - check your national system'
                    }
                ],
                'lawyer_referral': [
                    {
                        'name': 'Local Bar Association',
                        'note': 'Contact bar association in your country',
                        'cost': '€150-300/hour typical'
                    }
                ],
                'estimated_costs': {
                    'small_claims': '€50-300 court fees',
                    'mediation': '€500-1500',
                    'lawyer_hourly': '€150-300/hour',
                    'lawyer_flat_fee': '€2000-5000'
                }
            }
        }
        
        jurisdiction_data = resources.get(jurisdiction, resources['usa'])
        
        # Recommend path based on amount
        if amount_at_stake <= jurisdiction_data['small_claims_limit']:
            recommended_path = 'small_claims'
            reason = f"Amount (${amount_at_stake}) is within small claims limit. Cost-effective DIY option."
        elif amount_at_stake <= 25000:
            recommended_path = 'lawyer'
            reason = f"Amount (${amount_at_stake}) justifies hiring a lawyer. Consider contingency fee (30-40%)."
        else:
            recommended_path = 'lawyer'
            reason = f"High stakes (${amount_at_stake}). Definitely hire an experienced lawyer."
        
        return {
            **jurisdiction_data,
            'recommended_path': recommended_path,
            'recommendation_reason': reason,
            'amount_at_stake': amount_at_stake
        }


# Test the tools
async def test_tools():
    """Test all tools"""
    tools = ActionAgentTools()
    
    print("\n🧪 Testing Action Agent Tools\n")
    
    # Test 1: Search similar cases
    print("=" * 60)
    print("TEST 1: Search Similar Cases")
    print("=" * 60)
    result = await tools.search_similar_cases(
        issue_type='non_payment',
        jurisdiction='usa',
        keywords='small claims'
    )
    print(f"Found {result['total_found']} cases")
    if result.get('similar_cases'):
        print(f"First case: {result['similar_cases'][0]['title']}")
    
    # Test 2: Generate action plan
    print("\n" + "=" * 60)
    print("TEST 2: Generate Action Plan")
    print("=" * 60)
    plan = await tools.generate_action_plan(
        issue_description="Client won't pay $5,000 for completed website. Contract says Net 30, it's been 90 days.",
        jurisdiction='usa',
        amount_at_stake=5000,
        days_since_issue=90
    )
    print(f"Success probability: {plan.get('success_probability', 'N/A')}")
    
    # Test 3: Evidence checklist
    print("\n" + "=" * 60)
    print("TEST 3: Evidence Checklist")
    print("=" * 60)
    checklist = tools.get_evidence_checklist('non_payment')
    print(f"Critical evidence items: {len(checklist['critical_evidence'])}")
    print(f"Deadline: {checklist['deadline']}")
    
    # Test 4: Legal resources
    print("\n" + "=" * 60)
    print("TEST 4: Legal Resources")
    print("=" * 60)
    resources = tools.get_legal_resources('usa', 'non_payment', 5000)
    print(f"Recommended path: {resources['recommended_path']}")
    print(f"Reason: {resources['recommendation_reason']}")
    
    print("\n✅ All tools tested!")


if __name__ == "__main__":
    asyncio.run(test_tools())
