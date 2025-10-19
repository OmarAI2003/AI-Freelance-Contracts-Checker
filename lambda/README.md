# Lambda Orchestrator Function

AWS Lambda function that implements the orchestrator agent with A2A protocol support.

## Features

✅ **Intent Classification**: Keyword-based routing with context awareness
✅ **A2A Communication**: Proper Agent-to-Agent protocol with Bedrock AgentCore
✅ **Session Management**: DynamoDB-backed conversation history
✅ **Agent Routing**: Routes to specialist agents (real or dummy)
✅ **Error Handling**: Comprehensive logging and error recovery
✅ **Security**: Input validation, IAM role-based access

## Architecture

```
API Gateway → Lambda Orchestrator → Bedrock AgentCore Agents
                 ↓
              DynamoDB (Sessions)
```

## Environment Variables

Required environment variables:

```bash
DYNAMODB_TABLE=freelancer-sessions
S3_UPLOADS_BUCKET=freelancer-uploads-897722703585
ACTION_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD
ANALYSIS_AGENT_ARN=<empty-until-deployed>
EXPLANATION_AGENT_ARN=<empty-until-deployed>
NEGOTIATION_AGENT_ARN=<empty-until-deployed>
```

## API Endpoints

### POST /api/chat
Chat with the orchestrator.

**Request:**
```json
{
  "prompt": "My client won't pay me",
  "sessionId": "optional-session-id",
  "agent": "optional-specific-agent"
}
```

**Response:**
```json
{
  "response": "Agent response text",
  "agent": "action",
  "sessionId": "session-id",
  "timestamp": "2025-10-18T12:00:00.000Z"
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "lambda": {
    "function": "orchestrator-function",
    "version": "$LATEST",
    "memory": "512MB"
  },
  "agents": {
    "action": "deployed",
    "analysis": "pending",
    "explanation": "pending",
    "negotiation": "pending"
  }
}
```

### POST /api/upload
File upload endpoint (pending full implementation).

## Intent Classification

The orchestrator classifies user messages into categories:

| Intent | Keywords | Example |
|--------|----------|---------|
| **Analysis** | analyze, review, before sign | "Can you review this contract?" |
| **Explanation** | explain, what does, clarify | "What does indemnification mean?" |
| **Negotiation** | negotiate, counteroffer, modify | "I want to negotiate the payment terms" |
| **Action** | won't pay, breach, dispute, legal | "My client won't pay me" |

## A2A Communication Flow

1. **Intent Classification**: Classify user message → determine target agent
2. **Context Building**: Retrieve conversation history from DynamoDB
3. **Agent Invocation**: Call Bedrock AgentCore agent with context
4. **Response Handling**: Parse streaming response
5. **Session Update**: Save conversation to DynamoDB

## Deployment

### Package Lambda Function

```bash
cd src/lambda
pip install -r requirements.txt -t package/
cp orchestrator_lambda.py package/
cd package
zip -r ../orchestrator-lambda.zip .
```

### Deploy with AWS CLI

```bash
aws lambda create-function \
  --function-name freelancer-orchestrator \
  --runtime python3.11 \
  --role arn:aws:iam::897722703585:role/freelancer-lambda-role \
  --handler orchestrator_lambda.lambda_handler \
  --zip-file fileb://orchestrator-lambda.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    DYNAMODB_TABLE=freelancer-sessions,
    S3_UPLOADS_BUCKET=freelancer-uploads-897722703585,
    ACTION_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:897722703585:runtime/freelancer_action_agent-Q83Rk73nkD
  }"
```

### Update Existing Function

```bash
aws lambda update-function-code \
  --function-name freelancer-orchestrator \
  --zip-file fileb://orchestrator-lambda.zip
```

## Testing

### Test with AWS CLI

```bash
# Health check
aws lambda invoke \
  --function-name freelancer-orchestrator \
  --payload '{"httpMethod":"GET","path":"/api/health"}' \
  response.json && cat response.json

# Chat test
aws lambda invoke \
  --function-name freelancer-orchestrator \
  --payload '{"httpMethod":"POST","path":"/api/chat","body":"{\"prompt\":\"My client won\u0027t pay me\"}"}' \
  response.json && cat response.json
```

### Test Intent Classification

```python
from orchestrator_lambda import classify_intent

# Test cases
messages = [
    "Can you review this contract before I sign?",  # → analysis
    "What does indemnification mean?",              # → explanation
    "I want to negotiate the payment terms",        # → negotiation
    "My client won't pay me",                       # → action
]

for msg in messages:
    intent = classify_intent(msg, {})
    print(f"{msg} → {intent['agent']}")
```

## Monitoring

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/lambda/freelancer-orchestrator --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/freelancer-orchestrator \
  --filter-pattern "ERROR"
```

### CloudWatch Metrics

Key metrics to monitor:
- **Invocations**: Total number of Lambda invocations
- **Errors**: Function errors (should be < 1%)
- **Duration**: Execution time (target < 5 seconds)
- **Throttles**: Should be 0

## Security

### IAM Role Permissions

The Lambda function requires:
- `bedrock:InvokeAgent` - Call Bedrock AgentCore agents
- `dynamodb:Query`, `dynamodb:PutItem` - Session management
- `s3:GetObject`, `s3:PutObject` - File uploads
- `logs:CreateLogGroup`, `logs:PutLogEvents` - CloudWatch logging

See `aws/iam-policies/lambda-role.json` for complete policy.

### Input Validation

- All user inputs are validated and sanitized
- Session IDs are UUIDs
- Message length limits enforced (10KB max)
- ARN format validation

## Troubleshooting

### "Agent not found" Error

**Cause**: Agent ARN is incorrect or agent not deployed

**Fix**: Verify agent ARN with:
```bash
aws bedrock-agent-runtime list-agents --region us-east-1
```

### "Session not found" Error

**Cause**: DynamoDB table doesn't exist or IAM permissions missing

**Fix**: Create table and verify IAM role:
```bash
aws dynamodb describe-table --table-name freelancer-sessions
```

### "Timeout" Error

**Cause**: Agent taking too long to respond

**Fix**: Increase Lambda timeout:
```bash
aws lambda update-function-configuration \
  --function-name freelancer-orchestrator \
  --timeout 60
```

## Performance

**Typical metrics:**
- Cold start: ~2-3 seconds
- Warm invocation: ~500ms
- A2A call to agent: ~2-5 seconds
- Total response time: ~3-8 seconds

**Optimization tips:**
- Keep Lambda warm with CloudWatch Events (1 ping/5 min)
- Use provisioned concurrency for predictable latency
- Optimize DynamoDB queries (use indexes)
- Cache agent ARNs in memory

## Cost Estimate

**Lambda:**
- 10,000 requests/month
- 512MB memory, 5s average duration
- Cost: ~$4/month

**DynamoDB:**
- 1GB storage
- 100 WCU, 100 RCU
- Cost: ~$2.50/month

**Total Lambda + DynamoDB**: ~$6.50/month

## Next Steps

1. ✅ Lambda function created
2. ⏳ Deploy to AWS
3. ⏳ Connect to API Gateway
4. ⏳ Test A2A with Action Agent
5. ⏳ Integrate teammates' agents when ready

## Support

For issues or questions:
- Check CloudWatch logs: `/aws/lambda/freelancer-orchestrator`
- Review X-Ray traces for performance bottlenecks
- Test with dummy responses first (set agent ARNs to empty)
