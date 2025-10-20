# 🛡️ ContractGuard AI Comprehensive Guardrail System

This document outlines the comprehensive guardrail system for the AI-Freelance-Contracts-Checker project, ensuring safe, accurate, and compliant contract analysis across all three agents.

## 📋 Overview

The guardrail system implements 8 comprehensive steps to ensure AI safety and compliance:

1. **Guardrail Details** - Basic configuration and metadata
2. **Content Filters** - Block harmful content (hate speech, violence, etc.)
3. **Denied Topics** - Prevent unauthorized legal advice and illegal activities
4. **Word Filters** - Filter profanity and require legal disclaimers
5. **Sensitive Information Filters** - Protect PII and confidential data
6. **Contextual Grounding Check** - Ensure responses are grounded in knowledge base
7. **Automated Reasoning Check** - Validate logical consistency and evidence
8. **Review and Create** - Deploy and monitor the guardrail

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Analysis Agent │    │ Explanation Agent│    │Negotiation Agent│
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  ContractGuard Guardrail │
                    │                         │
                    │ • Content Filtering     │
                    │ • Topic Validation      │
                    │ • PII Protection        │
                    │ • Legal Compliance      │
                    │ • Evidence Grounding    │
                    └─────────────────────────┘
```

## 🚀 Quick Start

### 1. Deploy the Guardrail

```bash
cd src/infrastructure
python deploy_guardrail.py
```

### 2. Update Agent Code

Add guardrail integration to your agents:

```python
from infrastructure.guardrail_integration import with_guardrail, ContractGuardGuardrail

# Method 1: Using decorator
@with_guardrail(guardrail_id="your-guardrail-id", version="1", agent_type="analysis")
def analyze_contract(self, contract_text: str):
    # Your analysis logic here
    return analysis_result

# Method 2: Manual integration
guardrail = ContractGuardGuardrail("your-guardrail-id", "1")

def analyze_contract(self, contract_text: str):
    # Validate input
    input_result = guardrail.validate_input(contract_text, "analysis")
    if input_result.action == GuardrailAction.BLOCK:
        return {"error": input_result.message}
    
    # Your analysis logic
    result = perform_analysis(contract_text)
    
    # Validate output
    output_result = guardrail.validate_output(result, "analysis")
    return output_result.filtered_content or result
```

## 📊 Guardrail Configuration Details

### Step 1: Guardrail Details
- **Name**: ContractGuard AI Safety Guardrail
- **Description**: Multi-layered safety guardrail for freelance contract analysis
- **Tags**: Environment, compliance, and project metadata

### Step 2: Content Filters
| Filter Type | Strength | Action |
|-------------|----------|--------|
| Hate Speech | HIGH | BLOCK |
| Insults | MEDIUM | BLOCK |
| Sexual Content | HIGH | BLOCK |
| Violence | MEDIUM | BLOCK |
| Misconduct | HIGH | BLOCK |
| Prompt Attack | HIGH | BLOCK |

### Step 3: Denied Topics
- **Illegal Contract Advice**: Tax evasion, labor law circumvention
- **Unauthorized Legal Practice**: Specific legal representation advice
- **Personal Information Extraction**: Beyond contract analysis scope
- **Competitive Intelligence**: Extracting business secrets

### Step 4: Word Filters
- **Profanity Filter**: Blocks explicit language
- **Legal Disclaimer Trigger**: Auto-adds disclaimers for legal terms

### Step 5: Sensitive Information Filters
| PII Type | Action |
|----------|--------|
| SSN | ANONYMIZE |
| Credit Card | ANONYMIZE |
| Bank Account | ANONYMIZE |
| Phone Number | ANONYMIZE |
| Email Address | ANONYMIZE |
| Passport Number | ANONYMIZE |
| Driver License | ANONYMIZE |

### Step 6: Contextual Grounding
- **Grounding Threshold**: 0.8
- **Citation Required**: Yes
- **Hallucination Detection**: Enabled with 0.7 confidence threshold

### Step 7: Automated Reasoning
- **Legal Consistency**: 0.85 threshold
- **Risk Assessment Logic**: 0.9 threshold  
- **Evidence Support**: 0.8 threshold
- **Contradiction Detection**: Enabled
- **Logical Fallacy Detection**: Enabled

## 🎯 Agent-Specific Rules

### Analysis Agent
- Maximum risk escalation: CRITICAL
- Required evidence sources: 2 minimum
- Jurisdiction validation: REQUIRED
- No unauthorized legal advice

### Explanation Agent  
- Reading level: 8th grade
- Technical term definitions: REQUIRED
- Plain language requirement: Enabled
- Auto-disclaimer for legal terms

### Negotiation Agent
- Ethical negotiation only: Enabled
- No aggressive tactics: Enforced
- Collaborative approach: REQUIRED
- Conflict resolution focus

## 🔍 Monitoring and Compliance

### Logging
- **CloudWatch Group**: `/aws/bedrock/guardrails/contractguard`
- **Violation Level**: WARNING
- **Audit Trail**: 90-day retention

### Compliance Standards
- **GDPR**: Data minimization, consent tracking
- **CCPA**: Data deletion rights
- **Legal Ethics**: Unauthorized practice prevention

### Performance Metrics
- Response time threshold: 30 seconds
- Accuracy threshold: 85%
- Guardrail effectiveness monitoring

## 🛠️ Troubleshooting

### Common Issues

1. **Guardrail Blocking Valid Content**
   ```python
   # Check violation details
   result = guardrail.validate_input(content, agent_type)
   if result.violations:
       print("Violations:", result.violations)
   ```

2. **Missing Legal Disclaimers**
   - Automatically added for content containing legal keywords
   - Check `_needs_legal_disclaimer()` logic

3. **PII Detection False Positives**
   - Review regex patterns in configuration
   - Adjust anonymization rules

### Debug Mode
```python
import logging
logging.getLogger('guardrail_integration').setLevel(logging.DEBUG)
```

## 📈 Performance Optimization

### Caching
- Guardrail responses cached for identical inputs
- Cache TTL: 1 hour for validation results

### Batch Processing
```python
# Validate multiple inputs at once
results = guardrail.batch_validate([input1, input2, input3], agent_type)
```

### Async Support
```python
import asyncio

async def async_validate():
    result = await guardrail.validate_input_async(content, agent_type)
    return result
```

## 🔄 Updates and Maintenance

### Updating Guardrail Rules
1. Modify `guardrail_config.json`
2. Run `python deploy_guardrail.py --update`
3. Update agent configurations
4. Test with sample inputs

### Version Management
- Use semantic versioning (1.0.0, 1.1.0, etc.)
- Maintain backward compatibility
- Document breaking changes

### Monitoring Dashboard
Access guardrail metrics at:
- AWS CloudWatch: Guardrail performance
- Custom dashboard: `/aws/bedrock/guardrails/contractguard`

## 📞 Support

For guardrail issues:
1. Check CloudWatch logs for violation details
2. Review agent-specific rule configurations  
3. Validate AWS Bedrock guardrail status
4. Test with minimal examples to isolate issues

## 🔗 Related Documentation

- [AWS Bedrock Guardrails Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
- [Agent Configuration Guide](../agents/README.md)
- [Compliance Requirements](../../docs/COMPLIANCE.md)