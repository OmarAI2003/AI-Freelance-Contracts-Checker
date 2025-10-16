# ContractGuard AI

## Tagline
**AI Agent That Protects Freelancers From Unfair Contracts**

---

## Problem Statement
Freelancers worldwide lose over $5 billion annually to unfair, exploitative, or non-compliant contracts. Most lack legal expertise, face language barriers, and struggle to negotiate terms on platforms like Upwork, Fiverr, and Freelancer.com. Existing solutions are region-specific, expensive, or fail to address multi-jurisdictional risks and scams.

## Solution Overview
ContractGuard AI is a global, multilingual AI agent that analyzes, validates, and explains freelancer contracts in any language. It detects unfair clauses, compliance risks, scam patterns, and provides negotiation advice. The system supports English and Arabic (with more languages planned), and is designed for global freelancers, agencies, and platforms.

### Key Features
- **Multi-jurisdictional Compliance**: Checks contracts against global legal standards
- **Scam Detection**: Flags suspicious terms and payment risks
- **Negotiation Advice**: Suggests edits and negotiation strategies
- **Language Support**: English (primary)
- **Contract Type Selector**: Service Agreement, NDA, Work-for-Hire, Master Service Agreement, SOW
- **Professional UI**: Blue/White/Green color scheme for trust

## Solution Architecture
- **Frontend**: S3-hosted static website (React/HTML)
- **API Layer**: AWS API Gateway + Lambda (Python)
- **AI Processing**: AWS Bedrock AgentCore, Bedrock Foundation Models
- **Knowledge Base**: S3 corpus of global freelancer contracts

## AWS Services Used
- Amazon S3 (website, knowledge base)
- AWS Lambda (API, OCR)
- Amazon API Gateway
- Amazon Bedrock (AgentCore, Foundation Models)
- IAM (roles, permissions)
- CloudWatch (logging)

---

