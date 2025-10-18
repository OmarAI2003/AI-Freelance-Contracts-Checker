# Explanation Agent

**Developer**: Developer 2  
**Component**: Legal Explanation Agent  
**Timeline**: Day 1-3 (Oct 15-17, 2025)

---

## 📋 Overview

This folder contains the **Explanation Agent** - the second agent in the ContractGuard AI pipeline.

### Purpose
Translates complex legal jargon into plain English that anyone can understand (8th-grade reading level).

### Key Features
- **Legal Knowledge Base Search**: RAG with Bedrock Knowledge Base
- **Plain English Translation**: Simplifies legal terms
- **Good vs Bad Examples**: Shows fair alternative clauses
- **Reading Level Validation**: Ensures 8th-grade comprehension
- **Context-Aware**: Uses memory to maintain conversation flow

---

## 🛠️ Technologies Used

- **AWS Bedrock**: Claude 3.7 Sonnet model
- **Bedrock Knowledge Base**: Legal documents & statutes
- **AgentCore Memory**: Conversation history management
- **Amazon Kendra**: Document search & retrieval
- **Strands**: Tool integration library

---

## 📁 Files (To Be Created)

- `agent.py` - Main Explanation Agent implementation
- `tools.py` - Legal KB search tool (RAG)
- `prompts.py` - System prompts with reading level requirements
- `tests.py` - Unit tests with readability checks
- `deploy.py` - AgentCore deployment script
- `requirements.txt` - Python dependencies

---

## 📊 Output Format

```json
{
  "clause": "Indemnification: You shall indemnify...",
  "simple_explanation": "This means if something goes wrong, you pay for everything - even if it's not your fault.",
  "why_unfair": "Good contracts share responsibility fairly.",
  "good_alternative": "Both parties share costs for issues they cause.",
  "reading_level": "8th grade",
  "examples": [...]
}
```

---

## 🚀 Deployment

Deployed to **AWS Bedrock AgentCore Runtime** as a managed service.

**Agent ARN**: `arn:aws:bedrock:us-east-1:897722703585:agent/[AGENT_ID]`  
**Knowledge Base ID**: `[KB_ID from config.json]`

---

## 📖 Documentation

See `/docs/DEV2_EXPLANATION_AGENT.md` for complete implementation guide.
