import hashlib
import random
import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from urllib.request import Request, urlopen
from urllib.parse import quote
from html.parser import HTMLParser

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_data(self):
        return ''.join(self.text)

class YuyaAI:
    def __init__(self):
        self.knowledge_file = "knowledge.txt"
        self.users_file = "users.txt"
        self.conversations_dir = "conversations"
        self.smtp_email = "elammariachraf351@gmail.com"
        
        # Création des fichiers et dossiers nécessaires
        for file in [self.knowledge_file, self.users_file]:
            if not os.path.exists(file):
                open(file, 'a').close()
        
        if not os.path.exists(self.conversations_dir):
            os.makedirs(self.conversations_dir)

    def generate_user_id(self):
        """Génère un ID utilisateur unique à 10 chiffres"""
        while True:
            user_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
            if not self._check_user_id_exists(user_id):
                return user_id

    def _check_user_id_exists(self, user_id):
        """Vérifie si l'ID utilisateur existe déjà"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                for line in f:
                    if line.startswith(user_id + ':'):
                        return True
        return False

    def hash_password(self, password):
        """Hash le mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_activation_code(self):
        """Génère un code d'activation à 4 chiffres"""
        return ''.join([str(random.randint(0, 9)) for _ in range(4)])

    def send_activation_email(self, email, code):
        """Envoie un email avec le code d'activation"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_email
            msg['To'] = email
            msg['Subject'] = "Code d'activation Yuya"
            
            body = f"Votre code d'activation est : {code}"
            msg.attach(MIMEText(body, 'plain'))
            
            # Note: Dans une implémentation réelle, il faudrait configurer un serveur SMTP
            # Cette partie est simplifiée pour l'exemple
            print(f"Email envoyé à {email} avec le code {code}")
            return True
        except Exception as e:
            print(f"Erreur d'envoi d'email: {str(e)}")
            return False

    def register_user(self, email, password):
        """Inscrit un nouvel utilisateur"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "message": "Email invalide"}
        
        # Vérification si l'email existe déjà
        with open(self.users_file, 'r') as f:
            for line in f:
                if email in line:
                    return {"success": False, "message": "Email déjà utilisé"}
        
        user_id = self.generate_user_id()
        hashed_password = self.hash_password(password)
        activation_code = self.generate_activation_code()
        
        # Sauvegarde de l'utilisateur avec statut inactif
        with open(self.users_file, 'a') as f:
            f.write(f"{user_id}:{email}:{hashed_password}:inactive:{activation_code}\n")
        
        # Envoi du code d'activation
        if self.send_activation_email(email, activation_code):
            return {
                "success": True,
                "message": "Inscription réussie. Veuillez vérifier votre email pour le code d'activation.",
                "user_id": user_id
            }
        else:
            return {"success": False, "message": "Erreur lors de l'envoi du code d'activation"}

    def activate_account(self, user_id, code):
        """Active le compte utilisateur avec le code reçu"""
        lines = []
        found = False
        success = False
        
        with open(self.users_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if line.startswith(f"{user_id}:"):
                found = True
                parts = line.strip().split(':')
                if len(parts) >= 5 and parts[3] == "inactive" and parts[4] == code:
                    lines[i] = f"{user_id}:{parts[1]}:{parts[2]}:active\n"
                    success = True
                break
        
        if found and success:
            with open(self.users_file, 'w') as f:
                f.writelines(lines)
            return {"success": True, "message": "Compte activé avec succès"}
        
        return {"success": False, "message": "Code d'activation invalide"}

    def login(self, email, password):
        """Authentifie un utilisateur"""
        hashed_password = self.hash_password(password)
        
        with open(self.users_file, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 4 and parts[1] == email and parts[2] == hashed_password:
                    if parts[3] == "active":
                        return {
                            "success": True,
                            "message": "Connexion réussie",
                            "user_id": parts[0]
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Compte non activé"
                        }
        
        return {"success": False, "message": "Email ou mot de passe incorrect"}

    def search_web(self, query):
        """Recherche des informations sur le web sans API"""
        try:
            encoded_query = quote(query)
            # Simulation d'une recherche web simple (à adapter selon les besoins)
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = Request(
                f"https://ddg.gg/search?q={encoded_query}",
                headers=headers
            )
            response = urlopen(req).read().decode()
            
            # Extraction et nettoyage du texte
            stripper = HTMLStripper()
            stripper.feed(response)
            text = stripper.get_data()
            
            # Sauvegarde dans la base de connaissances
            with open(self.knowledge_file, 'a') as f:
                f.write(f"Q: {query}\nA: {text}\n\n")
            
            return text
        except Exception as e:
            return f"Erreur lors de la recherche : {str(e)}"

    def save_conversation(self, user_id, message, response):
        """Sauvegarde une conversation"""
        conversation_file = os.path.join(
            self.conversations_dir,
            f"conversation_{user_id}.txt"
        )
        
        with open(conversation_file, 'a') as f:
            f.write(f"User: {message}\nYuya: {response}\n\n")

    def get_conversation_history(self, user_id):
        """Récupère l'historique des conversations"""
        conversation_file = os.path.join(
            self.conversations_dir,
            f"conversation_{user_id}.txt"
        )
        
        if os.path.exists(conversation_file):
            with open(conversation_file, 'r') as f:
                return f.read()
        return ""

    def process_query(self, user_id, query):
        """Traite une requête utilisateur"""
        # Recherche dans la base de connaissances locale
        response = None
        with open(self.knowledge_file, 'r') as f:
            content = f.read()
            if query in content:
                response = content.split(query)[1].split('\n\n')[0].strip()
        
        # Si pas trouvé, recherche sur le web
        if not response:
            print("Recherche sur Internet...")
            response = self.search_web(query)
        
        # Sauvegarde de la conversation
        self.save_conversation(user_id, query, response)
        
        return {
            "success": True,
            "response": response,
            "source": "Internet" if not response else "Base de connaissances"
        }

# Instance globale de l'IA
yuya = YuyaAI()

# Point d'entrée pour le serveur web (à implémenter selon les besoins)
if __name__ == "__main__":
    print("Yuya AI Backend démarré...")