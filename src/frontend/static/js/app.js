// Freelancer Legal Assistant - Frontend Logic
// Handles UI interactions, agent orchestration, and A2A communication

// ============================================================================
// CONFIGURATION
// ============================================================================

// API Gateway URL - updated during deployment
const API_BASE_URL = 'https://inr0anapu2.execute-api.us-east-1.amazonaws.com';

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
    sessionId: generateSessionId(),
    currentAgent: 'orchestrator',
    uploadedFile: null,
    contractText: null,
    conversationHistory: [],
    isProcessing: false
};

// Agent configurations
const AGENTS = {
    orchestrator: {
        name: 'Orchestrator Agent',
        emoji: '🤖',
        color: 'orchestrator',
        description: 'Central coordinator'
    },
    analysis: {
        name: 'Analysis Agent',
        emoji: '📊',
        color: 'analysis',
        description: 'Contract analysis specialist'
    },
    explanation: {
        name: 'Explanation Agent',
        emoji: '📖',
        color: 'explanation',
        description: 'Legal terms expert'
    },
    negotiation: {
        name: 'Negotiation Agent',
        emoji: '💼',
        color: 'negotiation',
        description: 'Negotiation strategist'
    },
    action: {
        name: 'Action Agent',
        emoji: '⚖️',
        color: 'action',
        description: 'Dispute resolution specialist'
    }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
    setupDragAndDrop();
    setupAutoResize();
    console.log('🚀 Freelancer Legal Assistant initialized');
    console.log('Session ID:', state.sessionId);
});

function generateSessionId() {
    // Generate UUID-like session ID (minimum 33 chars for AgentCore)
    return 'session-' + Date.now() + '-' + 
           Math.random().toString(36).substr(2, 15) + 
           Math.random().toString(36).substr(2, 15);
}

// ============================================================================
// FILE UPLOAD HANDLING
// ============================================================================

function setupFileUpload() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', handleFileSelect);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    state.uploadedFile = file;
    
    // Show file info
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.classList.add('show');
    
    // Show continue button
    document.getElementById('continueBtn').style.display = 'block';
    document.getElementById('continueBtn').onclick = () => startChatWithFile(file);
    
    console.log('📄 File selected:', file.name);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================================================
// DRAG AND DROP
// ============================================================================

function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('drag-over');
        }, false);
    });
    
    uploadArea.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const file = files[0];
        document.getElementById('fileInput').files = files;
        handleFileSelect({ target: { files: [file] } });
    }
}

// ============================================================================
// CHAT INTERFACE
// ============================================================================

function startChat() {
    // Hide landing page, show chat
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('chatContainer').classList.add('active');
    
    // Send initial greeting ONLY if no file was uploaded
    if (!state.uploadedFile) {
        addAgentMessage(
            'orchestrator',
            `👋 Hello! I'm your Freelancer Legal Assistant. I coordinate a team of AI specialists to help you with contract-related issues.

I can help you with:
📊 **Contract Analysis** - Review contracts before signing
📖 **Legal Explanations** - Understand contract terms in plain English
💼 **Negotiations** - Strategy and counteroffers
⚖️ **Legal Action** - Resolve disputes after signing

What brings you here today? Feel free to describe your situation, or click one of the quick actions below!`
        );
    }
}

function startChatWithFile(file) {
    // Hide landing page, show chat
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('chatContainer').classList.add('active');
    
    // Send file-specific greeting
    addAgentMessage(
        'orchestrator',
        `📄 Great! I see you've uploaded **${file.name}**. 

I'll help you analyze this contract. Let me ask you a few questions first:

1. **What type of contract is this?** (e.g., freelance service agreement, NDA, work-for-hire)
2. **Have you already signed it**, or are you reviewing it before signing?
3. **What specific concerns do you have**, if any?

Feel free to answer in your own words!`
    );
    
    // In real implementation, you'd upload the file to backend
    // For now, we'll simulate extracting text
    extractFileText(file);
}

