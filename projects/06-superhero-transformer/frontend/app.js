// Configuration
const API_URL = 'https://olbnqojqu6ps7n2phm2tkkvnoi0ytbpv.lambda-url.us-east-1.on.aws/';
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');
const originalImage = document.getElementById('originalImage');
const superheroImage = document.getElementById('superheroImage');
const downloadBtn = document.getElementById('downloadBtn');

// State
let currentFilename = null;
let originalImageUrl = null;

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
    const validTypes = ['image/png', 'image/jpeg'];
    if (!validTypes.includes(file.type)) {
        showStatus('error', 'Invalid file type. Please upload JPG or PNG files only.');
        return;
    }
    
    if (file.size > MAX_FILE_SIZE) {
        showStatus('error', `File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB.`);
        return;
    }
    
    // Create local preview URL
    originalImageUrl = URL.createObjectURL(file);
    
    uploadFile(file);
}

async function uploadFile(file) {
    try {
        showStatus('processing', `Uploading ${file.name}...`);
        
        const arrayBuffer = await file.arrayBuffer();
        
        const response = await fetch(
            `${API_URL}/upload?filename=${encodeURIComponent(file.name)}`,
            {
                method: 'POST',
                body: arrayBuffer,
                headers: {
                    'Content-Type': 'application/octet-stream'
                }
            }
        );
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const { filename } = await response.json();
        currentFilename = filename;
        
        showStatus('processing', 'Transforming into superhero... This may take 10-15 seconds.');
        
        pollForResults();
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus('error', `Upload failed: ${error.message}`);
    }
}

async function pollForResults() {
    let attempts = 0;
    const maxAttempts = 60; // 60 seconds max for image generation
    
    const poll = async () => {
        try {
            const response = await fetch(`${API_URL}/result?filename=${encodeURIComponent(currentFilename)}`);
            
            if (response.status === 200) {
                const result = await response.json();
                displayResults(result);
                showStatus('success', 'Superhero transformation complete!');
                setTimeout(() => hideStatus(), 3000);
            } else if (response.status === 202) {
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, 1000);
                } else {
                    showStatus('error', 'Processing timeout. Please try again.');
                }
            } else if (response.status === 500) {
                const error = await response.json();
                showStatus('error', `Processing error: ${error.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Poll error:', error);
            showStatus('error', 'Failed to retrieve results. Please try again.');
        }
    };
    
    poll();
}

function displayResults(result) {
    resultsSection.style.display = 'flex';
    
    originalImage.src = originalImageUrl;
    superheroImage.src = result.superhero_url;
    
    downloadBtn.href = result.superhero_url;
    downloadBtn.download = result.superhero_image;
    
    resultsSection.scrollIntoView({ behavior: 'smooth' });
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
    originalImageUrl = null;
    hideStatus();
}
