# Negotiation Agent

**Developer**: Developer 3  
**Component**: Negotiation Strategy Agent  
**Timeline**: Day 1-3 (Oct 15-17, 2025)

---

## 📋 Overview

This folder contains the **Negotiation Agent** - the third agent in the ContractGuard AI pipeline.

### Purpose
Generates data-backed counter-proposals and negotiation strategies to help freelancers get fair terms.

### Key Features
- **Market Rate Comparison**: Real salary/rate data for freelancer roles
- **Case Law Search**: Similar disputes and outcomes
- **Counter-Proposal Generation**: Specific, fair alternatives
- **Email Templates**: Professional negotiation emails
- **Negotiation Tactics**: Strategic advice based on leverage

---

## 🛠️ Technologies Used

- **AWS Bedrock**: Claude 3.7 Sonnet model
- **Bedrock Knowledge Base**: Contract templates & case law
- **AgentCore Memory**: Negotiation history tracking
- **Market Data**: Bureau of Labor Statistics, Glassdoor, Upwork rates
- **Strands**: Tool integration library

---

## 📁 Files (To Be Created)

- `agent.py` - Main Negotiation Agent implementation
- `tools.py` - Market rate & case law search tools
- `prompts.py` - System prompts for negotiation coaching
- `tests.py` - Unit tests with market data validation
- `deploy.py` - AgentCore deployment script
- `requirements.txt` - Python dependencies

---

## 📊 Output Format

```json
{
  "counter_proposal": "Payment: Net 30 days at $100/hour",
  "market_data": {
    "current_rate": "$40/hr",
    "market_median": "$100/hr",
    "percentile": "15th (way below market)"
  },
  "justification": "California Labor Code § 204 + industry standard",
  "negotiation_email": "Dear [Client],\n\nThank you...",
  "tactics": ["Lead with data", "Frame as win-win", "Set deadline"],
  "similar_cases": [...]
}
```

---

## 🚀 Deployment

Deployed to **AWS Bedrock AgentCore Runtime** as a managed service.

**Agent ARN**: `arn:aws:bedrock:us-east-1:897722703585:agent/[AGENT_ID]`  
**Knowledge Base ID**: `[KB_ID from config.json]`

---

## 📖 Documentation

See `/docs/DEV3_NEGOTIATION_AGENT.md` for complete implementation guide.
