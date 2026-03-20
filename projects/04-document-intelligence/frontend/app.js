// Configuration - will be updated by deployment script
const API_URL = 'https://o73axp5a7fzg2nti6rhavce3qa0rxlcj.lambda-url.us-east-1.on.aws/';
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');

// State
let currentFilename = null;

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg'];
    if (!validTypes.includes(file.type)) {
        showStatus('error', 'Invalid file type. Please upload PDF, PNG, or JPEG files only.');
        return;
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showStatus('error', `File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB.`);
        return;
    }
    
    uploadFile(file);
}

async function uploadFile(file) {
    try {
        showStatus('processing', `Uploading ${file.name}...`);
        
        // Read file as ArrayBuffer
        const arrayBuffer = await file.arrayBuffer();
        
        // Upload directly to Lambda
        const response = await fetch(`${API_URL}/upload?filename=${encodeURIComponent(file.name)}`, {
            method: 'POST',
            body: arrayBuffer,
            headers: {
                'Content-Type': 'application/octet-stream'
            }
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const { filename } = await response.json();
        currentFilename = filename;
        
        showStatus('processing', 'Processing document... This may take a few seconds.');
        
        // Poll for results
        pollForResults();
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus('error', `Upload failed: ${error.message}`);
    }
}

async function pollForResults() {
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds max
    
    const poll = async () => {
        try {
            const response = await fetch(`${API_URL}/result?filename=${encodeURIComponent(currentFilename)}`);
            
            if (response.status === 200) {
                // Success - got results
                const result = await response.json();
                displayResults(result);
                showStatus('success', 'Document processed successfully!');
                setTimeout(() => hideStatus(), 3000);
            } else if (response.status === 202) {
                // Still processing
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, 1000);
                } else {
                    showStatus('error', 'Processing timeout. Please try again.');
                }
            } else if (response.status === 500) {
                // Error occurred
                const error = await response.json();
                const errorMsg = error.error || 'Unknown error';
                showStatus('error', errorMsg);
                
                // Show error in results section too
                resultsSection.style.display = 'flex';
                document.getElementById('documentType').textContent = 'Error';
                document.getElementById('summary').textContent = errorMsg;
                document.getElementById('keyFieldsCard').style.display = 'none';
                document.getElementById('extractedText').textContent = 'Processing failed';
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            console.error('Poll error:', error);
            showStatus('error', 'Failed to retrieve results. Please try again.');
        }
    };
    
    poll();
}

function displayResults(result) {
    // Show results section
    resultsSection.style.display = 'flex';
    
    // Document type
    document.getElementById('documentType').textContent = result.document_type || 'Unknown';
    
    // Summary
    document.getElementById('summary').textContent = result.summary || 'No summary available';
    
    // Key fields
    const keyFields = result.key_fields || {};
    const keyFieldsCard = document.getElementById('keyFieldsCard');
    const keyFieldsContainer = document.getElementById('keyFields');
    
    if (Object.keys(keyFields).length > 0) {
        keyFieldsCard.style.display = 'block';
        keyFieldsContainer.innerHTML = Object.entries(keyFields)
            .map(([key, value]) => `
                <div class="field-item">
                    <div class="field-name">${formatFieldName(key)}</div>
                    <div class="field-value">${escapeHtml(String(value))}</div>
                </div>
            `).join('');
    } else {
        keyFieldsCard.style.display = 'none';
    }
    
    // Extracted text
    document.getElementById('extractedText').textContent = result.extracted_text || 'No text extracted';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function formatFieldName(name) {
    return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showStatus(type, message) {
    statusMessage.className = `status-message show ${type}`;
    statusMessage.textContent = message;
}

function hideStatus() {
    statusMessage.className = 'status-message';
}

function clearResults() {
    resultsSection.style.display = 'none';
    fileInput.value = '';
    currentFilename = null;
    hideStatus();
}
