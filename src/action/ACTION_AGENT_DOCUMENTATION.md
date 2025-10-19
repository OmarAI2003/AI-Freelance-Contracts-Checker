# Action Agent - Complete Documentation

## Overview

**Agent Name**: `freelancer_action_agent`  
**Agent ARN**: `arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD`  
**Purpose**: AI-powered legal assistant helping freelancers resolve post-contract disputes with clients  
**Status**: ✅ DEPLOYED and OPERATIONAL on AWS Bedrock AgentCore Runtime

## Technology Stack

### Core Framework
- **AWS Bedrock AgentCore Runtime** - Serverless agent hosting platform
- **Strands SDK** (v1.13.0) - Agent framework with tool decorators
- **Strands Agents Tools** (v0.2.12) - Enhanced tool capabilities
- **Claude 3 Haiku** - Conversational AI model (`anthropic.claude-3-haiku-20240307-v1:0`)

### Dependencies
```
bedrock-agentcore==1.0.3
strands-agents==1.13.0
strands-agents-tools==0.2.12
duckduckgo-search>=6.2.0
boto3==1.40.55
```

### AWS Infrastructure
- **Region**: us-east-1
- **Account**: 897722703585
- **Execution Role**: AmazonBedrockAgentCoreSDKRuntime-us-east-1-68634593a8
- **Memory**: STM (Short-Term Memory) - `freelancer_action_agent_mem-Fh4JVHDpfJ`
- **ECR Repository**: 897722703585.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-freelancer_action_agent
- **Container Platform**: ARM64 (linux/arm64)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User/Frontend                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         AWS Bedrock AgentCore Runtime                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  BedrockAgentCoreApp (@app.entrypoint)              │   │
│  │  ├─ Receives payload: {"prompt": "user message"}    │   │
│  │  ├─ Routes to Strands Agent                         │   │
│  │  └─ Returns: {"result": {"role", "content"}}        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Strands Agent (Claude 3 Haiku)                     │   │
│  │  ├─ System Prompt: Conversational legal assistant   │   │
│  │  ├─ Gathers context through questions               │   │
│  │  ├─ Dynamically invokes tools                       │   │
│  │  └─ Provides empathetic, actionable advice          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  4 Custom Tools (@tool decorators)                  │   │
│  │  ├─ search_similar_cases (DuckDuckGo API)          │   │
│  │  ├─ generate_action_plan (Claude via Bedrock)      │   │
│  │  ├─ get_evidence_checklist (Structured data)       │   │
│  │  └─ get_legal_resources (Jurisdiction-specific)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Short-Term Memory (STM)                            │   │
│  │  └─ Retains conversation context across turns       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Agent Implementation Details

### Entry Point Pattern
```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore entry point - receives user prompts"""
    user_message = payload.get("prompt", "")
    response = action_agent(user_message)
    return {"result": response.message}
```

### Agent Configuration
```python
from strands import Agent, tool
from strands.models import BedrockModel

# Initialize model
model = BedrockModel(
    model_id="anthropic.claude-3-haiku-20240307-v1:0"
)

# Create agent with tools
action_agent = Agent(
    name="FreelancerActionAgent",
    model=model,
    tools=[
        search_similar_cases,
        generate_action_plan,
        get_evidence_checklist,
        get_legal_resources
    ],
    system_prompt="""You are a legal action assistant for freelancers..."""
)
```

### System Prompt Strategy
```
🎯 Role: Legal action assistant for freelancers with contract disputes

💬 Conversational Approach:
- Greet users warmly and empathetically
- Ask clarifying questions to understand situation
- Gather: issue type, jurisdiction, amount, timeline
- Use tools only when sufficient context is gathered
- Explain results in simple, actionable terms
- Provide step-by-step guidance

🛠️ Tool Usage:
- search_similar_cases: After understanding the dispute
- generate_action_plan: Once all key details collected
- get_evidence_checklist: When discussing documentation needs
- get_legal_resources: When advising on legal procedures
```

