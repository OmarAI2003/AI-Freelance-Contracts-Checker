# Action Agent Deployment Guide
## AWS Bedrock AgentCore + Strands SDK

Your Action Agent is now properly built using **AgentCore + Strands SDK** (the hackathon requirements)!

## ✅ What's Different Now

**BEFORE (Wrong):**
- ❌ Used Bedrock Agents (managed service)
- ❌ Manual Lambda deployment
- ❌ Action groups configuration

**NOW (Correct for Hackathon):**
- ✅ Uses **AWS Bedrock AgentCore Runtime**
- ✅ Uses **Strands SDK** for agent logic
- ✅ Conversational AI with 4 custom tools
- ✅ Proper `@app.entrypoint` decorator
- ✅ Simple deploy with `agentcore` CLI

## 📦 Architecture

```
action_agent_agentcore.py
├── bedrock_agentcore.runtime.BedrockAgentCoreApp  # AgentCore wrapper
├── strands.Agent                                   # Strands agent framework
├── strands.tool decorators                         # 4 custom tools
│   ├── @tool search_similar_cases
│   ├── @tool generate_action_plan
│   ├── @tool get_evidence_checklist
│   └── @tool get_legal_resources
└── @app.entrypoint invoke()                        # AgentCore entry point
```

## 🚀 Local Testing (Do This First!)

Test locally before deploying:

```powershell
# Install dependencies
cd d:\aws_hackathon\src\agents\action
pip install -r requirements.txt

# Test locally
python test_local_agentcore.py
```

**Expected Output:**
```
🧪 Testing Action Agent (AgentCore + Strands SDK)

📤 You: Hi, I need help with a problem
🤖 Agent Response:
   Hello! I'm here to help you with your contract dispute. 
   Could you tell me more about the problem you're facing?
   ...
```

## 📋 Deployment Steps

### Step 1: Install AgentCore CLI

```powershell
pip install bedrock-agentcore-starter-toolkit
```

### Step 2: Configure Your Agent

```powershell
cd d:\aws_hackathon\src\agents\action

# Configure (this creates .bedrock_agentcore.yaml)
agentcore configure `
  --entrypoint action_agent_agentcore.py `
  --name freelancer-action-agent `
  --auto-create-execution-role
```

**What this does:**
- Creates execution role with permissions
- Generates Dockerfile
- Creates `.bedrock_agentcore.yaml` config
- Sets up ECR repository

### Step 3: Deploy to AWS

```powershell
# Deploy (this builds container and deploys to AWS)
agentcore launch
```

**What this does:**
- Builds Docker container with your agent
- Pushes to Amazon ECR
- Deploys to AgentCore Runtime (Lambda-based)
- Returns agent ARN for invocation

### Step 4: Test Deployed Agent

```powershell
# Invoke your deployed agent
agentcore invoke '{"prompt":"Hello, my client won't pay me $5000"}'
```

## 🔍 Deployment Output

After `agentcore launch`, you'll see:

```
✅ Agent deployed successfully!
Agent ARN: arn:aws:bedrock-agentcore:us-east-1:897722703585:agent/xxxxx
Endpoint: https://xxxxx.lambda-url.us-east-1.on.aws/
```

**Save this information!** You'll need it to:
- Invoke the agent
- Integrate with frontend
- Monitor performance

## 🧪 Testing Your Deployed Agent

### Test 1: Simple Greeting
```powershell
agentcore invoke '{"prompt":"Hi, I need help"}'
```

**Expected:** Agent introduces itself and asks about your problem

### Test 2: Full Conversation
```powershell
# Message 1
agentcore invoke '{"prompt":"My client won't pay me"}'

# Message 2 (new session)
agentcore invoke '{"prompt":"My client won't pay me $5000 for web work, due 60 days ago, I'm in USA"}'
```

**Expected:** Agent provides actionable guidance, searches for cases, generates action plan

## 📊 What the Agent Does

### Conversational Flow:
1. **Greets user** - Warm introduction
2. **Asks questions** - Gathers context (amount, jurisdiction, timeline)
3. **Uses tools dynamically:**
   - `search_similar_cases` - Finds legal precedents
   - `generate_action_plan` - Creates personalized plan with Claude
   - `get_evidence_checklist` - Lists evidence to gather
   - `get_legal_resources` - Jurisdiction-specific resources
4. **Explains results** - Plain English, empathetic tone
5. **Provides next steps** - Actionable guidance

### Example Conversation:
```
User: "My client won't pay me"
Agent: "I'm sorry to hear that. To help you better:
        - How much are they refusing to pay?
        - When was payment originally due?
        - What jurisdiction are you in (USA/UK/EU)?"

User: "$5000, due 60 days ago, USA"
Agent: "Thank you. Let me search for similar cases and 
        create an action plan for you..."
        [Uses search_similar_cases tool]
        [Uses generate_action_plan tool]
        "Here's what you should do..."
```

## 🛠️ AgentCore Features Used

1. **Runtime** - Managed serverless execution
2. **Strands SDK** - Agent framework with tools
3. **Auto-scaling** - Handles multiple concurrent users
4. **Logging** - CloudWatch integration
5. **Security** - IAM-based execution role

## 📁 Files Created

- `action_agent_agentcore.py` - Main agent code (635 lines)
- `requirements.txt` - Python dependencies
- `test_local_agentcore.py` - Local testing script
- `.bedrock_agentcore.yaml` - Config (created by `agentcore configure`)
- `Dockerfile` - Container definition (created by `agentcore configure`)

## 🔄 Update Your Agent

After making changes:

```powershell
# Re-deploy
agentcore launch
```

AgentCore automatically:
- Rebuilds container
- Updates deployment
- Maintains same endpoint URL

## 🧹 Cleanup Old Resources

Delete the old Bedrock Agents infrastructure (not needed anymore):

```powershell
# Delete Lambda function
aws lambda delete-function `
  --function-name ActionAgentTools-20251018-024216 `
  --region us-east-1

# Delete Bedrock Agent
aws bedrock-agent delete-agent `
  --agent-id BKOO1E5O95 `
  --region us-east-1 `
  --skip-resource-in-use-check
```

## 🎯 Next Steps

1. ✅ **Test locally** - `python test_local_agentcore.py`
2. ✅ **Deploy to AgentCore** - `agentcore launch`
3. ✅ **Test deployed agent** - `agentcore invoke`
4. ✅ **Integrate with frontend** - Use agent ARN/URL
5. ✅ **Show to team** - Demo the conversational AI!

## 💡 Hackathon Points

This implementation highlights:
- ✅ **AgentCore Runtime** - Serverless agent hosting
- ✅ **Strands SDK** - Agent framework with tools
- ✅ **Custom Tools** - 4 domain-specific tools
- ✅ **Conversational AI** - Natural dialogue flow
- ✅ **Real-world Use Case** - Freelancer contract disputes
- ✅ **Bedrock Integration** - Uses Claude for dynamic responses

## 🆘 Troubleshooting

**Issue: "agentcore: command not found"**
```powershell
pip install bedrock-agentcore-starter-toolkit
```

**Issue: Model access error**
```powershell
# This is already handled - your model access was approved!
# The agent will work now with AgentCore
```

**Issue: Import errors**
```powershell
pip install -r requirements.txt
```

---

**Ready to deploy? Run:**
```powershell
cd d:\aws_hackathon\src\agents\action
agentcore configure --entrypoint action_agent_agentcore.py --name freelancer-action-agent --auto-create-execution-role
agentcore launch
```
