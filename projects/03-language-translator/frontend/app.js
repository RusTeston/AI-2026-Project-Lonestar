// Lambda Function URL - UPDATE THIS AFTER DEPLOYMENT
const LAMBDA_URL = 'https://3usd2qizpvp57tsk6b4qkifnym0lnkdi.lambda-url.us-east-1.on.aws/';

// Language options
const languages = [
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'ja', name: 'Japanese' },
    { code: 'zh', name: 'Chinese (Simplified)' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'it', name: 'Italian' },
    { code: 'ko', name: 'Korean' }
];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    populateLanguageSelectors();
    updateCharCounter();
});

// Populate language dropdowns
function populateLanguageSelectors() {
    const sourceSelect = document.getElementById('sourceLanguage');
    const targetSelect = document.getElementById('targetLanguage');
    
    // Add auto-detect option for source
    const autoOption = document.createElement('option');
    autoOption.value = 'auto';
    autoOption.textContent = 'Auto-detect';
    sourceSelect.appendChild(autoOption);
    
    // Add English option for source
    const enSourceOption = document.createElement('option');
    enSourceOption.value = 'en';
    enSourceOption.textContent = 'English';
    enSourceOption.selected = true;
    sourceSelect.appendChild(enSourceOption);
    
    // Add English option for target
    const enTargetOption = document.createElement('option');
    enTargetOption.value = 'en';
    enTargetOption.textContent = 'English';
    targetSelect.appendChild(enTargetOption);
    
    // Add all languages to both selectors
    languages.forEach(lang => {
        const sourceOption = document.createElement('option');
        sourceOption.value = lang.code;
        sourceOption.textContent = lang.name;
        sourceSelect.appendChild(sourceOption);
        
        const targetOption = document.createElement('option');
        targetOption.value = lang.code;
        targetOption.textContent = lang.name;
        targetSelect.appendChild(targetOption);
    });
    
    // Set Spanish as default target
    targetSelect.value = 'es';
}

// Update character counter
function updateCharCounter() {
    const textarea = document.getElementById('inputText');
    const counter = document.getElementById('charCounter');
    const length = textarea.value.length;
    counter.textContent = `${length} / 5000 characters`;
    
    if (length > 5000) {
        counter.style.color = '#c33';
    } else {
        counter.style.color = '#666';
    }
}

// Translate text
async function translateText() {
    const inputText = document.getElementById('inputText').value.trim();
    const sourceLanguage = document.getElementById('sourceLanguage').value;
    const targetLanguage = document.getElementById('targetLanguage').value;
    const translateButton = document.getElementById('translateButton');
    const resultBox = document.getElementById('resultBox');
    const errorMessage = document.getElementById('errorMessage');
    
    // Hide error message
    errorMessage.classList.remove('show');
    
    // Validate input
    if (!inputText) {
        showError('Please enter text to translate');
        return;
    }
    
    if (inputText.length > 5000) {
        showError('Text is too long. Maximum 5000 characters.');
        return;
    }
    
    // Disable button and show loading
    translateButton.disabled = true;
    translateButton.innerHTML = 'Translating<span class="loading"></span><span class="loading"></span><span class="loading"></span>';
    resultBox.textContent = 'Translating...';
    resultBox.classList.add('empty');
    
    try {
        // Call Lambda function
        const response = await fetch(LAMBDA_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: inputText,
                sourceLanguage: sourceLanguage,
                targetLanguage: targetLanguage
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display translated text
        resultBox.textContent = data.translatedText;
        resultBox.classList.remove('empty');
        
    } catch (error) {
        console.error('Translation error:', error);
        showError('Translation failed. Please try again.');
        resultBox.textContent = 'Translation failed';
        resultBox.classList.add('empty');
    } finally {
        // Re-enable button
        translateButton.disabled = false;
        translateButton.textContent = 'Translate';
    }
}

// Clear all fields
function clearAll() {
    document.getElementById('inputText').value = '';
    document.getElementById('resultBox').textContent = 'Translation will appear here...';
    document.getElementById('resultBox').classList.add('empty');
    document.getElementById('errorMessage').classList.remove('show');
    updateCharCounter();
    document.getElementById('inputText').focus();
}

// Show error message
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

// Test mode for local testing
const TEST_MODE = false;

if (TEST_MODE) {
    console.log('Running in TEST MODE');
    
    window.translateText = async function() {
        const inputText = document.getElementById('inputText').value.trim();
        const targetLanguage = document.getElementById('targetLanguage').value;
        const resultBox = document.getElementById('resultBox');
        
        if (!inputText) {
            showError('Please enter text to translate');
            return;
        }
        
        // Simulate translation delay
        resultBox.textContent = 'Translating...';
        resultBox.classList.add('empty');
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock translation
        const mockTranslations = {
            'en': 'Hello, this is a test translation.',
            'es': 'Hola, esta es una traducción de prueba.',
            'fr': 'Bonjour, ceci est une traduction de test.',
            'de': 'Hallo, das ist eine Testübersetzung.',
            'ja': 'こんにちは、これはテスト翻訳です。',
            'zh': '你好，这是一个测试翻译。',
            'pt': 'Olá, esta é uma tradução de teste.',
            'it': 'Ciao, questa è una traduzione di prova.',
            'ko': '안녕하세요, 이것은 테스트 번역입니다.'
        };
        
        resultBox.textContent = mockTranslations[targetLanguage] || 'Test translation';
        resultBox.classList.remove('empty');
    };
}
