# 🎯 AgentCore + Strands Quick Reference Guide

**Created**: October 17, 2025  
**Purpose**: Quick lookup for AWS Bedrock AgentCore and Strands SDK features for ContractGuard AI hackathon project

---

## 📚 Resources

### Documentation
- **AgentCore Docs**: https://docs.aws.amazon.com/bedrock-agentcore/
- **AgentCore Samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/
- **Strands SDK**: https://github.com/strands-agents/samples

### Installation
```bash
# Install AgentCore SDK
pip install amazon-bedrock-agentcore

# Install Strands SDK
pip install strands-agents

# Verify installation
python -c "import agentcore; print(agentcore.__version__)"
python -c "import strands; print(strands.__version__)"
```

---

## 🤖 AgentCore Primitives

### 1. Agents

**Basic Agent Setup**:
```python
from agentcore import Agent
from agentcore.models import BedrockModel

# Initialize Bedrock model
model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    region="us-east-1"
)

# Create agent
agent = Agent(
    name="MyAgent",
    model=model,
    instruction="You are an expert in...",
    tools=[tool1, tool2],
    memory=agent_memory,
    output_format="structured_json"
)

# Invoke agent
response = await agent.invoke({
    "input": "Analyze this contract..."
})
```

**Available Models**:
- `amazon.nova-pro-v1:0` - Best for complex reasoning
- `amazon.nova-lite-v1:0` - Fast, cost-effective
- `anthropic.claude-3-5-sonnet-20241022-v2:0` - Best for nuanced tasks

---

### 2. Tools

**Create Custom Tool**:
```python
from agentcore import Tool

@Tool.register("my_tool_name")
async def my_custom_tool(
    param1: str,
    param2: int = 10
) -> dict:
    """
    Tool description that agent will see.
    Be specific about what it does!
    
    Args:
        param1: Description of param1
        param2: Description of param2 with default value
        
    Returns:
        dict: Result with specific structure
    """
    # Tool implementation
    result = do_something(param1, param2)
    
    return {
        'success': True,
        'data': result,
        'metadata': {...}
    }
```

**Bedrock KB Tool (RAG)**:
```python
@Tool.register("knowledge_base_search")
async def kb_search(query: str, kb_id: str, num_results: int = 10) -> dict:
    """Search Bedrock Knowledge Base for relevant documents."""
    bedrock_agent = boto3.client('bedrock-agent-runtime')
    
    response = bedrock_agent.retrieve_and_generate(
        input={'text': query},
        retrieveAndGenerateConfiguration={
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0'
            },
            'type': 'KNOWLEDGE_BASE'
        }
    )
    
    # Extract citations for evidence linking
    citations = []
    for citation in response.get('citations', []):
        for ref in citation.get('retrievedReferences', []):
            citations.append({
                'text': ref['content']['text'],
                'source_url': ref['metadata'].get('source_url', ''),
                'document_id': ref['metadata'].get('document_id', ''),
                'confidence': ref.get('score', 0)
            })
    
    return {
        'answer': response['output']['text'],
        'citations': citations
    }
```

**External API Tool**:
```python
@Tool.register("web_search")
async def web_search(query: str, num_results: int = 5) -> dict:
    """Search the web for information."""
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            'https://api.tavily.com/search',
            params={'query': query, 'num_results': num_results},
            headers={'Authorization': f'Bearer {TAVILY_API_KEY}'}
        ) as response:
            data = await response.json()
            
    return {
        'results': data.get('results', []),
        'search_time': data.get('search_time', 0)
    }
```

---

### 3. Memory

**DynamoDB Memory Backend**:
```python
from agentcore import Memory

# Create persistent memory
memory = Memory(
    backend="dynamodb",
    table_name="my-agent-memory",
    ttl_seconds=86400  # 24 hours
)

# Memory is automatically saved/loaded by agent
# Structure:
{
    "session_id": "uuid-1234",
    "conversation_history": [
        {"role": "user", "content": "Hello"},
        {"role": "agent", "content": "Hi! How can I help?"}
    ],
    "context": {
        "user_preferences": {...},
        "task_state": {...}
    },
    "metadata": {
        "created_at": "2025-10-17T10:00:00Z",
        "last_updated": "2025-10-17T10:05:00Z"
    }
}
```

**In-Memory (Testing)**:
```python
memory = Memory(backend="in_memory")  # No persistence
```

**Custom Memory Backend**:
```python
from agentcore import MemoryBackend

class RedisMemory(MemoryBackend):
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
    
    async def save(self, session_id, data):
        await self.redis.set(session_id, json.dumps(data))
    
    async def load(self, session_id):
        data = await self.redis.get(session_id)
        return json.loads(data) if data else None
    
    async def delete(self, session_id):
        await self.redis.delete(session_id)

memory = Memory(backend=RedisMemory("redis://localhost:6379"))
```

