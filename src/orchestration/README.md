# Orchestration Layer

**Developer**: Developer 4 (Integration Lead)  
**Component**: Agent Orchestration & Workflow  
**Timeline**: Day 3-4 (Oct 17-18, 2025)

---

## 📋 Overview

This folder contains the **Orchestration Layer** that connects all three agents in a sequential workflow.

### Purpose
Coordinates the Analysis, Explanation, and Negotiation agents to produce a complete contract analysis.

### Workflow
1. User uploads contract
2. **Analysis Agent** → Detects risks and unfair clauses
3. **Explanation Agent** → Explains each unfair clause in plain English
4. **Negotiation Agent** → Generates counter-proposals for high-risk clauses
5. Final report → Combined output from all agents

---

## 🛠️ Technologies Used

- **Strands Workflow**: Sequential agent orchestration
- **AgentCore Memory**: Shared memory across agents
- **AWS Lambda**: Serverless execution (optional)
- **API Gateway**: REST API endpoints
- **S3**: Report storage

---

## 📁 Files (To Be Created)

- `workflow.py` - Main orchestration logic
- `deploy.py` - AgentCore deployment script
- `test_workflow.py` - End-to-end tests
- `api.py` - REST API endpoints (optional)

---

## 🔄 Data Flow

```
User Contract
    ↓
Analysis Agent (risks)
    ↓
Explanation Agent (plain English)
    ↓
Negotiation Agent (counter-proposals)
    ↓
Final Report (combined)
```

---

## 📊 Output Format

```json
{
  "analysis": {...},
  "explanations": [{...}],
  "negotiation": {...},
  "final_report_url": "s3://...",
  "overall_recommendation": "NEGOTIATE",
  "session_id": "uuid"
}
```

---

## 🚀 Deployment

Deployed to **AWS Bedrock AgentCore Runtime** as the main orchestrator.

**Orchestrator ARN**: `arn:aws:bedrock:us-east-1:897722703585:agent/[ORCHESTRATOR_ID]`

---

## 📖 Documentation

See `/docs/DEV4_INTEGRATION.md` for complete implementation guide.
