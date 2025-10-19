"""
Action Agent - Freelancer Contract Dispute Resolution
Built with AWS Bedrock AgentCore + Strands SDK

This agent helps freelancers take action after contract disputes.
Uses conversational AI to gather context and provide actionable guidance.
"""

import os
import logging
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
import boto3
import json
from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AgentCore App
app = BedrockAgentCoreApp()

# ============================================================================
# MEMORY CONFIGURATION - AgentCore Memory for conversation history
# ============================================================================

# Initialize memory client for conversation history
try:
    from bedrock_agentcore.memory import MemoryClient
    memory_client = MemoryClient(region_name='us-east-1')
    
    # Memory ID from .bedrock_agentcore.yaml
    memory_id = "freelancer_action_agent_mem-Fh4JVHDpfJ"
    default_actor_id = "user"
    
    logger.info(f"✅ Memory client initialized with ID: {memory_id}")
except Exception as e:
    logger.warning(f"⚠️ Memory client initialization failed: {e}")
    memory_client = None
    memory_id = None
    default_actor_id = "user"

# ============================================================================
# TOOLS - Define the 4 tools for Action Agent
# ============================================================================

@tool
def search_similar_cases(issue_type: str, jurisdiction: str, contract_text: str = "") -> str:
    """
    Search for similar legal cases and precedents using web search.
    
    Args:
        issue_type: Type of issue (non_payment, breach_of_contract, ip_theft, scope_creep)
        jurisdiction: Legal jurisdiction (USA, UK, EU)
        contract_text: Optional contract text to extract relevant terms
    
    Returns:
        String with similar cases and legal precedents
    """
    logger.info(f"Searching for cases: {issue_type} in {jurisdiction}")
    
    try:
        # Extract key terms from contract if provided
        contract_terms = []
        if contract_text:
            terms_to_find = ["payment", "net 30", "net 60", "deliverable", "milestone", 
                           "IP", "copyright", "intellectual property", "scope", "change request"]
            for term in terms_to_find:
                if term.lower() in contract_text.lower():
                    contract_terms.append(term)
        
        # Build search query
        query_parts = [issue_type.replace("_", " "), "freelancer", "contract", jurisdiction]
        if contract_terms:
            query_parts.extend(contract_terms[:3])  # Add top 3 relevant terms
        
        search_query = " ".join(query_parts)
        logger.info(f"Search query: {search_query}")
        
        # Perform search
        ddgs = DDGS()
        results = ddgs.text(search_query, region='us-en', safesearch='moderate', max_results=5)
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            href = result.get('href', '')
            
            # Filter English-only content
            if _is_english_text(title + body):
                formatted_results.append(f"{i}. **{title}**\n   {body}\n   Source: {href}\n")
        
        if formatted_results:
            return "\n".join(formatted_results)
        else:
            # Fallback to curated resources
            return _get_fallback_cases(issue_type, jurisdiction)
            
    except Exception as e:
        logger.error(f"Search error: {e}")
        return _get_fallback_cases(issue_type, jurisdiction)


@tool
def generate_action_plan(issue_description: str, jurisdiction: str, amount_at_stake: float, days_since_issue: int = 0) -> str:
    """
    Generate a personalized action plan using AI based on the specific situation.
    
    Args:
        issue_description: Description of the issue
        jurisdiction: Legal jurisdiction (USA, UK, EU)
        amount_at_stake: Amount of money involved
        days_since_issue: Days since the issue started
    
    Returns:
        Personalized action plan with specific steps
    """
    logger.info(f"Generating action plan for: {issue_description}")
    
    try:
        # Use Claude via Bedrock to generate contextual plan
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        prompt = f"""You are a legal action advisor for freelancers. Generate a specific, actionable plan.

Issue: {issue_description}
Jurisdiction: {jurisdiction}
Amount: ${amount_at_stake}
Days since issue: {days_since_issue}

Provide a numbered action plan with:
1. Immediate actions (next 24-48 hours)
2. Short-term actions (next 1-2 weeks)
3. Long-term considerations (if issue persists)

Be specific, practical, and empathetic. Focus on documentation, communication, and escalation paths."""

        # Try multiple models for fallback
        models = [
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0"
        ]
        
        for model_id in models:
            try:
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": prompt}]
                    })
                )
                
                result = json.loads(response['body'].read())
                return result['content'][0]['text']
            except Exception as e:
                logger.warning(f"Model {model_id} failed: {e}")
                continue
        
        # If all models fail, return structured fallback
        return _get_fallback_action_plan(issue_description, jurisdiction, amount_at_stake, days_since_issue)
        
    except Exception as e:
        logger.error(f"Action plan generation error: {e}")
        return _get_fallback_action_plan(issue_description, jurisdiction, amount_at_stake, days_since_issue)


