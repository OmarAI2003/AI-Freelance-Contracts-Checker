# Analysis Agent

**Developer**: Developer 1  
**Component**: Contract Analysis Agent  
**Timeline**: Day 1-3 (Oct 15-17, 2025)

---

## 📋 Overview

This folder contains the **Analysis Agent** - the first agent in the ContractGuard AI pipeline.

### Purpose
Analyzes uploaded contracts to detect unfair clauses and assess risk levels.

### Key Features
- **Contract Parser**: Extracts text from PDF/DOCX files
- **Jurisdiction Checker**: Validates legal compliance (USA, UK, EU)
- **Risk Scoring**: Classifies clauses from LOW to SCAM
- **Clause Detection**: Identifies unfair payment terms, termination clauses, IP rights, liability waivers

---

## 🛠️ Technologies Used

- **AWS Bedrock**: Claude 3.7 Sonnet model
- **AgentCore**: Agent framework with memory management
- **Strands**: Tool integration library
- **Python Libraries**: PyPDF2, python-docx, pydantic

---

## 📁 Files (To Be Created)

- `agent.py` - Main Analysis Agent implementation
- `tools.py` - Contract parser & jurisdiction checker tools
- `prompts.py` - System prompts for the agent
- `tests.py` - Unit tests
- `deploy.py` - AgentCore deployment script
- `requirements.txt` - Python dependencies

---

## 📊 Output Format

```json
{
  "overall_risk": "high",
  "unfair_clauses": [
    {
      "clause_type": "payment_terms",
      "text": "Payment: Net 90 days",
      "risk_level": "high",
      "reason": "Violates California 30-day payment law"
    }
  ],
  "recommendations": [...]
}
```

---

## 🚀 Deployment

Deployed to **AWS Bedrock AgentCore Runtime** as a managed service.

**Agent ARN**: `arn:aws:bedrock:us-east-1:897722703585:agent/[AGENT_ID]`

---

## 📖 Documentation

See `/docs/DEV1_ANALYSIS_AGENT.md` for complete implementation guide.
