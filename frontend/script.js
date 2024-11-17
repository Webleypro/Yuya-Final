// Variables globales
let currentUserId = null;
let isAuthenticated = false;
let currentConversationId = null;

// Configuration de base
const API_BASE_URL = 'http://localhost:5000';

// Éléments du DOM
const authContainer = document.getElementById('auth-container');
const mainContainer = document.getElementById('main-container');
const sidebar = document.getElementById('sidebar');
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const statusIndicator = document.getElementById('status-indicator');
const toggleSidebarButton = document.getElementById('toggle-sidebar');

// Formulaires
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const activationForm = document.getElementById('activation-form');

// Gestionnaires d'événements
loginForm.addEventListener('submit', handleLogin);
registerForm.addEventListener('submit', handleRegister);
activationForm.addEventListener('submit', handleActivation);

sendButton.addEventListener('click', handleSendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

toggleSidebarButton.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = `${userInput.scrollHeight}px`;
});

// Fonctions d'authentification
async function handleLogin(e) {
    e.preventDefault();
    const email = loginForm.querySelector('input[type="email"]').value;
    const password = loginForm.querySelector('input[type="password"]').value;

    showStatus('Connexion en cours...');

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (data.success) {
            currentUserId = data.user_id;
            isAuthenticated = true;
            showMainInterface();
            loadConversations();
        } else {
            showStatus(data.message, 'error');
        }
    } catch (error) {
        showStatus('Erreur de connexion', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const email = registerForm.querySelector('input[type="email"]').value;
    const password = registerForm.querySelector('input[type="password"]').value;

    showStatus('Inscription en cours...');

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (data.success) {
            currentUserId = data.user_id;
            showActivationForm();
            showStatus('Veuillez vérifier votre email pour le code d\'activation');
        } else {
            showStatus(data.message, 'error');
        }
    } catch (error) {
        showStatus('Erreur lors de l\'inscription', 'error');
    }
}

async function handleActivation(e) {
    e.preventDefault();
    const code = activationForm.querySelector('input').value;

    showStatus('Activation en cours...');

    try {
        const response = await fetch(`${API_BASE_URL}/activate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId, code }),
        });

        const data = await response.json();

        if (data.success) {
            isAuthenticated = true;
            showMainInterface();
            showStatus('Compte activé avec succès');
        } else {
            showStatus(data.message, 'error');
        }
    } catch (error) {
        showStatus('Erreur lors de l\'activation', 'error');
    }
}

// Gestion de l'interface principale
async function handleSendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage(message, 'user');
    userInput.value = '';
    showStatus('Yuya réfléchit...');

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId, query: message }),
        });

        const data = await response.json();

        if (data.success) {
            appendMessage(data.response, 'ai', data.source);
        } else {
            showStatus('Erreur lors du traitement de la requête', 'error');
        }
    } catch (error) {
        showStatus('Erreur de communication avec le serveur', 'error');
    }
}

function appendMessage(content, type, source = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = content;

    if (type === 'ai' && source) {
        const sourceLink = document.createElement('a');
        sourceLink.href = source;
        sourceLink.target = '_blank';
        sourceLink.textContent = 'Source';
        messageDiv.appendChild(sourceLink);
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Fonctions utilitaires
function showStatus(message, type = 'info') {
    statusIndicator.textContent = message;
    statusIndicator.className = `status-indicator ${type}`;
    statusIndicator.style.display = 'block';

    setTimeout(() => {
        statusIndicator.style.display = 'none';
    }, 3000);
}

function showMainInterface() {
    authContainer.classList.add('hidden');
    mainContainer.classList.remove('hidden');
}

function showActivationForm() {
    loginForm.classList.add('hidden');
    registerForm.classList.add('hidden');
    activationForm.classList.remove('hidden');
}