@tool
def get_evidence_checklist(issue_type: str) -> str:
    """
    Get a checklist of evidence to collect for the specific issue type.
    
    Args:
        issue_type: Type of issue (non_payment, breach_of_contract, ip_theft, scope_creep)
    
    Returns:
        Checklist of evidence to gather
    """
    logger.info(f"Getting evidence checklist for: {issue_type}")
    
    checklists = {
        "non_payment": """
📋 Evidence Checklist for Non-Payment:

✅ **Contract & Agreements:**
   - Original signed contract
   - Any amendments or addendums
   - Statement of Work (SOW)
   - Email confirmations of agreement

✅ **Proof of Work Completed:**
   - Project deliverables (files, code, designs)
   - Screenshots/recordings of completed work
   - Client feedback/approval emails
   - Version history showing your contributions

✅ **Communication Records:**
   - All email correspondence
   - Messages (Slack, WhatsApp, etc.)
   - Meeting notes
   - Invoice history

✅ **Payment Documentation:**
   - Invoices sent (with dates)
   - Payment reminders
   - Any partial payments received
   - Bank statements showing non-payment

✅ **Timeline Evidence:**
   - Project start/end dates
   - Deadline communications
   - Delivery confirmations
""",
        "breach_of_contract": """
📋 Evidence Checklist for Breach of Contract:

✅ **Contract Documentation:**
   - Original contract with all terms
   - Scope of work document
   - Any modifications agreed upon
   - Contract clauses being violated

✅ **Breach Evidence:**
   - Documentation of the specific breach
   - Dates when breaches occurred
   - Screenshots/photos of violations
   - Witness statements if applicable

✅ **Your Performance:**
   - Proof you met your obligations
   - Deliverables provided on time
   - Communication showing compliance
   - Client acknowledgments

✅ **Impact Documentation:**
   - Financial losses incurred
   - Time spent on corrections
   - Opportunity costs
   - Damage to reputation (if any)

✅ **Attempt to Resolve:**
   - Emails addressing the breach
   - Proposed solutions you offered
   - Meeting notes discussing issues
   - Mediation attempts
""",
        "ip_theft": """
📋 Evidence Checklist for IP Theft:

✅ **Ownership Proof:**
   - Original files with timestamps
   - Version control history (Git commits)
   - Creation process documentation
   - Drafts showing your work progression

✅ **Contract IP Clauses:**
   - IP ownership terms in contract
   - Work-for-hire agreements
   - Transfer of rights documentation
   - Usage rights agreed upon

✅ **Theft Evidence:**
   - Screenshots of unauthorized use
   - URLs where your work appears
   - Side-by-side comparisons
   - Dates of unauthorized use

✅ **Your Original Work:**
   - Source files
   - Raw assets
   - Process documentation
   - Design sketches/wireframes

✅ **Prior Art:**
   - Portfolio showing your style
   - Previous similar work
   - Timestamps proving creation date
   - Third-party verification
""",
        "scope_creep": """
📋 Evidence Checklist for Scope Creep:

✅ **Original Scope:**
   - Initial project proposal
   - Signed SOW/contract
   - Original requirements document
   - Agreed deliverables list

✅ **Additional Requests:**
   - Emails requesting extra work
   - Messages asking for changes
   - New requirements not in contract
   - Timeline of scope additions

✅ **Your Responses:**
   - Notifications of out-of-scope work
   - Requests for additional payment
   - Proposed change orders
   - Time tracking for extra work

✅ **Impact Documentation:**
   - Extra hours worked
   - Missed deadlines due to additions
   - Other projects delayed
   - Additional costs incurred

✅ **Approval Trail:**
   - What was approved vs delivered
   - Change request documentation
   - Client acknowledgment of extras
   - Budget discussions
"""
    }
    
    return checklists.get(issue_type, "Invalid issue type. Use: non_payment, breach_of_contract, ip_theft, or scope_creep")


