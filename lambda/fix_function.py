with open('orchestrator_lambda.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_until_next_def = False

for line in lines:
    if 'def call_bedrock_agent_a2a(' in line:
        skip_until_next_def = True
        new_func = '''def call_bedrock_agent_a2a(
    agent_arn: str,
    message: str,
    session_id: str
) -> str:
    try:
        logger.info(f"Invoking REAL AgentCore agent: {agent_arn}")
        logger.info(f"Session: {session_id}")
        logger.info(f"Message: {message[:100]}")
        
        response = bedrock_agentcore.invoke_agent(
            agentArn=agent_arn,
            sessionId=session_id,
            inputText=message
        )
        
        logger.info("Got response from AgentCore")
        
        agent_response = ""
        if 'completion' in response:
            event_stream = response['completion']
            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        agent_response += chunk['bytes'].decode('utf-8')
                elif 'text' in event:
                    agent_response += event['text']
        
        if not agent_response and 'output' in response:
            agent_response = response['output']
        elif not agent_response and 'text' in response:
            agent_response = response['text']
        
        if not agent_response:
            logger.warning("Empty response from agent")
            return "I received your message but I'm having trouble formulating a response. Please try again."
        
        logger.info(f"Agent response received ({len(agent_response)} chars)")
        return agent_response
    
    except Exception as e:
        logger.error(f"A2A call failed: {e}", exc_info=True)
        return f"I apologize, but I encountered an error processing your request. Error: {str(e)}"

'''
        new_lines.append(new_func)
        continue
    
    if skip_until_next_def:
        if line.startswith('def ') or line.startswith('# ==='):
            skip_until_next_def = False
        else:
            continue
    
    new_lines.append(line)

with open('orchestrator_lambda.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ Function replaced successfully')