## Tool Specifications

### 1. search_similar_cases
**Purpose**: Find legal precedents and similar dispute cases

**Signature**:
```python
@tool
def search_similar_cases(
    issue_type: str,
    jurisdiction: str,
    contract_text: str = ""
) -> str
```

**Parameters**:
- `issue_type`: Type of dispute (non_payment, breach_of_contract, ip_theft, scope_creep)
- `jurisdiction`: Legal jurisdiction (USA, UK, EU, Canada, Australia)
- `contract_text`: Optional contract text to extract key terms

**Implementation**:
- Uses DuckDuckGo Search API (`DDGS`)
- English-only filter (70% ASCII threshold via `_is_english_text()`)
- Region: `us-en` for English results
- Extracts contract terms: payment terms, deliverables, IP clauses
- Fallback: Returns curated legal resources if search fails
- Returns: Top 5 relevant cases with titles, snippets, URLs

**Example Query**:
```python
search_similar_cases(
    issue_type="non_payment",
    jurisdiction="USA",
    contract_text="Payment due Net 30..."
)
```

**Sample Output**:
```
🔍 Similar Cases and Legal Precedents:

1. Freelancer Non-Payment Case Study - Small Claims Success
   "Freelancer successfully recovered $5000 in small claims court..."
   https://example.com/case1

2. Contract Payment Disputes: What Freelancers Need to Know
   "Understanding your rights when clients don't pay..."
   https://example.com/case2
...
```

### 2. generate_action_plan
**Purpose**: Create AI-generated personalized action plan

**Signature**:
```python
@tool
def generate_action_plan(
    issue_description: str,
    jurisdiction: str,
    amount_at_stake: float,
    days_since_issue: int = 0
) -> str
```

**Parameters**:
- `issue_description`: Detailed description of the dispute
- `jurisdiction`: Legal jurisdiction
- `amount_at_stake`: Money involved in USD
- `days_since_issue`: Days since issue started (default: 0)

**Implementation**:
- Uses AWS Bedrock `invoke_model` API (boto3)
- Multi-model fallback chain:
  1. Claude 3 Haiku (primary)
  2. Claude 3 Sonnet (fallback)
  3. Claude 3 Sonnet (alternate)
- Structured prompt requesting:
  - Immediate actions (24-48 hours)
  - Short-term actions (1-2 weeks)
  - Long-term considerations
- Max tokens: 1000
- Temperature: 0.7 (balanced creativity)

**Example Request**:
```python
generate_action_plan(
    issue_description="Client won't pay $5000 for web dev work",
    jurisdiction="USA",
    amount_at_stake=5000.0,
    days_since_issue=60
)
```

**Sample Output**:
```
📋 Personalized Action Plan:

IMMEDIATE ACTIONS (Next 24-48 Hours):
1. Send formal payment demand letter via certified mail
2. Document all communications and work completed
3. Review your contract for payment terms and dispute resolution clauses

SHORT-TERM ACTIONS (Next 1-2 Weeks):
1. File a claim in small claims court (under $10,000 threshold)
2. Gather evidence: invoices, emails, project files
3. Consider mediation if client responds

LONG-TERM CONSIDERATIONS:
1. If no response, proceed with court hearing
2. Consider hiring collection agency if judgment obtained
3. Learn from this: require deposits for future projects
```

### 3. get_evidence_checklist
**Purpose**: Provide issue-specific evidence collection checklist

**Signature**:
```python
@tool
def get_evidence_checklist(issue_type: str) -> str
```

**Parameters**:
- `issue_type`: Type of dispute (non_payment, breach_of_contract, ip_theft, scope_creep)

**Implementation**:
- Static structured data (no API calls)
- 4 predefined checklists for common dispute types
- Categorized evidence items with checkboxes
- Practical, actionable items

**Checklist Categories**:

