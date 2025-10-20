# Negotiation Agent - AgentCore Runtime Deployment

## Overview
This agent helps freelancers negotiate better contract terms using AWS Bedrock AgentCore Runtime.

## Features
1. **Analyze Contract** - Identifies problematic clauses and unfair terms
2. **Explain Terms** - Simplifies complex legal language
3. **Negotiate Terms** - Generates strategies, counterproposals, and email templates
4. **Legal Advice** - Provides guidance on contract terms

## Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

Key dependencies:
- `bedrock-agentcore>=1.0.0` - AWS Bedrock AgentCore Runtime
- `boto3>=1.34.0` - AWS SDK
- `langchain>=0.1.0` - For LLM interactions
- `python-dotenv>=1.0.0` - Environment variable management

### AWS Requirements
1. AWS Account with Bedrock access
2. **Claude 3.5 Sonnet (v2)** model access enabled in Bedrock
   - Model ID: `anthropic.claude-3-sonnet-20240229-v1:0`
   - **Enable "Claude Sonnet 3.5 for all clients"** in AWS Bedrock Console
3. IAM role with the following permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock-runtime:InvokeModel",
           "bedrock-agent:*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

### Environment Variables
Create a `.env` file:
```env
AWS_REGION=us-east-1
AWS_BEARER_TOKEN_BEDROCK=your-bearer-token-here
```

## Enable Claude 3.5 Sonnet in AWS Bedrock

Before deploying, you must enable the Claude 3.5 Sonnet model:

1. **Login to AWS Console** and navigate to Amazon Bedrock
2. Go to **Model access** in the left sidebar
3. Click **Manage model access** or **Edit**
4. Find **Anthropic** section and check:
   - ☑️ **Claude 3.5 Sonnet** (anthropic.claude-3-sonnet-20240229-v1:0)
   - ☑️ **Enable for all clients** (if you want organization-wide access)
5. Click **Save changes**
6. Wait for the status to change to **Access granted** (usually takes 1-2 minutes)

**Note**: Model availability varies by region. Recommended regions:
- `us-east-1` (N. Virginia) - Most features
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)

## Deployment Steps

### Option 1: Deploy to AgentCore Runtime

1. **Install AgentCore CLI**:
```bash
pip install bedrock-agentcore-cli
```

2. **Initialize the agent**:
```bash
cd src/agents/negotiation
agentcore init
```

3. **Deploy the agent**:
```bash
agentcore deploy --name negotiation-agent --runtime python3.11
```

4. **Get the agent endpoint**:
```bash
agentcore describe negotiation-agent
```

### Option 2: Local Testing

Run the agent locally:
```bash
python deploy.py
```

Test with curl:
```bash
# Analyze Contract
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "action": "analyze_contract",
    "input": {
      "contract_text": "Payment Terms: Net 90 days. No late payment penalties."
    },
    "session_id": "test-session"
  }'

# Explain Terms
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "action": "explain_terms",
    "input": {
      "terms": "Indemnification clause: Provider indemnifies client for all claims."
    },
    "session_id": "test-session"
  }'

# Negotiate Terms
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "action": "negotiate_terms",
    "input": {
      "current_terms": "Payment: Net 90 days at $40/hour",
      "desired_changes": [
        "Reduce to Net 30",
        "Increase rate to $120/hour"
      ],
      "context": {
        "experience": "5 years",
        "role": "Senior Developer"
      }
    },
    "session_id": "test-session"
  }'

# Legal Advice
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "action": "legal_advice",
    "input": {
      "contract_text": "Non-compete: 5 years worldwide restriction",
      "question": "Is this enforceable in California?"
    },
    "session_id": "test-session"
  }'
```

## Integration with Website

### JavaScript/TypeScript Example

