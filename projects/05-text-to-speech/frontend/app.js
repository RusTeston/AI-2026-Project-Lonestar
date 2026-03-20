// Configuration
const API_URL = 'https://re7denuxpksnsoet2qbklz7np40bbfhn.lambda-url.us-east-1.on.aws/';
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const voiceEngine = document.getElementById('voiceEngine');
const voiceId = document.getElementById('voiceId');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');
const audioPlayer = document.getElementById('audioPlayer');
const audioSource = document.getElementById('audioSource');
const downloadBtn = document.getElementById('downloadBtn');

// State
let currentFilename = null;

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
voiceEngine.addEventListener('change', updateVoiceOptions);

// Initialize
updateVoiceOptions();

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
    const validTypes = ['text/plain', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
        showStatus('error', 'Invalid file type. Please upload TXT or PDF files only.');
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
        
        // Get voice settings
        const engine = voiceEngine.value;
        const voice = voiceId.value;
        
        // Upload to Lambda
        const response = await fetch(
            `${API_URL}/upload?filename=${encodeURIComponent(file.name)}&voiceEngine=${engine}&voiceId=${voice}`,
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
        
        showStatus('processing', 'Converting to speech... This may take a few seconds.');
        
        // Poll for results
        pollForResults();
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus('error', `Upload failed: ${error.message}`);
    }
}

async function pollForResults() {
    let attempts = 0;
    const maxAttempts = 30;
    
    const poll = async () => {
        try {
            const response = await fetch(`${API_URL}/result?filename=${encodeURIComponent(currentFilename)}`);
            
            if (response.status === 200) {
                // Success
                const result = await response.json();
                displayResults(result);
                showStatus('success', 'Audio generated successfully!');
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
                // Error
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
    // Show results section
    resultsSection.style.display = 'flex';
    
    // Set audio source
    audioSource.src = result.audio_url;
    audioPlayer.load();
    
    // Set download link
    downloadBtn.href = result.audio_url;
    downloadBtn.download = result.audio_file;
    
    // Display info
    document.getElementById('voiceInfo').textContent = 
        `${result.voice_id} (${result.voice_engine === 'neural' ? 'Neural' : 'Standard'})`;
    document.getElementById('textLength').textContent = 
        `${result.text_length} characters`;
    
    // Show truncation warning if needed
    if (result.truncated) {
        document.getElementById('truncatedWarning').style.display = 'block';
    } else {
        document.getElementById('truncatedWarning').style.display = 'none';
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function updateVoiceOptions() {
    const engine = voiceEngine.value;
    const currentVoice = voiceId.value;
    
    // Clear options
    voiceId.innerHTML = '';
    
    // Add options based on engine
    if (engine === 'neural') {
        const voices = [
            { id: 'Joanna', name: 'Joanna (Female, US)' },
            { id: 'Matthew', name: 'Matthew (Male, US)' },
            { id: 'Ruth', name: 'Ruth (Female, US)' },
            { id: 'Stephen', name: 'Stephen (Male, US)' }
        ];
        
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            if (voice.id === currentVoice) {
                option.selected = true;
            }
            voiceId.appendChild(option);
        });
    } else {
        const voices = [
            { id: 'Joanna', name: 'Joanna (Female, US)' },
            { id: 'Matthew', name: 'Matthew (Male, US)' },
            { id: 'Ivy', name: 'Ivy (Female, US)' },
            { id: 'Joey', name: 'Joey (Male, US)' }
        ];
        
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            if (voice.id === currentVoice) {
                option.selected = true;
            }
            voiceId.appendChild(option);
        });
    }
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
    audioPlayer.pause();
    audioSource.src = '';
    hideStatus();
}
