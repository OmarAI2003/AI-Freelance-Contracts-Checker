"""
Explanation Agent - Translates legal jargon into plain English using Claude 3.7 Sonnet
"""
from typing import Dict, Optional, Any, List
import json
from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel
from strands.hooks import HookRegistry
from bedrock_agentcore.memory import MemoryClient

from .prompts import EXPLANATION_SYSTEM_PROMPT
from .memory_hooks import ExplanationMemoryHooks


class GoodVersion(BaseModel):
    """Better version of the clause"""
    text: str = Field(description="Better clause wording")
    source: str = Field(description="Where this comes from")
    why_better: str = Field(description="Why it's better")


class ExplanationResponse(BaseModel):
    """Structured response from the Explanation Agent"""
    original_clause: str = Field(description="The exact legal text")
    plain_english: str = Field(description="Simple translation")
    what_it_means: str = Field(description="Practical explanation")
    freelancer_impact: str = Field(description="LOW/MEDIUM/HIGH risk level")
    real_world_example: str = Field(description="Concrete scenario")
    good_version: GoodVersion = Field(description="Better alternative")
    key_points: List[str] = Field(description="Warning points and tips")
    confidence: str = Field(description="HIGH/MEDIUM/LOW confidence")
    disclaimer: str = Field(description="Limitations and notes")


