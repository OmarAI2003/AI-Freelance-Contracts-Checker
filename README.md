# 🛡️ ContractGuard AI - Freelance Contract Analysis

> **AWS Bedrock Hackathon 2025** | AI-powered contract analysis for freelancers

Analyze contracts in 60 seconds. Know what you're signing. Negotiate better terms.

---

## 🎯 What It Does

ContractGuard AI helps freelancers worldwide:
- ✅ **Analyze** contracts for unfair clauses and hidden risks
- 📖 **Understand** complex legal jargon in plain English (8th-grade level)
- 🤝 **Negotiate** better terms with data-backed counter-proposals

---

## 🏗️ Architecture

**Multi-Agent System** powered by AWS Bedrock and Claude 3.7 Sonnet:

```
User Contract
    ↓
┌─────────────────────────┐
│  Analysis Agent (Dev 1) │ → Detects risks & unfair clauses
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Explanation Agent (Dev 2)│ → Translates legal → plain English
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Negotiation Agent (Dev 3)│ → Generates counter-proposals
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Orchestration (Dev 4)   │ → Combines all outputs
└─────────────────────────┘
    ↓
Final Report + Recommendation
```

---

## 📁 Project Structure

```
contractguard/
├── src/
│   ├── agents/
│   │   ├── analysis/ 
│   │   ├── explanation/     
│   │   └── negotiation/     
│   ├── orchestration/       
│   ├── frontend/            
│   └── infrastructure/      
├── tests/                   # Project tests
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Tech Stack

- **AWS Bedrock**: Claude 3.7 Sonnet (LLM)
- **AgentCore**: Bedrock agent framework
- **Strands**: Agent orchestration
- **Amazon Kendra**: Document search (optional)
- **S3**: Document storage
- **Python 3.10+**: Backend implementation

---

## 👥 Team

| Developer | Component | Folder | Status |
|-----------|-----------|--------|--------|
| Developer 1 | Analysis Agent | `src/agents/analysis/` | 🔨 In Progress |
| Developer 2 | Explanation Agent | `src/agents/explanation/` | 🔨 In Progress |
| Developer 3 | Negotiation Agent | `src/agents/negotiation/` | 🔨 In Progress |
| Developer 4 | Orchestration + Frontend | `src/orchestration/`, `src/frontend/` | ⏳ Pending |

---

**Built with ❤️ for freelancers who deserve fair contracts.**

**AWS Bedrock Hackathon 2025** | Team ContractGuard