```javascript
class NegotiationAgentClient {
  constructor(agentEndpoint) {
    this.endpoint = agentEndpoint;
  }

  async analyzeContract(contractText, sessionId = 'default') {
    const response = await fetch(`${this.endpoint}/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'analyze_contract',
        input: { contract_text: contractText },
        session_id: sessionId
      })
    });
    return await response.json();
  }

  async explainTerms(terms, sessionId = 'default') {
    const response = await fetch(`${this.endpoint}/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'explain_terms',
        input: { terms },
        session_id: sessionId
      })
    });
    return await response.json();
  }

  async negotiateTerms(currentTerms, desiredChanges, context = {}, sessionId = 'default') {
    const response = await fetch(`${this.endpoint}/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'negotiate_terms',
        input: {
          current_terms: currentTerms,
          desired_changes: desiredChanges,
          context: context
        },
        session_id: sessionId
      })
    });
    return await response.json();
  }

  async getLegalAdvice(contractText, question, sessionId = 'default') {
    const response = await fetch(`${this.endpoint}/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'legal_advice',
        input: {
          contract_text: contractText,
          question: question
        },
        session_id: sessionId
      })
    });
    return await response.json();
  }
}

// Usage
const agent = new NegotiationAgentClient('https://your-agent-endpoint.amazonaws.com');

// When user clicks "Analyze Contract"
const analysis = await agent.analyzeContract(contractText);
console.log(analysis.analysis);

// When user clicks "Explain Terms"
const explanation = await agent.explainTerms(terms);
console.log(explanation.explanation);

// When user clicks "Negotiate Terms"
const strategy = await agent.negotiateTerms(currentTerms, desiredChanges, context);
console.log(strategy.strategy);

// When user clicks "Legal Action"
const advice = await agent.getLegalAdvice(contractText, question);
console.log(advice.advice);
```

### React Example

```jsx
import { useState } from 'react';

function NegotiationAgent() {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  
  const agentClient = new NegotiationAgentClient('https://your-endpoint');

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const contractText = document.getElementById('contract-input').value;
      const response = await agentClient.analyzeContract(contractText);
      setResult(response.analysis);
    } catch (error) {
      setResult('Error: ' + error.message);
    }
    setLoading(false);
  };

  return (
    <div>
      <textarea id="contract-input" />
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Contract'}
      </button>
      <div>{result}</div>
    </div>
  );
}
```

## Payload Formats

### Analyze Contract
```json
{
  "action": "analyze_contract",
  "input": {
    "contract_text": "string"
  },
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "analysis": "string",
  "action": "analyze_contract",
  "session_id": "session-id"
}
```

### Explain Terms
```json
{
  "action": "explain_terms",
  "input": {
    "terms": "string"
  },
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "explanation": "string",
  "action": "explain_terms",
  "session_id": "session-id"
}
```

### Negotiate Terms
```json
{
  "action": "negotiate_terms",
  "input": {
    "current_terms": "string",
    "desired_changes": ["string"],
    "context": {
      "experience": "string",
      "role": "string",
      "location": "string"
    }
  },
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "strategy": "string",
  "action": "negotiate_terms",
  "session_id": "session-id"
}
```

### Legal Advice
```json
{
  "action": "legal_advice",
  "input": {
    "contract_text": "string",
    "question": "string"
  },
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "advice": "string",
  "action": "legal_advice",
  "session_id": "session-id"
}
```

## Monitoring & Logs

View agent logs:
```bash
agentcore logs negotiation-agent --follow
```

Monitor performance:
```bash
agentcore metrics negotiation-agent
```

## Model Specifications

**Claude 3.5 Sonnet (v2)** - `anthropic.claude-3-sonnet-20240229-v1:0`

### Features:
- **Context Window**: 200K tokens
- **Max Output**: 4096 tokens (we use 2048 for efficiency)
- **Multilingual Support**: English, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese
- **Advanced Reasoning**: Superior contract analysis and legal understanding
- **Structured Output**: Consistent format for parsing

### Configuration in Agent:
```python
model_kwargs = {
    "anthropic_version": "bedrock-2023-05-31",
    "temperature": 0.7,  # Balanced creativity and consistency
    "max_tokens": 2048    # Sufficient for detailed responses
}
```

### Why Claude 3.5 Sonnet?
- **Legal Understanding**: Trained on legal documents and contracts
- **Nuanced Analysis**: Can identify subtle unfair terms
- **Clear Communication**: Explains complex terms in simple language
- **Professional Tone**: Appropriate for business negotiations

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Ensure AWS credentials are properly configured
   - Check IAM role permissions
   - Verify bearer token is valid

2. **Model Not Available**
   - Request Claude 3 access in AWS Bedrock console
   - Check region availability

3. **Timeout Errors**
   - Increase timeout in AgentCore config
   - Optimize prompt length

## Testing

Run the test suite:
```bash
pytest tests.py -v
```

All 4 tests should pass:
- ✓ test_analyze_contract
- ✓ test_explain_terms
- ✓ test_negotiate_terms
- ✓ test_get_legal_advice

## Support

For issues or questions:
1. Check AWS Bedrock documentation
2. Review AgentCore Runtime docs
3. Contact the development team