@tool
def get_legal_resources(jurisdiction: str, issue_type: str, amount_at_stake: float) -> str:
    """
    Find legal resources and next steps based on jurisdiction and case value.
    
    Args:
        jurisdiction: Legal jurisdiction (USA, UK, EU)
        issue_type: Type of issue
        amount_at_stake: Amount of money involved
    
    Returns:
        Legal resources and recommended next steps
    """
    logger.info(f"Getting legal resources for {jurisdiction}, amount: ${amount_at_stake}")
    
    resources = {
        "USA": f"""
🇺🇸 Legal Resources for USA (Amount: ${amount_at_stake:,.2f})

{'📍 **Small Claims Court** (Recommended for this amount)' if amount_at_stake < 10000 else '📍 **Civil Court** (Required for this amount)'}

🔗 **Free Legal Resources:**
   - Legal Aid: https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help
   - Volunteer Lawyers: https://www.americanbar.org/groups/legal_services/flh-home/
   - Small Business Legal: https://www.sba.gov/business-guide/manage-your-business/get-legal-help

💰 **Cost-Effective Options:**
   - Small Claims Court (limits vary by state: $2,500-$25,000)
     * No lawyer needed
     * Lower filing fees ($30-$100)
     * Faster resolution (2-3 months)
   
   - Demand Letter Services:
     * LegalZoom: $49-$349
     * Rocket Lawyer: $39.99/month
     * UpCounsel: $200-$500

📋 **Next Steps:**
   1. Send certified demand letter (give 14-30 days to respond)
   2. If no response, file small claims (if under state limit)
   3. Consider arbitration if in contract
   4. Consult with freelancer-focused attorney

🏛️ **State Bar Associations:** (for attorney referrals)
   - Find yours: https://www.americanbar.org/groups/legal_services/flh-home/flh-bar-directories-and-lawyer-finders/

⚖️ **Alternative Dispute Resolution:**
   - American Arbitration Association: https://www.adr.org/
   - JAMS Mediation: https://www.jamsadr.com/
""",
        "UK": f"""
🇬🇧 Legal Resources for UK (Amount: £{amount_at_stake * 0.79:,.2f})

{'📍 **Money Claim Online** (Recommended)' if amount_at_stake < 15000 else '📍 **County Court** (Required)'}

🔗 **Free Legal Resources:**
   - Citizens Advice: https://www.citizensadvice.org.uk/
   - Law Centres: https://www.lawcentres.org.uk/
   - Free Legal Advice: https://www.gov.uk/find-legal-advice

💰 **Cost-Effective Options:**
   - Money Claim Online (up to £100,000)
     * Court fee: £35-£10,000 (based on claim value)
     * No solicitor needed for small claims
     * Online process
   
   - Pre-Action Protocol:
     * Send Letter Before Action (free)
     * Give 14 days to respond
     * Required before court action

📋 **Next Steps:**
   1. Send Letter Before Action (template: https://www.gov.uk/make-court-claim-for-money)
   2. Wait 14 days for response
   3. File claim online: https://www.moneyclaim.gov.uk/
   4. Consider mediation (required for some claims)

🏛️ **Professional Support:**
   - Solicitors for free/low cost: https://solicitors.lawsociety.org.uk/
   - Small Business Commissioner: https://www.smallbusinesscommissioner.gov.uk/

⚖️ **Alternative Dispute Resolution:**
   - Civil Mediation Council: https://www.civilmediation.org/
   - CEDR: https://www.cedr.com/
""",
        "EU": f"""
🇪🇺 Legal Resources for EU (Amount: €{amount_at_stake * 0.92:,.2f})

📍 **Varies by Country - General EU Resources**

🔗 **EU-Wide Resources:**
   - EU Justice Portal: https://e-justice.europa.eu/
   - European Small Claims: https://e-justice.europa.eu/35/EN/european_small_claims_procedure
   - Free Legal Aid: https://e-justice.europa.eu/42/EN/legal_aid

💰 **European Small Claims Procedure:**
   - For cross-border claims up to €5,000
   - Simplified procedure
   - Reduced costs
   - Recognition across EU

📋 **Country-Specific Steps:**
   - Germany: Mahnverfahren (dunning procedure)
   - France: Injonction de payer
   - Spain: Monitorio
   - Italy: Decreto ingiuntivo
   
   Each has online portals and simplified procedures

🏛️ **Professional Support:**
   - EECC (European Consumer Centre): https://ec.europa.eu/consumers/solving_consumer_disputes/non-judicial_redress/ecc-net/
   - National Bar Associations: https://www.ccbe.eu/

⚖️ **Online Dispute Resolution:**
   - EU ODR Platform: https://ec.europa.eu/consumers/odr/
   - Mediators across EU: https://e-justice.europa.eu/

💡 **Important:**
   - Each EU country has different procedures
   - Consider jurisdiction specified in contract
   - Language requirements vary
   - May need certified translations
"""
    }
    
    return resources.get(jurisdiction, "Invalid jurisdiction. Use: USA, UK, or EU")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _is_english_text(text: str) -> bool:
    """Check if text is primarily English (70% ASCII characters)."""
    if not text:
        return False
    ascii_count = sum(1 for c in text if ord(c) < 128)
    return (ascii_count / len(text)) > 0.7


