# Infrastructure

**Owner**: Team Lead (You)  
**Component**: AWS Resource Setup  
**Created**: October 17, 2025

---

## 📋 Overview

This folder contains the infrastructure setup scripts and configuration for ContractGuard AI.

### Purpose
One-time setup that creates all necessary AWS resources for the team.

---

## ☁️ AWS Resources Created

**Account**: 897722703585  
**Region**: us-east-1  
**Setup Date**: 2025-10-17

### S3 Buckets
- `contractguard-legal-docs-20251017-014038` → Legal documents (Dev 1 & 2)
- `contractguard-contracts-20251017-014038` → Contract templates (Dev 3)
- `contractguard-uploads-20251017-014038` → User uploads (Frontend)

### IAM Role
- **Name**: ContractGuardAgentRole-20251017-014038
- **ARN**: `arn:aws:iam::897722703585:role/ContractGuardAgentRole-20251017-014038`
- **Permissions**: S3, Bedrock, Kendra access

### Memory
- **ID**: contractguard-memory-20251017-014038
- **Purpose**: AgentCore memory management

### Model
- **ID**: us.anthropic.claude-3-7-sonnet-20250219-v1:0
- **Provider**: Anthropic (Claude 3.7 Sonnet)

---

## 📁 Files

- `setup.py` - Infrastructure creation script (already run ✅)
- `config.json` - AWS resource IDs (⚠️ **DO NOT COMMIT!**)
- `README.md` - This file

---

## 🔒 Security

**IMPORTANT**: `config.json` contains sensitive AWS resource IDs.

- ✅ Already in `.gitignore`
- ✅ Share privately with team (email, Slack DM)
- ❌ **NEVER** commit to GitHub
- ❌ **NEVER** share publicly

---

## 🚀 Usage

### For Team Lead (Already Done ✅)
```bash
cd src/infrastructure
python setup.py
```

### For Developers
1. Receive `config.json` from team lead
2. Save to `src/infrastructure/config.json`
3. Load in your agent code:
```python
import json
with open('src/infrastructure/config.json') as f:
    config = json.load(f)
    
bucket = config['legal_bucket']
role_arn = config['agent_role_arn']
```

---

## 📤 Upload Documents

Each developer uploads their PDFs to S3:

```bash
# Developer 1 & 2: Legal documents
aws s3 cp your-legal-doc.pdf s3://contractguard-legal-docs-20251017-014038/

# Developer 3: Contract templates
aws s3 cp your-contract.pdf s3://contractguard-contracts-20251017-014038/
```

---

## 📖 Documentation

See project root `/SETUP_COMPLETE.md` for full setup summary.
