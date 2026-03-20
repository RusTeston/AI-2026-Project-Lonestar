// API Gateway endpoint - UPDATE THIS AFTER DEPLOYMENT
const API_ENDPOINT = 'https://ri802yjmt0.execute-api.us-east-1.amazonaws.com/prod/chat';

// Send message to the chatbot
async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Disable input while processing
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    userInput.disabled = true;
    
    // Display user message
    addMessage(message, 'user');
    userInput.value = '';
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    try {
        // Call API Gateway
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        // Display bot response
        addMessage(data.response, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        // Re-enable input
        sendButton.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

// Add message to chat
function addMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (sender === 'bot') {
        contentDiv.innerHTML = `<strong>Cloud Advisor:</strong> ${formatMessage(text)}`;
    } else {
        contentDiv.textContent = text;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format bot message with basic markdown-like formatting
function formatMessage(text) {
    // Convert #### Heading to <h4>
    text = text.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
    
    // Convert ### Heading to <h3>
    text = text.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    
    // Convert ## Heading to <h3>
    text = text.replace(/^## (.*?)$/gm, '<h3>$1</h3>');
    
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');
    
    // Convert bullet points
    text = text.replace(/^- (.*?)$/gm, '• $1');
    
    return text;
}

// Add loading indicator
function addLoadingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'loading-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<strong>Cloud Advisor:</strong> Thinking<span class="loading"></span><span class="loading"></span><span class="loading"></span>';
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return 'loading-message';
}

// Remove loading indicator
function removeLoadingMessage(id) {
    const loadingMessage = document.getElementById(id);
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Allow Enter key to send message (Shift+Enter for new line)
document.getElementById('userInput').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

// Test mode - for local testing without API
const TEST_MODE = false;

if (TEST_MODE) {
    console.log('Running in TEST MODE - using mock responses');
    
    // Override sendMessage for testing
    window.sendMessage = async function() {
        const userInput = document.getElementById('userInput');
        const message = userInput.value.trim();
        
        if (!message) return;
        
        addMessage(message, 'user');
        userInput.value = '';
        
        const loadingId = addLoadingMessage();
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        removeLoadingMessage(loadingId);
        
        // Mock response
        const mockResponse = `Based on your requirements, I recommend the following AWS architecture:

**Recommended Services:**
- **Amazon EC2**: For compute resources
- **Amazon RDS**: For managed database
- **Amazon S3**: For static asset storage
- **Amazon CloudFront**: For content delivery

**Reasoning:**
This architecture provides scalability, reliability, and cost-effectiveness for your use case.

**Tradeoffs:**
- Higher initial setup complexity
- Managed services reduce operational overhead`;
        
        addMessage(mockResponse, 'bot');
    };
}


// Clear chat function
function clearChat() {
    const chatMessages = document.getElementById('chatMessages');
    
    // Clear all messages
    chatMessages.innerHTML = '';
    
    // Add back the welcome message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<strong>Cloud Advisor:</strong> Hello! I\'m your AWS Cloud Architecture Advisor. Describe your application or use case, and I\'ll recommend an appropriate AWS architecture with detailed reasoning.';
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Clear input
    document.getElementById('userInput').value = '';
    document.getElementById('userInput').focus();
}