function extractFileText(file) {
    // TODO: In production, send file to backend for text extraction
    // For now, simulate extraction
    const reader = new FileReader();
    reader.onload = (e) => {
        state.contractText = e.target.result;
        console.log('📝 Contract text extracted (simulated)');
    };
    
    if (file.type === 'text/plain') {
        reader.readAsText(file);
    } else {
        // For PDFs/Word docs, you'd use backend processing
        console.log('📄 File uploaded, awaiting backend processing');
    }
}

function resetChat() {
    if (confirm('Start a new chat? Current conversation will be lost.')) {
        state.sessionId = generateSessionId();
        state.conversationHistory = [];
        state.currentAgent = 'orchestrator';
        state.uploadedFile = null;
        state.contractText = null;
        
        document.getElementById('chatMessages').innerHTML = '';
        document.getElementById('landingPage').style.display = 'flex';
        document.getElementById('chatContainer').classList.remove('active');
        
        console.log('🔄 Chat reset, new session:', state.sessionId);
    }
}

// ============================================================================
// MESSAGE HANDLING
// ============================================================================

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message || state.isProcessing) return;
    
    // Add user message to UI
    addUserMessage(message);
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    
    // Process message
    processUserMessage(message);
}

function sendQuickMessage(message) {
    document.getElementById('chatInput').value = message;
    sendMessage();
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function addUserMessage(text) {
    const messagesContainer = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="message-agent-name">You</div>
                <div class="message-text">${escapeHtml(text)}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    // Add to history
    state.conversationHistory.push({
        role: 'user',
        content: text,
        timestamp: new Date().toISOString()
    });
}

function addAgentMessage(agentType, text, showTyping = true) {
    const agent = AGENTS[agentType];
    const messagesContainer = document.getElementById('chatMessages');
    
    // Update header to show current agent
    updateAgentHeader(agentType);
    
    // Show agent switch notification if different from orchestrator
    if (agentType !== 'orchestrator' && state.currentAgent !== agentType) {
        showAgentSwitchNotification(agentType);
    }
    
    state.currentAgent = agentType;
    
    // Show typing indicator
    if (showTyping) {
        showTypingIndicator();
        
        // Simulate typing delay
        setTimeout(() => {
            hideTypingIndicator();
            addMessageToDOM();
        }, 1500 + Math.random() * 1000);
    } else {
        addMessageToDOM();
    }
    
    function addMessageToDOM() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message agent';
        messageDiv.innerHTML = `
            <div class="message-avatar" style="background: linear-gradient(135deg, ${getAgentGradient(agentType)})">${agent.emoji}</div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="message-agent-name">${agent.name}</div>
                    <div class="message-text">${formatMessageText(text)}</div>
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
        
        // Add to history
        state.conversationHistory.push({
            role: 'agent',
            agent: agentType,
            content: text,
            timestamp: new Date().toISOString()
        });
    }
}

function showAgentSwitchNotification(agentType) {
    const agent = AGENTS[agentType];
    const messagesContainer = document.getElementById('chatMessages');
    
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'message';
    notificationDiv.innerHTML = `
        <div class="agent-switch-notification" style="background: linear-gradient(135deg, ${getAgentGradient(agentType)})">
            <span class="notification-icon">🔄</span>
            <div>
                <strong>Switching to ${agent.name}</strong>
                <div style="font-size: 0.875rem; opacity: 0.9;">${agent.description}</div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(notificationDiv);
    scrollToBottom();
}

function updateAgentHeader(agentType) {
    const agent = AGENTS[agentType];
    document.getElementById('agentName').textContent = agent.name;
    document.getElementById('agentAvatar').textContent = agent.emoji;
    document.getElementById('agentAvatar').className = `agent-avatar ${agentType}`;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message agent';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar" style="background: linear-gradient(135deg, ${getAgentGradient(state.currentAgent)})">${AGENTS[state.currentAgent].emoji}</div>
        <div class="message-content">
            <div class="typing-indicator show">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// ============================================================================
// ORCHESTRATOR LOGIC (INTENT CLASSIFICATION & ROUTING)
// ============================================================================

async function processUserMessage(message) {
    state.isProcessing = true;
    document.getElementById('sendBtn').disabled = true;
    
    try {
        // Classify intent
        const intent = classifyIntent(message);
        console.log('🧠 Intent detected:', intent);
        
        // Route to appropriate agent
        const response = await routeToAgent(intent, message);
        
        // Add agent response
        addAgentMessage(intent.agent, response);
        
    } catch (error) {
        console.error('❌ Error processing message:', error);
        addAgentMessage('orchestrator', 'I apologize, but I encountered an error processing your request. Please try again.');
    } finally {
        state.isProcessing = false;
        document.getElementById('sendBtn').disabled = false;
    }
}

function classifyIntent(message) {
    const lowerMessage = message.toLowerCase();
    
    // Analysis intent patterns
    if (lowerMessage.match(/analyz|review|check|before sign|should i sign|look at.*contract|examine/)) {
        return {
            agent: 'analysis',
            confidence: 0.9,
            keywords: ['analyze', 'review', 'contract']
        };
    }
    
    // Explanation intent patterns
    if (lowerMessage.match(/what does.*mean|explain|don't understand|clarify|simplify|what is|define|interpretation/)) {
        return {
            agent: 'explanation',
            confidence: 0.9,
            keywords: ['explain', 'meaning']
        };
    }
    
    // Negotiation intent patterns
    if (lowerMessage.match(/negotiat|counteroffer|change terms|modify|disagree|want different|bargain|proposal|amend/)) {
        return {
            agent: 'negotiation',
            confidence: 0.9,
            keywords: ['negotiate', 'change']
        };
    }
    
    // Action intent patterns
    if (lowerMessage.match(/won't pay|didn't pay|breach|violat|dispute|legal action|sue|court|lawyer|after sign|client problem|broken contract/)) {
        return {
            agent: 'action',
            confidence: 0.9,
            keywords: ['dispute', 'legal action']
        };
    }
    
    // Default to action agent for general queries (let Action Agent handle it)
    return {
        agent: 'action',
        confidence: 0.7,
        keywords: ['general']
    };
}

async function routeToAgent(intent, message) {
    const agentType = intent.agent;
    
    // Build context from conversation history
    const context = buildContext();
    
    // Call appropriate agent (real or dummy)
    if (agentType === 'action') {
        // Real Action Agent (already deployed)
        return await callRealActionAgent(message, context);
    } else {
        // Dummy agents for testing (until teammates finish)
        return await callDummyAgent(agentType, message, context);
    }
}

function buildContext() {
    // Get last 5 messages for context
    const recentHistory = state.conversationHistory.slice(-5);
    
    let context = '';
    if (state.contractText) {
        context += `[Contract uploaded: ${state.uploadedFile?.name}]\n\n`;
    }
    
    recentHistory.forEach(msg => {
        if (msg.role === 'user') {
            context += `User: ${msg.content}\n`;
        } else {
            context += `${AGENTS[msg.agent].name}: ${msg.content}\n`;
        }
    });
    
    return context;
}

// ============================================================================
// AGENT API CALLS
// ============================================================================

async function callRealActionAgent(message, context) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: message,
                context: context,
                sessionId: state.sessionId,
                agent: 'action'
            })
        });
        
        const data = await response.json();
        return data.response;
        
    } catch (error) {
        console.error('❌ Error calling Action Agent:', error);
        throw error;
    }
}

