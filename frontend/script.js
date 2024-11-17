// Variables globales
let currentUser = null;
let conversationHistory = [];
let sidebarOpen = false;

// Fonctions d'authentification
function showLogin() {
    document.querySelector('#login-form').classList.remove('hidden');
    document.querySelector('#register-form').classList.add('hidden');
    document.querySelector('#activation-form').classList.add('hidden');
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelector('.tab:first-child').classList.add('active');
}

function showRegister() {
    document.querySelector('#login-form').classList.add('hidden');
    document.querySelector('#register-form').classList.remove('hidden');
    document.querySelector('#activation-form').classList.add('hidden');
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelector('.tab:last-child').classList.add('active');
}

async function handleLogin(event) {
    event.preventDefault();
    const form = document.querySelector('#login-form');
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('http://localhost:5000/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = { id: data.user_id, email };
            showMainInterface();
            loadConversations();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Erreur de connexion au serveur');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const form = document.querySelector('#register-form');
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('http://localhost:5000/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.querySelector('#activation-form').classList.remove('hidden');
            document.querySelector('#register-form').classList.add('hidden');
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Erreur de connexion au serveur');
    }
}

async function handleActivation(event) {
    event.preventDefault();
    const code = document.querySelector('#activation-form input').value;
    const email = document.querySelector('#register-form input[type="email"]').value;

    try {
        const response = await fetch('http://localhost:5000/api/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Compte activé avec succès');
            showLogin();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Erreur de connexion au serveur');
    }
}

// Interface principale
function showMainInterface() {
    document.querySelector('#auth-container').classList.add('hidden');
    document.querySelector('#main-container').classList.remove('hidden');
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebarOpen = !sidebarOpen;
    sidebar.classList.toggle('open');
}

async function loadConversations() {
    // Cette fonction serait utilisée pour charger l'historique des conversations
    // depuis le serveur
    try {
        const response = await fetch(`http://localhost:5000/api/conversations/${currentUser.id}`);
        const data = await response.json();
        
        const conversationsList = document.querySelector('#conversations-list');
        conversationsList.innerHTML = '';
        
        data.forEach(conversation => {
            const element = document.createElement('div');
            element.className = 'conversation-item';
            element.textContent = conversation.title;
            element.onclick = () => loadConversation(conversation.id);
            conversationsList.appendChild(element);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des conversations:', error);
    }
}

function createMessage(text, isUser = false) {
    const message = document.createElement('div');
    message.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    if (!isUser) {
        // Effet de frappe pour les réponses de l'IA
        let index = 0;
        message.textContent = '';
        
        function typeWriter() {
            if (index < text.length) {
                message.textContent += text.charAt(index);
                index++;
                setTimeout(typeWriter, 20);
            }
        }
        
        typeWriter();
    } else {
        message.textContent = text;
    }
    
    return message;
}

async function sendMessage() {
    const input = document.querySelector('#user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    const chatContainer = document.querySelector('#chat-container');
    chatContainer.appendChild(createMessage(message, true));
    
    input.value = '';
    
    try {
        const response = await fetch('http://localhost:5000/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: message,
                user_id: currentUser.id
            })
        });
        
        const data = await response.json();
        
        // Création de la réponse avec mots-clés cliquables
        const aiMessage = createMessage(data.answer, false);
        
        // Ajout des sources comme mots-clés cliquables
        if (data.sources && data.sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            data.sources.forEach(source => {
                const keyword = document.createElement('span');
                keyword.className = 'keyword';
                keyword.textContent = source.title;
                keyword.onclick = () => window.open(source.link, '_blank');
                sourcesDiv.appendChild(keyword);
            });
            aiMessage.appendChild(sourcesDiv);
        }
        
        chatContainer.appendChild(aiMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
    } catch (error) {
        alert('Erreur lors de l\'envoi du message');
    }
}

// Event Listeners
document.querySelector('#login-form').addEventListener('submit', handleLogin);
document.querySelector('#register-form').addEventListener('submit', handleRegister);
document.querySelector('#activation-form').addEventListener('submit', handleActivation);

document.querySelector('#user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Initialize
showLogin();