**Non-Payment**:
```
✓ Original contract/agreement
✓ All invoices sent
✓ Proof of work completion (screenshots, files, demos)
✓ Communication timeline (emails, messages, calls)
✓ Payment terms documentation
✓ Any partial payments received
```

**Breach of Contract**:
```
✓ Signed contract with specific terms
✓ Documentation of breach incidents
✓ Your performance evidence
✓ Client's failure to perform
✓ Attempts to remedy the breach
✓ Financial impact documentation
```

**IP Theft**:
```
✓ Copyright registration or proof of creation
✓ Original work files with timestamps
✓ Contract IP ownership clauses
✓ Evidence of unauthorized use
✓ Communication about IP rights
✓ Damages assessment
```

**Scope Creep**:
```
✓ Original project scope
✓ All additional requests (emails, messages)
✓ Your responses to additional requests
✓ Time/cost impact of extra work
✓ Communication about scope changes
✓ Contract change order provisions
```

### 4. get_legal_resources
**Purpose**: Provide jurisdiction-specific legal resources and procedures

**Signature**:
```python
@tool
def get_legal_resources(
    jurisdiction: str,
    issue_type: str,
    amount_at_stake: float
) -> str
```

**Parameters**:
- `jurisdiction`: Legal jurisdiction (USA, UK, EU, Canada, Australia)
- `issue_type`: Type of dispute
- `amount_at_stake`: Money involved in USD

**Implementation**:
- Jurisdiction-specific guidance
- Amount-based recommendations (small claims vs. full litigation)
- Official resource links
- Step-by-step procedures

**USA Resources** (amount < $10,000):
```
🏛️ Small Claims Court
- Most states: $5,000-$10,000 limit
- No attorney required
- Filing fee: $25-$100
- Process: https://www.uscourts.gov/services-forms/small-claims

📞 Legal Aid Organizations
- Find local: https://www.lsc.gov/what-legal-aid/find-legal-aid
- Free/low-cost assistance

📋 State Bar Associations
- Lawyer referral services
- Mediation programs
- Ethics complaint procedures
```

**UK Resources**:
```
💻 Money Claim Online
- Claims up to £100,000
- https://www.gov.uk/make-money-claim

🤝 Citizens Advice
- Free legal guidance
- https://www.citizensadvice.org.uk

📧 Letter Before Action
- Required pre-litigation step
- Template: https://www.gov.uk/government/publications/letter-before-claim
```

**EU Resources**:
```
🇪🇺 European Small Claims Procedure
- Cross-border claims up to €5,000
- https://e-justice.europa.eu/169/EN/small_claims_procedure

🌐 Online Dispute Resolution (ODR) Platform
- https://ec.europa.eu/consumers/odr

🏛️ Country-Specific Courts
- Check national procedures
```

## Conversational Flow Example

**User**: "Hi, I need help"

**Agent**: "Hello! Welcome to the legal action assistant for freelancers. I'm here to help you with any contract disputes or issues you might be facing. How can I assist you today? Could you tell me a bit about the situation you're dealing with?"

---

**User**: "My client won't pay me $5000 for web development work. It's been 60 days past due and I'm in the USA."

**Agent**: "I'm sorry to hear about the non-payment issue with your client. That must be very frustrating. As a legal action assistant, I'm here to help you understand your options and take the right steps.

Let's start by gathering a few more details:
- Can you provide any of the contract text or details on the scope of work?
- Have you communicated with the client about the overdue payment?

Once I have those details, I can use my tools to search for similar legal cases, generate a personalized action plan, and provide recommendations on next steps specific to your jurisdiction.

The key will be documenting everything thoroughly, as that will be important evidence if this ends up requiring legal action. But there may be some other options to try first to resolve this amicably."

---

**User**: "Yes, I sent 3 reminder emails. The contract says Net 30 payment terms."

**Agent** (uses tools):
1. Calls `search_similar_cases("non_payment", "USA", "Net 30 payment terms")`
2. Calls `generate_action_plan("Client won't pay $5000 for web dev, 60 days overdue", "USA", 5000.0, 60)`
3. Calls `get_evidence_checklist("non_payment")`
4. Calls `get_legal_resources("USA", "non_payment", 5000.0)`

