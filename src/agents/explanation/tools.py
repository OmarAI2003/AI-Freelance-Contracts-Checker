"""
Tools for the Explanation Agent

NOTE: This agent uses a pure LLM approach (no external tools).

The agent relies on Claude's training data to explain legal concepts and contract clauses.
This provides:
- ⚡ Fast responses (no API calls)
- 💰 Free operation (no search API costs)
- 🔒 Privacy (no external data sharing)
- ✅ Reliability (no external dependencies)

The LLM has been trained on vast amounts of legal information through April 2024,
including contract law, labor laws, and freelance regulations.

DISCLAIMERS:
- Training data cutoff: April 2024
- For specific legal advice, consult an attorney
- Laws may have changed since training
- Responses are educational, not legal advice

For production enhancement, consider adding:
- Web search verification (Tavily, Serper)
- AWS Bedrock Knowledge Base for curated legal documents
- Real-time legal database integration (Westlaw, LexisNexis)
"""

# No tools needed for pure LLM approach
# The agent answers directly using Claude's training data
# No tools needed for pure LLM approach
# The agent answers directly using Claude's training data

__all__ = []  # No tools exported