def _get_fallback_cases(issue_type: str, jurisdiction: str) -> str:
    """Return curated legal resources as fallback."""
    fallback_resources = {
        "non_payment": [
            {"title": "Freelancer Payment Dispute Resolution Guide", "source": "Freelancers Union", "url": "https://www.freelancersunion.org"},
            {"title": "How to Handle Non-Paying Clients", "source": "NOLO Legal", "url": "https://www.nolo.com"},
            {"title": "Small Claims Court for Freelancers", "source": "LegalZoom", "url": "https://www.legalzoom.com"}
        ],
        "breach_of_contract": [
            {"title": "Understanding Breach of Contract", "source": "FindLaw", "url": "https://www.findlaw.com"},
            {"title": "Freelancer Contract Disputes", "source": "UpCounsel", "url": "https://www.upcounsel.com"},
            {"title": "Remedies for Contract Breach", "source": "NOLO", "url": "https://www.nolo.com"}
        ],
        "ip_theft": [
            {"title": "Protecting Your Intellectual Property", "source": "USPTO", "url": "https://www.uspto.gov"},
            {"title": "Copyright Infringement for Freelancers", "source": "Copyright.gov", "url": "https://www.copyright.gov"},
            {"title": "DMCA Takedown Process", "source": "Google", "url": "https://support.google.com"}
        ],
        "scope_creep": [
            {"title": "Managing Scope Creep", "source": "Freelancers Union", "url": "https://www.freelancersunion.org"},
            {"title": "Change Order Best Practices", "source": "PMI", "url": "https://www.pmi.org"},
            {"title": "Billing for Out-of-Scope Work", "source": "FreshBooks", "url": "https://www.freshbooks.com"}
        ]
    }
    
    resources = fallback_resources.get(issue_type, fallback_resources["non_payment"])
    result = f"Here are some curated resources for {issue_type} in {jurisdiction}:\n\n"
    for i, resource in enumerate(resources, 1):
        result += f"{i}. **{resource['title']}**\n   Source: {resource['source']} - {resource['url']}\n\n"
    
    return result