Then provides comprehensive guidance based on tool results.

## Deployment Process

### CLI Commands Used
```bash
# 1. Configure agent
agentcore configure \
  -e action_agent_agentcore.py \
  -n freelancer_action_agent \
  -r us-east-1 \
  -ni

# 2. Launch to AWS (CodeBuild ARM64 deployment)
agentcore launch

# 3. Check status
agentcore status

# 4. Test invocation
agentcore invoke '{"prompt": "Hello"}'
```

### CodeBuild Process (40 seconds)
```
QUEUED         → 1.2s
PROVISIONING   → 10.6s
DOWNLOAD_SOURCE → 1.2s
BUILD          → 15.5s (ARM64 container build)
POST_BUILD     → 10.9s (push to ECR)
COMPLETED      → 1.2s
```

### Deployment Artifacts
- `.bedrock_agentcore.yaml` - Agent configuration
- `.bedrock_agentcore/freelancer_action_agent/Dockerfile` - Container definition
- `.dockerignore` - Build exclusions (45 patterns)
- ECR image: `897722703585.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-freelancer_action_agent:latest`

## Observability

### CloudWatch Logs
```bash
# Tail logs (follow mode)
aws logs tail \
  /aws/bedrock-agentcore/runtimes/freelancer_action_agent-Q83Rk73nkD-DEFAULT \
  --log-stream-name-prefix "2025/10/18/[runtime-logs]" \
  --follow

# Last hour logs
aws logs tail \
  /aws/bedrock-agentcore/runtimes/freelancer_action_agent-Q83Rk73nkD-DEFAULT \
  --log-stream-name-prefix "2025/10/18/[runtime-logs]" \
  --since 1h
```

### GenAI Dashboard
**URL**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core

**Features**:
- Agent invocation metrics
- Tool usage statistics
- Response latency tracking
- Error rate monitoring
- X-Ray distributed tracing

**Note**: First data appears 10 minutes after deployment

### X-Ray Tracing
- Trace segment destination: CloudWatch Logs
- Indexing rules: Configured for transaction search
- Resource policy: Allows trace ingestion

## Memory Configuration

**Type**: Short-Term Memory (STM)  
**ID**: `freelancer_action_agent_mem-Fh4JVHDpfJ`  
**Mode**: STM_ONLY  
**Retention**: 30 days  
**Purpose**: Maintains conversation context across multiple turns

**Memory Behavior**:
- Stores user messages and agent responses
- Enables context-aware follow-up questions
- Automatically managed by AgentCore
- Session-based isolation (each session has unique ID)
- Provisioning time: 30-90 seconds after deployment

## Testing and Validation

### Manual Testing
```bash
# Test 1: Greeting
agentcore invoke '{"prompt": "Hi, I need help"}'

# Test 2: Dispute scenario
agentcore invoke '{"prompt": "My client won't pay me $5000 for web work. It's been 60 days past due and I'm in the USA."}'

# Test 3: Follow-up
agentcore invoke '{"prompt": "I sent 3 reminder emails. The contract says Net 30."}'
```

### Expected Behaviors
✅ Agent greets warmly and asks clarifying questions  
✅ Gathers context before using tools  
✅ Uses tools dynamically based on conversation  
✅ Provides empathetic, actionable advice  
✅ Remembers previous context (via STM)  
✅ Responds in conversational tone (not hardcoded)

### Known Limitations
- **English-only**: DuckDuckGo search filtered to English results
- **Claude 3 Haiku**: Faster but less capable than Sonnet/Opus (model switched due to marketplace access issues)
- **Static checklists**: Evidence checklists are predefined, not AI-generated
- **Regional coverage**: Legal resources for 5 jurisdictions (USA, UK, EU, Canada, Australia)

## Integration with Frontend

