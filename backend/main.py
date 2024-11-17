from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hashlib
import random
import json
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Configuration email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "elammariachraf351@gmail.com"
SENDER_PASSWORD = "slvt zmtn bevd iwqn"  # Utilisez un mot de passe d'application Google

class User:
    def __init__(self, user_id, email, password_hash, status="inactive"):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.status = status

def save_user(user):
    with open('users.txt', 'a') as f:
        f.write(f"{user.user_id}:{user.email}:{user.password_hash}:{user.status}\n")

def get_user(email):
    if not os.path.exists('users.txt'):
        return None
    with open('users.txt', 'r') as f:
        for line in f:
            user_id, user_email, password_hash, status = line.strip().split(':')
            if user_email == email:
                return User(user_id, user_email, password_hash, status)
    return None

def send_activation_code(email, code):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = "Code d'activation Yuya"
    
    body = f"Votre code d'activation est : {code}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erreur d'envoi d'email: {str(e)}")
        return False

def search_web(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for div in soup.find_all('div', class_='g'):
            title = div.find('h3')
            link = div.find('a')
            snippet = div.find('div', class_='VwiC3b')
            
            if title and link and snippet:
                results.append({
                    'title': title.text,
                    'link': link['href'],
                    'snippet': snippet.text
                })
        
        return results[:3]  # Retourne les 3 premiers résultats
    except Exception as e:
        print(f"Erreur de recherche: {str(e)}")
        return []

def save_conversation(user_id, query, response):
    filename = f"conversations/{user_id}.json"
    os.makedirs('conversations', exist_ok=True)
    
    conversation = {
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'response': response
    }
    
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                conversations = json.load(f)
        else:
            conversations = []
            
        conversations.append(conversation)
        
        with open(filename, 'w') as f:
            json.dump(conversations, f, indent=2)
            
    except Exception as e:
        print(f"Erreur de sauvegarde de conversation: {str(e)}")

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if get_user(email):
        return jsonify({'error': 'Email déjà utilisé'}), 400
    
    user_id = str(random.randint(1000000000, 9999999999))
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    activation_code = str(random.randint(1000, 9999))
    
    if send_activation_code(email, activation_code):
        user = User(user_id, email, password_hash)
        save_user(user)
        return jsonify({'message': 'Inscription réussie', 'activation_code': activation_code})
    else:
        return jsonify({'error': "Erreur d'envoi du code d'activation"}), 500

@app.route('/api/activate', methods=['POST'])
def activate():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    
    # Dans un cas réel, vous devriez vérifier le code avec celui stocké
    # Ici, nous simulons simplement l'activation
    user = get_user(email)
    if user and user.status == "inactive":
        # Mettre à jour le statut de l'utilisateur
        # Dans un cas réel, vous devriez mettre à jour le fichier users.txt
        return jsonify({'message': 'Compte activé avec succès'})
    return jsonify({'error': "Erreur d'activation"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = get_user(email)
    if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
        return jsonify({'message': 'Connexion réussie', 'user_id': user.user_id})
    return jsonify({'error': 'Identifiants invalides'}), 401

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('query')
    user_id = data.get('user_id')
    
    # Recherche sur le web
    print(f"Recherche sur Internet pour: {query}")
    results = search_web(query)
    
    # Formatage de la réponse
    response = {
        'answer': "Je recherche des informations pertinentes...",
        'sources': results
    }
    
    # Sauvegarde de la conversation
    save_conversation(user_id, query, response)
    
    return jsonify(response)

if __name__ == '__main__':
    print("=== Démarrage du serveur Yuya ===")
    print("Le serveur est accessible à l'adresse: http://localhost:5000")
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    app.run(debug=True, port=5000)