def _get_fallback_action_plan(issue_description: str, jurisdiction: str, amount: float, days: int) -> str:
    """Generate a structured action plan as fallback."""
    return f"""
📋 **Action Plan for Your Situation**

**Issue:** {issue_description}
**Jurisdiction:** {jurisdiction}
**Amount at Stake:** ${amount:,.2f}
**Days Since Issue:** {days}

**Immediate Actions (Next 24-48 hours):**
1. ✅ **Document Everything**
   - Gather all contracts, emails, and evidence
   - Create a timeline of events
   - Save all communication records

2. 📧 **Send Professional Communication**
   - Email client stating the issue clearly
   - Reference specific contract clauses
   - Provide a deadline for resolution (7-14 days)
   - Keep tone professional and factual

3. 📊 **Calculate Total Impact**
   - Amount owed or damages
   - Additional costs incurred
   - Time lost on the issue

**Short-term Actions (Next 1-2 weeks):**
4. ✉️ **Send Formal Demand Letter**
   - State the issue, amount, and deadline
   - Send via certified mail (proof of delivery)
   - Keep a copy for your records

5. 🤝 **Attempt Resolution**
   - Propose mediation or arbitration
   - Be open to reasonable compromise
   - Document all attempts to resolve

6. 💼 **Consult Legal Resources**
   - Contact freelancer legal aid
   - Review small claims court options
   - Consider arbitration if in contract

**If Issue Persists (After 2-4 weeks):**
7. ⚖️ **Escalate Formally**
   {'- File small claims court claim (amount under $10,000)' if amount < 10000 else '- Consult with attorney for civil action'}
   - Report to relevant professional bodies
   - Consider public review (carefully, avoid defamation)

8. 📱 **Protect Yourself Going Forward**
   - Update your contracts
   - Require deposits/milestones
   - Document everything in real-time

**Resources:**
- Jurisdiction: {jurisdiction} specific resources available
- Amount: {'Small claims court eligible' if amount < 10000 else 'May require attorney'}
- Timeframe: {days} days - {'Act quickly' if days > 60 else 'Still within reasonable timeframe'}
"""


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

def create_agent():
    """Create and configure the Strands agent with all tools."""
    logger.info("Creating Action Agent with Strands + AgentCore...")
    
    # Create Bedrock model - Using Claude 3.5 Sonnet for MUCH better tool calling
    # Haiku is too weak and hallucinates tool results instead of actually calling them
    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
    )
    
    # System prompt for conversational AI with strong tool usage guidance
    system_prompt = """You are a legal action assistant for freelancers with contract disputes.

🎯 **Your Role:**
Help freelancers understand their options and take appropriate action after experiencing contract problems with clients.

💬 **Conversational Approach:**
- Start by greeting the user warmly
- Ask clarifying questions to understand their situation
- **USE YOUR TOOLS ACTIVELY** - don't give generic advice!
- Explain results in simple, empathetic terms
- Provide actionable next steps

🛠️ **YOUR TOOLS - USE THEM!:**

1. **search_similar_cases** - ALWAYS use when user describes their issue
   - Example: User says "My client won't pay $7000 for freelance work in USA"
   - Action: IMMEDIATELY call search_similar_cases(issue_type="non_payment", jurisdiction="USA", contract_text="")
   
2. **generate_action_plan** - ALWAYS use after understanding the situation
   - Example: User provides issue details
   - Action: Call generate_action_plan(issue_type="non_payment", amount=7000, jurisdiction="USA", timeline="overdue", evidence_available=False)
   
3. **get_evidence_checklist** - Use when user asks what to prepare
   - Example: User asks "What evidence do I need?"
   - Action: Call get_evidence_checklist(issue_type="non_payment")
   
4. **get_legal_resources** - Use when user asks about legal options
   - Example: User wants to know next steps
   - Action: Call get_legal_resources(jurisdiction="USA", issue_type="non_payment")

📋 **IMPORTANT - Information Gathering:**
Once you have these basics, USE YOUR TOOLS:
- Issue type: non-payment, breach, IP theft, scope creep
- Amount involved: $X
- Jurisdiction: USA, UK, EU
- Timeline: when was payment due?

❌ **DO NOT:**
- Give generic legal advice without using tools
- Say "you should send a demand letter" without calling generate_action_plan
- Mention "similar cases" without calling search_similar_cases
- List evidence without calling get_evidence_checklist

✅ **DO:**
- Call search_similar_cases when user first describes issue
- Call generate_action_plan once you have amount + jurisdiction + issue type
- Use tools even if user doesn't explicitly ask
- Combine tool results with empathetic explanations

**Example Conversation:**
User: "My client won't pay me $7000 for freelance work in USA"
You: "I understand - non-payment is frustrating. Let me search for similar cases and create an action plan for you."
[CALL search_similar_cases(issue_type="non_payment", jurisdiction="USA")]
[CALL generate_action_plan(issue_type="non_payment", amount=7000, jurisdiction="USA", timeline="overdue")]
Then provide results with empathy.

Start by introducing yourself and asking how you can help!"""
    
    # Import conversation manager
    from strands.agent.conversation_manager import SummarizingConversationManager
    
    # Create conversation manager for long conversations
    conversation_manager = SummarizingConversationManager(
        summary_ratio=0.5,
        preserve_recent_messages=3
    )
    
    # Create agent with tools and conversation management
    agent = Agent(
        model=model,
        tools=[
            search_similar_cases,
            generate_action_plan,
            get_evidence_checklist,
            get_legal_resources
        ],
        system_prompt=system_prompt,
        conversation_manager=conversation_manager
    )
    
    logger.info("✅ Action Agent created successfully!")
    return agent, model, system_prompt, conversation_manager


