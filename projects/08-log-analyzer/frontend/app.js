const API_URL = 'https://gjktxu3tgjrvniffzqon2uqhvm0budfq.lambda-url.us-east-1.on.aws';
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const statusMessage = document.getElementById('statusMessage');
const resultsSection = document.getElementById('resultsSection');

let currentFilename = null;

uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => { if (e.target.files.length) handleFile(e.target.files[0]); });
uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('drag-over'); });
uploadArea.addEventListener('dragleave', e => { e.preventDefault(); uploadArea.classList.remove('drag-over'); });
uploadArea.addEventListener('drop', e => { e.preventDefault(); uploadArea.classList.remove('drag-over'); if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });

function handleFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['log', 'txt', 'csv', 'json'].includes(ext)) {
        showStatus('error', 'Invalid file type. Please upload LOG, TXT, CSV, or JSON files.');
        return;
    }
    if (file.size > MAX_FILE_SIZE) {
        showStatus('error', 'File too large. Maximum size is 5MB.');
        return;
    }
    uploadFile(file);
}

async function uploadFile(file) {
    try {
        showStatus('processing', `Uploading ${file.name}...`);
        const arrayBuffer = await file.arrayBuffer();

        const response = await fetch(`${API_URL}/upload?filename=${encodeURIComponent(file.name)}`, {
            method: 'POST',
            body: arrayBuffer,
            headers: { 'Content-Type': 'application/octet-stream' }
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Upload failed');
        }

        const { filename } = await response.json();
        currentFilename = filename;
        showStatus('processing', 'Analyzing log file... This may take 10-15 seconds.');
        pollForResults();
    } catch (error) {
        showStatus('error', `Upload failed: ${error.message}`);
    }
}

async function pollForResults() {
    let attempts = 0;
    const maxAttempts = 45;

    const poll = async () => {
        try {
            const response = await fetch(`${API_URL}/result?filename=${encodeURIComponent(currentFilename)}`);

            if (response.status === 200) {
                const result = await response.json();
                displayResults(result);
                showStatus('success', 'Analysis complete!');
                setTimeout(hideStatus, 3000);
            } else if (response.status === 202) {
                attempts++;
                if (attempts < maxAttempts) setTimeout(poll, 1000);
                else showStatus('error', 'Analysis timeout. Please try again.');
            } else if (response.status === 500) {
                const error = await response.json();
                showStatus('error', error.error || 'Analysis failed.');
            }
        } catch (error) {
            showStatus('error', 'Failed to retrieve results.');
        }
    };
    poll();
}

function displayResults(result) {
    const a = result.analysis || {};
    resultsSection.style.display = 'flex';

    // Log type & severity
    document.getElementById('logType').textContent = a.log_type || 'Unknown';
    const severityEl = document.getElementById('severity');
    const sev = (a.severity || 'UNKNOWN').toUpperCase();
    severityEl.textContent = sev;
    severityEl.className = `severity-badge severity-${sev}`;

    // Summary
    document.getElementById('summary').textContent = a.summary || 'No summary available';

    // Timeline
    const timelineCard = document.getElementById('timelineCard');
    if (a.timeline) {
        timelineCard.style.display = 'block';
        document.getElementById('timeline').textContent = a.timeline;
    } else {
        timelineCard.style.display = 'none';
    }

    // Errors
    renderErrors(a.errors || []);

    // Warnings
    renderWarnings(a.warnings || []);

    // Patterns
    renderPatterns(a.patterns || []);

    // Recommended Actions
    renderActions(a.recommended_actions || []);

    // Prevention Tips
    renderPrevention(a.prevention_tips || []);

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function renderErrors(errors) {
    const card = document.getElementById('errorsCard');
    const list = document.getElementById('errorsList');
    if (!errors.length) { card.style.display = 'none'; return; }

    card.style.display = 'block';
    document.getElementById('errorCount').textContent = errors.length;
    list.innerHTML = errors.map(e => `
        <div class="item-entry error-entry">
            <div class="item-title">${esc(e.error)}</div>
            <div class="item-meta">Severity: ${esc(e.severity)} | Count: ${esc(e.count)} | ${esc(e.line_reference)}</div>
            <div class="item-detail"><strong>Root Cause:</strong> ${esc(e.root_cause)}</div>
            <div class="item-detail"><strong>Fix:</strong> ${esc(e.fix)}</div>
        </div>
    `).join('');
}

function renderWarnings(warnings) {
    const card = document.getElementById('warningsCard');
    const list = document.getElementById('warningsList');
    if (!warnings.length) { card.style.display = 'none'; return; }

    card.style.display = 'block';
    document.getElementById('warningCount').textContent = warnings.length;
    list.innerHTML = warnings.map(w => `
        <div class="item-entry warning-entry">
            <div class="item-title">${esc(w.warning)}</div>
            <div class="item-meta">Count: ${esc(w.count)}</div>
            <div class="item-detail"><strong>Impact:</strong> ${esc(w.impact)}</div>
        </div>
    `).join('');
}

function renderPatterns(patterns) {
    const card = document.getElementById('patternsCard');
    const list = document.getElementById('patternsList');
    if (!patterns.length) { card.style.display = 'none'; return; }

    card.style.display = 'block';
    list.innerHTML = patterns.map(p => `
        <div class="item-entry pattern-entry">
            <div class="item-title">${esc(p.pattern)}</div>
            <div class="item-meta">Frequency: ${esc(p.frequency)}</div>
            <div class="item-detail"><strong>Significance:</strong> ${esc(p.significance)}</div>
        </div>
    `).join('');
}

function renderActions(actions) {
    const card = document.getElementById('actionsCard');
    const list = document.getElementById('actionsList');
    if (!actions.length) { card.style.display = 'none'; return; }

    card.style.display = 'block';
    list.innerHTML = actions.map(a => `
        <div class="item-entry action-entry">
            <div class="item-title">Priority ${esc(a.priority)}: ${esc(a.action)}</div>
            <div class="item-detail"><strong>Reason:</strong> ${esc(a.reason)}</div>
            ${a.commands ? `<div class="item-commands">${esc(a.commands)}</div>` : ''}
        </div>
    `).join('');
}

function renderPrevention(tips) {
    const card = document.getElementById('preventionCard');
    const list = document.getElementById('preventionList');
    if (!tips.length) { card.style.display = 'none'; return; }

    card.style.display = 'block';
    list.innerHTML = tips.map(t => `<li>${esc(t)}</li>`).join('');
}

function esc(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
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