---

### 4. Orchestration

**Basic Orchestrator**:
```python
from agentcore import Orchestrator

orchestrator = Orchestrator(
    name="MyOrchestrator",
    agents=[agent1, agent2, agent3],
    strategy="sequential",  # or "parallel"
    memory=shared_memory
)

# Invoke orchestrator
result = await orchestrator.execute({
    "input": "Complex task requiring multiple agents"
})
```

**Deploy to Lambda**:
```python
orchestrator.deploy(
    function_name="my-orchestrator",
    runtime="python3.11",
    memory_mb=3008,
    timeout_seconds=300,
    environment={
        'VAR1': 'value1',
        'VAR2': 'value2'
    }
)
```

---

## 🌐 Strands SDK Patterns

### 1. Workflow Definition

**Basic Workflow**:
```python
from strands import Workflow, State, Node

class MyWorkflow(Workflow):
    def __init__(self):
        super().__init__(name="MyWorkflow")
        self.state = State({'input': None, 'output': None})
        self.define_workflow()
    
    def define_workflow(self):
        # Add nodes (steps)
        self.add_node(
            "step1",
            agent=agent1,
            inputs=['input'],
            outputs=['intermediate']
        )
        
        self.add_node(
            "step2",
            agent=agent2,
            inputs=['intermediate'],
            outputs=['output']
        )
    
    async def run(self, input_data):
        self.state['input'] = input_data
        return await self.execute()
```

---

### 2. Parallel Execution

**Parallel Agents**:
```python
workflow.add_parallel_group(
    "parallel_analysis",
    nodes=[
        {
            "name": "usa_check",
            "agent": jurisdiction_agent,
            "inputs": ['contract'],
            "outputs": ['usa_result']
        },
        {
            "name": "uk_check",
            "agent": jurisdiction_agent,
            "inputs": ['contract'],
            "outputs": ['uk_result']
        },
        {
            "name": "eu_check",
            "agent": jurisdiction_agent,
            "inputs": ['contract'],
            "outputs": ['eu_result']
        }
    ]
)

# All 3 agents run simultaneously (3x faster!)
```

---

### 3. Conditional Branching

**Branch Based on State**:
```python
workflow.add_conditional_branch(
    "risk_router",
    condition=lambda state: state['risk_level'],
    branches={
        'LOW': ['explain_only'],
        'MEDIUM': ['explain_and_negotiate'],
        'HIGH': ['explain_and_negotiate'],
        'CRITICAL': ['urgent_action'],
        'SCAM': ['block_and_warn']
    }
)
```

---

### 4. State Management

**Persistent State**:
```python
from strands import StateManager

state_manager = StateManager(
    backend="dynamodb",
    table_name="workflow-state"
)

# Save checkpoint
await state_manager.save_checkpoint(workflow_id, state)

# Resume workflow
workflow = await state_manager.resume_workflow(workflow_id)
```

---

### 5. Error Handling

**Retry Strategy**:
```python
workflow.add_error_handler(
    node="api_call",
    retry_strategy={
        'max_retries': 3,
        'backoff': 'exponential',  # 1s, 2s, 4s
        'retry_on': ['ThrottlingException', 'TimeoutError']
    },
    fallback=lambda state: {
        'result': 'Error: Service temporarily unavailable'
    }
)
```

---

### 6. Agent Handoffs

**Dynamic Handoff**:
```python
# Agent can hand off to another agent
agent1.add_handoff(
    to_agent=agent2,
    condition=lambda state: state['needs_escalation'],
    message="Escalating to specialist agent"
)
```

---

### 7. Human-in-the-Loop (HITL)

**Human Review Node**:
```python
from strands import HumanReviewNode

workflow.add_node(
    "human_review",
    node_type=HumanReviewNode,
    review_prompt="Approve this action?",
    timeout_seconds=300,  # 5 minutes
    fallback="auto_approve"  # If no response
)
```

---

### 8. Observability

**CloudWatch + X-Ray**:
```python
from strands import ObservabilityConfig

workflow.configure_observability(
    ObservabilityConfig(
        log_level="INFO",
        trace_all_steps=True,
        cloudwatch_log_group="/aws/strands/my-workflow",
        xray_enabled=True,
        custom_metrics=[
            'workflow_duration',
            'agent_invocations',
            'error_rate'
        ]
    )
)

# View traces in AWS X-Ray console
# View metrics in CloudWatch
```

---

## 🎯 ContractGuard Implementation Checklist