async function callDummyAgent(agentType, message, context) {
    // Simulate API delay
    await sleep(1000 + Math.random() * 1500);
    
    // Return dummy responses based on agent type
    const dummyResponses = {
        orchestrator: getDummyOrchestratorResponse(message),
        analysis: getDummyAnalysisResponse(message),
        explanation: getDummyExplanationResponse(message),
        negotiation: getDummyNegotiationResponse(message)
    };
    
    return dummyResponses[agentType] || 'I\'m still learning! This agent is under development.';
}

// ============================================================================
// DUMMY AGENT RESPONSES (For Testing)
// ============================================================================

function getDummyOrchestratorResponse(message) {
    const responses = [
        `I understand you need assistance. Let me route you to the appropriate specialist who can best help with your situation.`,
        
        `Thank you for providing that information. Based on what you've told me, I'll connect you with the right expert from our team.`,
        
        `I'm analyzing your request to determine which of our specialists can provide the most relevant guidance. One moment...`,
        
        `Got it! Let me coordinate with our team to give you comprehensive assistance.`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

function getDummyAnalysisResponse(message) {
    return `📊 **Contract Analysis Specialist here!**

I'd be happy to review your contract. Based on your message, here's what I'll analyze:

🔍 **Key Areas I'll Examine:**
- Payment terms and conditions
- Intellectual property rights
- Liability and indemnification clauses
- Termination conditions
- Scope of work definition

📋 **To provide the best analysis, I need:**
1. The full contract document (if not already uploaded)
2. Your specific concerns or questions
3. Your role (client or freelancer)
4. Project type and value

Could you provide more details about the contract you'd like me to review?

*Note: This is a dummy response. The real Analysis Agent is being built by Dev 1.*`;
}

function getDummyExplanationResponse(message) {
    return `📖 **Legal Terms Expert here!**

Great question! Let me break down those legal terms in plain English.

🎯 **Simple Explanation:**
I can help clarify confusing legal jargon and explain what contract clauses actually mean for you.

💡 **For example, if you asked about:**
- **"Indemnification"** = You agree to protect the other party from lawsuits
- **"Force Majeure"** = Neither party is liable if something uncontrollable happens (like natural disasters)
- **"Liquidated Damages"** = Pre-agreed compensation if contract is broken

📝 **What would you like me to explain?**
Feel free to paste the specific clause or term you're confused about!

*Note: This is a dummy response. The real Explanation Agent is being built by Dev 2.*`;
}

function getDummyNegotiationResponse(message) {
    return `💼 **Negotiation Strategist here!**

I'm here to help you negotiate better terms! Let's work on this together.

🎯 **My Approach:**
1. Identify which terms you want to change
2. Understand your leverage and priorities
3. Craft a professional counteroffer
4. Draft negotiation emails

💪 **Common Negotiation Points:**
- Payment terms (deposits, milestones, net days)
- Intellectual property ownership
- Revisions and scope
- Liability caps
- Non-compete restrictions

📧 **I can help you draft:**
- Counteroffer proposals
- Negotiation emails
- Amendment requests

What specific terms do you want to negotiate?

*Note: This is a dummy response. The real Negotiation Agent is being built by Dev 3.*`;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function setupAutoResize() {
    const textarea = document.getElementById('chatInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
    });
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessageText(text) {
    // Convert markdown-like formatting
    text = escapeHtml(text);
    
    // Bold: **text**
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Lists: - item
    text = text.replace(/^- (.+)$/gm, '• $1');
    
    // Preserve line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

function getAgentGradient(agentType) {
    const gradients = {
        orchestrator: '#667eea 0%, #764ba2 100%',
        analysis: '#f093fb 0%, #f5576c 100%',
        explanation: '#4facfe 0%, #00f2fe 100%',
        negotiation: '#43e97b 0%, #38f9d7 100%',
        action: '#fa709a 0%, #fee140 100%'
    };
    return gradients[agentType] || gradients.orchestrator;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================================
// DEBUG HELPERS
// ============================================================================

window.debugState = () => {
    console.log('=== Current State ===');
    console.log('Session ID:', state.sessionId);
    console.log('Current Agent:', state.currentAgent);
    console.log('Uploaded File:', state.uploadedFile?.name || 'None');
    console.log('Conversation History:', state.conversationHistory.length, 'messages');
    console.log('Is Processing:', state.isProcessing);
};

window.testAllAgents = () => {
    console.log('🧪 Testing all agent responses...');
    
    setTimeout(() => addAgentMessage('orchestrator', 'Orchestrator test message'), 500);
    setTimeout(() => addAgentMessage('analysis', 'Analysis agent test message'), 1500);
    setTimeout(() => addAgentMessage('explanation', 'Explanation agent test message'), 2500);
    setTimeout(() => addAgentMessage('negotiation', 'Negotiation agent test message'), 3500);
    setTimeout(() => addAgentMessage('action', 'Action agent test message'), 4500);
};

console.log('💡 Debug commands available:');
console.log('- debugState() - View current application state');
console.log('- testAllAgents() - Test all agent UI components');