### SDK Integration
```python
from bedrock_agentcore import BedrockAgentCoreClient

client = BedrockAgentCoreClient(region_name="us-east-1")

response = client.invoke_agent(
    agentArn="arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD",
    sessionId="user-session-123",
    inputText="My client won't pay me"
)
```

### REST API Pattern
```python
import boto3

bedrock = boto3.client('bedrock-agentcore', region_name='us-east-1')

response = bedrock.invoke_agent(
    agentArn='arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD',
    sessionId='unique-session-id',
    inputText='User message here'
)
```

## Performance Characteristics

**Response Times** (approximate):
- Simple greeting: ~1-2 seconds
- With 1 tool call: ~3-5 seconds
- With multiple tools: ~8-12 seconds
- Action plan generation: ~4-6 seconds (Bedrock API call)

**Concurrency**: Serverless auto-scaling via AgentCore Runtime

**Cost Considerations**:
- Claude 3 Haiku: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- AgentCore Runtime: Charged per invocation + execution time
- DuckDuckGo Search: Free API

## Troubleshooting

### Issue: "Memory is still provisioning"
**Solution**: Wait 30-90 seconds after deployment for STM to activate

### Issue: "Model access is denied... aws-marketplace:ViewSubscriptions"
**Solution**: Either:
1. Add marketplace permissions to execution role
2. Use non-marketplace models (e.g., Claude 3 Haiku)

### Issue: "AccessDeniedException" for Bedrock
**Solution**: Verify execution role has `bedrock:InvokeModel` permissions

### Issue: Tools not being called
**Solution**: Check system prompt encourages tool usage and user provides enough context

## Future Enhancements

### Potential Improvements
1. **Multi-language support**: Expand beyond English
2. **Model upgrade**: Switch to Claude 3.5 Sonnet once marketplace access resolved
3. **Dynamic checklists**: Use AI to generate custom evidence lists
4. **Document analysis**: Add tool to parse contract PDFs
5. **Cost calculator**: Estimate litigation costs vs. settlement
6. **Template generator**: Create demand letters and legal documents
7. **Case outcome predictor**: ML model trained on case law
8. **Attorney matching**: Connect users with specialized lawyers

### A2A Multi-Agent Integration
- **Orchestrator pattern**: Central agent routing to specialized agents
- **Shared memory**: Unified conversation context across agents
- **Agent collaboration**: Analysis Agent → Explanation Agent → Action Agent workflow
- **Dynamic routing**: Intent-based selection of appropriate specialist agent

## Security Considerations

**IAM Permissions**:
- Execution role has least-privilege access
- Bedrock model invocation only
- DynamoDB for memory (managed by AgentCore)
- CloudWatch Logs write access

**Data Privacy**:
- User conversations stored in STM (30-day retention)
- No data persisted beyond memory retention period
- AWS regional data residency (us-east-1)

**API Security**:
- IAM authentication required for agent invocation
- Session-based isolation prevents cross-user access

## Support and Maintenance

**CloudWatch Alarms** (recommended):
- High error rate (>5%)
- High latency (>10 seconds)
- Tool failure rate

**Monitoring Checklist**:
- [ ] Daily error log review
- [ ] Weekly performance metrics
- [ ] Monthly cost analysis
- [ ] Quarterly model evaluation

**Update Process**:
1. Modify `action_agent_agentcore.py`
2. Run `agentcore launch` (redeploys in ~40 seconds)
3. Test with sample prompts
4. Monitor CloudWatch Logs for errors

---

## Quick Reference

**Agent ARN**:  
`arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD`

**Invoke Command**:  
```bash
agentcore invoke '{"prompt": "Your message here"}'
```

**Status Check**:  
```bash
agentcore status
```

**Logs**:  
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/freelancer_action_agent-Q83Rk73nkD-DEFAULT --follow
```

**Dashboard**:  
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**Author**: Dev 4 (Integration Lead)  
**Hackathon**: AWS Bedrock AgentCore + Strands SDK Challenge