### AgentCore Features ✅
- [ ] **Agent 1**: Analysis Agent (Nova Pro)
- [ ] **Agent 2**: Explanation Agent (Nova Lite)
- [ ] **Agent 3**: Negotiation Agent (Claude 3.5)
- [ ] **Agent 4**: Action Agent (Claude 3.5)
- [ ] **Tool 1**: LegalKBTool (Bedrock KB RAG)
- [ ] **Tool 2**: JurisdictionChecker (multi-jurisdiction API)
- [ ] **Tool 3**: ContractParser (extract structured data)
- [ ] **Tool 4**: MarketRateTool (external API)
- [ ] **Tool 5**: CaseLawSearch (vector search)
- [ ] **Memory**: DynamoDB persistence (conversation + state)
- [ ] **Orchestration**: Coordinate 4 agents

### Strands Features ✅
- [ ] **Sequential Workflow**: Analysis → Explanation → Negotiation
- [ ] **Parallel Execution**: Multi-jurisdiction checks (USA/UK/EU)
- [ ] **Conditional Branching**: Risk-based routing (LOW/MEDIUM/HIGH/CRITICAL/SCAM)
- [ ] **State Management**: DynamoDB checkpoints
- [ ] **Error Handling**: Retry strategies for all agents
- [ ] **Agent Handoffs**: Negotiation → Action escalation
- [ ] **HITL**: Human review for CRITICAL contracts
- [ ] **Observability**: CloudWatch + X-Ray tracing

### Evidence Linking (RAG Provenance) ✅
- [ ] Extract KB citation metadata
- [ ] Show source URLs for every claim
- [ ] Display confidence scores
- [ ] Link to exact legal documents

---

## 🏆 Hackathon Submission Checklist

### Code
- [ ] GitHub repo with all source code
- [ ] Requirements.txt with all dependencies
- [ ] README.md with setup instructions
- [ ] .env.example with API key templates

### Architecture
- [ ] Architecture diagram (PNG/SVG)
- [ ] Show AgentCore components (Agents, Tools, Memory, Orchestration)
- [ ] Show Strands workflow (sequential, parallel, conditional)
- [ ] Label AWS services used

### Demo Video (~3 minutes)
- [ ] Problem statement (0:00-0:30)
- [ ] Solution overview (0:30-1:00)
- [ ] Live demo (1:00-2:30)
  - Upload contract
  - Show analysis with evidence links
  - Show negotiation advice
  - Show action plan
- [ ] Technical highlights (2:30-3:00)
  - AgentCore primitives used
  - Strands patterns implemented
  - AWS services leveraged

### Deployment
- [ ] Live website URL
- [ ] API Gateway endpoint
- [ ] Lambda functions deployed
- [ ] Knowledge Bases created
- [ ] DynamoDB tables set up

### Documentation
- [ ] Text description (problem, solution, impact)
- [ ] Setup instructions (how to reproduce)
- [ ] API documentation
- [ ] Architecture explanation

---

## 🚀 Quick Start Commands

```bash
# 1. Configure AWS
aws configure --profile hackathon
# Enter your AWS Access Key ID when prompted
# Enter your AWS Secret Access Key when prompted
# Region: us-east-1

# 2. Install SDKs
pip install amazon-bedrock-agentcore strands-agents boto3

# 3. Enable Bedrock models
aws bedrock list-foundation-models --region us-east-1 --profile hackathon

# 4. Deploy infrastructure
python deploy_agentcore_infrastructure.py

# 5. Set up Knowledge Bases
python setup_knowledge_bases.py

# 6. Deploy agents
python deploy_analysis_agent_agentcore.py
python deploy_explanation_agent.py
python deploy_negotiation_agent.py
python deploy_action_agent.py

# 7. Deploy Strands workflow
python deploy_strands_workflow.py

# 8. Test full system
python test_full_workflow.py

# 9. Deploy frontend
python deploy_frontend.py
```

---

## 💡 Tips for Winning

1. **Use ALL AgentCore primitives** - Judges will look for Agents, Tools, Memory, Orchestration
2. **Use ALL Strands patterns** - Show sequential, parallel, conditional, HITL, error handling
3. **Evidence linking is key** - Every AI claim needs a source URL (RAG provenance)
4. **Real-world impact** - Emphasize $5B freelancer losses you're preventing
5. **Clean demo** - Practice demo video, keep it under 3 minutes, show end-to-end workflow
6. **Good architecture** - Clear diagram showing all components
7. **Reproducible** - Provide clear setup instructions
8. **Novel problem** - First AI agent for freelance contract protection
9. **Multi-jurisdiction** - USA/UK/EU law checking is impressive
10. **Observability** - Show CloudWatch logs and X-Ray traces in demo

---

## 📞 Support

- **AgentCore Issues**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues
- **Strands Issues**: https://github.com/strands-agents/samples/issues
- **AWS Support**: Use AWS Support Center
- **Hackathon Questions**: Check hackathon Discord/Slack

Good luck! 🚀