class ExplanationAgent:
    """Agent that translates legal jargon into plain English for freelancers"""
    
    def __init__(self, memory_id: str = None, enable_memory: bool = True):
        """Initialize Explanation Agent with memory
        
        Args:
            memory_id: Optional memory ID for AgentCore MemoryClient
            enable_memory: Whether to enable memory hooks (default: True)
        """
        # Initialize BedrockModel with Claude 3.7 Sonnet
        self.model = BedrockModel(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        )
        
        # Initialize memory client if memory_id provided
        self.memory_client = None
        self.memory_id = memory_id
        self.enable_memory = enable_memory and memory_id is not None
        
        if self.enable_memory:
            try:
                self.memory_client = MemoryClient()
                print("✅ Memory client initialized")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize memory client: {str(e)}")
                self.enable_memory = False
        
        # Initialize Strands Agent without tools (pure LLM approach)
        # The agent will answer directly using Claude's training data
        self.agent = Agent(
            model=self.model,
            tools=[],  # No external tools - pure LLM responses
            system_prompt=EXPLANATION_SYSTEM_PROMPT
        )
        
        # Get hook registry from agent
        self.hook_registry = self.agent.hooks
        
        # Store active memory hooks by session
        self.active_hooks = {}
    
    def explain(
        self,
        clause_text: str,
        clause_type: str = None,
        contract_type: str = None,
        session_id: str = None
    ) -> dict:
        """Explain legal clause in plain English
        
        Args:
            clause_text: The legal clause to explain
            clause_type: Type of clause (e.g., "indemnification", "payment", "IP")
            contract_type: Type of contract (e.g., "MSA", "SOW", "NDA")
            session_id: Session ID for memory tracking
            
        Returns:
            Dictionary with structured explanation including:
            - original_clause
            - plain_english
            - what_it_means
            - freelancer_impact
            - real_world_example
            - good_version
            - key_points
        """
        # Build context for the prompt
        context_parts = []
        if clause_type:
            context_parts.append(f"Clause Type: {clause_type}")
        if contract_type:
            context_parts.append(f"Contract Type: {contract_type}")
        
        context = " | ".join(context_parts) if context_parts else "General contract clause"
        
        # Construct the user prompt
        user_prompt = f"""Please explain this legal clause to a freelancer:

Context: {context}

Legal Clause:
"{clause_text}"

Please provide a complete explanation following the JSON output format specified in your system prompt. Make sure to:
1. Translate to simple 8th-grade language
2. Give a real-world scenario  
3. Show a better version if the clause is unfair
4. List key warning points
5. Include confidence level and any relevant disclaimers

Use your training knowledge of contract law, labor laws, and freelance regulations to provide accurate guidance.
Remember to note any limitations in your knowledge or jurisdictional considerations.

Return your response as valid JSON."""
        
        # If memory is enabled, set up memory hooks for this session
        memory_hooks = None
        if self.enable_memory and session_id:
            # Create or get existing hooks for this session
            if session_id not in self.active_hooks:
                memory_hooks = ExplanationMemoryHooks(
                    memory_client=self.memory_client,
                    memory_id=self.memory_id,
                    session_id=session_id
                )
                # Register hooks
                memory_hooks.register_hooks(self.hook_registry)
                self.active_hooks[session_id] = memory_hooks
                print(f"🔗 Memory hooks registered for session: {session_id}")
            else:
                memory_hooks = self.active_hooks[session_id]
                print(f"♻️  Reusing memory hooks for session: {session_id}")
        
        # Get explanation from agent using structured output
        try:
            # Use structured_output to get JSON response
            response = self.agent.structured_output(
                output_model=ExplanationResponse,
                prompt=user_prompt
            )
            
            # Convert Pydantic model to dict
            result = response.model_dump()
            
            # Store in memory if enabled (handled by hooks)
            if memory_hooks:
                try:
                    # Store the conversation turn
                    memory_hooks.memory_client.store_turn(
                        memory_id=self.memory_id,
                        actor_id=memory_hooks.actor_id,
                        session_id=session_id,
                        namespace=memory_hooks.namespace,
                        turn_data={
                            'user': user_prompt,
                            'assistant': json.dumps(result) if isinstance(result, dict) else str(result),
                            'clause_type': clause_type,
                            'contract_type': contract_type,
                            'impact': result.get('freelancer_impact', 'UNKNOWN')
                        }
                    )
                    print(f"💾 Explanation saved to memory")
                except Exception as e:
                    print(f"⚠️  Could not save to memory: {str(e)}")
            
            return result
            
        except Exception as e:
            print(f"Error explaining clause: {str(e)}")
            return {
                "original_clause": clause_text,
                "plain_english": f"Error processing clause: {str(e)}",
                "what_it_means": "An error occurred during explanation",
                "freelancer_impact": "UNKNOWN",
                "real_world_example": "Unable to provide example due to error",
                "good_version": {
                    "text": "Not available",
                    "source": "N/A",
                    "why_better": "N/A"
                },
                "key_points": ["Error occurred", "Please try again"]
            }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of explanations in a session
        
        Args:
            session_id: Session ID to get summary for
            
        Returns:
            Dictionary with session statistics
        """
        if session_id in self.active_hooks:
            return self.active_hooks[session_id].get_session_summary()
        else:
            return {
                'error': 'No active session found',
                'session_id': session_id
            }
    
    def clear_session_memory(self, session_id: str):
        """Clear memory for a specific session
        
        Args:
            session_id: Session ID to clear
        """
        if session_id in self.active_hooks:
            self.active_hooks[session_id].clear_session_memory()
            del self.active_hooks[session_id]
            print(f"🗑️  Session {session_id} cleared")
        else:
            print(f"⚠️  No active session found: {session_id}")
    
    def list_active_sessions(self) -> list:
        """List all active sessions with memory hooks
        
        Returns:
            List of session IDs
        """
        return list(self.active_hooks.keys())
    
    def get_conversation_history(self, session_id: str, k: int = 10) -> list:
        """Get conversation history for a session
        
        Args:
            session_id: Session ID to get history for
            k: Number of recent turns to retrieve (default: 10)
            
        Returns:
            List of conversation turns
        """
        if not self.enable_memory:
            return []
        
        try:
            return self.memory_client.get_last_k_turns(
                memory_id=self.memory_id,
                actor_id="freelancer",
                session_id=session_id,
                k=k
            )
        except Exception as e:
            print(f"⚠️  Could not retrieve history: {str(e)}")
            return []