# Initialize agent and components globally
action_agent, bedrock_model, action_system_prompt, conversation_manager = create_agent()
action_tools = [search_similar_cases, generate_action_plan, get_evidence_checklist, get_legal_resources]


# ============================================================================
# AGENTCORE ENTRYPOINT
# ============================================================================

@app.entrypoint
def invoke(payload):
    """
    Main entrypoint for AgentCore invocations with conversation memory support.
    
    Following AWS sample pattern from video-games-sales-assistant for memory retrieval.
    
    Args:
        payload: Dict with keys:
            - 'prompt' or 'inputText': User message
            - 'session_id': Session ID for memory retrieval
            - 'last_k_turns': Number of conversation turns to retrieve (default 10)
    
    Returns:
        Dict with 'result' key containing agent response
    """
    try:
        # Extract parameters from payload
        user_message = payload.get("inputText") or payload.get("prompt", "Hello! How can I help you today?")
        session_id = payload.get("session_id")
        last_k_turns = payload.get("last_k_turns", 10)
        
        logger.info(f"User message: {user_message}")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Last K turns: {last_k_turns}")
        
        # Retrieve conversation history from AgentCore Memory if session_id provided
        conversation_messages = []
        if session_id and memory_id:
            try:
                logger.info(f"🧠 Retrieving conversation history from memory...")
                logger.info(f"Memory ID: {memory_id}")
                logger.info(f"Actor ID: {default_actor_id}")
                
                # Get last K conversation turns using MemoryClient API
                recent_turns = memory_client.get_last_k_turns(
                    memory_id=memory_id,
                    actor_id=default_actor_id,
                    session_id=session_id,
                    k=last_k_turns
                )
                
                if recent_turns:
                    logger.info(f"✅ Retrieved {len(recent_turns)} conversation turns from memory")
                    
                    # Format conversation history for Strands Agent
                    # Each turn is a list of messages [user_msg, assistant_msg]
                    for turn in recent_turns:
                        for message in turn:
                            role = message.get('role', 'user').lower()
                            content = message.get('content', {})
                            
                            # Extract text from content
                            if isinstance(content, dict):
                                text = content.get('text', '')
                            else:
                                text = str(content)
                            
                            if text:
                                # Format for Strands Agent: role and content with text
                                conversation_messages.append({
                                    "role": role,
                                    "content": [{"text": text}]
                                })
                    
                    logger.info(f"✅ Formatted {len(conversation_messages)} messages for agent context")
                else:
                    logger.info("📭 No previous conversation history found in memory")
                    
            except Exception as mem_error:
                logger.warning(f"⚠️ Memory retrieval failed (continuing without history): {mem_error}")
        else:
            logger.info("ℹ️ No session_id provided or memory not configured - starting fresh conversation")
        
        # Create agent with conversation history if available
        if conversation_messages:
            logger.info(f"🤖 Creating agent with {len(conversation_messages)} historical messages")
            # Create a new agent instance with conversation history
            contextualized_agent = Agent(
                model=bedrock_model,
                system_prompt=action_system_prompt,
                tools=action_tools,
                conversation_manager=conversation_manager,
                messages=conversation_messages  # Pass historical messages
            )
            response = contextualized_agent(user_message)
        else:
            logger.info("🤖 Creating agent without history (fresh conversation)")
            # Use the global agent instance
            response = action_agent(user_message)
        
        logger.info(f"Agent response: {response.message}")
        return {"result": response.message}
        
    except Exception as e:
        logger.error(f"Error in invoke: {e}", exc_info=True)
        return {"result": f"I encountered an error: {str(e)}. Please try again."}


# ============================================================================
# MAIN - For local testing
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting Action Agent with AgentCore Runtime...")
    app.run()
